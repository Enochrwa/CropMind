"""
Server-side ONNX inference for enrichment layer.
The on-device TFLite model runs on the mobile app.
This runs on the server to double-check and provide richer metadata.
"""
import io
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from loguru import logger
from app.core.config import settings
from app.ml.disease_classes import CLASS_LABELS, get_disease_info

try:
    import onnxruntime as ort
    _ort_available = True
except ImportError:
    _ort_available = False
    logger.warning("onnxruntime not available — server-side inference disabled")

_session: Optional[object] = None


def load_model() -> None:
    global _session
    if not _ort_available:
        return
    try:
        _session = ort.InferenceSession(
            settings.ONNX_MODEL_PATH,
            providers=["CPUExecutionProvider"],
        )
        logger.info(f"ONNX model loaded from {settings.ONNX_MODEL_PATH}")
    except Exception as e:
        logger.warning(f"ONNX model not found: {e} — using client prediction only")


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    arr = np.array(img, dtype=np.float32) / 255.0
    # MobileNetV3 normalisation
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr - mean) / std
    return arr.transpose(2, 0, 1)[np.newaxis, :]  # NCHW


def predict(image_bytes: bytes) -> Tuple[str, float]:
    """Returns (class_label, confidence). Falls back if model not loaded."""
    if _session is None:
        return "unknown", 0.0
    try:
        input_arr = preprocess_image(image_bytes)
        input_name = _session.get_inputs()[0].name
        outputs = _session.run(None, {input_name: input_arr})
        logits = outputs[0][0]
        probs = np.exp(logits) / np.sum(np.exp(logits))
        idx = int(np.argmax(probs))
        return CLASS_LABELS[idx], float(probs[idx])
    except Exception as e:
        logger.error(f"Inference error: {e}")
        return "unknown", 0.0
