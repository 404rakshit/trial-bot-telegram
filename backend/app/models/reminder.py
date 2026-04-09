"""Reminder and UseCaseTemplate models"""
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.database import Base


class UseCaseTemplate(Base):
    """Pre-configured weather alert templates"""
    __tablename__ = "use_case_templates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Weather condition to check
    condition: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "rain", "snow", "clear"

    # Hours ahead to check (e.g., 6 for "rain in 6 hours")
    hours_ahead: Mapped[int] = mapped_column(Integer, nullable=False)

    # Default message template
    message_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Active/archived
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<UseCaseTemplate(name={self.name}, condition={self.condition})>"


class Reminder(Base):
    """User's active weather alert reminder"""
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Optional reference to template
    template_id: Mapped[int] = mapped_column(ForeignKey("use_case_templates.id"), nullable=True)

    # Weather condition to monitor
    condition: Mapped[str] = mapped_column(String(50), nullable=False)
    hours_ahead: Mapped[int] = mapped_column(Integer, nullable=False)

    # Custom message (overrides template if provided)
    custom_message: Mapped[str] = mapped_column(Text, nullable=True)

    # Active status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps (UTC)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_alerted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reminders")
    template: Mapped["UseCaseTemplate"] = relationship("UseCaseTemplate")

    def __repr__(self):
        return f"<Reminder(user_id={self.user_id}, condition={self.condition}, hours_ahead={self.hours_ahead})>"
