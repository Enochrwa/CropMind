"""
LLM service — uses local Ollama (Mistral 7B) to generate treatment plans
and agronomist Q&A responses.  Zero API cost.
"""
import json
import httpx
from typing import Any, Dict, List
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.config import settings

SYSTEM_PROMPT = """You are CropMind, an expert agricultural agronomist AI assistant.
You help smallholder farmers diagnose crop diseases and provide actionable treatment plans.
Always respond in the language requested. Be concise, practical, and specific.
Avoid generic advice — tailor to the exact disease, crop, and severity.
When recommending products, prefer locally available, affordable options.
Respond ONLY with valid JSON, no markdown, no extra text."""


TREATMENT_PROMPT = """Disease: {disease_key}
Crop: {crop_type}
Severity: {severity}
Detection confidence: {confidence:.0%}
Language: {language}

Generate a treatment plan as JSON with this exact structure:
{{
  "description": "2-sentence plain-language description of what this disease is",
  "urgency_message": "One sentence telling the farmer how urgently to act",
  "steps": [
    {{"step": 1, "action": "...", "product": "...", "timing": "..."}}
  ],
  "prevention": ["tip1", "tip2", "tip3"]
}}

Steps should be 3-5 practical actions. Product can be null if not applicable.
All text must be in language code: {language}"""


CHAT_PROMPT = """You are an expert agronomist helping a farmer.
Context:
- Crop: {crop_type}
- Disease: {disease_name}
- Farmer language: {language}
- Farm region: {region}

Farmer question: {question}

Answer in {language}. Be specific, practical, and encouraging. Max 150 words."""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _call_ollama(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 800,
                },
            },
        )
        response.raise_for_status()
        return response.json()["response"]


async def generate_treatment_plan(
    disease_key: str,
    crop_type: str,
    severity: str,
    language: str,
    confidence: float,
) -> Dict[str, Any]:
    prompt = TREATMENT_PROMPT.format(
        disease_key=disease_key,
        crop_type=crop_type,
        severity=severity,
        language=language,
        confidence=confidence,
    )
    try:
        raw = await _call_ollama(prompt)
        # Strip potential markdown fences
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(raw)
    except Exception as e:
        logger.error(f"LLM treatment plan error: {e}")
        return _fallback_treatment(disease_key, language)


async def generate_chat_response(
    question: str,
    crop_type: str,
    disease_name: str,
    language: str,
    region: str,
) -> str:
    prompt = CHAT_PROMPT.format(
        crop_type=crop_type,
        disease_name=disease_name,
        language=language,
        region=region,
        question=question,
    )
    try:
        system = f"You are a helpful agronomist. Respond in {language}. Be concise."
        return await _call_ollama(prompt, system=system)
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        return "I'm having trouble connecting right now. Please try again in a moment."


def _fallback_treatment(disease_key: str, language: str) -> Dict[str, Any]:
    """Static fallback if LLM is unavailable."""
    return {
        "description": f"Disease detected: {disease_key.replace('_', ' ').title()}. Please consult a local agronomist for detailed advice.",
        "urgency_message": "Act within 24-48 hours to prevent spread.",
        "steps": [
            {"step": 1, "action": "Remove and destroy severely affected plant parts", "product": None, "timing": "Immediately"},
            {"step": 2, "action": "Apply appropriate fungicide or pesticide", "product": "Ask local supplier", "timing": "Within 24 hours"},
            {"step": 3, "action": "Avoid overhead watering to reduce spread", "product": None, "timing": "Ongoing"},
        ],
        "prevention": [
            "Rotate crops each season",
            "Ensure adequate plant spacing for airflow",
            "Monitor plants weekly for early signs",
        ],
    }
