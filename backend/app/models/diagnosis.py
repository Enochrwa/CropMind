import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.db.session import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    farm_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("farms.id"), nullable=True)

    # Image
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    image_key: Mapped[str] = mapped_column(String(255), nullable=True)

    # On-device model output (sent by client)
    device_prediction: Mapped[str] = mapped_column(String(100), nullable=True)
    device_confidence: Mapped[float] = mapped_column(Float, nullable=True)

    # Server-side enrichment
    confirmed_disease: Mapped[str] = mapped_column(String(100), nullable=True)
    disease_display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=True)  # low / medium / high / critical
    confidence: Mapped[float] = mapped_column(Float, nullable=True)

    # Enrichment content (stored as JSON text)
    treatment_plan: Mapped[str] = mapped_column(Text, nullable=True)   # JSON
    suppliers_nearby: Mapped[str] = mapped_column(Text, nullable=True) # JSON
    market_price_data: Mapped[str] = mapped_column(Text, nullable=True) # JSON
    language: Mapped[str] = mapped_column(String(10), default="en")

    # Crop info
    crop_type: Mapped[str] = mapped_column(String(100), nullable=True)

    # Location for outbreak tracking
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)

    # Cost deducted
    cost_rwf: Mapped[int] = mapped_column(Integer, default=0)
    is_enriched: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="diagnoses")
    farm = relationship("Farm", back_populates="diagnoses")
