import logging
from telegram import Update
from telegram.ext import Application, ContextTypes
from ..core.parser import DealParser
from ..core.patterns import PatternManager
from .handlers import MessageHandler, ButtonHandler
from .keyboards import KeyboardManager
from .states import StateManager
import asyncio

logger = logging.getLogger('botstream.bot')

class TelegramBot:
    def __init__(self, token: str):
        """Initialize bot with token"""
        self.token = token
        self.pattern_manager = PatternManager()
        
        # Initialize components
        self.message_handler = MessageHandler(self.pattern_manager)
        self.button_handler = ButtonHandler()
        self.keyboard_manager = KeyboardManager()
        self.state_manager = StateManager()
        
        # Create application
        self.app = Application.builder().token(self.token).build()
        
        # Add handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup message and button handlers"""
        self.app.add_handler(self.message_handler.get_handler())
        self.app.add_handler(self.button_handler.get_handler())
    
    async def start(self):
        """Start the bot"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
    async def stop(self):
        """Stop the bot"""
        await self.app.stop()
        await self.app.shutdown()
    
    async def idle(self):
        """Keep the bot running"""
        try:
            # Keep running until interrupted
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass