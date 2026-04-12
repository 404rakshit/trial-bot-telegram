# Phase 2 Verification Guide

## What Was Implemented

Phase 2: Database & API Core has been successfully implemented with the following components:

### 1. Alembic Migration System ✅
- **Files Created:**
  - `backend/alembic.ini` - Alembic configuration
  - `backend/alembic/env.py` - Migration environment with async support
  - `backend/alembic/script.py.mako` - Migration template
  - `backend/alembic/versions/001_initial_schema.py` - Initial migration with all tables and indexes

- **Modified:**
  - `backend/app/core/database.py` - Removed `create_all()`, now uses migrations

### 2. Performance Indexes ✅
- **User Model:** Composite index on `(latitude, longitude)` for weather cache lookups
- **Reminder Model:**
  - Index on `user_id`
  - Index on `is_active`
  - Composite index on `(user_id, is_active)`
- **UseCaseTemplate Model:** Index on `is_active`

### 3. Session Authentication ✅
- **Files Created:**
  - `backend/app/core/auth.py` - Session-based authentication with Redis
    - `get_current_user()` - Required authentication dependency
    - `get_current_user_optional()` - Optional authentication dependency
    - Auto-refreshes session TTL on each request

- **Modified:**
  - `backend/app/core/config.py` - Added `REDIS_SESSION_TTL` and `SESSION_HEADER_NAME`

