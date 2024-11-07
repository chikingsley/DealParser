from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.mistral.client import DealParser
from core.models.deal import Deal
import logging
import json

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.deal_parser = DealParser()
        self.current_deals = {}  # Store deals by user_id
        self.editing_field = {}  # Store which field user is editing

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message = update.message.text
        
        try:
            # Send processing message
            processing_message = await update.message.reply_text(
                "Processing your deals... Please wait."
            )
            
            # Parse deals
            formatted_deals = self.deal_parser.parse_deals(message)
            if not formatted_deals:
                await processing_message.edit_text("No valid deals found in message.")
                return
                
            # Convert to Deal objects
            deals = [Deal.from_formatted_string(deal) for deal in formatted_deals]
            
            # Store deals for this user
            self.current_deals[user_id] = {
                'deals': deals,
                'current_index': 0
            }
            
            # Show first deal
            await self._show_deal(update, processing_message, user_id)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "Error processing your message. Please check the format and try again."
            )

    async def _show_deal(self, update: Update, message, user_id: int):
        """Show current deal with review options"""
        user_data = self.current_deals.get(user_id)
        if not user_data:
            return
            
        deal = user_data['deals'][user_data['current_index']]
        total_deals = len(user_data['deals'])
        current_num = user_data['current_index'] + 1
        
        # Format deal message
        deal_text = (
            f"Deal {current_num}/{total_deals}:\n\n"
            f"Region: {deal.region}\n"
            f"Partner: {deal.partner}\n"
            f"GEO: {deal.geo}\n"
            f"Language: {deal.language}\n"
            f"Source: {deal.source}\n"
            f"Model: {deal.model}\n"
            f"CPA: {deal.cpa if deal.cpa else 'N/A'}\n"
            f"CRG: {deal.crg if deal.crg else 'N/A'}\n"
            f"CPL: {deal.cpl if deal.cpl else 'N/A'}\n"
            f"Funnels: {deal.funnels}\n"
            f"CR: {deal.cr if deal.cr else 'N/A'}\n"
            f"Deduction Limit: {deal.deduction_limit if deal.deduction_limit else 'N/A'}"
        )
        
        # Create keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{current_num}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{current_num}")
            ],
            [InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{current_num}")]
        ]
        
        # Add navigation buttons if multiple deals
        if total_deals > 1:
            nav_buttons = []
            if current_num > 1:
                nav_buttons.append(
                    InlineKeyboardButton("⬅️ Previous", callback_data="prev")
                )
            if current_num < total_deals:
                nav_buttons.append(
                    InlineKeyboardButton("➡️ Next", callback_data="next")
                )
            keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update or send message
        if message:
            await message.edit_text(deal_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(deal_text, reply_markup=reply_markup) 

    async def handle_edit_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text input during field editing"""
        user_id = update.effective_user.id
        if user_id not in self.editing_field:
            return await self.handle_message(update, context)
            
        field = self.editing_field[user_id]
        new_value = update.message.text.strip()
        
        try:
            # Get current deal
            user_data = self.current_deals[user_id]
            deal = user_data['deals'][user_data['current_index']]
            
            # Update field
            deal_dict = deal.dict()
            deal_dict[field] = new_value
            
            # Create new deal with updated field
            updated_deal = Deal(**deal_dict)
            user_data['deals'][user_data['current_index']] = updated_deal
            
            # Clear editing state
            del self.editing_field[user_id]
            
            # Show updated deal
            await self._show_deal(update, None, user_id)
            
        except Exception as e:
            logger.error(f"Error updating field: {str(e)}", exc_info=True)
            await update.message.reply_text(
                f"Error updating {field}. Please try again or click 🔙 Back to cancel."
            )