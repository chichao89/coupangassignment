import os
from typing import List, Dict, Any
from pydantic import BaseSettings

class ScraperSettings(BaseSettings):
    """Configuration settings for the web scraper"""
    
    # Rate limiting settings
    MIN_DELAY: float = 1.0
    MAX_DELAY: float = 5.0
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    BACKOFF_FACTOR: float = 1.5
    
    # Browser settings
    HEADLESS: bool = True
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080
    PAGE_LOAD_TIMEOUT: int = 30
    
    # Anti-bot settings
    ROTATE_USER_AGENTS: bool = True
    USE_PROXY_ROTATION: bool = False
    PROXY_LIST: List[str] = []
    
    # Output settings
    OUTPUT_DIR: str = "output"
    OUTPUT_FORMAT: str = "json"  # json or csv
    
    # Pagination settings
    MAX_PAGES: int = 10
    PAGINATION_SELECTOR: str = ""
    NEXT_BUTTON_SELECTOR: str = ""
    
    # Target website settings
    TARGET_URL: str = ""
    PRODUCT_SELECTOR: str = ""
    FIELDS_TO_EXTRACT: Dict[str, str] = {}
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = ScraperSettings()