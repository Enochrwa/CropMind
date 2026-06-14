"""
Crop market price service.
In production: pull from open govt APIs / FAO / partner feeds.
For MVP: seeded static data per country + crop, updated weekly via Celery task.
"""
from typing import List
from datetime import datetime
from app.schemas.diagnosis import MarketPrice

# Seed prices (RWF/kg) — replace with DB lookup / live API
PRICE_SEED = {
    "RW": {
        "tomato": 500,
        "potato": 200,
        "corn": 150,
        "bean": 700,
        "cassava": 120,
        "banana": 300,
        "default": 200,
    },
    "KE": {
        "tomato": 45,   # KES
        "potato": 30,
        "corn": 25,
        "bean": 80,
        "default": 35,
    },
    "NG": {
        "tomato": 400,  # NGN
        "potato": 300,
        "corn": 180,
        "default": 250,
    },
}

CURRENCY_TO_RWF = {
    "RW": 1.0,
    "KE": 7.5,   # approximate
    "NG": 0.55,
    "UG": 0.22,
}

USD_RATE = 1200  # 1 USD ≈ 1200 RWF


async def get_market_prices(crop_type: str, country: str = "RW") -> List[MarketPrice]:
    country_prices = PRICE_SEED.get(country.upper(), PRICE_SEED["RW"])
    crop_key = crop_type.lower().split()[0]
    price_local = country_prices.get(crop_key, country_prices["default"])
    rate = CURRENCY_TO_RWF.get(country.upper(), 1.0)
    price_rwf = price_local * rate
    price_usd = price_rwf / USD_RATE

    return [
        MarketPrice(
            crop=crop_type,
            price_per_kg_rwf=round(price_rwf, 0),
            price_per_kg_usd=round(price_usd, 3),
            market=f"Local market ({country})",
            updated_at=datetime.utcnow().strftime("%Y-%m-%d"),
        )
    ]
