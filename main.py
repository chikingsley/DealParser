import logging
from pathlib import Path
import os
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler as TelegramMessageHandler, 
    CallbackQueryHandler, 
    filters
)
from bot.message import MessageHandler
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
        return

    # Create application
    application = Application.builder().token(token).build()

    # Initialize message handler
    message_handler = MessageHandler()

    # Add handlers
    application.add_handler(
        TelegramMessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            message_handler.handle_message
        )
    )
    
    # Add callback handler - this is what handles button presses
    application.add_handler(
        CallbackQueryHandler(message_handler.handle_callback)
    )

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 