import logging
from mistralai import Mistral
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time
import random
import json

load_dotenv()
logger = logging.getLogger(__name__)

class DealParser:
    def __init__(self):
        self._validate_api_key()
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("FINETUNED_MODEL_ID", "mistral-small-latest")
        self.max_retries = 3
        self.base_delay = 1

    def _validate_api_key(self):
        if not os.getenv("MISTRAL_API_KEY"):
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set. "
                "Please set it in your .env file."
            )

    async def parse_deals(self, text: str) -> List[Dict]:
        # Step 1: Analyze structure
        structure = await self._analyze_structure(text)
        
        # Step 2: Parse individual deals with context
        deals = []
        for deal_block in structure["deal_blocks"]:
            parsed_deal = await self._parse_deal(
                deal_block["text"],
                {
                    "shared_fields": structure["shared_fields"],
                    "inherits_from": deal_block["inherits_from"]
                }
            )
            deals.append(parsed_deal)
            
        return deals

    async def _analyze_structure(self, text: str) -> Dict:
        """First pass: Analyze structure and shared fields"""
        messages = DealPrompts.create_structure_prompt(text)
        response = await self._call_mistral(messages)
        return json.loads(response)

    async def _parse_deal(self, deal_text: str, context: Dict) -> Dict:
        """Second pass: Parse individual deal with context"""
        messages = DealPrompts.create_parsing_prompt(deal_text, context)
        response = await self._call_mistral(messages)
        return json.loads(response)

    async def get_conversation_response(self, text: str) -> str:
        """Get a conversational response for non-deal messages"""
        messages = [
            {"role": "system", "content": "You are a friendly AI assistant who helps process deals but can also chat about other topics."},
            {"role": "user", "content": text}
        ]

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error in conversation: {str(e)}")
            raise