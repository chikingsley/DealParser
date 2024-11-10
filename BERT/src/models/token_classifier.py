from transformers import BertForTokenClassification, BertConfig
from typing import Dict, Optional
import torch

class DealNERModel:
    def __init__(
        self,
        model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english",
        num_labels: int = 11,
        dropout: float = 0.1
    ):
        self.config = BertConfig.from_pretrained(
            model_name,
            num_labels=num_labels,
            hidden_dropout_prob=dropout
        )
        
        self.model = BertForTokenClassification.from_pretrained(
            model_name,
            config=self.config
        )
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        return outputs 