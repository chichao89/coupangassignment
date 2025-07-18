import time
import logging
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from src.scrapers.base_scraper import BaseScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings

logger = logging.getLogger(__name__)

class SeleniumScraper(BaseScraper):
    """Selenium-based scraper for JavaScript-heavy sites"""
    
    def __init__(self, 
                 target_url: str,
                 product_selector: str,
                 field_selectors: Dict[str, str],
                 anti_bot: Optional[AntiBot] = None,
                 use_undetected: bool = True):
        super().__init__(target_url, anti_bot)
        self.product_selector = product_selector
        self.field_selectors = field_selectors
        self.use_undetected = use_undetected
        self.driver: Optional[webdriver.Chrome] = None
        self.current_page = 1
        
    def setup_driver(self):
        """Setup Chrome driver with anti-detection measures"""
        if self.use_undetected:
            options = uc.ChromeOptions()
        else:
            options = Options()
        
        # Basic options
        if settings.HEADLESS:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        user_agent = self.anti_bot.get_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        
        try:
            if self.use_undetected:
                self.driver = uc.Chrome(options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
                
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(10)
            
            logger.info("Chrome driver setup successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            logger.warning(f"Element not found: {selector}")
            return False
    
    def wait_for_dynamic_content(self, max_wait: int = 30):
        """Wait for dynamic content to load"""
        # Wait for JavaScript to finish loading
        WebDriverWait(self.driver, max_wait).until(
            lambda driver: driver.execute_script("return jQuery.active == 0") if 
            driver.execute_script("return typeof jQuery != 'undefined'") else True
        )
        
        # Additional wait for AJAX requests
        time.sleep(2)
    
    def extract_product_data(self, page_source: str = None) -> List[Dict[str, Any]]:
        """Extract product data from current page"""
        if page_source is None:
            page_source = self.driver.page_source
        
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
                            elif field_name.lower() == 'link':
                                value = field_element.get('href', '')
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
                
                if any(product_data.values()):  # Only add if has some data
                    products.append(product_data)
            
        except Exception as e:
            logger.error(f"Error extracting products: {e}")
        
        return products
    
    def handle_pagination(self) -> bool:
        """Handle pagination and return True if more pages exist"""
        try:
            # Try different pagination strategies
            next_button_selectors = [
                "a[aria-label*='Next']",
                "a[class*='next']",
                "button[class*='next']",
                ".pagination .next",
                "[data-testid*='next']",
                "a:contains('Next')",
                "a:contains('→')"
            ]
            
            for selector in next_button_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled() and next_button.is_displayed():
                        # Scroll to button
                        self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
                        time.sleep(1)
                        
                        # Click next button
                        next_button.click()
                        self.current_page += 1
                        
                        # Wait for new content to load
                        time.sleep(self.anti_bot.get_random_delay())
                        self.wait_for_dynamic_content()
                        
                        logger.info(f"Navigated to page {self.current_page}")
                        return True
                        
                except NoSuchElementException:
                    continue
                except Exception as e:
                    logger.error(f"Error clicking next button with selector {selector}: {e}")
                    continue
            
            # Try URL-based pagination
            current_url = self.driver.current_url
            if "page=" in current_url:
                new_url = current_url.replace(f"page={self.current_page-1}", f"page={self.current_page}")
            else:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}page={self.current_page}"
            
            if new_url != current_url:
                self.driver.get(new_url)
                self.wait_for_dynamic_content()
                logger.info(f"Navigated to page {self.current_page} via URL")
                return True
            
        except Exception as e:
            logger.error(f"Pagination handling failed: {e}")
        
        return False
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method"""
        try:
            self.setup_driver()
            
            # Navigate to target URL
            logger.info(f"Starting scrape of {self.target_url}")
            self.driver.get(self.target_url)
            
            # Check for CAPTCHA
            if self.anti_bot.handle_captcha_detection(self.driver):
                logger.warning("CAPTCHA detected and handled")
            
            # Wait for initial content
            self.wait_for_dynamic_content()
            
            # Scrape first page
            products = self.extract_product_data()
            self.scraped_data.extend(products)
            
            # Handle pagination
            page_count = 1
            while page_count < settings.MAX_PAGES:
                if not self.handle_pagination():
                    logger.info("No more pages found")
                    break
                
                # Extract data from new page
                products = self.extract_product_data()
                self.scraped_data.extend(products)
                page_count += 1
                
                # Apply rate limiting
                self.anti_bot.apply_rate_limiting()
            
            logger.info(f"Scraping completed. Total products: {len(self.scraped_data)}")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
        
        return self.scraped_data