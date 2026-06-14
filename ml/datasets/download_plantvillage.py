"""
Download and prepare the PlantVillage dataset for CropMind training.
Dataset: 54,305 images, 38 classes (plant diseases + healthy)
Source : Kaggle (open license)

Usage:
    pip install kaggle
    # Set up ~/.kaggle/kaggle.json with your API key
    python download_plantvillage.py
"""
import os
import subprocess
import zipfile
from pathlib import Path

DATASET = "abdallahalidev/plantvillage-dataset"
OUTPUT_DIR = "./plantvillage"


def download():
    print("⬇️  Downloading PlantVillage dataset from Kaggle...")
    subprocess.run([
        "kaggle", "datasets", "download",
        "-d", DATASET,
        "-p", ".",
        "--unzip",
    ], check=True)
    print(f"✅ Dataset ready at: {OUTPUT_DIR}")
    # Count images
    total = sum(1 for _ in Path(OUTPUT_DIR).rglob("*.jpg"))
    total += sum(1 for _ in Path(OUTPUT_DIR).rglob("*.JPG"))
    print(f"📸 Total images: {total:,}")


if __name__ == "__main__":
    download()
