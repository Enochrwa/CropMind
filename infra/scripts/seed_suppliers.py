"""
Seed initial supplier data for pilot regions.
Run: python infra/scripts/seed_suppliers.py
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.supplier import Supplier
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

SEED_SUPPLIERS = [
    # Rwanda — Musanze
    {"name": "Agro-Rwanda Musanze", "phone": "+250788100001", "whatsapp": "+250788100001",
     "address": "Musanze, Northern Province, Rwanda", "country": "RW", "region": "Musanze",
     "lat": -1.4997, "lng": 29.6356,
     "products": '["tomato_late_blight","potato_late_blight","general","fungicide"]'},
    {"name": "Green Harvest Agro", "phone": "+250788100002", "whatsapp": "+250788100002",
     "address": "Kigali, Rwanda", "country": "RW", "region": "Kigali",
     "lat": -1.9441, "lng": 30.0619,
     "products": '["tomato_bacterial_spot","corn_common_rust","pesticide","fertilizer"]'},
    # Kenya — Nairobi
    {"name": "Kenya Seed Company", "phone": "+254700100001", "whatsapp": "+254700100001",
     "address": "Tom Mboya Street, Nairobi, Kenya", "country": "KE", "region": "Nairobi",
     "lat": -1.2921, "lng": 36.8219,
     "products": '["general","seed","fungicide","pesticide"]'},
    # Nigeria — Lagos
    {"name": "FarmPlus Nigeria", "phone": "+2348000100001", "whatsapp": "+2348000100001",
     "address": "Lagos Island, Lagos, Nigeria", "country": "NG", "region": "Lagos",
     "lat": 6.4541, "lng": 3.3947,
     "products": '["tomato_early_blight","corn_northern_leaf_blight","fungicide"]'},
]

async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession)

    async with async_session() as session:
        for data in SEED_SUPPLIERS:
            supplier = Supplier(
                name=data["name"],
                phone=data["phone"],
                whatsapp=data["whatsapp"],
                address=data["address"],
                country=data["country"],
                region=data["region"],
                products=data["products"],
                location=from_shape(Point(data["lng"], data["lat"]), srid=4326),
                is_verified=True,
                rating=4.5,
                rating_count=10,
            )
            session.add(supplier)
        await session.commit()
        print(f"✅ Seeded {len(SEED_SUPPLIERS)} suppliers")

if __name__ == "__main__":
    asyncio.run(seed())
