# Quick Start Scripts

## For Development Environment

### Start Everything
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f          # All services
docker-compose logs -f api      # Just API
docker-compose logs -f worker   # Just worker
```

### Stop Everything
```bash
docker-compose down
```

### Reset Everything (including data)
```bash
docker-compose down -v
docker-compose up -d --build
```

## For Staging Environment

```bash
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.staging.yml logs -f
docker-compose -f docker-compose.yml -f docker-compose.staging.yml down
```

## For Production Environment

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

## Database Commands

### Run migrations (when Phase 2 is done)
```bash
docker-compose exec api alembic upgrade head
```

### Create new migration
```bash
docker-compose exec api alembic revision --autogenerate -m "description"
```

### Access PostgreSQL
```bash
docker-compose exec postgres psql -U weather_user -d weather_bot
```

### Access Redis CLI
```bash
docker-compose exec redis redis-cli
```

## Frontend Development (without Docker)

```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

## Backend Development (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Access at http://localhost:8000
```
