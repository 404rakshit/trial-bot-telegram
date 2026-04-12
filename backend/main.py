"""
Simple entry point for running the FastAPI server

Usage:
    python main.py
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Weather Alert Bot API (MVP)")
    print("📝 Server will run on http://localhost:8000")
    print("📖 API docs available at http://localhost:8000/docs")
    print("🛑 Press CTRL+C to stop")
    print()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