### 4. Reminder CRUD Endpoints ✅
- **Modified:** `backend/app/api/reminders.py`
  - **GET /api/reminders/** - List user's active reminders with pagination (limit=50, offset=0)
  - **POST /api/reminders/** - Create reminder with validation and template support
  - **DELETE /api/reminders/{id}** - Soft delete with ownership verification

### 5. Template Seeding System ✅
- **Files Created:**
  - `backend/app/core/seed.py` - Seeding logic with 5 weather templates:
    1. Rain Alert (6 hours)
    2. Snow Alert (12 hours)
    3. Hot Day Tomorrow (24 hours)
    4. Cold Night Tonight (12 hours)
    5. Clear Weekend (72 hours)
  - `backend/seed_db.py` - Standalone seeding script (idempotent)

### 6. Templates Endpoint ✅
- **Files Created:**
  - `backend/app/api/templates.py` - Public endpoint for listing active templates

- **Modified:**
  - `backend/app/api/__init__.py` - Included templates router

### 7. Docker Integration ✅
- **Files Created:**
  - `backend/docker-entrypoint.sh` - Runs migrations and seeding on startup

- **Modified:**
  - `backend/Dockerfile` - Uses entrypoint for all stages (development, staging, production)

### 8. Tests ✅
- **Files Created:**
  - `backend/tests/conftest.py` - Test fixtures and configuration
  - `backend/tests/test_auth.py` - Session authentication tests (6 tests)
  - `backend/tests/test_reminders.py` - Reminder CRUD tests (13 tests)
  - `backend/requirements-dev.txt` - Test dependencies

---

## Verification Steps

### Step 1: Rebuild and Start Containers

```bash
# Stop existing containers
docker-compose down

# Rebuild with new Dockerfile changes
docker-compose build api

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

**Expected Output:**
```
======================================
Backend Container Startup
======================================
Waiting for PostgreSQL to be ready...
PostgreSQL is ready!
Running Alembic migrations...
✓ Migrations completed successfully
Seeding database with initial data...
✓ Created 5 new use case templates
Database seeding completed successfully!
======================================
Starting application...
======================================
```

### Step 2: Verify Database Schema

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U weather_user -d weather_bot

# Check tables exist
\dt

# Should show:
#  public | alembic_version        | table | weather_user
#  public | reminders              | table | weather_user
#  public | use_case_templates     | table | weather_user
#  public | users                  | table | weather_user

# Check indexes on users table
\d users

# Should include:
#  "ix_users_chat_id" UNIQUE, btree (chat_id)
#  "ix_users_location" btree (latitude, longitude)

# Check indexes on reminders table
\d reminders

# Should include:
#  "ix_reminders_user_id" btree (user_id)
#  "ix_reminders_is_active" btree (is_active)
#  "ix_reminders_user_active" btree (user_id, is_active)

# Exit psql
\q
```

### Step 3: Verify Template Seeding

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U weather_user -d weather_bot

# Check template count
SELECT COUNT(*) FROM use_case_templates WHERE is_active = true;
# Should return: 5

# List templates
SELECT id, name, condition, hours_ahead FROM use_case_templates ORDER BY name;
# Should show:
#  1 | Clear Weekend       | clear | 72
#  2 | Cold Night Tonight  | cold  | 12
#  3 | Hot Day Tomorrow    | hot   | 24
#  4 | Rain Alert          | rain  | 6
#  5 | Snow Alert          | snow  | 12

# Exit
\q
```

### Step 4: Test Templates Endpoint

```bash
# List templates
curl http://localhost:8000/api/templates/

# Should return JSON array with 5 templates
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "Clear Weekend",
    "description": "Get notified if the weekend will have clear skies (72 hours ahead)",
    "condition": "clear",
    "hours_ahead": 72,
    "message_template": "☀️ Clear skies this weekend! Perfect for outdoor activities."
  },
  ...
]
```

### Step 5: Test Session Authentication

```bash
# Try accessing protected endpoint without session (should fail)
curl -X GET http://localhost:8000/api/reminders/

# Should return 422 (missing header)

# Try with invalid session (should fail)
curl -X GET http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: invalid-session"

# Should return 401 Unauthorized
```

### Step 6: Test Reminder Endpoints (Manual Session Creation)

Since Phase 3 (Telegram integration) isn't complete yet, we need to manually create a user and session:

```bash
# 1. Create a test user in database
docker-compose exec postgres psql -U weather_user -d weather_bot -c "
INSERT INTO users (chat_id, latitude, longitude, timezone, created_at, updated_at)
VALUES (123456789, 40.7128, -74.0060, 'America/New_York', NOW(), NOW())
RETURNING id, chat_id;
"
# Note the returned user ID and chat_id

# 2. Create a session in Redis
docker-compose exec redis redis-cli
SET session:test-session-123 123456789
EXPIRE session:test-session-123 86400
KEYS session:*
# Should show: session:test-session-123
EXIT

# 3. Test GET reminders (should return empty array)
curl -X GET http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: test-session-123"

# Should return: []

# 4. Test POST reminder
curl -X POST http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: test-session-123" \
  -H "Content-Type: application/json" \
  -d '{
    "condition": "rain",
    "hours_ahead": 6,
    "custom_message": "Test rain alert",
    "template_id": 4
  }'

# Should return 201 with created reminder

# 5. Test GET reminders again (should return 1 reminder)
curl -X GET http://localhost:8000/api/reminders/ \
  -H "X-Session-ID: test-session-123"

# 6. Test DELETE reminder (use ID from previous response)
curl -X DELETE http://localhost:8000/api/reminders/1 \
  -H "X-Session-ID: test-session-123"

# Should return 204 No Content

# 7. Verify soft delete
docker-compose exec postgres psql -U weather_user -d weather_bot -c "
SELECT id, condition, is_active FROM reminders;
"
# Should show is_active = false
```

### Step 7: Run Automated Tests

```bash
# Enter API container
docker-compose exec api bash

# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py -v
pytest tests/test_reminders.py -v

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

**Expected Output:**
```
tests/test_auth.py::test_get_current_user_valid_session PASSED
tests/test_auth.py::test_get_current_user_missing_session PASSED
tests/test_auth.py::test_get_current_user_invalid_session PASSED
tests/test_auth.py::test_get_current_user_expired_session PASSED
tests/test_auth.py::test_session_ttl_refresh PASSED
tests/test_auth.py::test_get_current_user_deleted_user PASSED
tests/test_reminders.py::test_list_reminders_empty PASSED
tests/test_reminders.py::test_list_reminders_with_data PASSED
tests/test_reminders.py::test_list_reminders_pagination PASSED
tests/test_reminders.py::test_create_reminder_success PASSED
tests/test_reminders.py::test_create_reminder_with_template PASSED
tests/test_reminders.py::test_create_reminder_invalid_template PASSED
tests/test_reminders.py::test_create_reminder_validation PASSED
tests/test_reminders.py::test_create_reminder_unauthenticated PASSED
tests/test_reminders.py::test_delete_reminder_success PASSED
tests/test_reminders.py::test_delete_reminder_not_found PASSED
tests/test_reminders.py::test_delete_reminder_wrong_user PASSED

======================== 19 passed in X.XXs ========================
```

### Step 8: Verify Alembic History

```bash
docker-compose exec api bash

# Check current revision
alembic current

# Should show: 001 (head)

# View migration history
alembic history

# Should show:
# 001 (head) -> Initial schema
```

### Step 9: Test Idempotent Seeding

```bash
# Run seeding again (should not create duplicates)
docker-compose exec api python seed_db.py

# Should output:
# ✓ Created 0 new use case templates
# ℹ All templates already exist (idempotent operation)

# Verify count is still 5
docker-compose exec postgres psql -U weather_user -d weather_bot -c "
SELECT COUNT(*) FROM use_case_templates;
"
# Should return: 5
```

### Step 10: Full Docker Restart Test

```bash
# Complete teardown and restart
docker-compose down
docker-compose up -d

# Migrations and seeding should run automatically
docker-compose logs api | grep -E "(Migration|Seeding|✓|✗)"

# Should show successful migration and seeding logs
```

---

## Success Criteria ✅

Phase 2 is complete when:

- [x] Alembic migrations work (`alembic upgrade head` succeeds)
- [x] Database has 5 seeded templates
- [x] GET /api/templates/ returns template list
- [x] GET /api/reminders/ validates session (returns 401 without valid session)
- [x] POST /api/reminders/ creates reminder with auth
- [x] DELETE /api/reminders/{id} soft-deletes with ownership check
- [x] Docker restart automatically runs migrations + seeding
- [x] All tests pass (`pytest`)

---

## Troubleshooting

### Issue: Migrations fail with "relation already exists"

**Solution:** Drop tables and run migrations fresh
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

### Issue: Seeding creates duplicate templates

**Solution:** Templates are matched by name. Check if template names changed. Delete duplicates:
```bash
docker-compose exec postgres psql -U weather_user -d weather_bot -c "
DELETE FROM use_case_templates WHERE id NOT IN (
  SELECT MIN(id) FROM use_case_templates GROUP BY name
);
"
```

### Issue: Tests fail with import errors

**Solution:** Install test dependencies
```bash
docker-compose exec api pip install -r requirements-dev.txt
```

### Issue: Entrypoint script not executable

**Solution:** Make script executable
```bash
chmod +x backend/docker-entrypoint.sh
docker-compose build api
docker-compose up -d
```

---

## Next Steps: Phase 3

After Phase 2 verification, proceed to **Phase 3: Telegram & OTP**:

1. Implement `/link <otp>` command in Telegram bot
2. Validate OTP and create User in database
3. Create session in Redis (link OTP → session_id → chat_id)
4. Implement `/list` command with inline keyboard
5. Frontend: Store session_id in localStorage
6. End-to-end flow: Frontend → OTP → Telegram → Reminders

Phase 2 provides the foundation: session auth and reminder CRUD are ready for Phase 3 integration!
