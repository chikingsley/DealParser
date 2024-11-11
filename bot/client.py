import os
import sys
from enum import Enum

# Diagnostic print of Python environment
#print("Python Executable:", sys.executable)
#print("Python Version:", sys.version)
#print("Current Working Directory:", os.getcwd())

# Explicitly add virtual environment site-packages to Python path
##if venv_site_packages not in sys.path:
#    sys.path.insert(0, venv_site_packages)

# Comprehensive import handling
#def safe_import(module_name):
#    """
#    Safely import a module with detailed error reporting.
    
#    :param module_name: Name of the module to import
#    :return: Imported module
#    """
#    try:
#        import importlib
#        return importlib.import_module(module_name)
#    except ImportError as e:
#        print(f"Failed to import {module_name}: {e}")
#        print("Current Python Path:", sys.path)
#        raise

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
from bot.prompts import DealPrompts
import asyncio
from functools import partial
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.panel import Panel
from rich.text import Text

# Logging configuration
import logging
# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    logger.error(f"Error loading .env file: {e}")

# Initialize console
console = Console()

class ProgressStages(Enum):
    INIT = "Initializing"
    COMPLETE = "Complete"

class DealParser:
    def __init__(self):
        self._validate_api_key()
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = "ft:open-mistral-7b:974ca0be:20241109:10932b95"
        self.max_retries = 3
        self.base_delay = 1
        self.console = Console()

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
        results = []

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            expand=True,
            transient=False
        )

        with progress:
            try:
                # Single progress bar for overall process
                main_task = progress.add_task("🔍 Processing Deals...", total=100)
                
                # Analyze structure
                structure = await self._analyze_structure(text)
                progress.update(main_task, completed=20)  
                
                # Process all deals from all sections
                total_deals = self.get_total_deals(structure)
                progress_per_deal = 80 / total_deals if total_deals > 0 else 80  # Remaining 80% divided among deals
                
                # Iterate through sections and their deal blocks
                for section in structure.get("sections", []):
                    for deal_block in section.get("deal_blocks", []):
                        parsed_deal = await self._parse_deal(
                            deal_block["text"],
                            {
                                "shared_fields": section.get("shared_fields", {}),
                                "inherits_from": deal_block.get("inherits_from", [])
                            }
                        )
                        results.append(parsed_deal)
                        progress.update(main_task, advance=progress_per_deal)

                # Completion display (non-blocking)
                asyncio.create_task(self._show_completion_message(total_time_start, total_deals))
                
                # Format deals with language defaults
                formatted_deals = []
                for deal in results:
                    if not deal.get('language'):
                        geo = deal.get('geo', '').lower()
                        if any(eng_geo in geo for eng_geo in ['uk', 'us', 'gb', 'au', 'ca']):
                            deal['language'] = 'English'
                        else:
                            deal['language'] = 'Native'
                        
                    formatted_deals.append(deal)
                
                return formatted_deals

            except Exception as e:
                self.console.print(Panel(
                    f"❌ Error processing deals: {str(e)}", 
                    title="Error",
                    border_style="red"
                ))
                raise

    async def _show_completion_message(self, start_time: float, total_deals: int):
        """Show completion message without blocking main process"""
        await asyncio.sleep(0.2)  # Small delay for visual purposes only
        total_time = time.time() - start_time
        self.console.print()
        self.console.print(Panel(
            Text.assemble(
                ("✨ Deal Processing Complete!\n\n", "bold green"),
                (f"Total Time: {total_time:.2f} seconds\n", "blue"),
                (f"Deals Processed: {total_deals}", "blue")
            ),
            title="Summary",
            border_style="green"
        ))

    async def _analyze_structure(self, text: str) -> Dict:
        try:
            # Create an AI prompt to analyze the document structure
            messages = DealPrompts.create_structure_prompt(text)
            # logger.info("=== Structure Analysis ===")
            # logger.info(f"Input Text:\n{text}")
            
            # Send to Mistral AI and get response
            response = await self._call_mistral(messages)
            # logger.info(f"Structure Analysis Response:\n{response}")
            
            parsed_response = json.loads(response)
            
            # Detailed logging of structure analysis
            # logger.info("=== Parsed Structure ===")
            # logger.info(f"Shared Fields: {json.dumps(parsed_response.get('shared_fields', {}), indent=2)}")
            # logger.info(f"Number of Deal Blocks: {len(parsed_response.get('deal_blocks', []))}")
            for i, block in enumerate(parsed_response.get('deal_blocks', [])):
                logger.info(f"\nDeal Block {i+1}:")
                logger.info(f"Text: {block.get('text')}")
                logger.info(f"Inherits From: {block.get('inherits_from', [])}")
            
            return parsed_response
        except Exception as e:
            # logger.error(f"Error analyzing structure: {str(e)}")
            return {"deal_blocks": [{"text": text, "inherits_from": None}], "shared_fields": {}}

    async def _parse_deal(self, deal_text: str, context: Dict) -> Dict:
        try:
            # Log incoming deal and context
            logger.info("\n=== Parsing Deal ===")
            logger.info(f"Deal Text: {deal_text}")
            # logger.info(f"Context: {json.dumps(context, indent=2)}")
            
            # Extract and validate context
            shared_fields = context.get("shared_fields", {})
            inherits_from = context.get("inherits_from", [])
            
            # Build shared values with detailed logging
            shared_values = {}
            logger.info("\nProcessing Inherited Fields:")
            for field in inherits_from:
                if field in shared_fields and shared_fields[field] is not None:
                    value = shared_fields[field]
                    # Handle special field conversions
                    if field == "deduction_limit" and isinstance(value, str) and "%" in value:
                        value = float(value.strip("%")) / 100
                    shared_values[field] = value
                    logger.info(f"  {field}: {value}")
            
            # Create enhanced context
            context_with_values = {
                "shared_fields": shared_fields,
                "inherits_from": inherits_from,
                "shared_values": shared_values
            }
            
            # Generate and send prompt
            messages = DealPrompts.create_parsing_prompt(deal_text, context_with_values)
            response = await self._call_mistral(messages)
            logger.info(f"\nMistral Response:\n{response}")
            
            parsed_response = json.loads(response)
            
            # Ensure required structures exist
            if "parsed_data" not in parsed_response:
                parsed_response["parsed_data"] = {}
            if "metadata" not in parsed_response:
                parsed_response["metadata"] = {"confidence_flags": {}}
            
            # Apply inherited values with logging
            logger.info("\nApplying Inherited Values:")
            for field, value in shared_values.items():
                # Only inherit if the field is empty or None
                if not parsed_response["parsed_data"].get(field):
                    parsed_response["parsed_data"][field] = value
                    if "confidence_flags" not in parsed_response["metadata"]:
                        parsed_response["metadata"]["confidence_flags"] = {}
                    parsed_response["metadata"]["confidence_flags"][field] = "inherited"
                    logger.info(f"  Applied {field}: {value}")
                else:
                    logger.info(f"  Skipped {field} (already has value): {parsed_response['parsed_data'][field]}")
            
            # Log final parsed result
            logger.info("\nFinal Parsed Result:")
            logger.info(json.dumps(parsed_response, indent=2))
            
            return parsed_response
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return self._create_error_response(deal_text, "Invalid JSON response from AI")
            
        except Exception as e:
            logger.error(f"Error parsing deal: {str(e)}")
            return self._create_error_response(deal_text, str(e))

    def _create_error_response(self, deal_text: str, error_message: str) -> Dict:
        return {
            "raw_text": deal_text,  # Simple string assignment
            "parsed_data": {
                # All synchronous dictionary creation and assignments
                "partner": None,
                "region": "Unknown",
                "geo": "Unknown",
                "language": "Native",
                "source": None,
                "pricing_model": None,
                "cpa": None,
                "crg": None,
                "cpl": None,
                "funnels": [],  # Simple list creation
                "cr": None,
                "deduction_limit": None
            },
            "metadata": {
                # Dictionary comprehension - all synchronous
                "confidence_flags": {
                    field: "empty" for field in [
                        "partner", "region", "geo", "language", "source",
                        "pricing_model", "cpa", "crg", "cpl", "funnels",
                        "cr", "deduction_limit"
                    ]
                },
                "error": error_message  # Simple string assignment
            }
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

    async def parse_deals_with_progress(self, message):
        """Parse deals with progress updates."""
        yield ProgressStages.INIT
        
        # Parse deals
        deals = self.parse_deals(message)  # or however you currently parse deals
        
        yield ProgressStages.COMPLETE
        yield deals  # yield the deals instead of returning them

    def get_total_deals(self, structure):
        try:
            return sum(len(section["deal_blocks"]) for section in structure["sections"])
        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing structure: {e}")
            return 0

if __name__ == "__main__":
    import asyncio
    
    async def main():
        parser = DealParser()
        # Add a sample text or method to test the parser
        sample_text = "Your sample deal text here"
        deals = await parser.parse_deals(sample_text)
        print(deals)

    asyncio.run(main())
