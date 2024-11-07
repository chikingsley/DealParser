STRUCTURE_ANALYSIS_PROMPT = """First, analyze the structure of the input text and identify:
1. Structure type (single_line, multi_line_single_deal, multi_line_multiple_deals, etc.)
2. Shared fields (partner, language, model, etc.)
3. Number of distinct deals
4. Any field inheritance patterns

Return this analysis as JSON:
{
    "structure_type": "string",
    "shared_fields": {
        "partner": "string or null",
        "language": "string or null",
        // other shared fields
    },
    "deal_count": number,
    "deal_blocks": [
        {
            "text": "raw text for this deal",
            "inherits_from": ["list of fields inherited from shared context"]
        }
    ]
}"""

DEAL_PARSING_PROMPT = """Parse this specific deal block, using the provided shared context:

Shared Context:
{shared_context}

Deal Text:
{deal_text}

Return as JSON with confidence flags:
{
    "raw_text": "original text",
    "parsed_data": {
        "partner": string,
        "region": string,
        "geo": string,
        // other fields
    },
    "metadata": {
        "confidence_flags": {
            "partner": "explicit|inferred|inherited|empty",
            // flags for each field
        }
    }
}"""

class DealPrompts:
    @staticmethod
    def create_structure_prompt(text: str) -> List[Dict]:
        return [
            {"role": "system", "content": STRUCTURE_ANALYSIS_PROMPT},
            {"role": "user", "content": f"Analyze this text:\n{text}"}
        ]
    
    @staticmethod
    def create_parsing_prompt(deal_text: str, shared_context: Dict) -> List[Dict]:
        return [
            {"role": "system", "content": DEAL_PARSING_PROMPT},
            {"role": "user", "content": f"Parse with context:\n{json.dumps(shared_context)}\n\nDeal text:\n{deal_text}"}
        ]