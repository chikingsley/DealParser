import time
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ProgressHandler:
    def __init__(self, message):
        self.message = message
        self.steps: List[Dict] = []
        self.start_time = time.time()
        
    def _create_progress_bar(self, current: int, total: int) -> str:
        progress = current / total
        bar_length = 20
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        percentage = int(progress * 100)
        return f"[{bar}] {percentage}% ({current}/{total})"
        
    async def update_progress(self, stage: str, data: dict = None):
        """Update progress with history"""
        try:
            message = "--Deal Parsing Progress--\n\n"
            
            if stage == "init":
                message += "🔄 Starting Deal Parser Bot..."
                
            elif stage == "analyzing":
                message += ("✅ Deal Parser Bot Started\n"
                          "🔄 Analyzing Deal Structure...")
                
            elif stage == "structure_complete":
                message += ("✅ Deal Parser Bot Started\n"
                          "✅ Structure Analysis Complete\n")
                if data and 'total' in data:
                    message += f"🔄 Processing deal 1 of {data['total']}\n"
                    progress_bar = self._create_progress_bar(1, data['total'])
                    message += progress_bar
                    
            elif stage == "progress":
                current = data.get('current', 0)
                total = data.get('total', 0)
                if current and total:
                    message += ("✅ Deal Parser Bot Started\n"
                              "✅ Structure Analysis Complete\n"
                              f"🔄 Processing deal {current} of {total}\n")
                    progress_bar = self._create_progress_bar(current, total)
                    message += progress_bar
            
            # Only update if we have content to show
            if len(message.strip()) > len("--Deal Parsing Progress--"):
                await self.message.edit_text(message)
            
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")