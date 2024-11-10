from mistralai import MistralAsyncClient
from typing import List, Dict, Any
import json
import os
import logging
from prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class FineTunedDealParser:
    def __init__(self):
        self.client = MistralAsyncClient(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "ft:open-mistral-7b:974ca0be:20241109:10932b95"
        
    async def parse_deals(self, text: str) -> List[Dict]:
        """Parse deals using fine-tuned model"""
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ]
            
            # Call fine-tuned model
            chat_response = await self.client.chat(
                model=self.model,
                messages=messages,
                temperature=0.0
            )
            
            # Parse response
            response_text = chat_response.choices[0].message.content
            parsed_deals = json.loads(response_text)
            
            return [parsed_deals] if isinstance(parsed_deals, dict) else parsed_deals
            
        except Exception as e:
            logger.error(f"Error parsing deals: {str(e)}")
            return []
