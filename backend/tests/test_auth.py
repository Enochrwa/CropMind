import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={
        "phone": "+250780000001",
        "password": "securepassword",
        "full_name": "Test Farmer",
        "language": "kin",
        "country_code": "RW",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["language"] == "kin"


@pytest.mark.asyncio
async def test_register_duplicate(client):
    payload = {"phone": "+250780000002", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login(client):
    phone = "+250780000003"
    await client.post("/api/v1/auth/register", json={"phone": phone, "password": "mypass123"})
    response = await client.post("/api/v1/auth/login", json={
        "identifier": phone, "password": "mypass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    phone = "+250780000004"
    await client.post("/api/v1/auth/register", json={"phone": phone, "password": "correct"})
    response = await client.post("/api/v1/auth/login", json={
        "identifier": phone, "password": "wrong"
    })
    assert response.status_code == 401
