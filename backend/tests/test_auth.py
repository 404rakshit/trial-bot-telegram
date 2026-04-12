"""Tests for session authentication"""
import pytest
from httpx import AsyncClient
from redis.asyncio import Redis

from app.models.user import User


@pytest.mark.asyncio
async def test_get_current_user_valid_session(
    client: AsyncClient,
    test_user: User,
    test_session_id: str
):
    """Test successful authentication with valid session"""
    # Make a request with valid session header
    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": test_session_id}
    )

    # Should succeed (200 or 201)
    assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_get_current_user_missing_session(client: AsyncClient):
    """Test authentication fails without session header"""
    response = await client.get("/api/reminders/")

    # Should return 422 (validation error - missing required header)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_current_user_invalid_session(client: AsyncClient):
    """Test authentication fails with invalid session ID"""
    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": "invalid-session"}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "Invalid or expired session" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_expired_session(
    client: AsyncClient,
    test_redis: Redis,
    test_user: User
):
    """Test authentication fails with expired session"""
    # Create a session that immediately expires
    session_id = "expired-session"
    session_key = f"session:{session_id}"
    await test_redis.set(session_key, str(test_user.chat_id), ex=1)

    # Wait for expiration
    import asyncio
    await asyncio.sleep(2)

    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": session_id}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_ttl_refresh(
    client: AsyncClient,
    test_redis: Redis,
    test_user: User,
    test_session_id: str
):
    """Test that session TTL is refreshed on each request"""
    session_key = f"session:{test_session_id}"

    # Get initial TTL
    ttl_before = await test_redis.ttl(session_key)

    # Make a request to trigger TTL refresh
    await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": test_session_id}
    )

    # Get TTL after request
    ttl_after = await test_redis.ttl(session_key)

    # TTL should be refreshed (close to max)
    assert ttl_after >= 86400 - 10  # Allow 10 second tolerance


@pytest.mark.asyncio
async def test_get_current_user_deleted_user(
    client: AsyncClient,
    test_db,
    test_redis: Redis,
    test_user: User
):
    """Test authentication fails if user is deleted but session exists"""
    # Create session
    session_id = "orphan-session"
    session_key = f"session:{session_id}"
    await test_redis.set(session_key, str(test_user.chat_id), ex=86400)

    # Delete user from database
    await test_db.delete(test_user)
    await test_db.commit()

    response = await client.get(
        "/api/reminders/",
        headers={"X-Session-ID": session_id}
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]

    # Session should be cleaned up
    session_exists = await test_redis.exists(session_key)
    assert session_exists == 0
