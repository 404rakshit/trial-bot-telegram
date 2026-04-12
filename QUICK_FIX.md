# Quick Fix: Container Permission Denied Error

## What Happened
The Docker entrypoint script had permission issues, likely due to:
1. Windows CRLF line endings
2. Missing execute permissions
3. Incorrect path resolution

## What Was Fixed
✅ Updated Dockerfile to automatically convert CRLF → LF
✅ Changed entrypoint to use explicit `/bin/bash` execution
✅ Added timeout handling for PostgreSQL connection
✅ Made seeding non-critical (won't stop container if it fails)
✅ Added `.gitattributes` to prevent future line ending issues

## Steps to Fix (Choose One)

### Option 1: Full Rebuild (RECOMMENDED)

```bash
# Stop containers
docker compose down
# OR
docker-compose down

# Rebuild API container without cache
docker compose build api --no-cache
# OR
docker-compose build api --no-cache

# Start containers
docker compose up -d
# OR
docker-compose up -d

# Watch logs to verify success
docker compose logs -f api
# OR
docker-compose logs -f api
```

**Expected output:**
```
======================================
Backend Container Startup
======================================
Database config: weather_user@postgres/weather_bot
Waiting for PostgreSQL to be ready...
✓ PostgreSQL is ready!
Running Alembic migrations...
✓ Migrations completed successfully
Seeding database with initial data...
✓ Database seeding completed
======================================
Starting application...
======================================
```

### Option 2: Quick Workaround (If rebuild fails)

Create `docker-compose.override.yml`:
```yaml
version: '3.8'

services:
  api:
    entrypoint: []
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then:
```bash
docker compose up -d
docker compose exec api alembic upgrade head
docker compose exec api python seed_db.py
```

---

## Verify It's Working

```bash
# 1. Check container status (should say "Up")
docker compose ps api

# 2. Test API
curl http://localhost:8000/api/templates/

# 3. Check database
docker compose exec postgres psql -U weather_user -d weather_bot -c "\dt"
```

---

## If Still Failing

See `TROUBLESHOOTING_ENTRYPOINT.md` for detailed troubleshooting steps.

**Common issues:**
- PostgreSQL not starting → Check `docker compose logs postgres`
- Migration errors → Try `docker compose down -v` then `docker compose up -d`
- Port conflicts → Check if port 8000 is already in use

---

## Files Changed

These files were updated to fix the issue:
- ✅ `backend/Dockerfile` - Line ending conversion + explicit bash
- ✅ `backend/docker-entrypoint.sh` - Better error handling + timeout
- ✅ `.gitattributes` - Prevent future line ending issues (NEW)
- ✅ `docker-compose.override.yml.example` - Debugging template (NEW)
- ✅ `TROUBLESHOOTING_ENTRYPOINT.md` - Full troubleshooting guide (NEW)

**No changes needed to your code or configuration files!**
