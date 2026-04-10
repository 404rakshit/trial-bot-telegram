"""
Telegram Bot - Polling Mode (for local development)
Use this instead of webhooks when developing locally
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.core.config import settings
import asyncio


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Welcome to Weather Alert Bot!\n\n"
        "To link your account:\n"
        "1. Go to the web app and generate an OTP\n"
        "2. Send me: /link <your-otp-code>"
    )


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /link <OTP> command"""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide an OTP code.\n"
            "Usage: /link 123456"
        )
        return

    otp = context.args[0]
    chat_id = update.effective_chat.id

    # TODO: Validate OTP with Redis (Phase 3)
    await update.message.reply_text(
        f"✅ Received OTP: {otp}\n"
        f"📱 Your chat ID: {chat_id}\n\n"
        "⚠️ OTP validation will be implemented in Phase 3"
    )


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command - show reminders"""
    # TODO: Implement in Phase 3
    await update.message.reply_text(
        "📋 Your active reminders will appear here.\n"
        "⚠️ This feature will be implemented in Phase 3"
    )


async def main():
    """Start the bot in polling mode"""
    print("🤖 Starting Telegram Bot in POLLING mode...")
    print(f"📝 Bot Token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")

    # Create application
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("link", link_command))
    app.add_handler(CommandHandler("list", list_command))

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
