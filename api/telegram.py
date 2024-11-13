from telegram import Update
from telegram.ext import (
    Application, 
    MessageHandler as TelegramMessageHandler,
    filters, 
    CallbackContext
)
import os
from bot.message import MessageHandler

# Initialize message handler
message_handler = MessageHandler()

async def handler(update: Update, context: CallbackContext):
    """Route incoming messages to message handler"""
    await message_handler.handle_message(update, context)

def initialize_application():
    """Initialize and configure the application"""
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Use TelegramMessageHandler instead
    app.add_handler(TelegramMessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    
    return app