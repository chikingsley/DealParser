import json
from typing import Dict, List, Tuple
import pandas as pd
import re

class DealDataPreprocessor:
    def __init__(self):
        self.entity_patterns = {
            'PARTNER': r'Partner:\s*([^:\n]+)',
            'GEO': r'(?:GEO|Country):\s*([^:\n]+)',
            'PRICE': r'(?:Price|CPA \+ crg):\s*(\d+(?:,\d+)?(?:\.\d+)?\$?\s*\+\s*\d+(?:\.\d+)?%)',
            'SOURCE': r'(?:Source|source):\s*([^:\n]+)',
            'FUNNEL': r'(?:Landing Page|Funnels?):\s*([^:\n]+)'
        }

    def process_raw_text(self, text: str) -> List[Dict[str, str]]:
        """Process raw text into structured format with entity labels."""
        deals = text.split('\n\n')
        processed_deals = []
        
        for deal in deals:
            if not deal.strip():
                continue
                
            deal_entities = {}
            for entity_type, pattern in self.entity_patterns.items():
                match = re.search(pattern, deal, re.IGNORECASE)
                if match:
                    deal_entities[entity_type] = match.group(1).strip()
            
            if deal_entities:
                processed_deals.append(deal_entities)
                
        return processed_deals

    def create_token_labels(self, text: str, entities: Dict[str, str]) -> List[str]:
        """Create token-level labels for the text."""
        tokens = text.split()
        labels = ['O'] * len(tokens)
        
        for entity_type, value in entities.items():
            if not value:
                continue
                
            value_tokens = value.split()
            for i in range(len(tokens) - len(value_tokens) + 1):
                if tokens[i:i+len(value_tokens)] == value_tokens:
                    labels[i] = f'B-{entity_type}'
                    for j in range(1, len(value_tokens)):
                        labels[i+j] = f'I-{entity_type}'
                        
        return labels

    def prepare_training_data(self, raw_file: str, validation_file: str) -> Tuple[List[str], List[List[str]]]:
        """Prepare training data from raw text and validation files."""
        # Read raw text
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        # Read validation data
        validation_data = []
        with open(validation_file, 'r', encoding='utf-8') as f:
            for line in f:
                validation_data.append(json.loads(line))
        
        # Process deals
        processed_deals = self.process_raw_text(raw_text)
        
        texts = []
        labels = []
        
        for deal in processed_deals:
            deal_text = ' '.join([f"{k}: {v}" for k, v in deal.items()])
            texts.append(deal_text)
            labels.append(self.create_token_labels(deal_text, deal))
            
        return texts, labels 