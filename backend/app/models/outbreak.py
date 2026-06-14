import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from app.db.session import Base


class OutbreakReport(Base):
    __tablename__ = "outbreak_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disease: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(100), nullable=True)
    case_count: Mapped[int] = mapped_column(Integer, default=1)
    severity_avg: Mapped[float] = mapped_column(Float, default=0.0)
    location = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    week_of: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
