import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from fastapi import FastAPI, Request
import uvicorn
from api.telegram import handler, initialize_application
from dotenv import load_dotenv
import asyncio

# Create FastAPI app for local testing
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await initialize_application()

@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    """Local endpoint for testing"""
    return await handler(request)

def run_local_server():
    """Run local server for testing"""
    print("🚀 Starting local test server...")
    print("📝 Endpoints:")
    print("   POST http://localhost:8000/api/telegram")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    load_dotenv()
    run_local_server() 