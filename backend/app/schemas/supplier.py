from pydantic import BaseModel
from typing import Optional
import uuid


class SupplierOut(BaseModel):
    id: uuid.UUID
    name: str
    phone: Optional[str]
    whatsapp: Optional[str]
    address: Optional[str]
    country: str
    region: Optional[str]
    is_verified: bool
    rating: float
    rating_count: int

    model_config = {"from_attributes": True}
