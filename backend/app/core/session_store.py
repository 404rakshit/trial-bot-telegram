"""In-Memory Session and OTP Storage - MVP Simplified Version

This replaces Redis for local development. Data is cleared on restart,
which is acceptable for MVP/development purposes.
"""
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional, Dict, Tuple

# In-memory storage
# Format: {key: (value, expiry_time)}
otp_store: Dict[str, Tuple[str, datetime]] = {}
session_store: Dict[str, Tuple[int, datetime]] = {}
weather_cache: Dict[str, Tuple[dict, datetime]] = {}

# Thread-safe access
store_lock = Lock()


def save_otp(otp: str, session_id: str, ttl_seconds: int = 600) -> None:
    """Save OTP with expiration time

    Args:
        otp: The 6-digit OTP code
        session_id: The session ID to link to
        ttl_seconds: Time to live in seconds (default 10 minutes)
    """
    with store_lock:
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        otp_store[otp] = (session_id, expiry)
        _cleanup_expired(otp_store)


def get_otp(otp: str) -> Optional[str]:
    """Retrieve and validate OTP

    Args:
        otp: The OTP code to look up

    Returns:
        session_id if OTP is valid, None otherwise
    """
    with store_lock:
        if otp in otp_store:
            session_id, expiry = otp_store[otp]
            if datetime.utcnow() < expiry:
                return session_id
            # OTP expired, remove it
            del otp_store[otp]
    return None


def delete_otp(otp: str) -> None:
    """Delete an OTP after successful use"""
    with store_lock:
        if otp in otp_store:
            del otp_store[otp]


def save_session(session_id: str, chat_id: int, ttl_seconds: int = 86400) -> None:
    """Save session with chat_id mapping

    Args:
        session_id: Unique session identifier
        chat_id: Telegram chat_id
        ttl_seconds: Time to live in seconds (default 24 hours)
    """
    with store_lock:
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        session_store[session_id] = (chat_id, expiry)
        _cleanup_expired(session_store)


def get_session(session_id: str) -> Optional[int]:
    """Retrieve chat_id from session

    Args:
        session_id: The session ID to look up

    Returns:
        chat_id if session is valid, None otherwise
    """
    with store_lock:
        if session_id in session_store:
            chat_id, expiry = session_store[session_id]
            if datetime.utcnow() < expiry:
                return chat_id
            # Session expired, remove it
            del session_store[session_id]
    return None


def delete_session(session_id: str) -> None:
    """Delete a session"""
    with store_lock:
        if session_id in session_store:
            del session_store[session_id]


def save_weather_cache(cache_key: str, data: dict, ttl_seconds: int = 3600) -> None:
    """Cache weather API response

    Args:
        cache_key: Key for the cached data (e.g., "weather_lat_lon")
        data: Weather data to cache
        ttl_seconds: Time to live in seconds (default 1 hour)
    """
    with store_lock:
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        weather_cache[cache_key] = (data, expiry)
        _cleanup_expired(weather_cache)


def get_weather_cache(cache_key: str) -> Optional[dict]:
    """Retrieve cached weather data

    Args:
        cache_key: The cache key to look up

    Returns:
        Cached data if valid, None otherwise
    """
    with store_lock:
        if cache_key in weather_cache:
            data, expiry = weather_cache[cache_key]
            if datetime.utcnow() < expiry:
                return data
            # Cache expired, remove it
            del weather_cache[cache_key]
    return None


def _cleanup_expired(store: Dict[str, Tuple]) -> None:
    """Remove expired entries from a store

    This is called automatically during save operations.
    """
    now = datetime.utcnow()
    expired_keys = [k for k, (_, exp) in store.items() if now >= exp]
    for k in expired_keys:
        del store[k]


def get_stats() -> dict:
    """Get statistics about in-memory storage (for debugging)"""
    with store_lock:
        return {
            "otp_count": len(otp_store),
            "session_count": len(session_store),
            "weather_cache_count": len(weather_cache),
        }
