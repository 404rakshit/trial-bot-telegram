# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A SaaS-style Telegram Bot that sends highly configurable weather alerts (e.g., "Rain in 6 hours") to non-technical users based on their timezone. This is a split monorepo with a React frontend (Vercel) and Python FastAPI backend (self-hosted Docker).

## Architecture

**CRITICAL CONSTRAINT:** Backend runs on an older PC - all code must be optimized for low memory usage.

### Frontend (`/frontend`)
- **Stack:** React + Vite + Tailwind CSS
- **Deployment:** Vercel
- **Environment:** `VITE_API_URL` points to backend API

### Backend (`/backend`)
- **API:** FastAPI (Python) - Webhooks and REST endpoints
- **Database:** PostgreSQL (user data, reminders, templates)
- **Cache/Broker:** Redis (OTP storage, weather API cache)
- **Worker:** Celery or APScheduler (periodic weather checks)
- **Tunnel:** Cloudflare `cloudflared` for HTTPS exposure to Vercel

### Database Models ✅
- `User` - Telegram chat_id, timezone, location (with location index for weather caching)
- `UseCaseTemplate` - Pre-configured alert patterns (5 weather templates seeded)
- `Reminder` - User's active weather alerts (soft delete with indexes)

## Development Commands

### Backend
```bash
cd backend

# Setup & dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI locally (without Docker)
uvicorn app.main:app --reload

# Docker operations
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs -f api    # View API logs
docker-compose logs -f worker # View worker logs

# Database migrations (Alembic)
docker-compose exec api alembic upgrade head
docker-compose exec api alembic revision --autogenerate -m "description"
docker-compose exec api alembic current
docker-compose exec api alembic history

# Database seeding
docker-compose exec api python seed_db.py

# Tests
docker-compose exec api bash
pip install -r requirements-dev.txt
pytest                        # Run all tests
pytest -v                     # Verbose output
pytest tests/test_auth.py     # Auth tests
pytest tests/test_reminders.py # Reminder tests
```

### Frontend
```bash
cd frontend

# Setup & dependencies
npm install

# Development
npm run dev                   # Start dev server
npm run build                 # Production build
npm run preview               # Preview production build

# Linting & formatting (to be configured)
npm run lint
npm run format
```

## Core Technical Workflows

### 1. Anti-Spam OTP Flow
1. User configures alert on frontend
2. Frontend → `POST /api/generate-otp` → Backend
3. Backend generates 6-digit OTP, stores in Redis (10min TTL)
4. User sends `/link <OTP>` to Telegram bot
5. Backend validates OTP from Redis, saves `chat_id` to Postgres

### 2. Weather API Caching Strategy
- Round coordinates to 2 decimal places (~1km grid) before API calls
- Cache OpenWeatherMap responses in Redis for 1 hour
- Reduces API rate limit issues and improves response time

### 3. Timezone Handling
- **ALL database timestamps MUST be UTC**
- Alert calculations: compare UTC forecast times vs current UTC
- User's timezone used only for display/configuration

### 4. Telegram Command: `/list`
- Shows inline keyboard of user's active reminders
- Users can delete reminders directly from chat
- Implement using `python-telegram-bot` inline keyboard markup

## Development Phases

Build strictly step-by-step. **Do not proceed to next phase until current phase is tested and confirmed working.**

- [x] **Phase 1: Foundation** - Monorepo structure (`/frontend`, `/backend`), `docker-compose.yml` (Postgres, Redis, FastAPI, Worker) ✅ COMPLETE
- [x] **Phase 2: Database & API Core** - Alembic migrations, session auth, reminder CRUD, template seeding, performance indexes ✅ COMPLETE
- [ ] **Phase 3: Telegram & OTP** - Telegram webhook setup, `/start` and `/link <OTP>` commands, OTP generation endpoint
- [ ] **Phase 4: Weather Engine** - OpenWeatherMap integration with Redis caching, scheduled background task for alerts
- [ ] **Phase 5: React Frontend** - Vite UI for location/timezone/alert selection, OTP request flow
- [ ] **Phase 6: Deployment** - `cloudflared` in Docker Compose, CORS middleware for Vercel domain

## Critical Implementation Notes

### Memory Optimization
- Use database connection pooling with strict limits
- Implement pagination for all list queries
- Avoid loading all users/reminders into memory
- Use Redis TTL aggressively to prevent memory bloat

### Security
- Never expose Telegram bot token in frontend code
- Validate all Telegram webhook requests (verify token/signature)
- Rate limit OTP generation per IP/session
- Sanitize user input for weather alerts

### API Endpoints
```
# Implemented (Phase 1-2)
POST   /api/otp/generate          # Frontend requests OTP ✅
GET    /api/templates/            # List active use case templates ✅
GET    /api/reminders/            # User's active reminders (auth required) ✅
POST   /api/reminders/            # Create new reminder (auth required) ✅
DELETE /api/reminders/{id}        # Soft delete reminder (auth required) ✅

# To be implemented (Phase 3+)
POST   /api/webhook/telegram      # Telegram bot webhook
```

## Before Making Changes

1. **Identify current phase** - Check which phase checkboxes are completed above
2. **Confirm before heavy operations** - Ask before modifying database schema or installing large dependencies
3. **Keep code modular** - Separate concerns for memory efficiency
4. **Test incrementally** - Verify each component works before moving forward
