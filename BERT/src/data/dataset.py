from typing import Dict, List, Optional
import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizer

class DealNERDataset(Dataset):
    def __init__(
        self, 
        texts: List[str],
        labels: List[List[str]], 
        tokenizer: PreTrainedTokenizer,
        max_length: int = 128
    ):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Create label map
        self.label2id = {
            "O": 0,  # Outside any entity
            "B-PARTNER": 1,
            "I-PARTNER": 2, 
            "B-GEO": 3,
            "I-GEO": 4,
            "B-PRICE": 5,
            "I-PRICE": 6,
            "B-SOURCE": 7,
            "I-SOURCE": 8,
            "B-FUNNEL": 9,
            "I-FUNNEL": 10
        }
        self.id2label = {v: k for k, v in self.label2id.items()}

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx) -> Dict[str, torch.Tensor]:
        text = self.texts[idx]
        label = self.labels[idx]

        # Tokenize text and align labels
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        # Convert labels to ids and align with tokens
        label_ids = self._align_labels_with_tokens(label, encoding)

        return {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
            "labels": torch.tensor(label_ids)
        }

    def _align_labels_with_tokens(self, labels: List[str], encoding) -> List[int]:
        # Implementation for aligning labels with tokenized text
        # This needs careful handling of subwords and special tokens
        pass 