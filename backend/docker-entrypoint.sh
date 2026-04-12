#!/bin/bash
# Docker entrypoint script for backend
# Runs database migrations and seeding before starting the application

set -e  # Exit immediately if a command exits with a non-zero status

echo "======================================"
echo "Backend Container Startup"
echo "======================================"

# Set defaults for PostgreSQL connection
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_USER=${POSTGRES_USER:-weather_user}
POSTGRES_DB=${POSTGRES_DB:-weather_bot}

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "PostgreSQL is ready!"

# Run database migrations
echo "Running Alembic migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migrations failed!"
    exit 1
fi

# Seed database with initial data
echo "Seeding database with initial data..."
python seed_db.py

if [ $? -eq 0 ]; then
    echo "✓ Database seeding completed"
else
    echo "✗ Database seeding failed!"
    exit 1
fi

echo "======================================"
echo "Starting application..."
echo "======================================"

# Execute the main container command (passed as arguments to this script)
exec "$@"
