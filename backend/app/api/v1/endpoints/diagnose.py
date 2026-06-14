from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.session import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.schemas.diagnosis import DiagnoseRequest, DiagnoseResponse
from app.services.diagnosis_service import enrich_diagnosis
from app.services.whisper_service import transcribe_audio
from app.services.llm_service import generate_chat_response

router = APIRouter(prefix="/diagnose", tags=["diagnosis"])


@router.post("/enrich", response_model=DiagnoseResponse)
async def enrich(
    payload: DiagnoseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Takes the on-device model prediction and enriches it with:
    - Verified disease info
    - AI treatment plan (Mistral 7B)
    - Nearby supplier lookup (PostGIS)
    - Local market prices
    Deducts balance accordingly.
    """
    try:
        return await enrich_diagnosis(payload, current_user, db)
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


@router.post("/voice-question")
async def voice_question(
    audio: UploadFile = File(...),
    diagnosis_id: str = Form(...),
    crop_type: str = Form(...),
    disease_name: str = Form(...),
    region: str = Form(default="Unknown"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Transcribes farmer's voice question via Whisper,
    then generates AI agronomist response via Mistral 7B.
    """
    audio_bytes = await audio.read()
    text, detected_lang = await transcribe_audio(audio_bytes, current_user.language)
    if not text:
        raise HTTPException(status_code=422, detail="Could not transcribe audio")

    response = await generate_chat_response(
        question=text,
        crop_type=crop_type,
        disease_name=disease_name,
        language=current_user.language,
        region=region,
    )
    return {"question": text, "answer": response, "language": detected_lang}
