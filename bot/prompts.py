from typing import List, Dict
import json

STRUCTURE_ANALYSIS_PROMPT = """Analyze the structure of deal text and identify shared fields and individual deals.

Output Format:
{
    "sections": [
        {
            "shared_fields": {
                "partner": string,
                "language": string,
                "source": string,
                "model": string,
                "deduction_limit": number|null
            },
            "deal_blocks": [
                {
                    "text": string,  // Original deal text
                    "geo": string,
                    "pricing": {
                        "cpa": number,
                        "crg": number
                    },
                    "funnels": string[]
                }
            ]
        }
    ]
}

Key Rules:
1. Partner is shared when:
   - Appears as "Partner:" or "Company:" prefix
   - Applies until next partner declaration
   
2. Language is shared when:
   - Specified at section level (e.g., "ENG speaking")
   - Part of GEO (e.g., "BE fr", "NL nl")
   
3. Source is shared when:
   - Specified once for multiple deals
   - Normalize: fb->Facebook, gg->Google, etc.

4. Model is shared when:
   - Specified once (e.g., "model: cpa+crg")
   - Inferred from pricing format (e.g., "1350+13%" implies CPA+CRG)

5. Deal blocks must contain:
   - Original text
   - GEO code
   - Pricing (CPA/CRG values)
   - Funnels as array
"""

DEAL_PARSING_PROMPT = """Parse individual deal details using shared context.

Input Format:
{
    "shared_fields": {
        "partner": string,
        "language": string,
        "source": string,
        "model": string,
        "deduction_limit": number|null
    },
    "deal_text": string
}

Output Format:
{
    "raw_text": string,
    "parsed_data": {
        "partner": string,
        "region": "TIER1"|"TIER2"|"TIER3"|"LATAM"|"NORDICS"|"BALTICS",
        "geo": string,
        "language": string,
        "source": string,
        "pricing_model": "CPA"|"CPA/CRG"|"CPL",
        "cpa": number|null,
        "crg": number|null,
        "cpl": number|null,
        "funnels": string[],
        "cr": number|null,
        "deduction_limit": number|null
    }
}
"""

class DealPrompts:
    @staticmethod
    def create_structure_prompt(text: str) -> List[Dict]:
        return [
            {"role": "system", "content": STRUCTURE_ANALYSIS_PROMPT},
            {"role": "user", "content": f"Analyze this text:\n{text}"}
        ]
    
    @staticmethod
    def create_parsing_prompt(deal_text: str, shared_context: Dict) -> List[Dict]:
        formatted_context = json.dumps(shared_context, indent=2)
        prompt = f"""Parse this deal using the shared context and rules.

Shared Context:
{formatted_context}

Deal Text:
{deal_text}"""
        
        return [
            {"role": "system", "content": DEAL_PARSING_PROMPT},
            {"role": "user", "content": prompt}
        ]