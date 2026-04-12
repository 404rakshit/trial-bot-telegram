# Phase 1 Verification Checklist

Complete this checklist to verify Phase 1 is working correctly before moving to Phase 2.

---

## 🔧 Pre-Flight Setup

### ✅ 1. Environment Configuration

1. **Copy and configure environment file**:
   ```bash
   # Already done - verify it exists:
   ls .env.development
   ```

2. **Add your Telegram Bot Token**:
   ```bash
   # Edit .env.development and add:
   TELEGRAM_BOT_TOKEN=your_token_from_botfather
   ```

3. **Verify all env variables**:
   ```bash
   cat .env.development
   # Check: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, REDIS_URL, etc.
   ```

---

## 🐳 Docker Services Verification

### ✅ 2. Start All Services

On your Docker machine:

```bash
# Navigate to project
cd trial-bot-telegram

# Start all services
docker-compose up -d

# Expected output:
# Creating weather_bot_postgres_dev ... done
# Creating weather_bot_redis_dev    ... done
# Creating weather_bot_api_dev      ... done
# Creating weather_bot_worker_dev   ... done
# Creating weather_bot_frontend_dev ... done
```

### ✅ 3. Check Service Status

```bash
docker-compose ps
```

**Expected output** - All services should show "Up":
```
NAME                        STATUS      PORTS
weather_bot_postgres_dev    Up          0.0.0.0:5432->5432/tcp
weather_bot_redis_dev       Up          0.0.0.0:6379->6379/tcp
weather_bot_api_dev         Up          0.0.0.0:8000->8000/tcp
weather_bot_worker_dev      Up          (no ports)
weather_bot_frontend_dev    Up          0.0.0.0:5173->5173/tcp
```

**❌ If any service shows "Exit"**: Check logs (see step 4)

### ✅ 4. Check Logs for Errors

```bash
# Check all logs
docker-compose logs

# Check specific services
docker-compose logs api      # FastAPI backend
docker-compose logs postgres # Database
docker-compose logs redis    # Cache
docker-compose logs frontend # React frontend
docker-compose logs worker   # Background worker
```

**Expected in API logs**:
```
🚀 Starting Weather Alert Bot API...
✅ Database and Redis connections established
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**❌ If you see errors**: Note them and we'll debug

---

## 🗄️ Database Verification

### ✅ 5. Test PostgreSQL Connection

```bash
# Connect to database
docker-compose exec postgres psql -U weather_user -d weather_bot
```

**Expected**: PostgreSQL prompt appears
```
psql (15.x)
Type "help" for help.

weather_bot=#
```

**Test queries**:
```sql
-- List all tables (should show users, reminders, use_case_templates)
\dt

-- Check users table structure
\d users

-- Exit
\q
```

**Expected tables**:
- `users`
- `reminders`
- `use_case_templates`

**❌ If tables don't exist**: Database migration issue (Phase 2 will fix this)

### ✅ 6. Test Redis Connection

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Test commands
PING
# Expected: PONG

# Set test value
SET test "Hello Redis"
# Expected: OK

# Get test value
GET test
# Expected: "Hello Redis"

# Delete test value
DEL test
# Expected: (integer) 1

# Exit
exit
```

---

## 🌐 API Backend Verification

### ✅ 7. Test API Health Endpoint

**From your browser or curl**:

```bash
# Health check
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","database":"connected","redis":"connected"}
```

```bash
# Root endpoint
curl http://localhost:8000/

# Expected output:
# {"status":"healthy","service":"Weather Alert Bot API","version":"0.1.0"}
```

**❌ If connection refused**: API container not running - check logs

### ✅ 8. Test API Documentation

**Open in browser**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Expected**: Interactive API documentation loads

**Verify these endpoints exist**:
- `POST /api/otp/generate` - Generate OTP
- `GET /api/reminders/` - List reminders
- `POST /api/reminders/` - Create reminder
- `POST /api/webhook/telegram` - Telegram webhook

### ✅ 9. Test OTP Generation (API Only)

**Using curl**:
```bash
curl -X POST http://localhost:8000/api/otp/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-session-123"}'

# Expected output:
# {"otp":"123456","expires_in":600}
```

