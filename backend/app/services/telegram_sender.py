"""Telegram Message Sender

Handles sending notifications to Telegram users.
"""
import httpx
from typing import Optional
from app.core.config import settings


def send_telegram_message(chat_id: int, message: str) -> bool:
    """Send a message to a Telegram user

    Args:
        chat_id: Telegram chat ID
        message: Message text to send

    Returns:
        True if sent successfully, False otherwise
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        print("⚠️  Telegram bot token not configured")
        return False

    try:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",  # Support HTML formatting
        }

        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()

        print(f"✅ Message sent to chat_id {chat_id}")
        return True

    except httpx.HTTPError as e:
        print(f"❌ Error sending message to {chat_id}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error sending message: {e}")
        return False


def send_weather_alert(
    chat_id: int,
    condition: str,
    hours_ahead: int,
    weather_description: str,
    custom_message: Optional[str] = None
) -> bool:
    """Send a weather alert to a user

    Args:
        chat_id: Telegram chat ID
        condition: Weather condition (e.g., "rain", "snow")
        hours_ahead: Hours ahead when condition will occur
        weather_description: Current weather forecast description
        custom_message: Optional custom message from user

    Returns:
        True if sent successfully, False otherwise
    """
    if custom_message:
        message = custom_message
    else:
        # Default message format
        message = (
            f"🌤️ <b>Weather Alert</b>\n\n"
            f"Condition: <b>{condition.capitalize()}</b>\n"
            f"Expected in: <b>{hours_ahead} hours</b>\n"
            f"Forecast: {weather_description}"
        )

    return send_telegram_message(chat_id, message)
