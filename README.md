# Weather Alert Telegram Bot - MVP

A SaaS-style Telegram bot that sends highly configurable weather alerts to users based on their timezone and location preferences.

## 🎉 **MVP Ready!** Quick Start in 3 Steps:

```bash
# 1. Setup (Windows)
cd backend && setup_mvp.bat

# 2. Edit .env with your API keys
# Get Telegram token from @BotFather
# Get Weather API from openweathermap.org

# 3. Run
python main.py                   # Terminal 1: API
python app/bot_polling.py       # Terminal 2: Bot
```

**📖 Full guide:** See [`README_START_HERE.md`](README_START_HERE.md)

---

## 🚀 Features

✅ **Weather Alerts** - Get notified hours in advance
✅ **Telegram Integration** - Full bot commands (/start, /link, /list)
✅ **OTP Linking** - Secure account authentication
✅ **Background Checking** - Automatic weather monitoring
✅ **5 Templates** - Pre-configured alert patterns
✅ **Smart Caching** - Optimized API calls

## 🏗️ Current Architecture (MVP)

**Simplified Local Setup:**
- **Backend**: FastAPI (Python) with SQLite
- **Storage**: In-memory (OTP/sessions)
- **Bot**: Telegram polling mode
- **Checker**: Background thread (every 15 mins)
- **Frontend**: React + Vite (optional)

**No Docker/Redis/PostgreSQL required for MVP!**

## 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend - optional)
- **Telegram account** (for bot testing)
- **OpenWeatherMap account** (free tier)
- **Git**

### External Services
1. **Telegram Bot Token** - Create via [@BotFather](https://t.me/botfather)
2. **OpenWeatherMap API Key** - Sign up at [openweathermap.org](https://openweathermap.org/api)
3. **Cloudflare Account** - For `cloudflared` tunnel (staging/production)
4. **Vercel Account** - For frontend deployment (optional)

## 🛠️ Quick Start

### 1. Clone & Setup

```bash
git clone <repository-url>
cd trial-bot-telegram

# Copy environment files
cp .env.example .env.development
# Edit .env.development and add your API keys
```

### 2. Fill in API Keys

Edit `.env.development`:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENWEATHER_API_KEY=your_openweather_api_key
```

### 3. Start Development Environment

```bash
# Start all services (Postgres, Redis, API, Worker, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f api      # API logs
docker-compose logs -f worker   # Worker logs
docker-compose logs -f frontend # Frontend logs
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **PostgreSQL**: localhost:5432 (credentials in .env.development)
- **Redis**: localhost:6379

## 🌍 Multi-Environment Deployment

### Development (Local)
```bash
docker-compose up -d
```

### Staging
```bash
# Fill in .env.staging first
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

### Production
```bash
# Fill in .env.production first
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📂 Project Structure

```
trial-bot-telegram/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes (OTP, reminders, webhooks)
│   │   ├── core/             # Config, database, Redis
│   │   ├── models/           # SQLAlchemy models
│   │   ├── services/         # Business logic
│   │   └── workers/          # Background tasks
│   ├── tests/
│   ├── Dockerfile            # Multi-stage (dev/staging/prod)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── docker-compose.yml        # Development
├── docker-compose.staging.yml
├── docker-compose.prod.yml
├── .env.development
├── .env.staging
├── .env.production
└── CLAUDE.md                 # AI assistant guidance
```

## 🔧 Development Workflow

### Backend Development
```bash
cd backend

# Local Python development (without Docker)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload

# Run tests (Phase 2+)
pytest
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database Migrations (Phase 2+)
```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 Development Phases

- [x] **Phase 1: Foundation** - Monorepo structure, Docker setup ✅
- [ ] **Phase 2: Database & API Core** - Models, FastAPI lifecycle, Redis
- [ ] **Phase 3: Telegram & OTP** - Webhook, `/start`, `/link <OTP>`, `/list`
- [ ] **Phase 4: Weather Engine** - OpenWeatherMap integration, background tasks
- [ ] **Phase 5: React Frontend** - UI for location/timezone/alert setup
- [ ] **Phase 6: Deployment** - Cloudflared, CORS, production hardening

## 🐛 Troubleshooting

### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build

# Check service health
docker-compose ps
docker-compose logs api
```

### Database Connection Issues
```bash
# Check Postgres is running
docker-compose exec postgres pg_isready -U weather_user

# Connect to database
docker-compose exec postgres psql -U weather_user -d weather_bot
```

### Redis Issues
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Security Notes

- **Never commit** `.env.development`, `.env.staging`, or `.env.production` with real credentials
- Use strong passwords for production (min 20 characters)
- Rotate `SECRET_KEY` for each environment
- Enable Redis password in production
- Use HTTPS only (via cloudflared) in production

## 📄 License

[Your License Here]

## 🤝 Contributing

This is a personal project. Phase 1 complete - see CLAUDE.md for development guidance.

---

**Current Status**: Phase 1 Complete ✅
**Next**: Phase 2 - Database & API Core
