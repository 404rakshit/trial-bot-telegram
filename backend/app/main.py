"""FastAPI Main Application - Simplified MVP"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Weather Alert Bot API (MVP)...")
    init_db()
    print("✅ Database initialized (SQLite)")

    # Start background reminder checker
    from app.worker.reminder_checker import start_background_checker
    start_background_checker()

    yield

    # Shutdown
    print("🛑 Shutting down...")
    print("✅ Cleanup complete")


app = FastAPI(
    title="Weather Alert Bot API (MVP)",
    version="0.1.0-mvp",
    description="Telegram bot for configurable weather alerts (simplified local version)",
    lifespan=lifespan
)

# CORS middleware for frontend
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
def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Weather Alert Bot API (MVP)",
        "version": "0.1.0-mvp"
    }


@app.get("/health")
def health():
    """Detailed health check"""
    from app.core.session_store import get_stats

    return {
        "status": "healthy",
        "database": "sqlite",
        "storage": get_stats()
    }
