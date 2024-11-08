import json
from pathlib import Path
from typing import List, Dict, Any
from training_client import TrainingDealParser
import logging
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.console import Console

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()

class TrainingDataGenerator:
    def __init__(self):
        self.parser = TrainingDealParser()
        
    def generate_variations(self, deal_text: str) -> List[str]:
        """Generate variations of deal text"""
        variations = []
        
        # Original format
        variations.append(deal_text)
        
        # Remove emojis and special characters
        no_emoji = deal_text.encode('ascii', 'ignore').decode()
        variations.append(no_emoji)
        
        # Price format variations
        variations.extend([
            deal_text.replace("+", " + "),
            deal_text.replace("$", ""),
            deal_text.replace("$", "USD "),
            deal_text.replace("%", " percent"),
            deal_text.replace("PRICE:", "Price:"),
            deal_text.replace("PRICE:", "price:"),
            deal_text.replace("CPA:", "Price:"),
            deal_text.replace("CPL:", "Price:")
        ])
        
        # Source format variations
        variations.extend([
            deal_text.replace("fb", "Facebook"),
            deal_text.replace("FB", "facebook"),
            deal_text.replace("FB Traffic", "Facebook"),
            deal_text.replace("ggl", "Google"),
            deal_text.replace("GG", "Google"),
            deal_text.replace("search.display", "Google Display")
        ])
        
        # Funnel format variations
        if "Funnel:" in deal_text:
            variations.extend([
                deal_text.replace("Funnel:", "Funnels:"),
                deal_text.replace("Funnel:", "funnel:"),
                deal_text.replace("Funnel:", "Landing Page:")
            ])
            
        # CR format variations
        if "CR:" in deal_text:
            variations.extend([
                deal_text.replace("CR:", "cr:"),
                deal_text.replace("CR:", "Conversion Rate:"),
                deal_text.replace("-", " to ")  # For ranges like 8-10%
            ])
            
        # Partner/Company variations
        variations.extend([
            deal_text.replace("Company:", "Partner:"),
            deal_text.replace("Partner:", "Company:")
        ])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in variations if not (x in seen or seen.add(x))]

    def create_training_example(self, deal_text: str) -> List[Dict]:
        """Create training examples from deal text"""
        try:
            # Parse original deal
            parsed_deals = self.parser.parse_deals(deal_text)
            if not parsed_deals:
                return []
                
            # Generate variations
            variations = self.generate_variations(deal_text)
            
            # Create examples
            examples = []
            for variation in variations:
                for parsed_deal in parsed_deals:
                    example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a deal parsing assistant. Extract and format deal information according to the specified template."
                            },
                            {
                                "role": "user",
                                "content": variation
                            },
                            {
                                "role": "assistant",
                                "content": json.dumps(parsed_deal, ensure_ascii=False)
                            }
                        ]
                    }
                    examples.append(example)
                    
            return examples
            
        except Exception as e:
            logger.error(f"Error processing deal: {str(e)}")
            return []

    def process_data_file(self, input_file: str, output_file: str):
        """Process data file and create training dataset"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Read input file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split into deal blocks
            deals = [d for d in content.split('\n\n') if d.strip()]
            total_deals = len(deals)
            
            # Add main task
            main_task = progress.add_task(
                f"[cyan]Processing {total_deals} deals...", 
                total=total_deals
            )
            
            # Generate training examples
            all_examples = []
            for i, deal in enumerate(deals, 1):
                progress.update(main_task, description=f"[cyan]Deal {i}/{total_deals}")
                examples = self.create_training_example(deal)
                all_examples.extend(examples)
                progress.advance(main_task)
                
            # Save progress
            progress.update(main_task, description="[green]Saving examples...")
            
            # Save as JSONL
            output_path = Path(output_file)
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for example in all_examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
                    
            progress.update(main_task, description=f"[green]Done! Generated {len(all_examples)} examples")

def main():
    generator = TrainingDataGenerator()
    
    # Process data copy.md
    generator.process_data_file(
        'data/data copy.md',
        'data/training_data.jsonl'
    )

if __name__ == "__main__":
    main()