from typing import List, Dict
import json

STRUCTURE_ANALYSIS_PROMPT = """Analyze the structure of deal text and identify shared fields. A field is considered shared when it applies to ALL deals within a partner's section.

Key Rules for Shared Fields:
1. Partner is shared when:
   - It appears as "Partner:", "Company:", or similar prefix
   - It applies to all deals until the next partner declaration
   - Each "Partner:" section starts a new group with its own shared fields
2. Language is shared when:
   - It's specified at the section level (e.g., "ENG speaking", "NATIVE speaking")
   - It's part of a GEO specification (e.g., "BE fr", "NL nl")
   - It's mentioned in a group header
3. Source is shared when:
   - It's specified once for multiple deals in a section
   - It appears consistently for deals under the same partner
4. Model is shared when:
   - It's specified once for multiple deals (e.g., "model: cpa+crg")
   - It's consistent across a partner's deals
5. Deduction Limit is shared when:
   - It appears at the bottom of a partner's section
   - It's specified as a global limit (e.g., "until 5% wrong number", "all campaigns are until 5% wrong number")

CRITICAL RULES:
- Each "Partner:" declaration starts a new section with its own shared fields
- Shared fields only apply within their partner's section
- Language can be inferred from GEO codes (e.g., "BE fr" implies French)
- Multiple deals can share the same GEO with different funnels/prices

Example Analysis:
Input:
Partner: Sutra
AU - 1300+13% - mainly Beatskai iq (fb)
UK - 1350+10% - mainly Immediate core (native/fb)

Partner: Deum
ENG speaking
NO FI IE SE - 1200+10% - Quantum AI (fb)
FR fr - 1000+9% - Quantum AI (fb)

Should output:
{
    "structure_type": "multi_line_multiple_deals",
    "sections": [
        {
            "shared_fields": {
                "partner": "Sutra"
            },
            "deal_blocks": [
                {
                    "text": "AU - 1300+13% - mainly Beatskai iq (fb)",
                    "inherits_from": ["partner"],
                    "shared_values": {"partner": "Sutra"}
                },
                {
                    "text": "UK - 1350+10% - mainly Immediate core (native/fb)",
                    "inherits_from": ["partner"],
                    "shared_values": {"partner": "Sutra"}
                }
            ]
        },
        {
            "shared_fields": {
                "partner": "Deum",
                "language": "ENG"
            },
            "deal_blocks": [
                {
                    "text": "NO FI IE SE - 1200+10% - Quantum AI (fb)",
                    "inherits_from": ["partner", "language"],
                    "shared_values": {
                        "partner": "Deum",
                        "language": "ENG"
                    }
                },
                {
                    "text": "FR fr - 1000+9% - Quantum AI (fb)",
                    "inherits_from": ["partner"],
                    "shared_values": {
                        "partner": "Deum",
                        "language": "French"
                    }
                }
            ]
        }
    ]
}

Return this analysis as JSON:
{
    "structure_type": "single_line|multi_line_single_deal|multi_line_multiple_deals|multi_line_multi_geo",
    "sections": [
        {
            "shared_fields": {
                "partner": "string or null",
                "language": "string or null",
                "source": "string or null",
                "model": "string or null",
                "deduction_limit": "string or null"
            },
            "deal_blocks": [
                {
                    "text": "raw text for this deal",
                    "inherits_from": ["list of inherited field names"],
                    "shared_values": {
                        "field_name": "actual inherited value"
                    }
                }
            ]
        }
    ]
}"""

DEAL_PARSING_PROMPT = """Parse a single deal with awareness of shared/inherited values.

CRITICAL: If a field exists in shared_values, YOU MUST USE THAT VALUE in the parsed_data output. Do not look for it in the deal text.

INHERITANCE RULES (HIGHEST PRIORITY):
1. ALWAYS check shared_values first - if a value exists there, use it exactly as provided
2. Only look in deal text if the field is not in shared_values
3. Mark confidence_flags as "inherited" for any value taken from shared_values

Deal-Specific Rules (USE ONLY IF NO INHERITED VALUE):
1. Partner:
   - Look for explicit "Partner:" prefix
   - Default to null if not found and not inherited
   
2. Region: Classify GEO into:
   - LATAM: AR, BO, BR, CL, CO, CR, CU, DO, EC, SV, GT, HN, MX, NI, PA, PY, PE, UY, VE
   - NORDICS: DK, FI, IS, NO, SE
   - BALTICS: EE, LV, LT
   - TIER1: AU, CA, FR, DE, IT, JP, NL, NZ, SG, ES, GB, US, UK, BE, CH, AT, IE
   - TIER3: All other countries

3. Language:
   - Use inherited value if present
   - Look for language specifications in GEO (e.g., "BE fr", "NL nl")
   - Look for explicit language mentions (e.g., "native", "eng")
   - Default to "Native" if not found

4. Source:
   - Use inherited value if present
   - Look for source in parentheses or after dash
   - Common values: fb, Facebook, Google, SEO, Taboola, etc.
   - Multiple sources should be comma-separated

5. Pricing Model:
   - Format "X+Y%" indicates "CPA/CRG"
   - Single number with "cpl" indicates "CPL"
   - Look for explicit "model:" prefix

6. Numbers:
   - CPA: Number before "+" in "X+Y%"
   - CRG: Convert Y to decimal in "X+Y%" (e.g., 10% -> 0.10)
   - CPL: Direct number in CPL model
   - Remove currency symbols and spaces

7. Funnels:
   - Look for funnel names after pricing info
   - Common indicators: "Landing Page:", "Funnel:", "mainly", "mostly"
   - Comma-separated list if multiple

8. CR (Conversion Rate):
   - Look for "cr:", "CR:", or percentage ranges
   - Convert to decimal (e.g., "10-12%" -> 0.11 for average)

9. Deduction Limit:
   - Use inherited value if present
   - Look for "until X% wrong number"
   - Convert to decimal

10. Special Cases:
    - Handle emoji prefixes (🇬🇧, 🇺🇸, etc.)
    - Clean whitespace and special characters
    - Normalize case for consistent matching

Return JSON in this format:
{
    "raw_text": "original deal text",
    "parsed_data": {
        "partner": "string or null",
        "region": "LATAM|NORDICS|BALTICS|TIER1|TIER3",
        "geo": "two-letter country code",
        "language": "string",
        "source": "string",
        "pricing_model": "CPL|CPA/CRG",
        "cpa": "number or null",
        "crg": "number or null",
        "cpl": "number or null",
        "funnels": ["array of strings"],
        "cr": "number or null",
        "deduction_limit": "number or null"
    },
    "metadata": {
        "confidence_flags": {
            "partner": "explicit|inherited|empty",
            "region": "explicit|inherited|empty",
            "geo": "explicit|inherited|empty",
            "language": "explicit|inherited|empty",
            "source": "explicit|inherited|empty",
            "pricing_model": "explicit|inherited|empty",
            "cpa": "explicit|inherited|empty",
            "crg": "explicit|inherited|empty",
            "cpl": "explicit|inherited|empty",
            "funnels": "explicit|inherited|empty",
            "cr": "explicit|inherited|empty",
            "deduction_limit": "explicit|inherited|empty"
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
