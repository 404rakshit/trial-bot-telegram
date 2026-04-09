"""Redis client for caching and OTP storage"""
import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,  # Low limit for memory efficiency
    )
    # Test connection
    await redis_client.ping()


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client
