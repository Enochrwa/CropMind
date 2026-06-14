from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import uuid
from datetime import datetime


class UserCreate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str
    full_name: Optional[str] = None
    language: str = "en"
    country_code: Optional[str] = None
    region: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    identifier: str  # phone or email
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    phone: Optional[str]
    email: Optional[str]
    full_name: Optional[str]
    language: str
    country_code: Optional[str]
    region: Optional[str]
    balance_rwf: float
    diagnosis_count: int
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
