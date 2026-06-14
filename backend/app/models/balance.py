import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
import enum


class TransactionType(str, enum.Enum):
    TOPUP = "topup"
    DIAGNOSIS = "diagnosis"
    VOICE = "voice"
    REFUND = "refund"
    BONUS = "bonus"


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount_rwf: Mapped[float] = mapped_column(Float, nullable=False)  # positive = credit, negative = debit
    balance_after: Mapped[float] = mapped_column(Float, nullable=False)
    reference_id: Mapped[str] = mapped_column(String(255), nullable=True)  # diagnosis_id, payment_id etc.
    description: Mapped[str] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
