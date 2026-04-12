"""
Telegram Bot - Polling Mode (MVP Simplified)
Handles user linking and reminder management via Telegram
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from app.core.config import settings
from app.core.session_store import get_otp, delete_otp, save_session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.reminder import Reminder
import asyncio
import secrets


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if not update.message:
        return

    await update.message.reply_text(
        "👋 Welcome to Weather Alert Bot!\n\n"
        "To link your account:\n"
        "1. Go to the web app and generate an OTP\n"
        "2. Send me: /link <your-otp-code>\n\n"
        "Commands:\n"
        "/link <otp> - Link your account\n"
        "/list - View your reminders"
    )


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /link <OTP> command

    Flow:
    1. User sends /link <otp>
    2. Validate OTP from in-memory store
    3. Get session_id from OTP
    4. Check if user already exists by chat_id
    5. If new user, prompt for location/timezone (simplified: use defaults for MVP)
    6. Create/update user in database
    7. Link session_id to chat_id
    8. Delete OTP (single use)
    """
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an OTP code.\n"
            "Usage: /link 123456"
        )
        return

    otp = context.args[0].strip()
    chat_id = update.effective_chat.id

    # Validate OTP
    session_id = get_otp(otp)
    
    print("session_id: ", session_id)

    if not session_id:
        await update.message.reply_text(
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
            await update.message.reply_text(
                "✅ Account already linked!\n"
                "Your existing settings have been preserved."
            )
        else:
            # Create new user with default location (can be updated later)
            # For MVP, use a default location - San Francisco
            user = User(
                chat_id=chat_id,
                latitude=37.77,  # San Francisco (rounded to 2 decimals)
                longitude=-122.42,
                timezone="America/Los_Angeles"
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            await update.message.reply_text(
                "✅ Account linked successfully!\n\n"
                "📍 Default location: San Francisco, CA\n"
                "🕐 Default timezone: America/Los_Angeles\n\n"
                "You can now create reminders from the web app.\n"
                "Use /list to view your reminders."
            )

        # Save session
        save_session(session_id, chat_id, settings.SESSION_TTL)

    finally:
        db.close()


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command - show reminders with inline keyboard

    Shows all active reminders with a delete button for each.
    """
    if not update.message:
        return

    chat_id = update.effective_chat.id

    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.chat_id == chat_id).first()

        if not user:
            await update.message.reply_text(
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
            await update.message.reply_text(
                "📋 You have no active reminders.\n\n"
                "Create one from the web app!"
            )
            return

        # Build message with inline keyboard
        message = "📋 <b>Your Active Reminders:</b>\n\n"

        keyboard = []
        for idx, reminder in enumerate(reminders, 1):
            message += (
                f"{idx}. <b>{reminder.condition.capitalize()}</b> "
                f"in {reminder.hours_ahead}h\n"
            )
            if reminder.custom_message:
                message += f"   💬 {reminder.custom_message[:50]}...\n"

            # Add delete button
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ Delete #{idx}",
                    callback_data=f"delete_{reminder.id}"
                )
            ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

    finally:
        db.close()


async def delete_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete reminder button press"""
    query = update.callback_query
    await query.answer()

    # Extract reminder ID from callback data
    reminder_id = int(query.data.split("_")[1])
    chat_id = update.effective_chat.id

    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.chat_id == chat_id).first()

        if not user:
            await query.edit_message_text("❌ Account not found.")
            return

        # Get reminder and verify ownership
        reminder = (
            db.query(Reminder)
            .filter(Reminder.id == reminder_id)
            .filter(Reminder.user_id == user.id)
            .first()
        )

        if not reminder:
            await query.edit_message_text("❌ Reminder not found.")
            return

        # Soft delete
        reminder.is_active = False
        db.commit()

        await query.edit_message_text(
            f"✅ Deleted reminder: {reminder.condition.capitalize()} in {reminder.hours_ahead}h\n\n"
            "Use /list to see your remaining reminders."
        )

    finally:
        db.close()


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot"""
    print(f"❌ Error while handling update {update}:")
    print(f"   {context.error}")

    # Try to notify the user if possible
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ An error occurred while processing your request.\n"
                "Please try again or contact support if the issue persists."
            )
        except Exception:
            pass  # Ignore errors while sending error message


async def main():
    """Start the bot in polling mode"""
    print("🤖 Starting Telegram Bot in POLLING mode (MVP)...")

    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not configured in .env")
        return

    print(f"📝 Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")

    # Create application
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("link", link_command))
    app.add_handler(CommandHandler("list", list_command))

    # Add callback query handler for inline buttons
    app.add_handler(CallbackQueryHandler(delete_reminder_callback, pattern="^delete_"))

    # Add error handler
    app.add_error_handler(error_handler)

    print("✅ Bot started! Press Ctrl+C to stop.")
    print("💡 Send /start to your bot in Telegram to test")

    # Start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping bot...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
