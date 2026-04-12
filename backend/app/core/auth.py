"""Session-based authentication using in-memory storage"""
from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.session_store import get_session, save_session
from app.models.user import User


def get_current_user(
    session_id: str = Header(..., alias=settings.SESSION_HEADER_NAME),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate session and return current user.

    Flow:
    1. Extract session_id from X-Session-ID header
    2. Look up chat_id in memory session store
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

    # Get chat_id from in-memory session store
    chat_id = get_session(session_id)

    if not chat_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    # Query user from database
    user = db.query(User).filter(User.chat_id == chat_id).first()

    if not user:
        # User was deleted but session still exists - clean up
        from app.core.session_store import delete_session
        delete_session(session_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Refresh session TTL to keep active users logged in
    save_session(session_id, chat_id, settings.SESSION_TTL)

    return user


def get_current_user_optional(
    session_id: Optional[str] = Header(None, alias=settings.SESSION_HEADER_NAME),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication dependency.
    Returns User if session is valid, None otherwise.
    Does not raise exceptions for missing/invalid sessions.
    """
    if not session_id:
        return None

    try:
        chat_id = get_session(session_id)

        if not chat_id:
            return None

        user = db.query(User).filter(User.chat_id == chat_id).first()

        if user:
            # Refresh session TTL
            save_session(session_id, chat_id, settings.SESSION_TTL)

        return user

    except Exception:
        # Silently fail for optional auth
        return None
