"""
Whisper voice transcription service.
Uses faster-whisper (CTranslate2) — 4x faster than openai-whisper on CPU.
"""
from typing import Tuple
from loguru import logger

_model = None


def load_whisper() -> None:
    global _model
    try:
        from faster_whisper import WhisperModel
        from app.core.config import settings
        _model = WhisperModel(settings.WHISPER_MODEL, device=settings.WHISPER_DEVICE, compute_type="int8")
        logger.info(f"Whisper model loaded: {settings.WHISPER_MODEL}")
    except Exception as e:
        logger.warning(f"Whisper not available: {e}")


async def transcribe_audio(audio_bytes: bytes, language: str = None) -> Tuple[str, str]:
    """Returns (transcription_text, detected_language)."""
    if _model is None:
        return "", "en"
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        segments, info = _model.transcribe(
            tmp_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(s.text for s in segments).strip()
        return text, info.language
    except Exception as e:
        logger.error(f"Whisper transcription error: {e}")
        return "", "en"
    finally:
        os.unlink(tmp_path)
