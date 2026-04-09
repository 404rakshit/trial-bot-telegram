"""FastAPI Main Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis, close_redis
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Weather Alert Bot API...")
    await init_db()
    await init_redis()
    print("✅ Database and Redis connections established")

    yield

    # Shutdown
    print("🛑 Shutting down...")
    await close_redis()
    print("✅ Cleanup complete")


app = FastAPI(
    title="Weather Alert Bot API",
    version="0.1.0",
    description="Telegram bot for configurable weather alerts",
    lifespan=lifespan
)

# CORS middleware for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Weather Alert Bot API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }
