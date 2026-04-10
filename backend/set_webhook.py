"""
Script to set Telegram webhook URL
Run this after you have your public URL from cloudflared
"""
import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

if not TELEGRAM_BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env.development")
    sys.exit(1)

if not TELEGRAM_WEBHOOK_URL:
    print("❌ Error: TELEGRAM_WEBHOOK_URL not found in .env.development")
    print("💡 Hint: Set it to your cloudflared URL, e.g.:")
    print("   TELEGRAM_WEBHOOK_URL=https://your-tunnel.trycloudflare.com/api/webhook/telegram")
    sys.exit(1)


def set_webhook():
    """Set the webhook URL for Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

    payload = {
        "url": TELEGRAM_WEBHOOK_URL,
        "allowed_updates": ["message", "callback_query"]
    }

    print(f"🔗 Setting webhook to: {TELEGRAM_WEBHOOK_URL}")

    response = requests.post(url, json=payload)
    result = response.json()

    if result.get("ok"):
        print("✅ Webhook set successfully!")
        print(f"📝 Response: {result}")
    else:
        print(f"❌ Failed to set webhook: {result}")
        sys.exit(1)


def get_webhook_info():
    """Get current webhook information"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"

    response = requests.get(url)
    result = response.json()

    if result.get("ok"):
        info = result.get("result", {})
        print("\n📊 Current Webhook Info:")
        print(f"   URL: {info.get('url', 'Not set')}")
        print(f"   Pending updates: {info.get('pending_update_count', 0)}")
        if info.get('last_error_message'):
            print(f"   ⚠️  Last error: {info.get('last_error_message')}")
    else:
        print(f"❌ Failed to get webhook info: {result}")


def delete_webhook():
    """Delete the webhook (switch back to polling)"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"

    response = requests.post(url)
    result = response.json()

    if result.get("ok"):
        print("✅ Webhook deleted successfully!")
        print("💡 You can now use polling mode")
    else:
        print(f"❌ Failed to delete webhook: {result}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "delete":
            delete_webhook()
        elif sys.argv[1] == "info":
            get_webhook_info()
        else:
            print("Usage:")
            print("  python set_webhook.py        # Set webhook")
            print("  python set_webhook.py info   # Get webhook info")
            print("  python set_webhook.py delete # Delete webhook")
    else:
        set_webhook()
        get_webhook_info()
