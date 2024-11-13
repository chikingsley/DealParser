import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from fastapi import FastAPI, Request, logger
import uvicorn
from api.telegram import handler, initialize_application
from dotenv import load_dotenv
import asyncio
from telegram import Update
from telegram.ext import CallbackContext

# Create FastAPI app for local testing
app = FastAPI()

# Store telegram app instance
telegram_app = None

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global telegram_app
    telegram_app = initialize_application()
    await telegram_app.initialize()
    await telegram_app.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global telegram_app
    try:
        await telegram_app.stop()
    except asyncio.CancelledError:
        # Gracefully handle cancellation
        pass
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    """Local endpoint for testing"""
    global telegram_app
    
    # Get JSON data from request
    json_data = await request.json()
    
    # Create Update object from JSON
    update = Update.de_json(json_data, telegram_app.bot)
    
    # Create context
    context = CallbackContext(telegram_app)
    
    # Handle update
    await handler(update, context)
    
    # Return success response
    return {"status": "ok"}

def run_local_server():
    """Run local server for testing"""
    print("🚀 Starting local test server...")
    print("📝 Endpoints:")
    print("   POST http://localhost:8000/api/telegram")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    load_dotenv()
    run_local_server()
