from pydantic import BaseModel, Field
from typing import Optional, List
import hashlib
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class Deal(BaseModel):
    region: str
    partner: str
    geo: str
    language: str = "Native"
    source: str = "&"
    model: str = "cpa_crg"
    cpa: Optional[float] = None
    crg: Optional[float] = None
    cpl: Optional[float] = None
    funnels: List[str]
    cr: Optional[float] = None
    deduction_limit: Optional[float] = None

    def get_hash(self) -> str:
        """Generate a hash of the deal's core attributes"""
        deal_string = (
            f"{self.geo.upper()}|"
            f"{self.cpa or ''}|{self.crg or ''}|{self.cpl or ''}|"
            f"{self.source.lower()}|"
            f"{'|'.join(sorted(self.funnels))}|"
            f"{self.partner.lower()}"
        )
        return hashlib.md5(deal_string.encode()).hexdigest()

class DealProcessor:
    def __init__(self):
        self.db_path = Path("data/deals.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
        self.seen_deals = self._load_seen_deals()
        self.deals = self._load_deals()

    def _init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deals (
                    id INTEGER PRIMARY KEY,
                    region TEXT,
                    partner TEXT,
                    geo TEXT,
                    language TEXT,
                    source TEXT,
                    model TEXT,
                    cpa REAL,
                    crg REAL,
                    cpl REAL,
                    funnels TEXT,
                    cr REAL,
                    deduction_limit REAL,
                    hash TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS seen_deals (
                    hash TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _load_seen_deals(self) -> set:
        """Load seen deal hashes from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT hash FROM seen_deals")
            return set(row[0] for row in cursor.fetchall())

    def _load_deals(self) -> List[Deal]:
        """Load deals from database"""
        deals = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM deals ORDER BY created_at DESC")
            for row in cursor.fetchall():
                deals.append(Deal(
                    region=row[1],
                    partner=row[2],
                    geo=row[3],
                    language=row[4],
                    source=row[5],
                    model=row[6],
                    cpa=row[7],
                    crg=row[8],
                    cpl=row[9],
                    funnels=row[10].split('|'),
                    cr=row[11],
                    deduction_limit=row[12]
                ))
        return deals

    def is_duplicate(self, deal_text: str, processed_deal: Optional[Deal] = None) -> bool:
        """Check if a deal is a duplicate and store if not"""
        text_hash = hashlib.md5(deal_text.encode()).hexdigest()
        
        if text_hash in self.seen_deals:
            return True
            
        if processed_deal:
            deal_hash = processed_deal.get_hash()
            if deal_hash in self.seen_deals:
                return True
            
            # Store new deal
            with sqlite3.connect(self.db_path) as conn:
                # Store deal
                conn.execute(
                    """
                    INSERT INTO deals 
                    (region, partner, geo, language, source, model, cpa, crg, cpl, funnels, cr, deduction_limit, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        processed_deal.region,
                        processed_deal.partner,
                        processed_deal.geo,
                        processed_deal.language,
                        processed_deal.source,
                        processed_deal.model,
                        processed_deal.cpa,
                        processed_deal.crg,
                        processed_deal.cpl,
                        '|'.join(processed_deal.funnels),
                        processed_deal.cr,
                        processed_deal.deduction_limit,
                        deal_hash
                    )
                )
                # Store hash
                conn.execute(
                    "INSERT INTO seen_deals (hash) VALUES (?)",
                    (deal_hash,)
                )
                
            self.seen_deals.add(deal_hash)
            self.deals.append(processed_deal)
                
        self.seen_deals.add(text_hash)
        return False

    def check_duplicate_details(self, deal_text: str, processed_deal: Optional[Deal] = None) -> dict:
        """Check if and why a deal is a duplicate"""
        result = {
            "is_duplicate": False,
            "reason": None,
            "existing_deal": None,
            "created_at": None
        }
        
        # Check text hash
        text_hash = hashlib.md5(deal_text.encode()).hexdigest()
        if text_hash in self.seen_deals:
            result["is_duplicate"] = True
            result["reason"] = "Exact text match"
            
            # Get original deal details
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT created_at FROM seen_deals WHERE hash = ?", 
                    (text_hash,)
                )
                row = cursor.fetchone()
                if row:
                    result["created_at"] = row[0]
            
            return result
            
        # Check processed deal
        if processed_deal:
            deal_hash = processed_deal.get_hash()
            if deal_hash in self.seen_deals:
                result["is_duplicate"] = True
                result["reason"] = "Similar deal exists"
                
                # Get existing deal details
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT * FROM deals WHERE hash = ?", 
                        (deal_hash,)
                    )
                    row = cursor.fetchone()
                    if row:
                        result["existing_deal"] = Deal(
                            region=row[1],
                            partner=row[2],
                            geo=row[3],
                            language=row[4],
                            source=row[5],
                            model=row[6],
                            cpa=row[7],
                            crg=row[8],
                            cpl=row[9],
                            funnels=row[10].split('|'),
                            cr=row[11],
                            deduction_limit=row[12]
                        )
                        result["created_at"] = row[14]  # created_at column
                
        return result