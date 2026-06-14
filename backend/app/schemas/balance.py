from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from app.models.balance import TransactionType


class TopUpRequest(BaseModel):
    amount_rwf: float
    payment_method: str = "stripe"  # stripe | momo | cash_agent
    payment_reference: Optional[str] = None


class BalanceOut(BaseModel):
    balance_rwf: float
    user_id: uuid.UUID


class TransactionOut(BaseModel):
    id: uuid.UUID
    type: TransactionType
    amount_rwf: float
    balance_after: float
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
