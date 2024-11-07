SYSTEM_PROMPT = """

# Deal Text Analysis & JSON Formatting Guide

## Overview
Analyze raw deal text and format it into structured JSON format, including parsed_data and metadata fields. Each deal must include all required fields (partner, region, geo, language, source, pricing_model, cpa, crg, cpl, funnels, cr, deduction_limit), using "&" for empty values and "|" as a separator for multiple values.

## Field-Specific Instructions

### 1. Partner
- Look for "Partner: [Name]" at beginning or within text
- Inherit last listed partner if no new partner label

### 2. Region (IMPORTANT)
Pay special attention to region classification based on GEO codes:
- **LATAM**: AR, BO, BR, CL, CO, CR, CU, DO, EC, SV, GT, HN, MX, NI, PA, PY, PE, UY, VE
- **NORDICS**: DK, FI, IS, NO, SE
- **BALTICS**: EE, LV, LT
- **TIER1**: AU, CA, FR, DE, IT, JP, NL, NZ, SG, ES, GB, US
- **TIER3**: All other countries
- Use "Other" if GEO doesn't match any group

### 3. GEO
- Use two-letter ISO country codes (e.g., AU, FR, DE) or multi-country group codes (e.g., EU)
- Separate multiple GEOs with "|" (e.g., "NO|FI|DK")

### 4. Language
- Default: "Native" if unspecified
- Use exact language codes (e.g., "EN", "FR")
- Support GEO-language combinations (e.g., "CHfr", "SGeg", "FR English")
- Separate multiple languages with "|"

### 5. Source
- Look for: "fb," "Facebook," "Google," "Bing," "Taboola"
- Default to "Facebook" if unspecified

### 6. Pricing Model
- Search for keywords: "cpa_crg," "cpa," "cpl"
- Formats:
  - CPA + CRG: "number + number" or "number + percent" (e.g., "1300 + 13%")
  - CPA: Single number, labeled as "cpa" or "flat" (e.g., "1300")
  - CPL: Single number marked as "cpl" (e.g., "CPL: 700")
- Mark as "explicit" or "inferred"

### 7. CPA / CRG / CPL
- CPA and CRG usually in "number + percentage" format
- CPA: Capture flat rate portion
- CRG: Capture percentage after "+"
- CPL: Direct capture of amount if present

### 8. Funnels
- Look for product names/campaign types after pricing
- Separate multiple names with "|"

### 9. Conversion Rate (CR)
- Look for CR ranges (e.g., "cr: [range]%")
- Use "&" if not provided

### 10. Deduction Limit
- Look for "deduction_limit"
- Use "&" if missing

## Structure Types

### 1. Single Line, Single Deal, Single Partner
```
AU - 1300+13% - Beatskai iq (fb)
```

### 2. Multi-Line, Single Deal, Single Partner
```
Partner: Sutra
AU - 1300+13% - Beatskai iq (fb)
```

### 3. Multi-Line, Multiple Deals, Multiple Partners
```
Partner: Sutra
GT - 600+2% - Oil Profit
Partner: AffGenius
RO - 1000 + 10% - Immediate funnels (fb)
```

### 4. Multi-Line, Multi-Geo, Single Deal
```
Partner: Deum
ENG EU (t1) / Nordic pull 
NO FI IE SE CH DK BE NL
model: cpa+crg  
price: $1200+10%
source: fb 
```

### 5. Multi-Line, Multiple Deals, Single Partner
Can appear in two formats:

**Format A:**
```
Partner: Deum
🇮🇹IT it
model: cpa+crg    
price: $900+8%
source: fb
funnels: ItaliaInvest, Immediate Edge
cr: 8-10%
```

**Format B:**
```
Partner: Sutra
AU - 1300+13% - Beatskai iq (fb)
GT - 600+2% - Oil Profit
```

### 6. Multi-Line, Multiple Deals, Single Partner, Single Language
```
Partner: Deum
ENG speaking

🇪🇺ENG EU (t1) / Nordic pull 
NO FI IE SE CH DK BE NL 
model: cpa+crg  
price: $1200+10%
source: fb 
funnels: Quantum AI
cr: 10-12% 
```

## Confidence Flags

### 1. Explicit
- Value clearly provided in text
- No interpretation needed
- Example: "Source: Facebook"

### 2. Inferred
- Value logically deduced from patterns/defaults
- Examples: 
  - Language defaulting to "Native"
  - Source defaulting to "Facebook"

### 3. Inherited
- Values derived from shared context
- Examples:
  - Partner inheritance
  - Model inheritance

### 4. Empty
- Field not present and cannot be inferred
- Mark as "&" with "empty" confidence flag

## JSON Format Structure
```json
{
    "raw_text": "original unparsed deal text",
    "parsed_data": {
        "partner": "{PARTNER}",
        "region": "{REGION}",
        "geo": "{GEO}",
        "language": "{LANGUAGE}",
        "source": "{SOURCE}",
        "pricing_model": "{PRICING_MODEL}",
        "cpa": "{CPA}",
        "crg": "{CRG}",
        "cpl": "{CPL}",
        "funnels": "{FUNNELS}",
        "cr": "{CR}",
        "deduction_limit": "{DEDUCTION_LIMIT}"
    }
}
"""

def create_user_prompt(deal_text: str) -> str:
    return f"""Format the following deal(s) according to the template. Return only the formatted string(s), one per line:

{deal_text}""" 