import logging
from pathlib import Path
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from core.models.deal import DealProcessor, Deal
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

processor = DealProcessor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me deal information and I will process it.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
    I can help process deal information. Commands:
    /start - Start the bot
    /help - Show this help message
    /stats - Show deal statistics
    """
    await update.message.reply_text(help_text)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show statistics about processed deals."""
    deals = processor.deals
    geos = set(deal.geo for deal in deals)
    partners = set(deal.partner for deal in deals)
    
    stats_text = f"""
    Total deals processed: {len(deals)}
    Unique geos: {len(geos)}
    Geos: {sorted(geos)}
    Unique partners: {len(partners)}
    Partners: {sorted(partners)}
    """
    await update.message.reply_text(stats_text)

async def process_deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process deal information sent by user."""
    try:
        deal_text = update.message.text
        
        # Check for duplicates with details
        duplicate_check = processor.check_duplicate_details(deal_text)
        
        if duplicate_check["is_duplicate"]:
            response = f"⚠️ This appears to be a duplicate deal\nReason: {duplicate_check['reason']}\n"
            if duplicate_check["created_at"]:
                response += f"Originally seen: {duplicate_check['created_at']}\n"
            if duplicate_check["existing_deal"]:
                response += f"Existing deal: {duplicate_check['existing_deal'].dict()}"
            await update.message.reply_text(response)
            return
            
        # For now, just acknowledge receipt
        await update.message.reply_text("Processing new deal...")
        logger.info(f"Received new deal text: {deal_text}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error processing deal: {str(e)}")

def main():
    """Start the bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_deal))

    application.run_polling()

if __name__ == '__main__':
    main() 