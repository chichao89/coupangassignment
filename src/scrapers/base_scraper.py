import json
import csv
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from src.utils.anti_bot import AntiBot
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, 
                 target_url: str,
                 anti_bot: Optional[AntiBot] = None,
                 output_dir: str = "output"):
        self.target_url = target_url
        self.anti_bot = anti_bot or AntiBot()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.scraped_data: List[Dict[str, Any]] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def extract_product_data(self, page_source: str) -> List[Dict[str, Any]]:
        """Extract product data from page source"""
        pass
    
    @abstractmethod
    def handle_pagination(self) -> bool:
        """Handle pagination and return True if more pages exist"""
        pass
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method"""
        pass
    
    def save_data(self, filename: Optional[str] = None) -> str:
        """Save scraped data to file"""
        if not self.scraped_data:
            logger.warning("No data to save")
            return ""
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        if settings.OUTPUT_FORMAT.lower() == "csv":
            filename = filename or f"scraped_data_{timestamp}.csv"
            filepath = self.output_dir / filename
            
            df = pd.DataFrame(self.scraped_data)
            df.to_csv(filepath, index=False)
            
        else:  # Default to JSON
            filename = filename or f"scraped_data_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filepath}")
        return str(filepath)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            "total_products": len(self.scraped_data),
            "target_url": self.target_url,
            "output_format": settings.OUTPUT_FORMAT,
            "unique_fields": list(set().union(*(d.keys() for d in self.scraped_data))) if self.scraped_data else []
        }
    
    def validate_data(self) -> bool:
        """Validate scraped data quality"""
        if not self.scraped_data:
            return False
        
        # Check if we have at least the minimum required products
        if len(self.scraped_data) < 50:
            logger.warning(f"Only {len(self.scraped_data)} products scraped, target was at least 50")
        
        # Check for empty records
        empty_records = sum(1 for item in self.scraped_data if not any(item.values()))
        if empty_records > 0:
            logger.warning(f"Found {empty_records} empty records")
        
        return True