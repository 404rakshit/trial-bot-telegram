# Quick Reference Card - Weather Alert Bot MVP

## 🚀 Quick Start (Copy-Paste)

```bash
# Setup
cd backend
setup_mvp.bat                    # Windows
# Edit .env with your API keys
python seed_templates.py

# Run (3 terminals)
python main.py                   # Terminal 1
python app/bot_polling.py       # Terminal 2
cd ../frontend && npm run dev   # Terminal 3
```

## 📝 Essential Commands

### Backend
```bash
python main.py                   # Start API server
python app/bot_polling.py       # Start Telegram bot
python seed_templates.py        # Seed database
python test_mvp.py             # Test everything
```

### Frontend
```bash
npm install                     # Install deps (once)
npm run dev                     # Start dev server
```

### Database
```bash
sqlite3 reminders.db           # Open database
.tables                        # List tables
.schema users                  # Show schema
.quit                          # Exit
```

## 🔗 Important URLs

- API Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Frontend: http://localhost:5173

## 📱 Telegram Commands

```
/start               # Welcome message
/link <otp>          # Link account (e.g., /link 123456)
/list                # Show your reminders
```

## 🌐 API Endpoints

### Public (No Auth)
```bash
GET  /health                    # System status
GET  /api/templates/            # List templates
POST /api/otp/generate          # Generate OTP
```

### Authenticated (Need X-Session-ID header)
```bash
GET    /api/reminders/          # List reminders
POST   /api/reminders/          # Create reminder
DELETE /api/reminders/{id}      # Delete reminder
```

## 🧪 Test Commands

### Generate OTP
```bash
curl -X POST http://localhost:8000/api/otp/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123"}'
```

### List Templates
```bash
curl http://localhost:8000/api/templates/
```

### Create Reminder
```bash
curl -X POST http://localhost:8000/api/reminders/ \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: test-123" \
  -d '{
    "condition": "rain",
    "hours_ahead": 6,
    "custom_message": "Bring umbrella!"
  }'
```

### List Reminders
```bash
curl http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: test-123"
```

## 🔧 Configuration (.env)

```env
TELEGRAM_BOT_TOKEN=123456789:ABC...    # From @BotFather
OPENWEATHER_API_KEY=abc123...          # From openweathermap.org
DEBUG=True
ENV=development
```

## 📊 Default Templates

1. **Morning Rain Alert** - Rain in 6 hours
2. **Evening Rain Alert** - Rain in 12 hours
3. **Snow Alert** - Snow in 6 hours
4. **Clear Weather** - Sunny in 6 hours
5. **Storm Warning** - Storm in 3 hours

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check token
cat .env | grep TELEGRAM_BOT_TOKEN

# Restart bot
Ctrl+C in bot terminal
python app/bot_polling.py
```

### Database issues?
```bash
# Delete and recreate
rm reminders.db
python seed_templates.py
```

### OTP expired?
```bash
# Generate new one
curl -X POST http://localhost:8000/api/otp/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "my-session"}'
```

### Weather API not working?
- Check API key is correct
- Wait 10 mins after signup (activation time)
- Check free tier quota (1000 calls/day)

## 📁 File Locations

```
backend/
├── .env                        # Your config HERE
├── reminders.db                # SQLite database
├── main.py                     # Run this
├── app/bot_polling.py         # And this
└── seed_templates.py          # Run once

Logs appear in terminals (stdout)
```

## 🔢 Default Settings

- OTP expires: 10 minutes
- Session expires: 24 hours
- Weather cache: 1 hour
- Check interval: 15 minutes
- Alert cooldown: 6 hours

## 📞 Support

1. **Read first:** `STARTUP_GUIDE_MVP.md`
2. **Run tests:** `python test_mvp.py`
3. **Check logs:** Look at terminal output
4. **Review docs:** `backend/README_MVP.md`

## ⚡ Performance Tips

- Weather API is cached for 1 hour
- Use pagination for large lists
- Sessions auto-expire (no cleanup needed)
- Background checker runs every 15 mins

## 🎯 Common Use Cases

### Test full flow
```bash
# 1. Generate OTP
curl -X POST http://localhost:8000/api/otp/generate \
  -d '{"session_id": "test"}' -H "Content-Type: application/json"

# 2. Link in Telegram
/link 123456

# 3. Create reminder
curl -X POST http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: test" \
  -H "Content-Type: application/json" \
  -d '{"condition": "rain", "hours_ahead": 6}'

# 4. Check in Telegram
/list
```

### Monitor system
```bash
# Terminal 1: Watch API
tail -f # watch API terminal output

# Terminal 2: Watch bot
tail -f # watch bot terminal output

# Check health
watch -n 5 curl -s http://localhost:8000/health
```

### Debug issues
```bash
# Check running processes
ps aux | grep python

# Check ports
netstat -an | findstr 8000

# Test database
python -c "from app.core.database import *; init_db(); print('OK')"
```

## 🎨 Weather Conditions

Supported conditions:
- `rain` - Any rain
- `snow` - Snow
- `clear` - Clear sky
- `clouds` - Cloudy
- `thunderstorm` - Storms
- `drizzle` - Light rain
- `mist`, `fog` - Low visibility

## 📈 Next Steps

1. ✅ Get MVP running
2. 📝 Create custom reminders
3. 🎨 Build frontend UI
4. 🧪 Add more features
5. 🚀 Deploy to production

---

**Need more help?**
- Detailed guide: `STARTUP_GUIDE_MVP.md`
- Architecture: `MVP_CHANGES_SUMMARY.md`
- Checklist: `IMPLEMENTATION_CHECKLIST.md`
