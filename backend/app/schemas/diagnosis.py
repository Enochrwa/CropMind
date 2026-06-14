from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime


class TreatmentStep(BaseModel):
    step: int
    action: str
    product: Optional[str] = None
    timing: Optional[str] = None


class MarketPrice(BaseModel):
    crop: str
    price_per_kg_rwf: float
    price_per_kg_usd: float
    market: str
    updated_at: str


class SupplierResult(BaseModel):
    id: str
    name: str
    phone: Optional[str]
    whatsapp: Optional[str]
    distance_km: float
    address: Optional[str]
    is_verified: bool
    rating: float


class EnrichmentResult(BaseModel):
    disease_display_name: str
    severity: str  # low / medium / high / critical
    confidence: float
    description: str
    urgency_message: str
    treatment_steps: List[TreatmentStep]
    prevention_tips: List[str]
    suppliers: List[SupplierResult]
    market_prices: List[MarketPrice]
    language: str


class DiagnoseRequest(BaseModel):
    # What the on-device model detected
    device_prediction: str
    device_confidence: float
    crop_type: str
    farm_id: Optional[uuid.UUID] = None
    image_key: Optional[str] = None  # S3 key after upload
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    language: str = "en"


class DiagnoseResponse(BaseModel):
    diagnosis_id: uuid.UUID
    is_enriched: bool
    cost_rwf: int
    balance_remaining: float
    result: EnrichmentResult
    created_at: datetime

    model_config = {"from_attributes": True}
