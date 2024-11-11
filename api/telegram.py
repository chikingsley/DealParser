from telegram import Update
from telegram.ext import Application, MessageHandler as TelegramMessageHandler, CallbackQueryHandler, filters
from bot.message import MessageHandler
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize your message handler
message_handler = MessageHandler()

async def initialize_application():
    """Initialize the application with the bot token"""
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add handlers
    app.add_handler(TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_message))
    app.add_handler(CallbackQueryHandler(message_handler.handle_callback))
    
    await app.initialize()
    return app

# Initialize application at module level
application = None

async def handle_webhook(request):
    """Handle incoming webhook requests from Telegram"""
    global application
    
    try:
        # Initialize application if not already initialized
        if application is None:
            application = await initialize_application()
        
        # Parse the update from request body
        if hasattr(request, 'json'):
            data = await request.json()
        else:
            data = json.loads(request.body)
            
        update = Update.de_json(data, application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ok"})
        }
        
    except Exception as e:
        print(f"Error processing update: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

async def handler(request):
    """Main handler for Vercel"""
    if request.method == "POST":
        # Verify webhook secret if needed
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        if webhook_secret:
            if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != webhook_secret:
                return {
                    "statusCode": 403,
                    "body": json.dumps({"error": "Unauthorized"})
                }
        
        return await handle_webhook(request)
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        } 