import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.environ["PYTHONPATH"] = str(project_root)

import pytest
from httpx import AsyncClient
from app.db.connection import close_mongo_connection, connect_to_mongo
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def _setup_database():
    """Setup test database"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()

@pytest.fixture()
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture()
def api_headers():
    """API headers with test key"""
    return {"x-api-key": "supersecret1"}
