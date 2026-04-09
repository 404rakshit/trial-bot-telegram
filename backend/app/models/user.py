"""User model"""
from sqlalchemy import String, Float, DateTime, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """Telegram user with location and timezone"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)

    # Location (rounded to 2 decimals for caching)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Timezone (IANA timezone string, e.g., "America/New_York")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Timestamps (always UTC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reminders: Mapped[list["Reminder"]] = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(chat_id={self.chat_id}, timezone={self.timezone})>"
