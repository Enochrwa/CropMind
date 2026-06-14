"""
CropMind Disease Classifier Training Script
============================================
Model  : MobileNetV3-Small (fine-tuned)
Dataset: PlantVillage (38 classes, 54,305 images)
Output : cropmind_v1.tflite (on-device) + cropmind_v1.onnx (server)
Runtime: ~2-4 hours on Google Colab T4 GPU (free tier)

Usage:
    python train_mobilenet.py --data_dir ./datasets/plantvillage --epochs 30

Colab notebook: ../notebooks/01_train_classifier.ipynb
"""
import argparse
import os
import json
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
from torchvision.models import MobileNet_V3_Small_Weights
from torch.optim.lr_scheduler import CosineAnnealingLR
import numpy as np


def get_transforms(is_train: bool):
    if is_train:
        return transforms.Compose([
            transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            transforms.RandomRotation(30),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def build_model(num_classes: int) -> nn.Module:
    model = models.mobilenet_v3_small(weights=MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    # Replace classifier head for our number of classes
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def export_onnx(model, output_path: str, num_classes: int):
    model.eval()
    dummy = torch.randn(1, 3, 224, 224)
    torch.onnx.export(
        model, dummy, output_path,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
        opset_version=17,
    )
    print(f"✅ ONNX model saved: {output_path}")


def export_tflite(onnx_path: str, tflite_path: str):
    """Convert ONNX → TFLite via onnx-tf + TensorFlow."""
    try:
        import onnx
        from onnx_tf.backend import prepare
        import tensorflow as tf

        onnx_model = onnx.load(onnx_path)
        tf_rep = prepare(onnx_model)
        tf_rep.export_graph("/tmp/cropmind_tf")

        converter = tf.lite.TFLiteConverter.from_saved_model("/tmp/cropmind_tf")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        tflite_model = converter.convert()

        with open(tflite_path, "wb") as f:
            f.write(tflite_model)
        size_mb = os.path.getsize(tflite_path) / (1024 * 1024)
        print(f"✅ TFLite model saved: {tflite_path} ({size_mb:.1f} MB)")
    except ImportError as e:
        print(f"⚠️  TFLite export skipped (missing: {e}). ONNX model available.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", default="./datasets/plantvillage")
    parser.add_argument("--output_dir", default="../exports")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--val_split", type=float, default=0.15)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🔧 Training on: {device}")

    # Dataset
    full_dataset = datasets.ImageFolder(args.data_dir, transform=get_transforms(True))
    num_classes = len(full_dataset.classes)
    print(f"📂 Classes: {num_classes} | Images: {len(full_dataset)}")

    # Save class mapping
    os.makedirs(args.output_dir, exist_ok=True)
    class_map = {v: k for k, v in full_dataset.class_to_idx.items()}
    with open(f"{args.output_dir}/class_labels.json", "w") as f:
        json.dump(class_map, f, indent=2)

    # Split
    val_size = int(len(full_dataset) * args.val_split)
    train_size = len(full_dataset) - val_size
    train_ds, val_ds = random_split(full_dataset, [train_size, val_size])
    val_ds.dataset.transform = get_transforms(False)

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=4, pin_memory=True)

    # Model
    model = build_model(num_classes).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_val_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        scheduler.step()

        print(f"Epoch {epoch:03d}/{args.epochs} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.3f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.3f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), f"{args.output_dir}/cropmind_best.pth")
            print(f"  ✅ New best: {best_val_acc:.3f}")

    print(f"\n🎯 Training complete. Best val accuracy: {best_val_acc:.3f}")

    # Load best and export
    model.load_state_dict(torch.load(f"{args.output_dir}/cropmind_best.pth"))
    onnx_path = f"{args.output_dir}/cropmind_v1.onnx"
    tflite_path = f"{args.output_dir}/cropmind_v1.tflite"
    export_onnx(model, onnx_path, num_classes)
    export_tflite(onnx_path, tflite_path)


if __name__ == "__main__":
    main()
