# api/telegram.py
from telegram import Update
from telegram.ext import Application, filters, CallbackQueryHandler
from bot.message import MessageHandler
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize your message handler
message_handler = MessageHandler()

# Initialize the application with the bot token
application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

# Add handlers
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler.handle_message))
application.add_handler(CallbackQueryHandler(message_handler.handle_callback))

async def handle_webhook(request):
    """Handle incoming webhook requests from Telegram"""
    try:
        # Parse the update
        update = Update.de_json(request.json(), application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return {"statusCode": 200, "body": "ok"}
        
    except Exception as e:
        print(f"Error processing update: {str(e)}")
        return {"statusCode": 500, "body": str(e)}

# This is the main handler that Vercel will call
async def handler(request):
    """Main handler for Vercel"""
    # Verify webhook secret if needed
    webhook_secret = os.getenv("WEBHOOK_SECRET")
    if webhook_secret:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != webhook_secret:
            return {"statusCode": 403, "body": "Unauthorized"}
    
    return await handle_webhook(request)
