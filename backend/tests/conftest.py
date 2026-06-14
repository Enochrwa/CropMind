import asyncio
import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Ensure `backend/` is on sys.path so `from app.xxx import ...` works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set env vars before any app imports
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test.db"
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-secret-key-for-ci"

# ── Patch 1: postgresql.UUID → CompatUUID (SQLite doesn't understand UUID) ──
import uuid as _uuid
from sqlalchemy import String, Text, TypeDecorator
import sqlalchemy.dialects.postgresql as pg_module


class CompatUUID(TypeDecorator):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return _uuid.UUID(str(value)) if value is not None else None


pg_module.UUID = CompatUUID

# ── Patch 2: geoalchemy2.Geography → Text (SQLite has no spatial types) ──
class CompatGeography(Text):
    """Drop-in replacement for GeoAlchemy2 Geography that works with SQLite."""
    def __init__(self, geometry_type=None, srid=None, **kwargs):
        super().__init__()

import geoalchemy2
geoalchemy2.Geography = CompatGeography
_geo_mod = sys.modules.get("geoalchemy2")
if _geo_mod:
    _geo_mod.Geography = CompatGeography

# ── Now it's safe to import the app ──────────────────────────────────────────
from app.db.session import Base, get_db, AsyncSessionLocal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import app.db.session as session_module

# Import all models so Base.metadata is fully populated
from app.models import user, balance, diagnosis, farm, outbreak, supplier  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Replace module-level engine/session with SQLite equivalents
session_module.engine = test_engine
session_module.AsyncSessionLocal = TestSessionLocal


async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


from app.main import app

app.dependency_overrides[get_db] = override_get_db


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    db_path = os.path.join(os.path.dirname(__file__), "..", "test.db")
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
