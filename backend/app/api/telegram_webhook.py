"""Telegram Webhook Handler - Sync Version

Handles incoming updates from Telegram via webhook.
Set webhook URL to: https://bot.example.me/api/webhook/telegram
"""
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.session_store import get_otp, delete_otp, save_session
from app.models.user import User
from app.models.reminder import Reminder

import httpx

router = APIRouter()


def send_message(chat_id: int, text: str, reply_markup: Dict[str, Any] = None, parse_mode: str = None):
    """Send a message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None


def edit_message_text(chat_id: int, message_id: int, text: str):
    """Edit a message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error editing message: {e}")
        return None


def answer_callback_query(callback_query_id: str, text: str = None):
    """Answer a callback query"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/answerCallbackQuery"

    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error answering callback: {e}")
        return None


def handle_start_command(chat_id: int):
    """Handle /start command"""
    send_message(
        chat_id,
        "👋 Welcome to Weather Alert Bot!\n\n"
        "To link your account:\n"
        "1. Go to the web app and generate an OTP\n"
        "2. Send me: /link <your-otp-code>\n\n"
        "Commands:\n"
        "/link <otp> - Link your account\n"
        "/list - View your reminders"
    )


def handle_link_command(chat_id: int, args: list):
    """Handle /link <OTP> command"""
    if not args:
        send_message(
            chat_id,
            "❌ Please provide an OTP code.\n"
            "Usage: /link 123456"
        )
        return

    otp = args[0].strip()

    # Validate OTP
    session_id = get_otp(otp)
    print(f"🔍 OTP validation: {otp} → session_id: {session_id}")

    if not session_id:
        send_message(
            chat_id,
            "❌ Invalid or expired OTP.\n\n"
            "Please generate a new OTP from the web app."
        )
        return

    # Delete OTP (single use)
    delete_otp(otp)

    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.chat_id == chat_id).first()

        if user:
            # User exists, just update session
            send_message(
                chat_id,
                "✅ Account already linked!\n"
                "Your existing settings have been preserved."
            )
        else:
            # Create new user with default location
            user = User(
                chat_id=chat_id,
                latitude=37.77,  # San Francisco (rounded to 2 decimals)
                longitude=-122.42,
                timezone="America/Los_Angeles"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            send_message(
                chat_id,
                "✅ Account linked successfully!\n\n"
                "📍 Default location: San Francisco, CA\n"
                "🕐 Default timezone: America/Los_Angeles\n\n"
                "You can now create reminders from the web app.\n"
                "Use /list to view your reminders."
            )

        # Save session
        save_session(session_id, chat_id, settings.SESSION_TTL)
        print(f"✅ Session saved: {session_id} → chat_id: {chat_id}")

    except Exception as e:
        print(f"❌ Error in link_command: {e}")
        send_message(chat_id, "⚠️ An error occurred. Please try again.")
    finally:
        db.close()


def handle_list_command(chat_id: int):
    """Handle /list command - show reminders"""
    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.chat_id == chat_id).first()

        if not user:
            send_message(
                chat_id,
                "❌ Account not linked.\n\n"
                "Please use /link <otp> to link your account first."
            )
            return

        # Get active reminders
        reminders = (
            db.query(Reminder)
            .filter(Reminder.user_id == user.id)
            .filter(Reminder.is_active == True)
            .order_by(Reminder.created_at.desc())
            .all()
        )

        if not reminders:
            send_message(
                chat_id,
                "📋 You have no active reminders.\n\n"
                "Create one from the web app!"
            )
            return

        # Build message with inline keyboard
        message = "📋 <b>Your Active Reminders:</b>\n\n"

        keyboard_buttons = []
        for idx, reminder in enumerate(reminders, 1):
            message += (
                f"{idx}. <b>{reminder.condition.capitalize()}</b> "
                f"in {reminder.hours_ahead}h\n"
            )
            if reminder.custom_message:
                message += f"   💬 {reminder.custom_message[:50]}...\n"

            # Add delete button
            keyboard_buttons.append([{
                "text": f"🗑️ Delete #{idx}",
                "callback_data": f"delete_{reminder.id}"
            }])

        reply_markup = {
            "inline_keyboard": keyboard_buttons
        }

        send_message(chat_id, message, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        print(f"❌ Error in list_command: {e}")
        send_message(chat_id, "⚠️ An error occurred. Please try again.")
    finally:
        db.close()


def handle_callback_query(callback_query: Dict[str, Any]):
    """Handle inline button callbacks"""
    query_id = callback_query.get("id")
    data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    # Answer the callback query immediately
    answer_callback_query(query_id)

    if not data.startswith("delete_"):
        return

    # Extract reminder ID
    try:
        reminder_id = int(data.split("_")[1])
    except (IndexError, ValueError):
        edit_message_text(chat_id, message_id, "❌ Invalid reminder ID.")
        return

    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.chat_id == chat_id).first()

        if not user:
            edit_message_text(chat_id, message_id, "❌ Account not found.")
            return

        # Get reminder and verify ownership
        reminder = (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id)
            .filter(Reminder.user_id == user.id)
            .first()
        )

        if not reminder:
            edit_message_text(chat_id, message_id, "❌ Reminder not found.")
            return

        # Soft delete
        reminder.is_active = False
        db.commit()

        edit_message_text(
            chat_id,
            message_id,
            f"✅ Deleted reminder: {reminder.condition.capitalize()} in {reminder.hours_ahead}h\n\n"
            "Use /list to see your remaining reminders."
        )

    except Exception as e:
        print(f"❌ Error in callback_query: {e}")
        edit_message_text(chat_id, message_id, "⚠️ An error occurred.")
    finally:
        db.close()


@router.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Handle incoming Telegram updates via webhook.

    Webhook URL should be set to: https://bot.example.me/api/webhook/telegram
    """
    try:
        # Get the update data
        update = await request.json()

        print(f"📨 Received update: {update.get('update_id', 'unknown')}")

        # Handle callback queries (inline button presses)
        if "callback_query" in update:
            handle_callback_query(update["callback_query"])
            return {"ok": True}

        # Handle messages
        message = update.get("message")
        if not message:
            return {"ok": True}

        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")

        if not chat_id or not text:
            return {"ok": True}

        # Parse command and arguments
        parts = text.split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        # Handle commands
        if command == "/start":
            handle_start_command(chat_id)
        elif command == "/link":
            handle_link_command(chat_id, args)
        elif command == "/list":
            handle_list_command(chat_id)
        else:
            # Unknown command
            send_message(
                chat_id,
                "❓ Unknown command. Try:\n"
                "/start - Get started\n"
                "/link <otp> - Link your account\n"
                "/list - View reminders"
            )

        return {"ok": True}

    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        # Return 200 OK even on error to prevent Telegram from retrying
        return {"ok": True}


@router.get("/telegram")
async def webhook_info():
    """Get webhook info (for debugging)"""
    return {
        "webhook_url": "https://bot.example.me/api/webhook/telegram",
        "status": "ready",
        "note": "Set this webhook URL using set_webhook.py"
    }
