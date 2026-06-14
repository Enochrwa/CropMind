import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


async def get_token(client, phone="+250780100001"):
    r = await client.post("/api/v1/auth/register", json={
        "phone": phone, "password": "testpass123"
    })
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_topup(client_fixture):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_token(client)
        response = await client.post(
            "/api/v1/balance/topup",
            json={"amount_rwf": 2000, "payment_reference": "test_ref_001"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["balance_rwf"] == 2000.0


@pytest.mark.asyncio
async def test_topup_below_minimum():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_token(client, "+250780100002")
        response = await client.post(
            "/api/v1/balance/topup",
            json={"amount_rwf": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
