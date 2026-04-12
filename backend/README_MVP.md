# Weather Alert Bot - MVP Backend

Simplified local development version without Docker/Redis complexity.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in `backend/` directory:

```env
# Get token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Get API key from openweathermap.org (free tier)
OPENWEATHER_API_KEY=your_api_key_here

# Optional settings
DEBUG=True
ENV=development
```

**How to get tokens:**
- **Telegram Bot**: Message @BotFather on Telegram, use `/newbot` command
- **Weather API**: Sign up at https://openweathermap.org/api (free tier: 1000 calls/day)

### 3. Seed Database

```bash
# Run seed script to create default templates
python seed_templates.py
```

### 4. Run the Application

You need **3 terminal windows**:

#### Terminal 1: Backend API
```bash
cd backend
venv\Scripts\activate
python main.py
```
Server runs on: http://localhost:8000
API docs: http://localhost:8000/docs

#### Terminal 2: Telegram Bot
```bash
cd backend
venv\Scripts\activate
python app/bot_polling.py
```

#### Terminal 3: Frontend (see frontend README)
```bash
cd frontend
npm run dev
```

## Testing the MVP

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 2. Test OTP Generation
```bash
curl -X POST http://localhost:8000/api/otp/generate \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"test-123\"}"
```

### 3. Link Telegram Account
1. Send `/start` to your bot on Telegram
2. Generate OTP from web UI or API
3. Send `/link <otp>` to bot
4. Bot confirms account linked

### 4. Create Reminder
- Use web UI to create a weather reminder
- Bot will check conditions every 15 minutes
- You'll receive notifications when conditions match

### 5. List Reminders
- Send `/list` to bot on Telegram
- Delete reminders using inline buttons

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Settings
│   │   ├── database.py         # SQLite connection
│   │   ├── session_store.py    # In-memory OTP/sessions
│   │   └── auth.py             # Authentication
│   ├── models/
│   │   ├── user.py             # User model
│   │   └── reminder.py         # Reminder & Template models
│   ├── api/
│   │   ├── otp.py              # OTP generation
│   │   ├── reminders.py        # Reminder CRUD
│   │   └── templates.py        # Template list
│   ├── services/
│   │   ├── weather.py          # OpenWeatherMap API
│   │   └── telegram_sender.py  # Send notifications
│   ├── worker/
│   │   └── reminder_checker.py # Background task
│   ├── bot_polling.py          # Telegram bot
│   └── main.py                 # FastAPI app
├── main.py                     # Entry point
├── seed_templates.py           # Database seeder
├── .env                        # Your config (create this!)
└── requirements.txt
```

## API Endpoints

### Public Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health check
- `GET /api/templates/` - List weather templates
- `POST /api/otp/generate` - Generate OTP for linking

### Authenticated Endpoints
Require `X-Session-ID` header:
- `GET /api/reminders/` - List your reminders
- `POST /api/reminders/` - Create reminder
- `DELETE /api/reminders/{id}` - Delete reminder

## Troubleshooting

### Bot not responding
- Check TELEGRAM_BOT_TOKEN in .env
- Make sure bot_polling.py is running
- Check for errors in bot terminal

### Weather not working
- Check OPENWEATHER_API_KEY in .env
- Verify API key is active (can take 10 minutes after signup)
- Check API quota (free tier: 1000 calls/day)

### Database errors
- Delete `reminders.db` and restart
- Run `python seed_templates.py` again

### Session expired
- Sessions last 24 hours by default
- Generate new OTP and re-link if needed

## MVP Limitations

✅ **Works for MVP:**
- Local development
- Single developer testing
- Quick prototyping

❌ **Not production-ready:**
- Data lost on restart (in-memory sessions)
- No encryption (local only)
- Single instance (can't scale)
- No monitoring/logging

## Upgrading to Production

When ready for production:
1. Replace SQLite with PostgreSQL
2. Replace in-memory storage with Redis
3. Add Docker deployment
4. Use webhook mode instead of polling
5. Add proper logging and monitoring
6. Add tests (pytest framework ready)

See main CLAUDE.md for full production architecture.
