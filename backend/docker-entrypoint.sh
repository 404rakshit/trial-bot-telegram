#!/bin/bash
# Docker entrypoint script for backend
# Runs database migrations and seeding before starting the application

set -e  # Exit immediately if a command exits with a non-zero status

echo "======================================"
echo "Backend Container Startup"
echo "======================================"

# Set defaults for PostgreSQL connection
export POSTGRES_HOST=${POSTGRES_HOST:-postgres}
export POSTGRES_USER=${POSTGRES_USER:-weather_user}
export POSTGRES_DB=${POSTGRES_DB:-weather_bot}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-weather_pass}

echo "Database config: $POSTGRES_USER@$POSTGRES_HOST/$POSTGRES_DB"

# Wait for PostgreSQL to be ready (with timeout)
echo "Waiting for PostgreSQL to be ready..."
RETRY_COUNT=0
MAX_RETRIES=30  # 60 seconds timeout

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "✗ PostgreSQL connection timeout after ${MAX_RETRIES} attempts"
    echo "Continuing anyway - migrations will fail if DB is not ready"
    break
  fi
  echo "PostgreSQL is unavailable - attempt $RETRY_COUNT/$MAX_RETRIES"
  sleep 2
done

if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
  echo "✓ PostgreSQL is ready!"
fi

# Run database migrations
echo "Running Alembic migrations..."
if alembic upgrade head; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migrations failed!"
    echo "Check DATABASE_URL and ensure PostgreSQL is accessible"
    exit 1
fi

# Seed database with initial data (non-critical, don't exit on failure)
echo "Seeding database with initial data..."
if python seed_db.py; then
    echo "✓ Database seeding completed"
else
    echo "⚠ Database seeding failed (non-critical, continuing...)"
fi

echo "======================================"
echo "Starting application..."
echo "======================================"

# Execute the main container command (passed as arguments to this script)
exec "$@"
