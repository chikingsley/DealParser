import json
import random
from pathlib import Path
import sys
import os
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_training.training_client import TrainingDealParser  # Use local parser instead of API

console = Console()

def create_validation_set():  # Remove async since TrainingDealParser is sync
    console.print("\n[bold cyan]Starting validation set creation...[/]")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            # Initialize parser
            init_task = progress.add_task("[cyan]Initializing parser...", total=1)
            parser = TrainingDealParser()
            progress.update(init_task, completed=1)
            
            # Read data
            read_task = progress.add_task("[cyan]Reading data file...", total=1)
            with open('data/data copy.md', 'r') as f:
                content = f.read()
            progress.update(read_task, completed=1)
            
            # Split deals
            deals = [d.strip() for d in content.split('\n\n') if d.strip()]
            console.print(f"[green]Found {len(deals)} deal blocks[/]")
            
            # Shuffle and split
            random.shuffle(deals)
            split_idx = int(len(deals) * 0.8)
            train_deals = deals[:split_idx]
            val_deals = deals[split_idx:]
            
            console.print(f"[green]Split into {len(train_deals)} training and {len(val_deals)} validation deals[/]")
            
            # Process validation deals
            validation_examples = []
            process_task = progress.add_task(
                "[cyan]Processing validation deals...", 
                total=len(val_deals)
            )
            
            for deal in val_deals:
                # Parse deal using local parser
                parsed_deals = parser.parse_deals(deal)  # No await needed
                if parsed_deals:
                    example = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a deal parsing assistant. Extract and format deal information according to the specified template."
                            },
                            {
                                "role": "user", 
                                "content": deal
                            },
                            {
                                "role": "assistant",
                                "content": json.dumps(parsed_deals[0], ensure_ascii=False)
                            }
                        ]
                    }
                    validation_examples.append(example)
                progress.update(process_task, advance=1)
            
            # Save validation set
            save_task = progress.add_task("[cyan]Saving validation set...", total=1)
            output_path = Path('data/validation_data.jsonl')
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w') as f:
                for example in validation_examples:
                    f.write(json.dumps(example) + '\n')
                    
            progress.update(save_task, completed=1)
            
            console.print(f"\n[bold green]✓ Created validation set with {len(validation_examples)} examples[/]")
            console.print(f"[bold green]✓ Saved to {output_path}[/]")
            
            return len(train_deals), len(validation_examples)
        
    except FileNotFoundError:
        console.print("[bold red]Error: Could not find data copy.md[/]")
        return 0, 0
    except Exception as e:
        console.print(f"[bold red]Error creating validation set: {str(e)}[/]")
        return 0, 0

if __name__ == "__main__":
    train_size, val_size = create_validation_set()  # No asyncio needed