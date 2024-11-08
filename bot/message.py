from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.client import DealParser
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.deal_parser = DealParser()
        self.current_deals = {}
        self.deal_statuses = {}  # Track status of each deal
        self.user_states = {}  # Track user states
        self.session_timeout = 3600  # 1 hour
        self.editing_state = {}  # Track who's editing what
        
    def _cleanup_old_sessions(self):
        """Remove expired sessions"""
        current_time = time.time()
        expired = [
            user_id for user_id, data in self.user_states.items()
            if current_time - data['last_activity'] > self.session_timeout
        ]
        for user_id in expired:
            del self.user_states[user_id]
            del self.current_deals[user_id]

    async def _format_deal_message(self, deal, index: int, total: int, user_id: int) -> str:
        """Format deal with status emoji and raw text"""
        # Get deal status
        status = self.deal_statuses.get(user_id, {}).get(index-1)
        
        # Choose status emoji
        status_emoji = "📋"  # Default
        if status == 'approved':
            status_emoji = "✅"
        elif status == 'rejected':
            status_emoji = "❌"
            
        # Get parsed data from correct location
        parsed_data = deal.get('parsed_data', deal)
        raw_text = deal.get('raw_text', '')
            
        return (
            f"{status_emoji} Deal {index} of {total}\n\n"
            f"📝 Original Text:\n{raw_text}\n\n"
            f"📊 Deal Details:\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🤝 Partner: {parsed_data.get('partner', 'N/A')}\n"
            f"🌍 Region: {parsed_data.get('region', 'N/A')}\n"
            f"🗺 GEO: {parsed_data.get('geo', 'N/A')}\n"
            f"🗣 Language: {parsed_data.get('language', 'Native')}\n"
            f"📱 Source: {parsed_data.get('source', 'N/A')}\n"
            f"💰 Pricing Model: {parsed_data.get('pricing_model', 'N/A')}\n"
            f"💵 CPA: {parsed_data.get('cpa', 'N/A')}\n"
            f"📈 CRG: {f'{parsed_data.get('crg')*100}%' if parsed_data.get('crg') else 'N/A'}\n"
            f"🎯 CPL: {parsed_data.get('cpl', 'N/A')}\n"
            f"🔄 Funnels: {', '.join(parsed_data.get('funnels', [])) or 'N/A'}\n"
            f"📊 CR: {f'{parsed_data.get('cr')*100}%' if parsed_data.get('cr') else 'N/A'}\n"
            f"━━━━━━━━━━━━━━━"
        )

    async def _create_keyboard(self, current_index: int, total_deals: int, statuses: dict) -> InlineKeyboardMarkup:
        keyboard = []
        
        # Navigation buttons
        if total_deals > 1:
            nav_row = []
            if current_index > 0:
                nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{current_index}"))
            if current_index < total_deals - 1:
                nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"next_{current_index}"))
            if nav_row:
                keyboard.append(nav_row)

        # Action buttons with status
        status = statuses.get(current_index)
        approve_text = "✅ Approved" if status == 'approved' else "Approve ?"
        reject_text = "❌ Rejected" if status == 'rejected' else "Reject ?"
        
        keyboard.extend([
            [
                InlineKeyboardButton(approve_text, callback_data=f"approve_{current_index}"),
                InlineKeyboardButton(reject_text, callback_data=f"reject_{current_index}")
            ],
            [InlineKeyboardButton("✏️ Edit", callback_data=f"edit_{current_index}")]
        ])

        return InlineKeyboardMarkup(keyboard)

    async def _update_field_value(self, field: str, value: str) -> Any:
        """Validate and convert field values"""
        try:
            if field in ['crg', 'cr']:
                # Remove % if present and convert to decimal
                value = value.replace('%', '')
                return float(value) / 100
            elif field in ['cpa', 'cpl']:
                # Convert to float
                return float(value)
            elif field == 'pricing_model':
                # Validate pricing model
                valid_models = ['CPA/CRG', 'CPA', 'CPL']
                if value.upper() not in valid_models:
                    raise ValueError(f"Must be one of: {', '.join(valid_models)}")
                return value.upper()
            else:
                # String fields
                return value.strip()
        except ValueError as e:
            raise ValueError(f"Invalid value for {field}: {str(e)}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if not update.message or not update.message.text:
            return
            
        user_id = update.effective_user.id
        message = update.message.text
        
        # Check if user is editing a field
        if user_id in self.editing_state:
            try:
                edit_info = self.editing_state[user_id]
                deal_index = edit_info['deal_index']
                field = edit_info['field']
                
                # Validate and convert value
                try:
                    validated_value = await self._update_field_value(field, message)
                except ValueError as e:
                    await update.message.reply_text(f"❌ {str(e)}\nPlease try again.")
                    return
                
                # Update the deal
                deal = self.current_deals[user_id]['deals'][deal_index]
                if 'parsed_data' in deal:
                    deal['parsed_data'][field] = validated_value
                else:
                    deal[field] = validated_value
                
                # Clear editing state
                del self.editing_state[user_id]
                
                # Show updated deal
                await update.message.reply_text(
                    await self._format_deal_message(
                        deal,
                        deal_index + 1,
                        len(self.current_deals[user_id]['deals']),
                        user_id
                    ),
                    reply_markup=await self._create_keyboard(
                        deal_index,
                        len(self.current_deals[user_id]['deals']),
                        self.deal_statuses.get(user_id, {})
                    )
                )
                return
                
            except Exception as e:
                logger.error(f"Error updating field: {str(e)}")
                await update.message.reply_text("❌ Error updating field. Please try again.")
                return
        
        # Normal deal processing
        try:
            # Send processing message
            processing_message = await update.message.reply_text(
                "🔄 Processing your deals...\n"
                "Please wait while I analyze the information."
            )
            
            # Parse deals
            formatted_deals = await self.deal_parser.parse_deals(message)
            logger.debug(f"Received from Mistral: {formatted_deals}")  # Added debug log
            
            if not formatted_deals:
                await processing_message.edit_text(
                    "❌ No valid deals found.\n\n"
                    "Please format your deals like this:\n"
                    "Partner: Name\n"
                    "GEO - Price+CRG% - Funnels (source)"
                )
                return
                
            # Store deals for this user
            self.current_deals[user_id] = {
                'deals': formatted_deals,
                'current_index': 0
            }
            
            logger.debug(f"Stored deals for user {user_id}: {self.current_deals[user_id]}")  # Added debug log
            
            # Show first deal
            await self._display_current_deal(update, processing_message, user_id)
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ Error processing your message.\n"
                "Please check the format and try again."
            )

    async def _display_current_deal(self, update: Update, message, user_id: int):
        """Display current deal with navigation"""
        user_data = self.current_deals.get(user_id)
        if not user_data:
            return

        current_index = user_data['current_index']
        total_deals = len(user_data['deals'])
        deal = user_data['deals'][current_index]

        # Pass user_id to _format_deal_message
        deal_text = await self._format_deal_message(
            deal, 
            current_index + 1, 
            total_deals,
            user_id
        )
        
        # Create keyboard
        reply_markup = await self._create_keyboard(current_index, total_deals, self.deal_statuses.get(user_id, {}))

        try:
            if message:
                await message.edit_text(deal_text, reply_markup=reply_markup)
            else:
                await update.message.reply_text(deal_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error displaying deal: {str(e)}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        try:
            await query.answer()
            
            # Handle final action buttons
            if query.data.startswith('final_'):
                action = query.data.split('_')[1]
                
                if action == 'discard':
                    # Clear user data
                    if user_id in self.current_deals:
                        del self.current_deals[user_id]
                    if user_id in self.deal_statuses:
                        del self.deal_statuses[user_id]
                        
                    await query.edit_message_text(
                        "🗑️ Deals Discarded Successfully\n\n"
                        "Your deals have been cleared from the system. "
                        "Thank you for using the Deal Parser."
                    )
                    
                    await update.effective_chat.send_message(
                        "🎯 Ready for New Deals\n\n"
                        "I'm standing by to assist with your next batch of deals.\n"
                        "Simply paste your deals when ready, and I'll help process them with precision."
                    )
                    return
                    
                elif action == 'reprocess':
                    # Reset statuses but keep deals
                    if user_id in self.deal_statuses:
                        del self.deal_statuses[user_id]
                    
                    # First show confirmation
                    await query.edit_message_text(
                        "♺ Reprocessing Deals\n\n"
                        "Starting fresh with your original deals. "
                        "Let's review them again."
                    )
                    
                    # Then send new message with first deal
                    if user_id in self.current_deals:
                        self.current_deals[user_id]['current_index'] = 0
                        # Create new message instead of editing
                        await update.effective_chat.send_message(
                            text=await self._format_deal_message(
                                self.current_deals[user_id]['deals'][0],
                                1,
                                len(self.current_deals[user_id]['deals']),
                                user_id
                            ),
                            reply_markup=await self._create_keyboard(
                                0,
                                len(self.current_deals[user_id]['deals']),
                                {}  # Reset statuses
                            )
                        )
                    return
                    
                elif action == 'notion':
                    await query.edit_message_text(
                        "⚪️ Deals Successfully Submitted\n\n"
                        "Your approved deals have been securely transferred to Notion. "
                        "You can now access them in your workspace."
                    )
                    
                    await update.effective_chat.send_message(
                        "📋 Ready for Your Next Submission\n\n"
                        "The Deal Parser is ready to assist with more deals.\n"
                        "Feel free to submit your next batch whenever you're ready."
                    )
                    return
            
            # Split callback data
            parts = query.data.split('_')
            action = parts[0]
            index = int(parts[-1])  # Last part is always the index
            
            user_data = self.current_deals.get(user_id)
            if not user_data:
                return
                
            total_deals = len(user_data['deals'])
            current_deal = user_data['deals'][index]
            
            if action == 'edit':
                # Show edit options keyboard
                keyboard = [
                    [
                        InlineKeyboardButton("Partner", callback_data=f"editfield_partner_{index}"),
                        InlineKeyboardButton("GEO", callback_data=f"editfield_geo_{index}")
                    ],
                    [
                        InlineKeyboardButton("CPA", callback_data=f"editfield_cpa_{index}"),
                        InlineKeyboardButton("CRG", callback_data=f"editfield_crg_{index}")
                    ],
                    [
                        InlineKeyboardButton("CPL", callback_data=f"editfield_cpl_{index}"),
                        InlineKeyboardButton("CR", callback_data=f"editfield_cr_{index}")
                    ],
                    [
                        InlineKeyboardButton("Source", callback_data=f"editfield_source_{index}"),
                        InlineKeyboardButton("Funnels", callback_data=f"editfield_funnels_{index}")
                    ],
                    [
                        InlineKeyboardButton("Language", callback_data=f"editfield_language_{index}"),
                        InlineKeyboardButton("Pricing Model", callback_data=f"editmodel_{index}")
                    ],
                    [InlineKeyboardButton("🔙 Back", callback_data=f"back_{index}")]
                ]
                await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
                
            elif action == 'editmodel':
                # Show pricing model options
                keyboard = [
                    [InlineKeyboardButton("CPA/CRG", callback_data=f"setmodel_CPA/CRG_{index}")],
                    [InlineKeyboardButton("CPA", callback_data=f"setmodel_CPA_{index}")],
                    [InlineKeyboardButton("CPL", callback_data=f"setmodel_CPL_{index}")],
                    [InlineKeyboardButton("🔙 Back", callback_data=f"edit_{index}")]
                ]
                await query.edit_message_reply_markup(InlineKeyboardMarkup(keyboard))
                
            elif action == 'setmodel':
                # Update pricing model
                model = parts[1]
                deal = self.current_deals[user_id]['deals'][index]
                if 'parsed_data' in deal:
                    deal['parsed_data']['pricing_model'] = model
                else:
                    deal['pricing_model'] = model
                    
                # Show updated deal
                await query.edit_message_text(
                    await self._format_deal_message(deal, index + 1, total_deals, user_id),
                    reply_markup=await self._create_keyboard(index, total_deals, self.deal_statuses.get(user_id, {}))
                )
                
            elif action == 'editfield':
                # Store editing state
                self.editing_state[user_id] = {
                    'field': parts[1],
                    'deal_index': index
                }
                
                # Show edit prompt
                await query.edit_message_text(
                    f"Please enter new value for {parts[1]}:\n\n" +
                    (await self._format_deal_message(current_deal, index + 1, total_deals, user_id)) +
                    "\n\nType your new value or click Back to cancel.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back", callback_data=f"back_{index}")
                    ]])
                )
                
            elif action == 'back':
                # Return to main deal view
                await self._display_current_deal(update, query.message, user_id)
                
            # Handle regular deal buttons (approve, reject, next, prev, back)
            elif action == 'approve':
                # Update status
                if user_id not in self.deal_statuses:
                    self.deal_statuses[user_id] = {}
                self.deal_statuses[user_id][index] = 'approved'
                
                # If there's a next deal, show it
                if index < total_deals - 1:
                    user_data['current_index'] = index + 1
                    next_deal = user_data['deals'][index + 1]
                    await query.edit_message_text(
                        await self._format_deal_message(next_deal, index + 2, total_deals, user_id),
                        reply_markup=await self._create_keyboard(index + 1, total_deals, self.deal_statuses[user_id])
                    )
                else:
                    # If this was the last deal, show summary
                    await self._show_summary(update, user_id)
                    
            elif action == 'reject':
                # Update status
                if user_id not in self.deal_statuses:
                    self.deal_statuses[user_id] = {}
                self.deal_statuses[user_id][index] = 'rejected'
                
                # If there's a next deal, show it
                if index < total_deals - 1:
                    user_data['current_index'] = index + 1
                    next_deal = user_data['deals'][index + 1]
                    await query.edit_message_text(
                        await self._format_deal_message(next_deal, index + 2, total_deals, user_id),
                        reply_markup=await self._create_keyboard(index + 1, total_deals, self.deal_statuses[user_id])
                    )
                else:
                    # If this was the last deal, show summary
                    await self._show_summary(update, user_id)
                    
            elif action == 'next':
                if index < total_deals - 1:
                    user_data['current_index'] = index + 1
                    await self._display_current_deal(update, query.message, user_id)
                    
            elif action == 'prev':
                if index > 0:
                    user_data['current_index'] = index - 1
                    await self._display_current_deal(update, query.message, user_id)
                    
            elif action == 'discard_all':
                # Clear user data
                if user_id in self.current_deals:
                    del self.current_deals[user_id]
                if user_id in self.deal_statuses:
                    del self.deal_statuses[user_id]
                
                # Show professional confirmation
                await query.edit_message_text(
                    "🗑️ Deals Discarded Successfully\n\n"
                    "Your deals have been cleared from the system. "
                    "Thank you for using the Deal Parser."
                )
                
                await update.effective_chat.send_message(
                    "🎯 Ready for New Deals\n\n"
                    "I'm standing by to assist with your next batch of deals.\n"
                    "Simply paste your deals when ready, and I'll help process them with precision."
                )
                
            elif action == 'reprocess_all':
                # Reset statuses but keep deals
                if user_id in self.deal_statuses:
                    del self.deal_statuses[user_id]
                
                # Confirmation message
                await query.edit_message_text(
                    "♺ Reprocessing Deals\n\n"
                    "Starting fresh with your original deals. "
                    "Let's review them again."
                )
                
                # Start over with first deal
                if user_id in self.current_deals:
                    self.current_deals[user_id]['current_index'] = 0
                    await self._display_current_deal(update, None, user_id)
                    
            elif action == 'submit_notion':
                # Show professional confirmation
                await query.edit_message_text(
                    "⚪️ Deals Successfully Submitted\n\n"
                    "Your approved deals have been securely transferred to Notion. "
                    "You can now access them in your workspace."
                )
                
                await update.effective_chat.send_message(
                    "📋 Ready for Your Next Submission\n\n"
                    "The Deal Parser is ready to assist with more deals.\n"
                    "Feel free to submit your next batch whenever you're ready."
                )
                
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await query.answer("Error processing button click")

    async def _show_summary(self, update: Update, user_id: int):
        """Show summary of all deals"""
        user_data = self.current_deals.get(user_id)
        if not user_data:
            return
            
        approved_deals = []
        rejected_deals = []
        
        for index, deal in enumerate(user_data['deals']):
            status = self.deal_statuses[user_id].get(index)
            if not status:
                continue
                
            # Format deal for summary
            parsed_data = deal.get('parsed_data', deal)
            deal_text = (
                f"{parsed_data.get('partner', 'N/A')} "
                f"[{', '.join(parsed_data.get('source', '').split('|'))}] "
                f"{parsed_data.get('geo', 'N/A')} "
                f"{parsed_data.get('language', 'Native')} "
            )
            
            # Add pricing
            if parsed_data.get('crg'):
                deal_text += f"{parsed_data.get('cpa', 'N/A')} + {parsed_data.get('crg')*100}%"
            elif parsed_data.get('cpl'):
                deal_text += f"{parsed_data.get('cpl')} CPL"
            elif parsed_data.get('cpa'):
                deal_text += f"{parsed_data.get('cpa')} CPA"
                
            # Add funnels
            funnels = parsed_data.get('funnels', [])
            if funnels:
                deal_text += f"\nFunnels: {', '.join(funnels)}"
            
            if status == 'approved':
                approved_deals.append(deal_text)
            else:
                rejected_deals.append(deal_text)
        
        # Create summary message
        summary = (
            "DEALS PARSER SUMMARY\n\n"
            "✅ Approved Deals\n"
            f"{chr(10).join(approved_deals) if approved_deals else 'None'}\n\n"
            "❌ Rejected Deals\n"
            f"{chr(10).join(rejected_deals) if rejected_deals else 'None'}"
        )
        
        # Create final action buttons with fixed callback data
        keyboard = [
            [InlineKeyboardButton("🗑️ Discard All Deals 🗑️", callback_data="final_discard")],
            [InlineKeyboardButton("♺ Reprocess Deals ♺", callback_data="final_reprocess")],
            [InlineKeyboardButton("⚪️ Submit to Notion ⚪️", callback_data="final_notion")]
        ]
        
        await update.effective_chat.send_message(
            text=summary,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )