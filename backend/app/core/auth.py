"""Session-based authentication using Redis"""
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from redis.asyncio import Redis
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import get_redis
from app.models.user import User


async def get_current_user(
    session_id: str = Header(..., alias=settings.SESSION_HEADER_NAME),
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate session and return current user.

    Flow:
    1. Extract session_id from X-Session-ID header
    2. Look up chat_id in Redis: session:{session_id} -> chat_id
    3. Query User by chat_id from database
    4. Refresh session TTL on successful validation
    5. Return User object

    Raises:
        HTTPException: 401 if session invalid or user not found
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID required in header"
        )

    # Get chat_id from Redis session
    session_key = f"session:{session_id}"
    chat_id_str = await redis.get(session_key)

    if not chat_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    try:
        chat_id = int(chat_id_str)
    except ValueError:
        # Invalid chat_id format in Redis
        await redis.delete(session_key)  # Clean up invalid session
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session data"
        )

    # Query user from database
    result = await db.execute(
        select(User).where(User.chat_id == chat_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # User was deleted but session still exists
        await redis.delete(session_key)  # Clean up orphaned session
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Refresh session TTL to keep active users logged in
    await redis.expire(session_key, settings.REDIS_SESSION_TTL)

    return user


async def get_current_user_optional(
    session_id: Optional[str] = Header(None, alias=settings.SESSION_HEADER_NAME),
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns User if session is valid, None otherwise.
    Does not raise exceptions for missing/invalid sessions.
    """
    if not session_id:
        return None

    try:
        session_key = f"session:{session_id}"
        chat_id_str = await redis.get(session_key)

        if not chat_id_str:
            return None

        chat_id = int(chat_id_str)

        result = await db.execute(
            select(User).where(User.chat_id == chat_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Refresh session TTL
            await redis.expire(session_key, settings.REDIS_SESSION_TTL)

        return user

    except (ValueError, Exception):
        # Silently fail for optional auth
        return None
