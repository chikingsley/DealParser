import json
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)

class TrainingDealParser:
    def __init__(self):
        # Region classifications from DealFormatting.md
        self.LATAM = ['AR', 'BO', 'BR', 'CL', 'CO', 'CR', 'CU', 'DO', 'EC', 'SV', 'GT', 'HN', 'MX', 'NI', 'PA', 'PY', 'PE', 'UY', 'VE']
        self.NORDICS = ['DK', 'FI', 'IS', 'NO', 'SE']
        self.BALTICS = ['EE', 'LV', 'LT']
        self.TIER1 = ['AU', 'CA', 'FR', 'DE', 'IT', 'JP', 'NL', 'NZ', 'SG', 'ES', 'GB', 'US', 'UK']
        
        # Source normalizations
        self.SOURCE_MAPPINGS = {
            'fb': 'Facebook',
            'facebook': 'Facebook',
            'fb traffic': 'Facebook',
            'ggl': 'Google',
            'google': 'Google',
            'gg': 'Google',
            'search.display': 'Google Display',
            'seo': 'SEO',
            'msn': 'MSN',
            'taboola': 'Taboola',
            'native': 'Native',
            'nativeads': 'Native Ads',
            'bing': 'Bing'
        }
        
        # Language mappings
        self.LANGUAGE_MAPPINGS = {
            'eng': 'English',
            'english': 'English',
            'en': 'English',
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'pt': 'Portuguese',
            'it': 'Italian',
            'nl': 'Dutch',
            'ru': 'Russian'
        }

    def parse_deals(self, text: str) -> List[Dict]:
        """Parse deals with shared context awareness"""
        try:
            # Get shared context first
            shared_context = self._extract_shared_context(text)
            
            # Split into individual deals
            deals = self._split_deals(text)
            
            parsed_deals = []
            for deal in deals:
                parsed = self._parse_single_deal(deal, shared_context)
                if parsed:
                    parsed_deals.append(parsed)
                    
            return parsed_deals
            
        except Exception as e:
            logger.error(f"Error parsing deals: {str(e)}")
            return []

    def _extract_shared_context(self, text: str) -> Dict:
        """Extract context shared across all deals"""
        context = {
            'partner': None,
            'language': None,
            'deduction_limit': None,
            'source': None
        }
        
        # Extract partner
        partner_match = re.search(r'Partner:?\s*([^:\n]+)', text, re.IGNORECASE)
        if partner_match:
            context['partner'] = partner_match.group(1).strip()
            
        # Extract deduction limit
        if 'wrong number' in text.lower():
            limit_match = re.search(r'until\s*(\d+(?:\.\d+)?)\s*%\s*wrong', text, re.IGNORECASE)
            if limit_match:
                context['deduction_limit'] = float(limit_match.group(1)) / 100
                
        # Extract shared language
        lang_match = re.search(r'(?:speaking|language):\s*([^:\n]+)', text, re.IGNORECASE)
        if lang_match:
            context['language'] = self._normalize_language(lang_match.group(1))
            
        return context

    def _split_deals(self, text: str) -> List[str]:
        """Split text into individual deals"""
        deals = []
        current_deal = []
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # New deal indicators
            new_deal = (
                bool(re.match(r'^[A-Z]{2}\b', line)) or  # Country code
                bool(re.match(r'^GEO:?\s*', line, re.IGNORECASE)) or  # GEO: prefix
                bool(re.match(r'^🇪🇺|^🇺🇸|^🇬🇧', line))  # Flag emoji
            )
            
            if new_deal and current_deal:
                deals.append('\n'.join(current_deal))
                current_deal = []
                
            current_deal.append(line)
            
        if current_deal:
            deals.append('\n'.join(current_deal))
            
        return deals

    def _parse_single_deal(self, text: str, shared_context: Dict) -> Dict:
        """Parse single deal with context"""
        try:
            # Extract all fields
            partner = self._extract_partner(text) or shared_context.get('partner')
            geo = self._extract_geo(text)
            region = self._determine_region(geo)
            language = self._extract_language(text) or shared_context.get('language', 'Native')
            source = self._extract_source(text) or shared_context.get('source', 'Facebook')
            pricing_model = self._determine_pricing_model(text)
            cpa = self._extract_cpa(text)
            crg = self._extract_crg(text)
            cpl = self._extract_cpl(text)
            funnels = self._extract_funnels(text)
            cr = self._extract_cr(text)
            deduction_limit = self._extract_deduction_limit(text) or shared_context.get('deduction_limit')
            
            return {
                'raw_text': text,
                'parsed_data': {
                    'partner': partner,
                    'region': region,
                    'geo': geo,
                    'language': language,
                    'source': source,
                    'pricing_model': pricing_model,
                    'cpa': cpa,
                    'crg': crg,
                    'cpl': cpl,
                    'funnels': funnels,
                    'cr': cr,
                    'deduction_limit': deduction_limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing deal: {str(e)}")
            return None

    def _normalize_language(self, text: str) -> str:
        """Normalize language codes"""
        text = text.lower().strip()
        
        # Check language mappings
        for code, lang in self.LANGUAGE_MAPPINGS.items():
            if code in text:
                return lang
                
        # Handle special cases
        if 'nat' in text or '(nat)' in text:
            return 'Native'
            
        return 'Native'  # Default

    def _extract_partner(self, text: str) -> str:
        """Extract partner name"""
        partner_match = re.search(r'Partner:?\s*([^:\n]+)', text, re.IGNORECASE)
        if partner_match:
            return partner_match.group(1).strip()
        return "&"

    def _extract_geo(self, text: str) -> str:
        """Extract country code(s)"""
        # Look for explicit GEO field
        geo_match = re.search(r'GEO:?\s*([A-Z]{2}(?:\s*[,|]\s*[A-Z]{2})*)', text, re.IGNORECASE)
        if geo_match:
            return '|'.join(re.findall(r'[A-Z]{2}', geo_match.group(1)))
            
        # Look for country codes at start of lines
        codes = re.findall(r'^([A-Z]{2})\b', text, re.MULTILINE)
        if codes:
            return '|'.join(codes)
            
        return "&"

    def _determine_region(self, geo: str) -> str:
        """Determine region from country code"""
        if '|' in geo:  # Multiple GEOs
            geos = geo.split('|')
            regions = set(self._determine_region(g) for g in geos)
            return '|'.join(regions)
            
        if geo in self.LATAM:
            return 'LATAM'
        elif geo in self.NORDICS:
            return 'NORDICS'
        elif geo in self.BALTICS:
            return 'BALTICS'
        elif geo in self.TIER1:
            return 'TIER1'
        return 'TIER3'

    def _extract_source(self, text: str) -> str:
        """Extract and normalize traffic sources"""
        text = text.lower()
        sources = set()
        
        # Check source mappings
        for key, value in self.SOURCE_MAPPINGS.items():
            if key in text:
                sources.add(value)
                
        # Look for explicit source field
        source_match = re.search(r'source:?\s*([^:\n]+)', text, re.IGNORECASE)
        if source_match:
            source_text = source_match.group(1).lower()
            for key, value in self.SOURCE_MAPPINGS.items():
                if key in source_text:
                    sources.add(value)
                    
        return '|'.join(sorted(sources)) if sources else 'Facebook'

    def _determine_pricing_model(self, text: str) -> str:
        """Determine pricing model"""
        text = text.lower()
        
        if '+' in text and any(x in text for x in ['%', 'crg']):
            return 'CPA/CRG'
        elif 'cpl' in text:
            return 'CPL'
        return 'CPA'

    def _extract_cpa(self, text: str) -> float:
        """Extract CPA value"""
        # Look for price with percentage
        price_match = re.search(r'(?:price:?\s*)?(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:\$|USD)?\s*\+', text, re.IGNORECASE)
        if price_match:
            return float(price_match.group(1).replace(',', ''))
            
        # Look for flat CPA
        cpa_match = re.search(r'(?:cpa|price):?\s*(\d+(?:,\d+)?(?:\.\d+)?)', text, re.IGNORECASE)
        if cpa_match:
            return float(cpa_match.group(1).replace(',', ''))
            
        return None

    def _extract_crg(self, text: str) -> float:
        """Extract CRG value"""
        # Look for percentage after +
        crg_match = re.search(r'\+\s*(\d+(?:\.\d+)?)\s*%', text)
        if crg_match:
            return float(crg_match.group(1)) / 100
        return None

    def _extract_cpl(self, text: str) -> float:
        """Extract CPL value"""
        cpl_match = re.search(r'(?:cpl|lead):?\s*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
        if cpl_match:
            return float(cpl_match.group(1))
        return None

    def _extract_funnels(self, text: str) -> List[str]:
        """Extract funnel names"""
        funnels = []
        
        # Look for explicit funnel field
        funnel_match = re.search(r'(?:funnel|landing page)s?:?\s*([^:\n]+)', text, re.IGNORECASE)
        if funnel_match:
            funnels = [f.strip() for f in re.split(r'[,/]', funnel_match.group(1))]
            
        # Look for funnels after dash
        if not funnels:
            dash_match = re.search(r'-\s*([^-\n]+?)(?:\s*\(|$)', text)
            if dash_match:
                funnels = [f.strip() for f in re.split(r'[,/]', dash_match.group(1))]
                
        return [f for f in funnels if f and not any(s in f.lower() for s in ['fb', 'facebook', 'google'])]

    def _extract_cr(self, text: str) -> float:
        """Extract conversion rate"""
        # Look for CR range
        cr_range = re.search(r'cr:?\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
        if cr_range:
            return (float(cr_range.group(1)) + float(cr_range.group(2))) / 200
            
        # Look for single CR value
        cr_match = re.search(r'(?:cr|doing):?\s*(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
        if cr_match:
            return float(cr_match.group(1)) / 100
            
        return None

    def _extract_deduction_limit(self, text: str) -> float:
        """Extract deduction limit"""
        limit_match = re.search(r'(?:until|deduction limit):?\s*(\d+(?:\.\d+)?)\s*%', text, re.IGNORECASE)
        if limit_match:
            return float(limit_match.group(1)) / 100
        return None