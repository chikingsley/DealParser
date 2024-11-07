import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class CallbackHandler:
    def __init__(self, message_handler):
        self.message_handler = message_handler
        self._last_callback_time = 0

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks with debounce"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        # Debounce check
        current_time = time.time()
        if current_time - self._last_callback_time < 0.5:
            await query.answer("Please wait...")
            return
        self._last_callback_time = current_time
        
        try:
            await query.answer()
            
            action, index = query.data.split('_')
            index = int(index)
            
            if action in ['prev', 'next']:
                user_data = self.message_handler.current_deals.get(user_id)
                if user_data:
                    if action == 'next' and index < len(user_data['deals']) - 1:
                        user_data['current_index'] = index + 1
                    elif action == 'prev' and index > 0:
                        user_data['current_index'] = index - 1
                    await self.message_handler._display_current_deal(update, query.message, user_id)
                    
            elif action == 'confirm':
                await query.message.reply_text(f"✅ Deal {index + 1} confirmed!")
                
            elif action == 'reject':
                await query.message.reply_text(f"❌ Deal {index + 1} rejected!")
                
            elif action == 'edit':
                await self._show_edit_options(query, index)
                
        except Exception as e:
            logger.error(f"Error in callback: {str(e)}")
            await query.message.reply_text("Error processing button click")

    async def _show_edit_options(self, query, index: int):
        """Show edit options keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("Partner", callback_data=f"edit_partner_{index}"),
                InlineKeyboardButton("Region", callback_data=f"edit_region_{index}")
            ],
            [
                InlineKeyboardButton("GEO", callback_data=f"edit_geo_{index}"),
                InlineKeyboardButton("Source", callback_data=f"edit_source_{index}")
            ],
            [
                InlineKeyboardButton("CPA", callback_data=f"edit_cpa_{index}"),
                InlineKeyboardButton("CRG", callback_data=f"edit_crg_{index}")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data=f"back_to_review_{index}")]
        ]
        await query.message.edit_reply_markup(InlineKeyboardMarkup(keyboard))