"""
Translation service using Helsinki-NLP OPUS-MT models (free, self-hosted).
Falls back gracefully if models not loaded.
"""
from typing import Optional
from loguru import logger

SUPPORTED_LANGS = {"en", "fr", "sw", "kin", "ha", "am", "pt"}
_pipelines: dict = {}


def load_translation_models() -> None:
    """Called at startup — loads Helsinki-NLP models into memory."""
    try:
        from transformers import pipeline
        pairs = [("en", "fr"), ("en", "sw"), ("fr", "en"), ("sw", "en")]
        for src, tgt in pairs:
            model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
            try:
                _pipelines[f"{src}-{tgt}"] = pipeline(
                    "translation",
                    model=model_name,
                    device=-1,  # CPU
                )
                logger.info(f"Translation model loaded: {src}→{tgt}")
            except Exception as e:
                logger.warning(f"Could not load {model_name}: {e}")
    except ImportError:
        logger.warning("transformers not available — translation disabled")


async def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    if src_lang == tgt_lang:
        return text
    key = f"{src_lang}-{tgt_lang}"
    pipe = _pipelines.get(key)
    if not pipe:
        logger.warning(f"No translation pipeline for {key}")
        return text
    try:
        result = pipe(text, max_length=512)
        return result[0]["translation_text"]
    except Exception as e:
        logger.error(f"Translation error {key}: {e}")
        return text


async def translate_enrichment(enrichment: dict, target_lang: str) -> dict:
    """Translate enrichment result dict fields if LLM didn't produce in target lang."""
    if target_lang == "en":
        return enrichment
    # In production: translate description, urgency_message, treatment steps
    # For now return as-is (LLM handles target language natively)
    return enrichment
