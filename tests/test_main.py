import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "GitHub Badge API" in response.json()["message"]

@pytest.mark.asyncio
async def test_custom_badge():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/badge/custom?label=Hello&value=World")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert b"Hello: World" in response.content