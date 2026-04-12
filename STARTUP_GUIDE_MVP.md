# 🚀 Weather Alert Bot - MVP Startup Guide

Quick guide to get your local MVP running in minutes!

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher (for frontend)
- Telegram account
- OpenWeatherMap account (free)

---

## Part 1: Backend Setup (5 minutes)

### Step 1: Get API Credentials

#### A. Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### B. OpenWeatherMap API Key
1. Go to https://openweathermap.org/api
2. Click "Sign Up" (free tier is enough)
3. Verify your email
4. Go to API keys section
5. Copy your API key
6. **Note:** New API keys take ~10 minutes to activate

### Step 2: Install Backend

```bash
cd backend

# Option A: Automated setup (Windows)
setup_mvp.bat

# Option B: Manual setup
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### Step 3: Configure Environment

Edit `backend/.env` file:

```env
TELEGRAM_BOT_TOKEN=paste_your_bot_token_here
OPENWEATHER_API_KEY=paste_your_api_key_here
```

### Step 4: Initialize Database

```bash
# Still in backend/ directory with venv activated
python seed_templates.py
```

You should see:
```
✅ Successfully seeded 5 templates
```

### Step 5: Test Setup

```bash
python test_mvp.py
```

All tests should pass! ✅

---

## Part 2: Running the Application

You need **3 terminal windows**:

### Terminal 1: Backend API Server

```bash
cd backend
venv\Scripts\activate
python main.py
```

**Expected output:**
```
🚀 Starting Weather Alert Bot API (MVP)
📝 Server will run on http://localhost:8000
✅ Database initialized (SQLite)
✅ Background reminder checker thread started
```

**Test it:** Open http://localhost:8000/docs in your browser

### Terminal 2: Telegram Bot

```bash
cd backend
venv\Scripts\activate
python app/bot_polling.py
```

**Expected output:**
```
🤖 Starting Telegram Bot in POLLING mode (MVP)...
✅ Bot started! Press Ctrl+C to stop.
```

**Test it:** Send `/start` to your bot on Telegram

### Terminal 3: Frontend (Optional for MVP)

```bash
cd frontend
npm install          # First time only
npm run dev
```

**Expected output:**
```
Local: http://localhost:5173
```

---

## Part 3: Testing End-to-End Flow

### Test 1: Link Your Telegram Account

1. **Generate OTP** (using curl or Postman):
   ```bash
   curl -X POST http://localhost:8000/api/otp/generate \
     -H "Content-Type: application/json" \
     -d "{\"session_id\": \"my-first-session\"}"
   ```

   Response:
   ```json
   {
     "otp": "123456",
     "expires_in": 600
   }
   ```

2. **Link on Telegram:**
   - Open your bot on Telegram
   - Send: `/link 123456` (use your actual OTP)
   - Bot replies: ✅ Account linked successfully!

3. **Verify:**
   - Send `/list` to bot
   - Should say "You have no active reminders"

### Test 2: Create a Reminder

**Using API:**
```bash
curl -X POST http://localhost:8000/api/reminders/ \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: my-first-session" \
  -d "{
    \"condition\": \"rain\",
    \"hours_ahead\": 6,
    \"custom_message\": \"Remember your umbrella!\"
  }"
```

**Verify:**
- Send `/list` to bot on Telegram
- You should see your reminder
- Try deleting it using the inline button

### Test 3: Wait for Alert (or Trigger Manually)

The bot checks every 15 minutes. For testing:
1. Create a reminder for a common condition
2. Wait for the check (or restart the server to trigger immediately)
3. You'll receive a Telegram message if conditions match

---

## Common Issues & Solutions

### ❌ "TELEGRAM_BOT_TOKEN not configured"
- Check `.env` file exists in `backend/` directory
- Make sure token doesn't have quotes around it
- Token should start with a number and contain a colon

### ❌ "Invalid or expired OTP"
- OTPs expire in 10 minutes
- Generate a new one
- Make sure backend server is running

### ❌ "Error fetching weather"
- Check OPENWEATHER_API_KEY in `.env`
- New API keys take ~10 minutes to activate
- Free tier has 1000 calls/day limit

### ❌ Bot not responding to commands
- Make sure `bot_polling.py` is running
- Check for errors in that terminal
- Verify bot token is correct
- Try sending `/start` again

### ❌ "Database already has X templates"
- This is normal - templates were already seeded
- You can delete `reminders.db` to start fresh

### ❌ Port 8000 already in use
- Another server is using that port
- Stop it or change port in `backend/main.py`

---

## What You Should See

### Healthy System

**Terminal 1 (API Server):**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
🔄 Background reminder checker started
⏰ Checking reminders at 2026-04-12T10:00:00
📋 Found 1 active reminders to check
✅ Reminder check completed in 1.23s
💤 Sleeping for 900 seconds...
```

**Terminal 2 (Telegram Bot):**
```
✅ Bot started! Press Ctrl+C to stop.
💡 Send /start to your bot in Telegram to test
```

**Terminal 3 (Frontend):**
```
VITE v5.0.0  ready in 234 ms
➜  Local:   http://localhost:5173/
```

---

## MVP Features Checklist

After setup, you should be able to:

- ✅ Generate OTP from API
- ✅ Link Telegram account with `/link <otp>`
- ✅ Create reminders via API
- ✅ View reminders with `/list` on Telegram
- ✅ Delete reminders from Telegram
- ✅ Receive weather alerts automatically
- ✅ List available templates via API

---

## Next Steps

### For Development:
1. Check API documentation: http://localhost:8000/docs
2. Explore database: `sqlite3 backend/reminders.db`
3. Monitor logs in each terminal window

### For Production:
See `CLAUDE.md` for full production architecture with:
- Docker deployment
- PostgreSQL database
- Redis caching
- Webhook mode (instead of polling)
- Proper monitoring

---

## Quick Reference

### Useful Commands

```bash
# Backend
python main.py                    # Start API server
python app/bot_polling.py        # Start Telegram bot
python seed_templates.py         # Seed database
python test_mvp.py              # Test everything

# Frontend
npm run dev                      # Start dev server
npm run build                    # Production build

# Database
sqlite3 reminders.db            # Open database
.tables                         # List tables
.quit                           # Exit
```

### API Endpoints

- `GET /health` - System health
- `GET /api/templates/` - List templates
- `POST /api/otp/generate` - Generate OTP
- `GET /api/reminders/` - List reminders (auth required)
- `POST /api/reminders/` - Create reminder (auth required)
- `DELETE /api/reminders/{id}` - Delete reminder (auth required)

### Telegram Commands

- `/start` - Welcome message
- `/link <otp>` - Link account
- `/list` - Show reminders

---

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review terminal output for errors
3. Run `python test_mvp.py` to diagnose
4. Check `backend/README_MVP.md` for details

---

**🎉 That's it! You now have a working weather alert bot running locally.**

Next: Build the frontend UI or start customizing the alerts!
