"""
测试配置
SCALE OS v10.0
"""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def client():
    """HTTP 客户端"""
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac