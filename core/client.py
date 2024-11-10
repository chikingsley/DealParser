import os
import sys

# Diagnostic print of Python environment
print("Python Executable:", sys.executable)
print("Python Version:", sys.version)
print("Current Working Directory:", os.getcwd())

# Explicitly add virtual environment site-packages to Python path
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'venv', f'lib/python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages'))
if venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Comprehensive import handling
def safe_import(module_name):
    """
    Safely import a module with detailed error reporting.
    
    :param module_name: Name of the module to import
    :return: Imported module
    """
    try:
        import importlib
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"Failed to import {module_name}: {e}")
        print("Current Python Path:", sys.path)
        raise

# Verify package availability
# pylint: disable=unused-import,wrong-import-order
import mistralai
import dotenv
import rich

# Actual imports
from mistralai import Mistral
from dotenv import load_dotenv
from typing import List, Dict, Any
import time
import random
import json
from core.prompts import DealPrompts
import asyncio
from functools import partial
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

# Logging configuration
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Error loading .env file: {e}")

# Initialize console
console = Console()

class DealParser:
    def __init__(self):
        self._validate_api_key()
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "ft:open-mistral-7b:974ca0be:20241109:10932b95"
        self.max_retries = 3
        self.base_delay = 1

    def _validate_api_key(self):
        """Validate API key exists"""
        try:
            if not os.getenv("MISTRAL_API_KEY"):
                logger.error("MISTRAL_API_KEY environment variable not set")
                raise ValueError(
                    "MISTRAL_API_KEY environment variable not set. "
                    "Please set it in your .env file."
                )
        except Exception as e:
            logger.error(f"API key validation error: {str(e)}")
            raise

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
            logger.info(f"Structure Analysis Input:\n{text}")
            
            response = await self._call_mistral(messages)
            logger.info(f"Structure Analysis Output:\n{response}")
            
            parsed_response = json.loads(response)
            
            # Validate shared fields
            if parsed_response.get("shared_fields"):
                logger.info(f"Detected Shared Fields: {parsed_response['shared_fields']}")
            
            return parsed_response
        except Exception as e:
            logger.error(f"Error analyzing structure: {str(e)}")
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
        for attempt in range(self.max_retries):  # Keep retry loop
            try:
                # Use complete_async directly instead of run_in_executor
                response = await self.client.chat.complete_async(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                    response_format={"type": "json_object"}
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

if __name__ == "__main__":
    import asyncio
    
    async def main():
        parser = DealParser()
        # Add a sample text or method to test the parser
        sample_text = "Your sample deal text here"
        deals = await parser.parse_deals(sample_text)
        print(deals)

    asyncio.run(main())
