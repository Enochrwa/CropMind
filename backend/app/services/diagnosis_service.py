"""
Core diagnosis enrichment service.
Takes device prediction → returns full enrichment (treatment, suppliers, prices, AI advisory).
"""
import json
import uuid
from typing import Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.models.user import User
from app.models.diagnosis import Diagnosis
from app.models.balance import BalanceTransaction, TransactionType
from app.schemas.diagnosis import DiagnoseRequest, DiagnoseResponse, EnrichmentResult
from app.ml.disease_classes import get_disease_info
from app.services.supplier_service import find_nearby_suppliers
from app.services.market_price_service import get_market_prices
from app.services.llm_service import generate_treatment_plan
from app.services.translation_service import translate_enrichment


async def enrich_diagnosis(
    request: DiagnoseRequest,
    user: User,
    db: AsyncSession,
) -> DiagnoseResponse:
    """Main enrichment pipeline."""

    # 1. Balance check
    cost = settings.DIAGNOSIS_COST_RWF
    if user.balance_rwf < cost:
        raise ValueError(f"Insufficient balance. Need {cost} RWF, have {user.balance_rwf:.0f} RWF.")

    # 2. Resolve disease info
    disease_info = get_disease_info(request.device_prediction, request.language)

    # 3. Get treatment plan from LLM
    treatment_data = await generate_treatment_plan(
        disease_key=request.device_prediction,
        crop_type=request.crop_type,
        severity=disease_info["severity"],
        language=request.language,
        confidence=request.device_confidence,
    )

    # 4. Find nearby suppliers
    suppliers = []
    if request.latitude and request.longitude:
        suppliers = await find_nearby_suppliers(
            disease_key=request.device_prediction,
            lat=request.latitude,
            lng=request.longitude,
            db=db,
        )

    # 5. Market prices
    market_prices = await get_market_prices(
        crop_type=request.crop_type,
        country=user.country_code or "RW",
    )

    # 6. Build enrichment result
    enrichment = EnrichmentResult(
        disease_display_name=disease_info["display_name"],
        severity=disease_info["severity"],
        confidence=request.device_confidence,
        description=treatment_data.get("description", ""),
        urgency_message=treatment_data.get("urgency_message", ""),
        treatment_steps=treatment_data.get("steps", []),
        prevention_tips=treatment_data.get("prevention", []),
        suppliers=suppliers,
        market_prices=market_prices,
        language=request.language,
    )

    # 7. Deduct balance (atomic)
    new_balance = user.balance_rwf - cost
    await db.execute(
        update(User)
        .where(User.id == user.id)
        .values(
            balance_rwf=new_balance,
            diagnosis_count=User.diagnosis_count + 1,
        )
    )

    # 8. Record transaction
    tx = BalanceTransaction(
        user_id=user.id,
        type=TransactionType.DIAGNOSIS,
        amount_rwf=-cost,
        balance_after=new_balance,
        description=f"Diagnosis: {disease_info['display_name']} on {request.crop_type}",
    )
    db.add(tx)

    # 9. Save diagnosis record
    diag = Diagnosis(
        user_id=user.id,
        farm_id=request.farm_id,
        device_prediction=request.device_prediction,
        device_confidence=request.device_confidence,
        confirmed_disease=request.device_prediction,
        disease_display_name=disease_info["display_name"],
        severity=disease_info["severity"],
        confidence=request.device_confidence,
        crop_type=request.crop_type,
        treatment_plan=json.dumps(treatment_data),
        suppliers_nearby=json.dumps([s.model_dump() for s in suppliers]),
        market_price_data=json.dumps([p.model_dump() for p in market_prices]),
        language=request.language,
        cost_rwf=cost,
        is_enriched=True,
        image_key=request.image_key,
    )

    if request.latitude and request.longitude:
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point
        diag.location = from_shape(Point(request.longitude, request.latitude), srid=4326)
        diag.country = user.country_code
        diag.region = user.region

    db.add(diag)
    await db.flush()

    logger.info(f"Diagnosis enriched: {diag.id} | user={user.id} | disease={request.device_prediction}")

    return DiagnoseResponse(
        diagnosis_id=diag.id,
        is_enriched=True,
        cost_rwf=cost,
        balance_remaining=new_balance,
        result=enrichment,
        created_at=diag.created_at,
    )
