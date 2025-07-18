import random
import time
import asyncio
from typing import List, Optional, Dict, Any
from fake_useragent import UserAgent
import requests
from retrying import retry
import logging

logger = logging.getLogger(__name__)

class AntiBot:
    """Anti-bot detection and mitigation utilities"""
    
    def __init__(self, 
                 min_delay: float = 1.0,
                 max_delay: float = 5.0,
                 proxy_list: Optional[List[str]] = None,
                 rotate_user_agents: bool = True):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.proxy_list = proxy_list or []
        self.rotate_user_agents = rotate_user_agents
        self.ua = UserAgent() if rotate_user_agents else None
        self.current_proxy_index = 0
        self.request_count = 0
        self.last_request_time = 0
        
    def get_random_delay(self) -> float:
        """Generate a random delay between min and max delay"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_user_agent(self) -> str:
        """Get a random user agent"""
        if self.rotate_user_agents and self.ua:
            return self.ua.random
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from rotation"""
        if not self.proxy_list:
            return None
        
        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        
        return {
            "http": proxy,
            "https": proxy
        }
    
    def apply_rate_limiting(self):
        """Apply intelligent rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Increase delay based on request count
        if self.request_count > 10:
            self.min_delay = min(self.min_delay * 1.1, 10.0)
        
        delay = self.get_random_delay()
        
        if time_since_last_request < delay:
            sleep_time = delay - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def make_request(self, url: str, **kwargs) -> requests.Response:
        """Make a request with anti-bot measures"""
        self.apply_rate_limiting()
        
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = self.get_user_agent()
        kwargs['headers'] = headers
        
        proxy = self.get_proxy()
        if proxy:
            kwargs['proxies'] = proxy
        
        try:
            response = requests.get(url, **kwargs)
            
            # Handle rate limiting responses
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    sleep_time = int(retry_after)
                    logger.warning(f"Rate limited. Sleeping for {sleep_time} seconds")
                    time.sleep(sleep_time)
                raise Exception("Rate limited")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def detect_captcha(self, page_source: str) -> bool:
        """Detect if page contains CAPTCHA"""
        captcha_indicators = [
            "captcha", "recaptcha", "hcaptcha", 
            "robot", "verify", "security check",
            "cloudflare", "distil", "incapsula"
        ]
        
        page_lower = page_source.lower()
        return any(indicator in page_lower for indicator in captcha_indicators)
    
    def handle_captcha_detection(self, driver, max_wait: int = 60):
        """Handle CAPTCHA detection by waiting or alerting"""
        if self.detect_captcha(driver.page_source):
            logger.warning("CAPTCHA detected. Manual intervention may be required.")
            # In a real scenario, you might implement CAPTCHA solving services
            time.sleep(max_wait)
            return True
        return False