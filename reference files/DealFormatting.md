# Deal Data Formatting Instructions

FORMAT:
[Region]-[Partner]-[GEO]-[Language]-[Source]-[Model]-[CPA]-[CRG]-[CPL]-[Funnels]-[CR]-[DeductionLimit]

## Field Rules

1. REGION (Required)
   Select one:
   - LATAM: AR, BO, BR, CL, CO, CR, CU, DO, EC, SV, GT, HN, MX, NI, PA, PY, PE, UY, VE
   - NORDICS: DK, FI, IS, NO, SE
   - BALTICS: EE, LV, LT
   - TIER1: AU, CA, FR, DE, IT, JP, NL, NZ, SG, ES, GB, US
   - TIER3: All other countries

2. PARTNER (Required)
   - Use exact company name
   - Remove special characters/emojis
   - Use "&" if not specified

3. GEO (Required)
   - Use ISO 2-letter country codes
   - Multi-geo: separate with "|" (e.g., UK|IE|NL)
   - Regional codes allowed if specified (e.g., EU)

4. LANGUAGE (Required)
   Default: "Native" if:
   - No language specified
   - Listed as "nat" or "(nat)"
   - Explicitly stated as "Native"
   
   Otherwise validate given language:
   - english, eng, en → English
   - french, fr, fre → French
   - spanish, es, esp → Spanish
   - german, de, ger → German
   - portuguese, pt, por → Portuguese
   - italian, it, ita → Italian
   - dutch, nl, dut → Dutch
   - russian, ru, rus → Russian
   Multiple languages: separate with "|" (e.g., English|French)

5. SOURCE (Required)
   Validate and normalize:
   - fb, FB, Facebook → Facebook
   - gg, GG, google → Google
   - msn, MSN → MSN
   - ig, IG, instagram → Instagram
   - na, NA, nativeads → Native Ads
   - taboola, Taboola → Taboola
   - bing, Bing → Bing
   - tiktok, TikTok → TikTok
   - seo, SEO → SEO
   
   Combinations:
   - Preserve specific combinations (e.g., Google SEO)
   - Split others with "|" (e.g., FB+GG → Facebook|Google)
   Use "&" if not specified

6. MODEL (Required)
   One of:
   - cpa_crg: CPA + Revenue Share
   - cpa: Fixed CPA only
   - cpl: Cost Per Lead only

7. CPA (Required for cpa/cpa_crg)
   - Numbers only
   - No currency symbols
   - Round to whole number
   - Use "&" if not applicable

8. CRG (Required for cpa_crg)
   - Convert to decimal (9% → 0.09)
   - Use "&" if not applicable

9. CPL (Required for cpl)
   - Numbers only
   - No currency symbols
   - Round to whole number
   - Use "&" if not applicable

10. FUNNELS (Required)
    - Separate multiple with "|"
    - Keep exact names
    - Remove extra spaces
    - Use "&" if not specified

11. CR (Optional)
    - Use "&" if not specified
    - Range: use "|" (8-10% → 8|10)
    - Single: whole number (8% → 8)
    - "doing X%" means CR

12. DEDUCTION LIMIT (Optional)
    - Convert to decimal (5% → 0.05)
    - Use "&" if not specified
    - "until X% wrong number" means Deduction Limit

## Model Type Rules
- Price has "+%" (900+7%) → model is cpa_crg
- Flat price (900) → model is cpa
- Listed as "cpl" or per lead price → model is cpl

## Examples

1. CPA+CRG, Multi-Geo:
```
TIER1-FTD Company-UK|IE|NL-Native-Facebook|Google-cpa_crg-1200-0.10-&-QuantumAI-&-0.05
```

2. CPL, Single Geo, Specified Language:
```
LATAM-Deum-MX-Spanish-Facebook-cpl-&-&-15-Oil Profit|Riquezal-&-&
```

3. CPA, Default Language:
```
TIER1-Rayzone-NL-Native-Facebook-cpa-1300-&-&-Finance Phantom Bot|Finance Phantom AI-12-&
```

4. Mixed Sources:
```
TIER1-Sutra-FR-French-Facebook|Google SEO-cpa_crg-1000-0.09-&-ByteToken360-10-0.05
```

## Input/Output Examples

Input:
```
Partner: Sutra
FR 1000+9% doing 10% ByteToken360 - FB GG. until 5% wrong number.
```
Output:
```
TIER1-Sutra-FR-French-Facebook|Google-cpa_crg-1000-0.09-&-ByteToken360-10-0.05
```

Input:
```
Partner: Deum
🇲🇽MX es
Cpl 15$
Source: FB
Funnel: Oil profit, Riquezal 
cr: 2-3%
```
Output:
```
LATAM-Deum-MX-Spanish-Facebook-cpl-&-&-15-Oil Profit|Riquezal-2|3-&
```

## Key Notes
- Use "&" for any missing/n/a fields
- Keep funnel names exactly as provided
- Keep multi-geo deals together (don't split)
- CR only if explicitly stated
- Language defaults to "Native" unless specified
- All fields must be present in output