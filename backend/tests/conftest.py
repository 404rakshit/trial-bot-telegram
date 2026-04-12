"""Pytest configuration and fixtures"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis

from app.main import app
from app.core.database import Base, get_db
from app.core.redis_client import get_redis
from app.models.user import User
from app.models.reminder import UseCaseTemplate


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database for each test"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Provide session
    async with async_session() as session:
        yield session

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_redis():
    """Mock Redis client for tests"""
    # Use fakeredis for testing
    from fakeredis import aioredis as fake_aioredis
    redis = await fake_aioredis.create_redis_pool()
    yield redis
    redis.close()
    await redis.wait_closed()


@pytest.fixture
async def client(test_db: AsyncSession, test_redis: Redis) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database and redis overrides"""

    async def override_get_db():
        yield test_db

    async def override_get_redis():
        return test_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """Create a test user"""
    user = User(
        chat_id=123456789,
        latitude=40.7128,
        longitude=-74.0060,
        timezone="America/New_York"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    return user


@pytest.fixture
async def test_template(test_db: AsyncSession) -> UseCaseTemplate:
    """Create a test template"""
    template = UseCaseTemplate(
        name="Test Rain Alert",
        description="Test template",
        condition="rain",
        hours_ahead=6,
        message_template="Test message",
        is_active=True
    )
    test_db.add(template)
    await test_db.commit()
    await test_db.refresh(template)
    return template


@pytest.fixture
async def test_session_id(test_redis: Redis, test_user: User) -> str:
    """Create a test session in Redis"""
    session_id = "test-session-123"
    session_key = f"session:{session_id}"
    await test_redis.set(session_key, str(test_user.chat_id), ex=86400)
    return session_id
