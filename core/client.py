import logging
from mistralai import Mistral
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import time
import random
import json
from .prompts import DealPrompts
import asyncio
from functools import partial
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

load_dotenv()
logger = logging.getLogger(__name__)
console = Console()

class DealParser:
    def __init__(self):
        self._validate_api_key()
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "mistral-large-latest"
        self.max_retries = 3
        self.base_delay = 1

    def _validate_api_key(self):
        """Validate API key exists"""
        if not os.getenv("MISTRAL_API_KEY"):
            logger.error("MISTRAL_API_KEY environment variable not set")
            raise ValueError(
                "MISTRAL_API_KEY environment variable not set. "
                "Please set it in your .env file."
            )

    async def parse_deals(self, text: str) -> List[Dict]:
        total_time_start = time.time()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                # Get total steps
                structure = await self._analyze_structure(text)
                total_steps = len(structure["deal_blocks"]) + 1  # +1 for structure analysis
                
                # Step 1: Structure Analysis
                task = progress.add_task(
                    f"🤖 Analyzing structure... (Step 1/{total_steps})", 
                    total=1
                )
                progress.update(task, completed=1)
                
                # Step 2: Parse each deal
                deals = []
                for i, deal_block in enumerate(structure["deal_blocks"], 2):  # Start from 2
                    task = progress.add_task(
                        f"🤖 Processing deal... (Step {i}/{total_steps})", 
                        total=1
                    )
                    parsed_deal = await self._parse_deal(
                        deal_block["text"],
                        {
                            "shared_fields": structure["shared_fields"],
                            "inherits_from": deal_block["inherits_from"]
                        }
                    )
                    deals.append(parsed_deal)
                    progress.update(task, completed=1)
                
                # Add a small pause before showing completion
                await asyncio.sleep(1)  # 1 second pause
                
                # Clear previous lines
                console.print("\n")  # Add blank line
                
                # Show total time
                total_time = time.time() - total_time_start
                console.print(f"✨ Completed all steps in {total_time:.2f} seconds")
                
                return deals
        except Exception as e:
            logger.error(f"Error parsing deals: {str(e)}")
            raise

    async def _analyze_structure(self, text: str) -> Dict:
        """First pass: Analyze structure and shared fields"""
        try:
            messages = DealPrompts.create_structure_prompt(text)
            response = await self._call_mistral(messages)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
            # Return a basic structure instead of raising
            return {"deal_blocks": [{"text": text, "inherits_from": None}], "shared_fields": {}}

    async def _parse_deal(self, deal_text: str, context: Dict) -> Dict:
        """Second pass: Parse individual deal with context"""
        try:
            messages = DealPrompts.create_parsing_prompt(deal_text, context)
            response = await self._call_mistral(messages)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error parsing deal: {str(e)}")
            # Return a basic deal structure instead of raising
            return {
                "partner": "Unknown",
                "region": "Unknown",
                "geo": "Unknown",
                "language": "Native",
                "source": "&",
                "pricing_model": "Unknown",
                "cpa": None,
                "crg": None,
                "cpl": None,
                "funnels": [],
                "cr": None
            }

    async def _call_mistral(self, messages: List[Dict]) -> str:
        """Make API call to Mistral with proper async handling"""
        for attempt in range(self.max_retries):
            try:
                # Run the synchronous Mistral call in a thread pool
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    partial(
                        self.client.chat.complete,
                        model=self.model,
                        messages=messages,
                        temperature=0.0,
                        response_format={"type": "json_object"}
                    )
                )
                
                # Log response for debugging
                content = response.choices[0].message.content
                logger.debug(f"Mistral response: {content}")
                return content
                
            except Exception as e:
                if "429" in str(e) and attempt < self.max_retries - 1:
                    delay = (self.base_delay * (2 ** attempt) + 
                            random.uniform(0, 0.1 * (2 ** attempt)))
                    logger.warning(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"Error calling Mistral API: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                continue
