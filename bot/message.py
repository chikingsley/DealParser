from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.client import DealParser
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.deal_parser = DealParser()
        self.current_deals = {}  # Store deals by user_id
        self.state_manager = StateManager()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message = update.message.text
        
        try:
            # Send processing message
            processing_message = await update.message.reply_text(
                "💫 Processing your deals... Please wait."
            )
            
            # Parse deals
            formatted_deals = self.deal_parser.parse_deals(message)
            if not formatted_deals:
                await processing_message.edit_text("❌ No valid deals found in message.")
                return
                
            # Show deals
            await self._show_deal(update, processing_message, formatted_deals)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ Error processing your message. Please check the format and try again."
            )

    async def _show_deal(self, update: Update, message, deals: list):
        """Show deals with review options"""
        user_id = update.effective_user.id
        total_deals = len(deals)
        
        # Store deals for this user
        self.current_deals[user_id] = {
            'deals': deals,
            'current_index': 0
        }
        
        await self._display_current_deal(update, message, user_id)

    async def _display_current_deal(self, update: Update, message, user_id: int):
        """Display current deal with navigation"""
        user_data = self.current_deals.get(user_id)
        if not user_data:
            return

        current_index = user_data['current_index']
        total_deals = len(user_data['deals'])
        deal = user_data['deals'][current_index]

        # Format deal message
        deal_text = (
            f"📋 Deal {current_index + 1} of {total_deals} to review:\n\n"
            f"📊 Deal Details:\n"
            f"• Partner: {deal.get('partner', 'N/A')}\n"
            f"• Region: {deal.get('region', 'N/A')}\n"
            f"• GEO: {deal.get('geo', 'N/A')}\n"
            f"• Language: {deal.get('language', 'Native')}\n"
            f"• Source: {deal.get('source', 'N/A')}\n"
            f"• Pricing Model: {'CPA/CRG' if deal.get('crg') else 'N/A'}\n"
            f"• CPA: {deal.get('cpa', 'N/A')}\n"
            f"• CRG: {f'{deal.get('crg')*100}%' if deal.get('crg') else 'N/A'}\n"
            f"• CPL: {deal.get('cpl', 'N/A')}\n"
            f"• Funnels: {', '.join(deal.get('funnels', [])) or 'N/A'}\n"
            f"• CR: {f'{deal.get('cr')*100}%' if deal.get('cr') else 'N/A'}"
        )

        # Create keyboard
        keyboard = []
        
        # Add navigation buttons
        nav_row = []
        if current_index > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_index}"))
        if current_index < total_deals - 1:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_index}"))
        if nav_row:
            keyboard.append(nav_row)

        # Add action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{current_index}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{current_index}")
            ],
            [InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{current_index}")]
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            if message:
                await message.edit_text(deal_text, reply_markup=reply_markup)
            else:
                await update.message.reply_text(deal_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error displaying deal: {str(e)}")