import logging
from mistralai import Mistral
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from core.prompts import SYSTEM_PROMPT, create_user_prompt
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
        self.base_delay = 1  # Base delay in seconds

    def _validate_api_key(self):
        if not os.getenv("MISTRAL_API_KEY"):
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set. "
                "Please set it in your .env file."
            )

    def parse_deals(self, deal_text: str) -> List[Dict[str, Any]]:
        """Parse deals from text and return structured deal data"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": create_user_prompt(deal_text)}
        ]

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                    response_format={"type": "json_object"}  # Ensure JSON response
                )

                try:
                    # Parse JSON response
                    content = response.choices[0].message.content.strip()
                    parsed_response = json.loads(content)
                    
                    # Handle both single deal and multiple deals
                    if isinstance(parsed_response, dict):
                        return [parsed_response]
                    elif isinstance(parsed_response, list):
                        return parsed_response
                    else:
                        raise ValueError("Unexpected response format")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {content}")
                    raise
                    
            except Exception as e:
                if "429" in str(e) and attempt < self.max_retries - 1:
                    delay = (self.base_delay * (2 ** attempt) + 
                            random.uniform(0, 0.1 * (2 ** attempt)))
                    logger.warning(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                logger.error(f"Error calling Mistral API: {str(e)}")
                raise