**Using Swagger UI** (http://localhost:8000/docs):
1. Click on `POST /api/otp/generate`
2. Click "Try it out"
3. Enter request body:
   ```json
   {
     "session_id": "test-session-123"
   }
   ```
4. Click "Execute"
5. Expected Response: `200 OK` with 6-digit OTP

**Verify in Redis**:
```bash
docker-compose exec redis redis-cli

# Check OTP was stored
KEYS otp:*
# Expected: "otp:123456" (your OTP)

GET otp:123456
# Expected: "test-session-123"

# Check TTL (should be ~600 seconds = 10 minutes)
TTL otp:123456
# Expected: (integer) ~595

exit
```

---

## 🎨 Frontend Verification

### ✅ 10. Test Frontend Access

**Open in browser**:
- http://localhost:5173

**Expected**:
- Beautiful gradient blue/indigo page loads
- "Weather Alert Bot" heading
- "Get Started" button visible

**❌ If page doesn't load**: Check frontend logs

### ✅ 11. Test Frontend OTP Generation (End-to-End)

**In the browser** (http://localhost:5173):

1. Click **"Get Started"** button
   - Button text changes to "Generating..."

2. Wait ~1 second

3. **Expected result**:
   - Large 6-digit OTP code appears (e.g., "123456")
   - "Expires in 10 minutes" message
   - Instructions to use `/link` command in Telegram
   - "Generate New OTP" button appears

4. Click **"Generate New OTP"**
   - Should return to initial state
   - Click "Get Started" again
   - Should get a new (different) OTP

**❌ If OTP generation fails**:
- Open browser console (F12)
- Check for CORS errors or network errors
- Check API logs: `docker-compose logs api`

**Verify OTP in Redis**:
```bash
docker-compose exec redis redis-cli
KEYS otp:*
# Should show your OTP
exit
```

---

## 🤖 Telegram Bot Verification

### ✅ 12. Test Telegram Bot (Polling Mode)

**On your dev machine** (not Docker):

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start polling bot**:
   ```bash
   python -m app.bot_polling
   ```

   **Expected output**:
   ```
   🤖 Starting Telegram Bot in POLLING mode...
   📝 Bot Token: 123456789:...
   ✅ Bot started! Press Ctrl+C to stop.
   💡 Send /start to your bot in Telegram to test
   ```

3. **Open Telegram** and search for your bot

4. **Test commands**:

   **Send**: `/start`
   ```
   Expected:
   👋 Welcome to Weather Alert Bot!

   To link your account:
   1. Go to the web app and generate an OTP
   2. Send me: /link <your-otp-code>
   ```

   **Send**: `/link 123456`
   ```
   Expected:
   ✅ Received OTP: 123456
   📱 Your chat ID: 123456789

   ⚠️ OTP validation will be implemented in Phase 3
   ```

   **Send**: `/list`
   ```
   Expected:
   📋 Your active reminders will appear here.
   ⚠️ This feature will be implemented in Phase 3
   ```

5. **Stop the bot**: Press `Ctrl+C`

**❌ If bot doesn't respond**:
- Check `TELEGRAM_BOT_TOKEN` in `.env.development`
- Verify bot is running (see console output)
- Check for errors in console

---

## 🔍 Integration Test (Complete Flow)

### ✅ 13. End-to-End User Flow

**Simulate a real user experience**:

1. **Frontend** (http://localhost:5173):
   - Click "Get Started"
   - Note the OTP code (e.g., "123456")

2. **Verify in Redis**:
   ```bash
   docker-compose exec redis redis-cli
   GET otp:123456
   # Should return a session ID
   exit
   ```

3. **Telegram**:
   - Make sure bot is running: `python -m app.bot_polling`
   - Open Telegram, find your bot
   - Send: `/link 123456` (your OTP)
   - Bot should respond with your chat ID

4. **Check API Logs**:
   ```bash
   docker-compose logs api | tail -20
   # Should see OTP generation request logged
   ```

**✅ Success**: Complete flow works from frontend → API → Redis → Telegram bot!

---

## 📊 Final Verification Checklist

Mark each item as you complete it:

**Docker Services:**
- [ ] All 5 containers running (`docker-compose ps`)
- [ ] No errors in logs (`docker-compose logs`)
- [ ] Postgres accepting connections
- [ ] Redis responding to PING

**API Backend:**
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible at `/docs`
- [ ] OTP generation works via API
- [ ] OTP stored in Redis with TTL

**Frontend:**
- [ ] Page loads at localhost:5173
- [ ] "Get Started" button works
- [ ] OTP appears after clicking
- [ ] Can generate multiple OTPs

**Telegram Bot:**
- [ ] Bot responds to `/start`
- [ ] Bot responds to `/link <otp>`
- [ ] Bot responds to `/list`
- [ ] Chat ID is displayed

**Integration:**
- [ ] Frontend → API → Redis flow works
- [ ] Redis TTL set correctly (10 minutes)
- [ ] CORS working (no browser errors)
- [ ] All components communicate successfully

---

## ✅ Phase 1 Complete!

If all checks pass, congratulations! 🎉

**You've successfully completed:**
- ✅ Monorepo structure setup
- ✅ Docker multi-environment configuration
- ✅ PostgreSQL database with models
- ✅ Redis caching layer
- ✅ FastAPI backend with CORS
- ✅ React + Vite frontend
- ✅ Telegram bot (polling mode)
- ✅ End-to-end OTP flow

**Next Steps:**
1. Commit all changes to git
2. Review Phase 1 completion with your team
3. Plan Phase 2: Database migrations, OTP validation, user management

---

## 🐛 Common Issues & Fixes

### Issue: "Port already in use"
```bash
# Find and kill process using port 5432/6379/8000/5173
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Then restart:
docker-compose down
docker-compose up -d
```

### Issue: "Cannot connect to database"
```bash
# Check Postgres is running
docker-compose ps postgres

# Check Postgres logs
docker-compose logs postgres

# Restart Postgres
docker-compose restart postgres
```

### Issue: "CORS error in browser"
- Check API logs for CORS middleware configuration
- Verify `CORS_ORIGINS` in `.env.development` includes `http://localhost:5173`
- Restart API: `docker-compose restart api`

### Issue: "Frontend shows blank page"
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### Issue: "OTP not generating"
- Open browser console (F12) to see errors
- Check API is running: `curl http://localhost:8000/health`
- Check Redis is running: `docker-compose exec redis redis-cli PING`
- Verify `VITE_API_URL` in frontend env

---

## 📸 Screenshots to Capture

For your documentation, take screenshots of:
1. ✅ `docker-compose ps` showing all services "Up"
2. ✅ API Swagger docs at `/docs`
3. ✅ Frontend with generated OTP
4. ✅ Telegram bot responding to `/start`
5. ✅ Redis showing stored OTP

---

**Ready for Phase 2?** Let me know when all checks pass! 🚀
