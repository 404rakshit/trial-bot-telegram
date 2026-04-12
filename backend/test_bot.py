"""Quick test to verify bot can start"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing bot imports...")

try:
    from app.core.config import settings
    print("✅ Config imported")

    from app.core.database import SessionLocal
    print("✅ Database imported")

    from app.models.user import User
    from app.models.reminder import Reminder
    print("✅ Models imported")

    print(f"\n📝 Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"🌤️  Weather API: {settings.OPENWEATHER_API_KEY[:20]}...")

    if not settings.TELEGRAM_BOT_TOKEN or settings.TELEGRAM_BOT_TOKEN == "your_bot_token_from_botfather":
        print("\n⚠️  Telegram token not configured!")
        sys.exit(1)

    if not settings.OPENWEATHER_API_KEY or settings.OPENWEATHER_API_KEY == "your_api_key_here":
        print("\n⚠️  Weather API key not configured!")
        sys.exit(1)

    print("\n✅ All checks passed! Bot is ready to start.")
    print("\nTo start the bot, run:")
    print("  python bot_polling.py")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
