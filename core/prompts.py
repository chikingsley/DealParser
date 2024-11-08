from typing import List, Dict
import json

STRUCTURE_ANALYSIS_PROMPT = """Analyze the structure of deal text and identify shared fields. Pay special attention to these structure types:

1. Single Line, Single Deal:
Example: "AU - 1300+13% - Beatskai iq (fb)"

2. Multi-Line, Single Deal:
Example: 
"Partner: Sutra
AU - 1300+13% - Beatskai iq (fb)"

3. Multi-Line, Multiple Deals:
Example:
"Partner: Sutra
GT - 600+2% - Oil Profit
Partner: AffGenius
RO - 1000 + 10% - Immediate funnels (fb)"

4. Multi-Line, Multi-Geo Single Deal:
Example:
"Partner: Deum
ENG EU (t1) / Nordic pull 
NO FI IE SE CH DK BE NL
model: cpa+crg  
price: $1200+10%
source: fb"

Return this analysis as JSON:
{
    "structure_type": "single_line|multi_line_single_deal|multi_line_multiple_deals|multi_line_multi_geo",
    "shared_fields": {
        "partner": "string or null",
        "language": "string or null",
        "source": "string or null",
        "model": "string or null"
    },
    "deal_count": number,
    "deal_blocks": [
        {
            "text": "raw text for this deal",
            "inherits_from": ["partner", "language", etc]
        }
    ]
}"""

DEAL_PARSING_PROMPT = """Parse this deal using these rules:

1. Partner: Look for "Partner:" or inherit from context
2. Region: Classify GEO into:
   - LATAM: AR, BO, BR, CL, CO, CR, CU, DO, EC, SV, GT, HN, MX, NI, PA, PY, PE, UY, VE
   - NORDICS: DK, FI, IS, NO, SE
   - BALTICS: EE, LV, LT
   - TIER1: AU, CA, FR, DE, IT, JP, NL, NZ, SG, ES, GB, US
   - TIER3: All other countries
3. GEO: Use two-letter country codes
4. Language: Default "Native" if unspecified
5. Source: Look for fb, Facebook, Google, etc. Default to "Facebook" if unspecified
6. Pricing Model: 
   - If format is "X+Y%" -> "CPA/CRG"
   - Single number with "cpl" -> "CPL"
7. CPA: Number before "+" in "X+Y%"
8. CRG: Convert Y to decimal in "X+Y%" (e.g., 10% -> 0.10)
9. Funnels: Product names after pricing
10. CR: Look for "cr: X%" or "X-Y%"

Shared Context:
{shared_context}

Deal Text:
{deal_text}

Return as JSON:
{
    "raw_text": "original text",
    "parsed_data": {
        "partner": string,
        "region": string,
        "geo": string,
        "language": string,
        "source": string,
        "pricing_model": string,
        "cpa": number or null,
        "crg": number or null,
        "cpl": number or null,
        "funnels": [string],
        "cr": number or null
    },
    "metadata": {
        "confidence_flags": {
            "partner": "explicit|inferred|inherited|empty",
            "region": "explicit|inferred|inherited|empty",
            "geo": "explicit|inferred|inherited|empty",
            "language": "explicit|inferred|inherited|empty",
            "source": "explicit|inferred|inherited|empty",
            "pricing_model": "explicit|inferred|inherited|empty",
            "cpa": "explicit|inferred|inherited|empty",
            "crg": "explicit|inferred|inherited|empty",
            "cpl": "explicit|inferred|inherited|empty",
            "funnels": "explicit|inferred|inherited|empty",
            "cr": "explicit|inferred|inherited|empty"
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