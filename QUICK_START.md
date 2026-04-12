# Quick Start - Phase 1 Testing

Fast track to test Phase 1 in under 5 minutes!

## 1️⃣ Setup Environment (30 seconds)

```bash
# Add your Telegram bot token
nano .env.development
# Set: TELEGRAM_BOT_TOKEN=your_token_here
```

## 2️⃣ Start Docker (1 minute)

```bash
docker-compose up -d
docker-compose ps  # Verify all services are "Up"
```

## 3️⃣ Test API (30 seconds)

```bash
# Test health
curl http://localhost:8000/health

# Open API docs in browser
# http://localhost:8000/docs
```

## 4️⃣ Test Frontend (1 minute)

```bash
# Open in browser
# http://localhost:5173

# Click "Get Started" → Should show 6-digit OTP
```

## 5️⃣ Test Telegram Bot (2 minutes)

```bash
cd backend
pip install -r requirements.txt
python -m app.bot_polling
```

In Telegram:
- Send `/start` to your bot
- Send `/link 123456`

---

## ✅ Success Criteria

- [ ] All 5 Docker containers running
- [ ] API returns `{"status":"healthy"}`
- [ ] Frontend shows OTP after clicking "Get Started"
- [ ] Telegram bot responds to commands

## 🐛 Issues?

See detailed troubleshooting in `PHASE_1_VERIFICATION.md`

---

**All working?** Congrats! Phase 1 complete! 🎉

**Having issues?** Check the full guide: `PHASE_1_VERIFICATION.md`
