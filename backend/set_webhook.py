"""
Set Telegram Webhook URL

This script configures your Telegram bot to use webhook mode instead of polling.

Usage:
    python set_webhook.py
"""
import sys
import io
import httpx

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.core.config import settings


def set_webhook(webhook_url: str):
    """Set the webhook URL for the Telegram bot"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/setWebhook"

    payload = {
        "url": webhook_url,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": True,  # Clear any pending updates
    }

    try:
        print(f"🔧 Setting webhook to: {webhook_url}")
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()

        result = response.json()

        if result.get("ok"):
            print("✅ Webhook set successfully!")
            print(f"   URL: {webhook_url}")
            print(f"   Response: {result.get('description', 'OK')}")
            return True
        else:
            print(f"❌ Failed to set webhook: {result}")
            return False

    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False


def get_webhook_info():
    """Get current webhook information"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getWebhookInfo"

    try:
        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()

        result = response.json()

        if result.get("ok"):
            info = result.get("result", {})
            print("\n📊 Current Webhook Info:")
            print(f"   URL: {info.get('url', 'Not set')}")
            print(f"   Pending updates: {info.get('pending_update_count', 0)}")
            print(f"   Last error: {info.get('last_error_message', 'None')}")
            if info.get('last_error_date'):
                from datetime import datetime
                error_date = datetime.fromtimestamp(info['last_error_date'])
                print(f"   Last error date: {error_date}")
            return info
        else:
            print(f"❌ Failed to get webhook info: {result}")
            return None

    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return None


def delete_webhook():
    """Delete the webhook (switch back to polling mode)"""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/deleteWebhook"

    payload = {"drop_pending_updates": True}

    try:
        print("🗑️  Deleting webhook...")
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()

        result = response.json()

        if result.get("ok"):
            print("✅ Webhook deleted successfully!")
            print("   Bot is now in polling mode (if you run bot_polling.py)")
            return True
        else:
            print(f"❌ Failed to delete webhook: {result}")
            return False

    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("Telegram Webhook Configuration")
    print("=" * 60)

    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not configured in .env")
        sys.exit(1)

    print(f"\n📝 Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...")

    # Show current webhook info
    get_webhook_info()

    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("=" * 60)
    print("1. Set webhook (enable webhook mode)")
    print("2. Delete webhook (switch to polling mode)")
    print("3. View webhook info")
    print("4. Exit")
    print()

    choice = input("Enter your choice (1-4): ").strip()

    if choice == "1":
        webhook_url = input("\nEnter webhook URL (or press Enter for default): ").strip()

        if not webhook_url:
            webhook_url = "https://bot.expdev.me/api/webhook/telegram"
            print(f"Using default: {webhook_url}")

        print()
        if set_webhook(webhook_url):
            print("\n✅ Done! Your bot is now in webhook mode.")
            print("   Make sure your FastAPI server is running:")
            print("   python main.py")
        else:
            print("\n❌ Failed to set webhook. Check the error above.")

    elif choice == "2":
        print()
        if delete_webhook():
            print("\n✅ Done! Webhook deleted.")
            print("   To use polling mode, run:")
            print("   python bot_polling.py")
        else:
            print("\n❌ Failed to delete webhook.")

    elif choice == "3":
        print()
        get_webhook_info()

    elif choice == "4":
        print("\n👋 Goodbye!")
        sys.exit(0)

    else:
        print("\n❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
