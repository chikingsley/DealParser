from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

class CallbackHandler:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self.editing_field = {}  # Store which field user is editing

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        try:
            await query.answer()
            
            if query.data == "next":
                await self._handle_navigation(update, user_id, 1)
            elif query.data == "prev":
                await self._handle_navigation(update, user_id, -1)
            elif query.data.startswith("confirm_"):
                await self._handle_confirmation(update, user_id)
            elif query.data.startswith("reject_"):
                await self._handle_rejection(update, user_id)
            elif query.data.startswith("edit_"):
                await self._handle_edit_selection(update, user_id, query.data)
            elif query.data == "back_to_review":
                await self._handle_back_to_review(update, user_id)
            elif query.data.startswith("field_"):
                await self._handle_field_edit(update, user_id, query.data)
            
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}", exc_info=True)
            await query.message.reply_text("Error processing your request.")

    async def _handle_navigation(self, update: Update, user_id: int, direction: int):
        """Handle next/prev navigation"""
        user_data = self.message_handler.current_deals.get(user_id)
        if not user_data:
            return
            
        new_index = user_data['current_index'] + direction
        if 0 <= new_index < len(user_data['deals']):
            user_data['current_index'] = new_index
            await self.message_handler._show_deal(update, update.callback_query.message, user_id)

    async def _handle_confirmation(self, update: Update, user_id: int):
        """Handle deal confirmation"""
        user_data = self.message_handler.current_deals.get(user_id)
        if not user_data:
            return
            
        deal = user_data['deals'][user_data['current_index']]
        await update.callback_query.message.reply_text(f"Deal confirmed!\n\nDetails saved:\n{deal.json(indent=2)}")
        
        # Move to next deal if available
        if user_data['current_index'] < len(user_data['deals']) - 1:
            await self._handle_navigation(update, user_id, 1)
        else:
            # Clear deals if this was the last one
            self.message_handler.current_deals.pop(user_id, None)

    async def _handle_rejection(self, update: Update, user_id: int):
        """Handle deal rejection"""
        await update.callback_query.message.reply_text("Deal rejected.")
        await self._handle_navigation(update, user_id, 1)

    async def _handle_edit_selection(self, update: Update, user_id: int, callback_data: str):
        """Show edit options for deal fields"""
        keyboard = [
            [InlineKeyboardButton("Region", callback_data="field_region"),
             InlineKeyboardButton("Partner", callback_data="field_partner")],
            [InlineKeyboardButton("GEO", callback_data="field_geo"),
             InlineKeyboardButton("Language", callback_data="field_language")],
            [InlineKeyboardButton("Source", callback_data="field_source"),
             InlineKeyboardButton("Model", callback_data="field_model")],
            [InlineKeyboardButton("CPA", callback_data="field_cpa"),
             InlineKeyboardButton("CRG", callback_data="field_crg")],
            [InlineKeyboardButton("CPL", callback_data="field_cpl"),
             InlineKeyboardButton("Funnels", callback_data="field_funnels")],
            [InlineKeyboardButton("CR", callback_data="field_cr"),
             InlineKeyboardButton("Deduction Limit", callback_data="field_deduction_limit")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_review")]
        ]
        
        await update.callback_query.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def _handle_field_edit(self, update: Update, user_id: int, callback_data: str):
        """Handle field editing"""
        field = callback_data.replace("field_", "")
        self.editing_field[user_id] = field
        
        await update.callback_query.message.reply_text(
            f"Please enter the new value for {field.replace('_', ' ').title()}:"
        )

    async def _handle_back_to_review(self, update: Update, user_id: int):
        """Return to deal review screen"""
        await self.message_handler._show_deal(update, update.callback_query.message, user_id) 