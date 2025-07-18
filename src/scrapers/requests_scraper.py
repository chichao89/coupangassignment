import re
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings

logger = logging.getLogger(__name__)

class RequestsScraper(BaseScraper):
    """Requests-based scraper for static content"""
    
    def __init__(self, 
                 target_url: str,
                 product_selector: str,
                 field_selectors: Dict[str, str],
                 anti_bot: Optional[AntiBot] = None):
        super().__init__(target_url, anti_bot)
        self.product_selector = product_selector
        self.field_selectors = field_selectors
        self.session = requests.Session()
        self.current_page = 1
        self.base_url = f"{urlparse(target_url).scheme}://{urlparse(target_url).netloc}"
        
        # Setup session with default headers
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def make_request(self, url: str) -> requests.Response:
        """Make HTTP request with anti-bot measures"""
        return self.anti_bot.make_request(
            url, 
            session=self.session,
            timeout=settings.REQUEST_TIMEOUT
        )
    
    def extract_product_data(self, page_source: str) -> List[Dict[str, Any]]:
        """Extract product data from page source"""
        soup = BeautifulSoup(page_source, 'html.parser')
        products = []
        
        try:
            # Find all product containers
            product_elements = soup.select(self.product_selector)
            logger.info(f"Found {len(product_elements)} products on page {self.current_page}")
            
            for element in product_elements:
                product_data = {}
                
                # Extract each field
                for field_name, selector in self.field_selectors.items():
                    try:
                        field_element = element.select_one(selector)
                        if field_element:
                            # Get text content, handle different attributes
                            if field_name.lower() in ['image', 'img', 'photo']:
                                value = field_element.get('src') or field_element.get('data-src', '')
                                # Convert relative URLs to absolute
                                if value and not value.startswith('http'):
                                    value = urljoin(self.base_url, value)
                            elif field_name.lower() == 'link':
                                value = field_element.get('href', '')
                                # Convert relative URLs to absolute
                                if value and not value.startswith('http'):
                                    value = urljoin(self.base_url, value)
                            else:
                                value = field_element.get_text(strip=True)
                            
                            product_data[field_name] = value
                        else:
                            product_data[field_name] = ""
                            
                    except Exception as e:
                        logger.error(f"Error extracting {field_name}: {e}")
                        product_data[field_name] = ""
                
                # Add metadata
                product_data['page_number'] = self.current_page
                product_data['scraped_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
                product_data['source_url'] = self.current_url if hasattr(self, 'current_url') else self.target_url
                
                if any(product_data.values()):  # Only add if has some data
                    products.append(product_data)
            
        except Exception as e:
            logger.error(f"Error extracting products: {e}")
        
        return products
    
    def find_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find next page URL using various strategies"""
        # Strategy 1: Look for next button/link
        next_selectors = [
            "a[aria-label*='Next']",
            "a[class*='next']",
            ".pagination .next a",
            ".pagination a[rel='next']",
            "a:contains('Next')",
            "a:contains('→')",
            "a:contains('»')"
        ]
        
        for selector in next_selectors:
            try:
                if selector.endswith(")"):  # CSS :contains() selector
                    # Use text-based search for contains selectors
                    links = soup.find_all('a')
                    text_to_find = selector.split("'")[1]
                    for link in links:
                        if text_to_find.lower() in link.get_text().lower():
                            href = link.get('href')
                            if href:
                                return urljoin(self.base_url, href)
                else:
                    next_link = soup.select_one(selector)
                    if next_link:
                        href = next_link.get('href')
                        if href:
                            return urljoin(self.base_url, href)
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Strategy 2: Look for numbered pagination
        pagination_links = soup.select(".pagination a, .pager a, .page-numbers a")
        current_page_num = str(self.current_page)
        next_page_num = str(self.current_page + 1)
        
        for link in pagination_links:
            if link.get_text(strip=True) == next_page_num:
                href = link.get('href')
                if href:
                    return urljoin(self.base_url, href)
        
        # Strategy 3: URL pattern analysis
        if "page=" in current_url:
            # Replace page parameter
            new_url = re.sub(r'page=\d+', f'page={self.current_page + 1}', current_url)
            if new_url != current_url:
                return new_url
        elif "/page/" in current_url:
            # Replace page in path
            new_url = re.sub(r'/page/\d+', f'/page/{self.current_page + 1}', current_url)
            if new_url != current_url:
                return new_url
        else:
            # Add page parameter
            separator = "&" if "?" in current_url else "?"
            return f"{current_url}{separator}page={self.current_page + 1}"
        
        return None
    
    def handle_pagination(self) -> bool:
        """Handle pagination and return True if more pages exist"""
        try:
            response = self.make_request(self.current_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            next_url = self.find_next_page_url(soup, self.current_url)
            
            if next_url and next_url != self.current_url:
                # Test if next page exists and has content
                test_response = self.make_request(next_url)
                if test_response.status_code == 200:
                    test_soup = BeautifulSoup(test_response.text, 'html.parser')
                    test_products = test_soup.select(self.product_selector)
                    
                    if test_products:  # If products found on next page
                        self.current_url = next_url
                        self.current_page += 1
                        logger.info(f"Found next page: {next_url}")
                        return True
                    else:
                        logger.info("Next page exists but contains no products")
                        return False
                else:
                    logger.info(f"Next page returned status {test_response.status_code}")
                    return False
            
        except Exception as e:
            logger.error(f"Error in pagination: {e}")
        
        return False
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method"""
        try:
            logger.info(f"Starting scrape of {self.target_url}")
            self.current_url = self.target_url
            
            # Scrape first page
            response = self.make_request(self.current_url)
            response.raise_for_status()
            
            # Check for CAPTCHA
            if self.anti_bot.detect_captcha(response.text):
                logger.warning("CAPTCHA detected in response")
                return []
            
            products = self.extract_product_data(response.text)
            self.scraped_data.extend(products)
            
            # Handle pagination
            page_count = 1
            while page_count < settings.MAX_PAGES:
                if not self.handle_pagination():
                    logger.info("No more pages found")
                    break
                
                # Get new page content
                response = self.make_request(self.current_url)
                response.raise_for_status()
                
                # Extract data from new page
                products = self.extract_product_data(response.text)
                self.scraped_data.extend(products)
                page_count += 1
                
                # Apply rate limiting
                self.anti_bot.apply_rate_limiting()
            
            logger.info(f"Scraping completed. Total products: {len(self.scraped_data)}")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            self.session.close()
        
        return self.scraped_data