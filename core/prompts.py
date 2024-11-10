from typing import List, Dict
import json

STRUCTURE_ANALYSIS_PROMPT = """Analyze the structure of deal text and identify shared fields. A field is considered shared when it applies to ALL deals in the text.

Key Rules for Shared Fields:
1. Partner is shared when:
   - It appears at the start with "Partner:" or "Company:" and applies to all following deals
   - It's mentioned once and clearly applies to multiple deals
2. Language is shared when:
   - It's specified once at the top level (e.g., "ENG speaking", "NATIVE speaking")
   - It applies consistently across all deals
3. Source is shared when:
   - It's specified once for all deals (e.g., "source: fb" at top)
4. Model is shared when:
   - It's specified once and applies to all deals (e.g., "model: cpa+crg")
5. Deduction Limit is shared when:
   - It appears at the bottom (e.g., "all campaigns are until 5% wrong number")
   - It's specified as a global limit (e.g., "until 5% wrong number")

Examples of Shared Fields:
1. "Partner: Sutra
    AU - 1300+13%
    US - 1400+15%"
    → Partner "Sutra" is shared

2. "Language: Native
    Partner: Deum
    NO - 1200+10%
    FI - 1200+10%"
    → Both "Language" and "Partner" are shared

3. "Company: FTD Company
    🇩🇪DE(nat) — Oil Profit, Bitcoin 360 Ai"
    → Company/Partner is shared

4. "ENG speaking
    Partner: Deum"
    → Language is shared

5. "all campaigns are until 5% wrong number"
    → Deduction limit is shared

Return this analysis as JSON:
{
    "structure_type": "single_line|multi_line_single_deal|multi_line_multiple_deals|multi_line_multi_geo",
    "shared_fields": {
        "partner": "string or null",
        "language": "string or null",
        "source": "string or null",
        "model": "string or null",
        "deduction_limit": "string or null"
    },
    "deal_count": number,
    "deal_blocks": [
        {
            "text": "raw text for this deal",
            "inherits_from": ["partner", "language", "deduction_limit", etc]
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