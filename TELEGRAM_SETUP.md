# Telegram Bot Setup Guide

## Step 1: Add Your Bot Token

Edit `.env.development` and add your bot token:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz  # Your actual token
```

---

## Step 2: Choose Your Mode

### 🔧 Option A: Development Mode (Polling) - RECOMMENDED FOR TESTING

**Easiest way to test locally without webhooks:**

1. **Start the bot**:
   ```bash
   cd backend

   # Install dependencies first if not using Docker
   pip install -r requirements.txt

   # Run polling bot
   python -m app.bot_polling
   ```

2. **Test in Telegram**:
   - Open Telegram and search for your bot
   - Send `/start` command
   - Send `/link 123456` (test OTP validation)
   - Send `/list` (test reminders list)

3. **Stop the bot**: Press `Ctrl+C`

**Pros:** Simple, works anywhere, no setup needed
**Cons:** Bot must be running manually, doesn't work with Docker worker

---

### 🌐 Option B: Production Mode (Webhooks) - FOR STAGING/PRODUCTION

**Use when you want automatic message handling:**

#### Step 2.1: Get a Public URL with Cloudflare Tunnel

**Quick Test (Temporary URL):**
```bash
# Download cloudflared: https://github.com/cloudflare/cloudflared/releases
# Then run:
cloudflared tunnel --url http://localhost:8000

# You'll get a URL like: https://random-words.trycloudflare.com
# This URL changes each time you restart
```

**Permanent Setup (Recommended):**

1. Create Cloudflare account: https://dash.cloudflare.com/sign-up

2. Install cloudflared:
   - Windows: Download from https://github.com/cloudflare/cloudflared/releases
   - Add to PATH

3. Create tunnel:
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create weather-bot
   ```

4. Get tunnel token:
   ```bash
   cloudflared tunnel token weather-bot
   # Copy the token
   ```

5. Add to `.env.development`:
   ```bash
   CLOUDFLARE_TUNNEL_TOKEN=your-token-here
   ```

6. Start with Docker:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
   ```

7. Your public URL will be shown in logs or Cloudflare dashboard

#### Step 2.2: Set the Webhook URL

1. **Add your public URL to `.env.development`**:
   ```bash
   TELEGRAM_WEBHOOK_URL=https://your-tunnel.trycloudflare.com/api/webhook/telegram
   ```

2. **Run the webhook setup script**:
   ```bash
   cd backend
   pip install requests python-dotenv
   python set_webhook.py
   ```

   You should see:
   ```
   ✅ Webhook set successfully!
   📊 Current Webhook Info:
      URL: https://your-tunnel.trycloudflare.com/api/webhook/telegram
      Pending updates: 0
   ```

3. **Test**: Send a message to your bot - it should be received by your FastAPI webhook endpoint

#### Webhook Management Commands:

```bash
# Check webhook status
python set_webhook.py info

# Delete webhook (switch back to polling)
python set_webhook.py delete

# Set webhook again
python set_webhook.py
```

---

## Step 3: Verify It Works

### Test Bot Commands:

1. **Open Telegram** and search for your bot (name you gave to @BotFather)

2. **Send `/start`**:
   ```
   Expected response:
   👋 Welcome to Weather Alert Bot!

   To link your account:
   1. Go to the web app and generate an OTP
   2. Send me: /link <your-otp-code>
   ```

3. **Send `/link 123456`**:
   ```
   Expected response:
   ✅ Received OTP: 123456
   📱 Your chat ID: 123456789

   ⚠️ OTP validation will be implemented in Phase 3
   ```

4. **Send `/list`**:
   ```
   Expected response:
   📋 Your active reminders will appear here.
   ⚠️ This feature will be implemented in Phase 3
   ```

---

## Troubleshooting

### Polling Mode Issues:

**Bot doesn't respond:**
- Check `TELEGRAM_BOT_TOKEN` in `.env.development`
- Make sure bot script is running (`python -m app.bot_polling`)
- Check for errors in console

### Webhook Mode Issues:

**"Failed to set webhook":**
- Ensure your URL is HTTPS (http:// won't work)
- Telegram must be able to reach your URL
- Test URL manually: `curl https://your-url.com/health`

**"Connection refused":**
- Make sure FastAPI is running
- Check cloudflared tunnel is active
- Verify firewall isn't blocking

**Check webhook status:**
```bash
python set_webhook.py info
```

**Delete webhook and switch back to polling:**
```bash
python set_webhook.py delete
python -m app.bot_polling
```

---

## Summary

| Mode | Use Case | Setup Difficulty | Reliability |
|------|----------|------------------|-------------|
| **Polling** | Development, testing | ⭐ Easy | ⭐⭐⭐ Good for dev |
| **Webhook** | Staging, production | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Production-ready |

**Recommendation:** Start with **polling mode** for Phase 1-3 testing, switch to **webhooks** for Phase 4+ deployment.

---

## Next Steps

Once your bot is responding:
1. ✅ Phase 1 complete!
2. Move to Phase 2: Implement OTP validation with Redis
3. Move to Phase 3: Complete Telegram webhook handler
