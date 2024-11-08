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
   - cpa_crg: CPA + Conversion Rate Guarantee 
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

Input:
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

🇪🇺ENG EU (t1+t2) 
NO FI IE SE CH DK BE NL + SK SI CZ 
model: cpa+crg  
price: $1200+8% 
source: fb 
funnels: Quantum AI
cr: 8-9%

🇨🇦CA eng
model: cpa+crg   
price: $1100+10% 
source: fb 
funnels: Quantum AI
cr: 10%
```
Output:
```
TIER1-Deum-NO|FI|IE|SE|CH|DK|BE|NL-English-Facebook-cpa_crg-1200-0.10-&-Quantum AI-10|12-&
TIER1-Deum-NO|FI|IE|SE|CH|DK|BE|NL|SK|SI|CZ-English-Facebook-cpa_crg-1200-0.08-&-Quantum AI-8|9-&
TIER1-Deum-CA-English-Facebook-cpa_crg-1100-0.10-&-Quantum AI-10-&
```

Input:
```
Partner: AffGenius
RO
1000 + 10 %
cap: 10
Immediate funnels
fb

IT
Funnel: Immediate funnel
Price: 1200+11%  - test
Source: fb

IT
Price: 1300+13
Funnels: OpuTrade 2.0 App
Source:FB
```
Output:
```
TIER3-AffGenius-RO-Native-Facebook-cpa_crg-1000-0.10-&-Immediate funnels-&-&
TIER1-AffGenius-IT-Native-Facebook-cpa_crg-1200-0.11-&-Immediate funnel-&-&
TIER1-AffGenius-IT-Native-Facebook-cpa_crg-1300-0.13-&-OpuTrade 2.0 App-&-&
```

Input:
```
Company: FTD Company
🇩🇪DE(nat) —  Oil Profit, Bitcoin 360 Ai, Immediate Edge, HB-Swiss, BITCOINEER
CR: 8-10%
PRICE: 1000$+9% CRG

🇪🇸ES (nat) — Trade App, Immediate Connect, BITCOINEER, Gemini2, BtcBillionaire, Repsol,IndiTex Capital
CR: 6-7%
PRICE: 950$+7% CRG

🇨🇱CL —Antofagasta, Bitcoin Billionaire, BITEVEX, OilProfit, Falabella
CR: 3%
PRICE: 600$+3% CRG
```   
Output:
```
TIER1-FTD Company-DE-Native-&-cpa_crg-1000-0.09-&-Oil Profit|Bitcoin 360 Ai|Immediate Edge|HB-Swiss|BITCOINEER-8|10-&
TIER1-FTD Company-ES-Native-&-cpa_crg-950-0.07-&-Trade App|Immediate Connect|BITCOINEER|Gemini2|BtcBillionaire|Repsol|IndiTex Capital-6|7-&
LATAM-FTD Company-CL-Native-&-cpa_crg-600-0.03-&-Antofagasta|Bitcoin Billionaire|BITEVEX|OilProfit|Falabella-3-&
```   

Input:
```
Partner: Acolyte
UK 1250+13% mostly DenixAI, Dendexol, Immediate Vortex, Immediate Elevation, Immutable Corvex, InstaDynex, EvoPrimeX
DE 1300+17% mostly Bitcoin Buyer - Bing.
ES 1200+12% mostly Bitnextese Band, BTC Bank, Iberdrola, AI Trading, Immediate Edge. - NativeAds, Google 
CA 1200+12% mostly Quantum - FB, GG
CL 700+4% mostly SQM Crypto profit - FB.
MX 700+2.5% mostly Oil profit - FB.
CR 700+4% mostly Oil profit - FB.
have more latam if needed, lmk which geo :)

all campaigns are until 5% wrong number.
```
Output:
```
TIER1-Acolyte-UK-Native-&-cpa_crg-1250-0.13-&-DenixAI|Dendexol|Immediate Vortex|Immediate Elevation|Immutable Corvex|InstaDynex|EvoPrimeX-&-0.05
TIER1-Acolyte-DE-Native-Bing-cpa_crg-1300-0.17-&-Bitcoin Buyer-&-0.05
TIER1-Acolyte-ES-Native-Native Ads|Google-cpa_crg-1200-0.12-&-Bitnextese Band|BTC Bank|Iberdrola|AI Trading|Immediate Edge-&-0.05
TIER1-Acolyte-CA-Native-Facebook|Google-cpa_crg-1200-0.12-&-Quantum-&-0.05
LATAM-Acolyte-CL-Native-Facebook-cpa_crg-700-0.04-&-SQM Crypto profit-&-0.05
LATAM-Acolyte-MX-Native-Facebook-cpa_crg-700-0.025-&-Oil profit-&-0.05
LATAM-Acolyte-CR-Native-Facebook-cpa_crg-700-0.04-&-Oil profit-&-0.05
```

Input:
```
Partner: Acolyte
FR 1050+8% doing 10%
ByteToken360 - FB GG.

FR 1000+9% doing 10%
ByteToken360 - FB GG.
until 5% wrong number.

FR 1150+13% mostly Bitcoin bank. Taboola.
doing 15-20% !

SG-en 1550+20% mostly azaliumbit.
No invalid leads

CO 650+2% / 13$  Oil profit
PE 650+3% / 19.5$ Cripto Peru
```
Output:
```
TIER1-Acolyte-FR-Native-Facebook|Google-cpa_crg-1050-0.08-&-ByteToken360-10-&
TIER1-Acolyte-FR-Native-Facebook|Google-cpa_crg-1000-0.09-&-ByteToken360-10-0.05
TIER1-Acolyte-FR-Native-Taboola-cpa_crg-1150-0.13-&-Bitcoin bank-15|20-&
TIER1-Acolyte-SG-English-&-cpa_crg-1550-0.20-&-azaliumbit-&-0.00
LATAM-Acolyte-CO-Native-&-cpa_crg-650-0.02-&-Oil profit-&-&
LATAM-Acolyte-PE-Native-&-cpa_crg-650-0.03-&-Cripto Peru-&-&
```

Input:
```
Partner: Genio
GEO: SG               
CPA + crg :  1350$ + 13%                           
Landing Page: Tradeshop AI, Bitcoin GPT, Big Money Rush  
Source: SEO + FB

GEO: BE  nl                  
CPA + crg : 1350$ + 13%                     
Landing Page: HyperTrader AI GPT Dutch  
      
GEO:  BE fr                 
CPA + crg :  1350$ + 13%                                  
Landing Page: Immediate X AI  
 
GEO: BE fr nl    
CPA + crg :  1350$ + 13%                             
Landing Page: Tradeshop AI, Bitcoin GPT, Big Money Rush    
Source: SEO + FB    

```
Output:
```
TIER1-Genio-SG-Native-SEO|Facebook-cpa_crg-1350-0.13-&-Tradeshop AI|Bitcoin GPT|Big Money Rush-&-&
TIER3-Genio-BE-Dutch-&-cpa_crg-1350-0.13-&-HyperTrader AI GPT Dutch-&-&
TIER3-Genio-BE-French-&-cpa_crg-1350-0.13-&-Immediate X AI-&-&
TIER3-Genio-BE-French|Dutch-SEO|Facebook-cpa_crg-1350-0.13-&-Tradeshop AI|Bitcoin GPT|Big Money Rush-&-&
```

## Key Notes
- Use "&" for any missing/n/a fields
- Keep funnel names exactly as provided
- Keep multi-geo deals together (don't split)
- CR only if explicitly stated
- Language defaults to "Native" unless specified
- All fields must be present in output