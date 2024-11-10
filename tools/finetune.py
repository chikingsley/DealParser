from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments
)
from trl import SFTTrainer
from datasets import load_dataset
import torch
from pathlib import Path
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    BarColumn,
    MofNCompleteColumn
)
from rich.console import Console
import time
import os

os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"

def train(
    training_data="data/training_data.jsonl",
    output_dir="models/deal-parser-v1",
    epochs=3
):
    console = Console()
    console.print("\n[bold cyan]Starting training...[/]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        # Load tokenizer
        load_task = progress.add_task("[cyan]Loading model...", total=1)
        tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.3",
            padding_side="right"
        )
        tokenizer.pad_token = tokenizer.eos_token
        
        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.3",
            device_map="mps",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        progress.update(load_task, completed=1)
        
        # Load dataset
        data_task = progress.add_task("[cyan]Loading dataset...", total=1)
        dataset = load_dataset('json', data_files=training_data)
        progress.update(data_task, completed=1)
        
        # Setup training
        setup_task = progress.add_task("[cyan]Setting up training...", total=1)
        
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            learning_rate=1e-4,
            logging_steps=1,
            save_strategy="epoch",
            optim="adamw_torch",
            gradient_checkpointing=True,
            fp16=False,
            report_to="none"
        )
        
        # Initialize SFTTrainer
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset["train"],
            tokenizer=tokenizer,
            args=training_args,
            max_seq_length=2048,
            dataset_text_field="messages",  # Our data format
            packing=False  # Don't pack sequences
        )
        progress.update(setup_task, completed=1)
        
        # Train
        trainer.train()
        
        # Save
        model.save_pretrained(output_dir)

if __name__ == "__main__":
    console = Console()
    console.print("\n🚀 Starting fine-tuning process...")
    start_time = time.time()
    train()
    duration = time.time() - start_time
    console.print(f"\n✨ Fine-tuning completed in {duration:.2f} seconds")