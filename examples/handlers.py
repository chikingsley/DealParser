from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, 
    MessageHandler as TGMessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import logging
from ..core.parser import DealParser

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self, pattern_manager):
        self.pattern_manager = pattern_manager
        self.parser = DealParser(pattern_manager)
        self.current_deals = {}  # Store deals by user_id
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message = update.message.text
        logger.info(f"Processing message from user {user_id}")
        
        try:
            await update.message.reply_text("Processing your message...")
            
            # Parse deals from message
            deals = self.parser.parse_message(message)
            
            if not deals:
                await update.message.reply_text("No valid deals found in message.")
                return
                
            # Store deals for this user
            self.current_deals[user_id] = {
                'deals': deals,
                'current_index': 0
            }
            
            # Show first deal
            await self._show_deal(update, user_id)
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}", exc_info=True)
            await update.message.reply_text("Error processing your message. Please try again.")
    
    async def _show_deal(self, update, user_id):
        """Show current deal with review options"""
        user_data = self.current_deals.get(user_id)
        if not user_data:
            return
            
        deal = user_data['deals'][user_data['current_index']]
        total_deals = len(user_data['deals'])
        current_num = user_data['current_index'] + 1
        
        # Format deal message
        message = (
            f"Deal {current_num}/{total_deals}:\n\n"
            f"GEO: {deal.get('geo', 'N/A')}\n"
            f"Partner: {deal.get('partner', 'N/A')}\n"
            f"Price: {deal.get('price', 'N/A')}\n"
            f"CR: {deal.get('cr', 'N/A')}\n"
            f"Sources: {deal.get('sources', 'N/A')}\n"
        )
        
        # Create review keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data="confirm"),
                InlineKeyboardButton("❌ Reject", callback_data="reject")
            ],
            [InlineKeyboardButton("✏️ Edit", callback_data="edit")]
        ]
        
        if total_deals > 1:
            nav_buttons = []
            if current_num > 1:
                nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data="prev"))
            if current_num < total_deals:
                nav_buttons.append(InlineKeyboardButton("➡️ Next", callback_data="next"))
            keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    def get_handler(self) -> TGMessageHandler:
        """Return the message handler"""
        return TGMessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        )

class ButtonHandler:
    def __init__(self):
        self.message_handler = None  # Will be set by TelegramBot
    
    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        try:
            await query.answer()
            
            if query.data == "next":
                user_data = self.message_handler.current_deals.get(user_id)
                if user_data and user_data['current_index'] < len(user_data['deals']) - 1:
                    user_data['current_index'] += 1
                    await self.message_handler._show_deal(update, user_id)
                    
            elif query.data == "prev":
                user_data = self.message_handler.current_deals.get(user_id)
                if user_data and user_data['current_index'] > 0:
                    user_data['current_index'] -= 1
                    await self.message_handler._show_deal(update, user_id)
                    
            elif query.data in ["confirm", "reject"]:
                await query.message.reply_text(f"Deal {query.data}ed!")
                
            elif query.data == "edit":
                # Show edit options
                keyboard = [
                    [InlineKeyboardButton("GEO", callback_data="edit_geo")],
                    [InlineKeyboardButton("Partner", callback_data="edit_partner")],
                    [InlineKeyboardButton("Price", callback_data="edit_price")],
                    [InlineKeyboardButton("CR", callback_data="edit_cr")],
                    [InlineKeyboardButton("Sources", callback_data="edit_sources")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_to_review")]
                ]
                await query.message.edit_reply_markup(InlineKeyboardMarkup(keyboard))
                
        except Exception as e:
            logger.error(f"Error handling button: {str(e)}", exc_info=True)
            await query.message.reply_text("Error processing button click.")
    
    def get_handler(self) -> CallbackQueryHandler:
        """Return the button handler"""
        return CallbackQueryHandler(self.handle_button)