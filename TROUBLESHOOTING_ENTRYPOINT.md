# Troubleshooting: Docker Entrypoint Issues

## Problem
- Container shows "permission denied" when executing `/docker-entrypoint.sh`
- HTTP 400 errors
- Container fails to start

## Solutions

### Solution 1: Rebuild with Fixed Dockerfile (RECOMMENDED)

The Dockerfile has been updated to handle Windows line endings and use explicit bash execution.

```bash
# Stop all containers
docker compose down
# OR
docker-compose down

# Rebuild the API container
docker compose build api --no-cache
# OR
docker-compose build api --no-cache

# Start containers
docker compose up -d
# OR
docker-compose up -d

# Check logs
docker compose logs -f api
# OR
docker-compose logs -f api
```

### Solution 2: Temporarily Disable Entrypoint (for debugging)

If you need to debug without the entrypoint, create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  api:
    entrypoint: []  # Disable entrypoint
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Then run:
```bash
docker compose up -d
```

**After debugging, remove `docker-compose.override.yml` to restore entrypoint functionality.**

### Solution 3: Manual Migration Inside Container

If the entrypoint fails but container starts without it:

```bash
# Enter the running container
docker compose exec api bash

# Run migrations manually
alembic upgrade head

# Run seeding manually
python seed_db.py

# Exit
exit
```

### Solution 4: Fix Line Endings Locally (Windows)

If you're on Windows and the file has CRLF line endings:

```bash
# Navigate to backend folder
cd backend

# Option A: Using dos2unix (if available)
dos2unix docker-entrypoint.sh

# Option B: Using sed
sed -i 's/\r$//' docker-entrypoint.sh

# Option C: Using Git
git config core.autocrlf input
git rm --cached docker-entrypoint.sh
git add docker-entrypoint.sh
git commit -m "Fix line endings"

# Make executable
chmod +x docker-entrypoint.sh

# Rebuild
docker compose build api --no-cache
```

---

## Verification Steps

After applying a solution, verify it works:

### 1. Check Container Status
```bash
docker compose ps

# API should show "Up" status, not "Restarting" or "Exited"
```

### 2. Check Container Logs
```bash
docker compose logs api

# Should see:
# ======================================
# Backend Container Startup
# ======================================
# Waiting for PostgreSQL to be ready...
# ✓ PostgreSQL is ready!
# Running Alembic migrations...
# ✓ Migrations completed successfully
# Seeding database with initial data...
# ✓ Database seeding completed
# ======================================
# Starting application...
# ======================================
```

### 3. Test API Endpoint
```bash
curl http://localhost:8000/api/templates/

# Should return JSON with templates (or empty array if seeding failed)
```

### 4. Check Database
```bash
docker compose exec postgres psql -U weather_user -d weather_bot

# Check if tables exist
\dt

# Should show: users, reminders, use_case_templates, alembic_version

# Exit
\q
```

---

## Common Issues and Fixes

### Issue: "PostgreSQL connection timeout"

**Cause:** Database container not ready or environment variables incorrect

**Fix:**
1. Check PostgreSQL is running: `docker compose ps postgres`
2. Check environment variables in `.env.development`:
   ```
   POSTGRES_HOST=postgres
   POSTGRES_USER=weather_user
   POSTGRES_PASSWORD=weather_pass
   POSTGRES_DB=weather_bot
   DATABASE_URL=postgresql://weather_user:weather_pass@postgres:5432/weather_bot
   ```
3. Restart: `docker compose down && docker compose up -d`

### Issue: "Migrations failed"

**Cause:** Database URL incorrect or tables already exist with wrong schema

**Fix:**
```bash
# Drop all tables and start fresh
docker compose down -v  # -v removes volumes
docker compose up -d
```

### Issue: "Seeding failed" (Non-critical)

**Cause:** Templates already exist or database connection issue

**Fix:**
- Seeding failure is non-critical, the app will still start
- Templates can be seeded manually: `docker compose exec api python seed_db.py`

### Issue: HTTP 400 errors

**Cause:** Application starting before migrations complete

**Fix:**
- The new entrypoint ensures migrations run first
- If still occurring, check application logs: `docker compose logs api`
- Look for Python errors in the FastAPI startup

### Issue: "exec format error"

**Cause:** Windows CRLF line endings

**Fix:**
- The Dockerfile now automatically converts line endings
- If still occurring, manually fix: `sed -i 's/\r$//' backend/docker-entrypoint.sh`
- Rebuild: `docker compose build api --no-cache`

---

## Alternative: Skip Entrypoint Permanently (NOT RECOMMENDED)

If you want to run migrations manually every time:

1. Edit `docker-compose.yml` and remove the entrypoint from the Dockerfile
2. Comment out ENTRYPOINT lines in `backend/Dockerfile`
3. Run migrations manually after each container restart

**This is NOT recommended for production or team environments.**

---

## Need More Help?

1. **Check full logs:**
   ```bash
   docker compose logs --tail=100 api
   ```

2. **Check if file permissions are correct in container:**
   ```bash
   docker compose run --rm api ls -la /app/docker-entrypoint.sh
   # Should show: -rwxr-xr-x (executable)
   ```

3. **Test entrypoint script syntax:**
   ```bash
   docker compose run --rm api bash -n /app/docker-entrypoint.sh
   # Should output nothing if syntax is OK
   ```

4. **Try running entrypoint manually:**
   ```bash
   docker compose run --rm api bash /app/docker-entrypoint.sh uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## Quick Fix Summary

**Most likely fix for your current issue:**

```bash
# 1. Stop everything
docker compose down

# 2. Rebuild without cache
docker compose build api --no-cache

# 3. Start again
docker compose up -d

# 4. Watch logs
docker compose logs -f api

# 5. If it fails, try the override approach above
```

The Dockerfile has been updated to:
- ✅ Convert CRLF to LF automatically
- ✅ Use explicit `/bin/bash` execution
- ✅ Use absolute paths for entrypoint
- ✅ Add better error messages and timeout handling
- ✅ Make seeding non-critical (won't stop container if it fails)
