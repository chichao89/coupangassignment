import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings

logger = logging.getLogger(__name__)

class PlaywrightScraper(BaseScraper):
    """Playwright-based scraper for modern web automation"""
    
    def __init__(self, 
                 target_url: str,
                 product_selector: str,
                 field_selectors: Dict[str, str],
                 anti_bot: Optional[AntiBot] = None):
        super().__init__(target_url, anti_bot)
        self.product_selector = product_selector
        self.field_selectors = field_selectors
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.current_page = 1
    
    async def setup_browser(self):
        """Setup Playwright browser with anti-detection measures"""
        try:
            playwright = await async_playwright().start()
            
            # Browser configuration
            self.browser = await playwright.chromium.launch(
                headless=settings.HEADLESS,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}"
                ]
            )
            
            # Create context with anti-detection
            context = await self.browser.new_context(
                user_agent=self.anti_bot.get_user_agent(),
                viewport={"width": settings.WINDOW_WIDTH, "height": settings.WINDOW_HEIGHT},
                java_script_enabled=True
            )
            
            # Create page
            self.page = await context.new_page()
            
            # Remove webdriver traces
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            # Set timeouts
            self.page.set_default_timeout(settings.PAGE_LOAD_TIMEOUT * 1000)
            
            logger.info("Playwright browser setup successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Playwright browser: {e}")
            raise
    
    async def wait_for_dynamic_content(self, max_wait: int = 30):
        """Wait for dynamic content to load"""
        try:
            # Wait for network to be idle
            await self.page.wait_for_load_state("networkidle", timeout=max_wait * 1000)
            
            # Additional wait for any remaining JavaScript
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.warning(f"Timeout waiting for dynamic content: {e}")
    
    async def extract_product_data(self, page_source: str = None) -> List[Dict[str, Any]]:
        """Extract product data from current page"""
        if page_source is None:
            page_source = await self.page.content()
        
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
    
    async def handle_pagination(self) -> bool:
        """Handle pagination and return True if more pages exist"""
        try:
            # Try different pagination strategies
            next_button_selectors = [
                "a[aria-label*='Next']",
                "a[class*='next']",
                "button[class*='next']",
                ".pagination .next",
                "[data-testid*='next']"
            ]
            
            for selector in next_button_selectors:
                try:
                    # Check if element exists and is visible
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible() and await element.is_enabled():
                        # Scroll to element
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(1)
                        
                        # Click next button
                        await element.click()
                        self.current_page += 1
                        
                        # Wait for new content
                        await asyncio.sleep(self.anti_bot.get_random_delay())
                        await self.wait_for_dynamic_content()
                        
                        logger.info(f"Navigated to page {self.current_page}")
                        return True
                        
                except Exception as e:
                    logger.error(f"Error with selector {selector}: {e}")
                    continue
            
            # Try URL-based pagination
            current_url = self.page.url
            if "page=" in current_url:
                new_url = current_url.replace(f"page={self.current_page-1}", f"page={self.current_page}")
            else:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}page={self.current_page}"
            
            if new_url != current_url:
                await self.page.goto(new_url)
                await self.wait_for_dynamic_content()
                logger.info(f"Navigated to page {self.current_page} via URL")
                return True
            
        except Exception as e:
            logger.error(f"Pagination handling failed: {e}")
        
        return False
    
    async def scrape_async(self) -> List[Dict[str, Any]]:
        """Async scraping method"""
        try:
            await self.setup_browser()
            
            # Navigate to target URL
            logger.info(f"Starting scrape of {self.target_url}")
            await self.page.goto(self.target_url, wait_until="networkidle")
            
            # Check for CAPTCHA indicators
            page_content = await self.page.content()
            if self.anti_bot.detect_captcha(page_content):
                logger.warning("CAPTCHA detected. Manual intervention may be required.")
                await asyncio.sleep(60)  # Wait for manual intervention
            
            # Wait for initial content
            await self.wait_for_dynamic_content()
            
            # Scrape first page
            products = await self.extract_product_data()
            self.scraped_data.extend(products)
            
            # Handle pagination
            page_count = 1
            while page_count < settings.MAX_PAGES:
                if not await self.handle_pagination():
                    logger.info("No more pages found")
                    break
                
                # Extract data from new page
                products = await self.extract_product_data()
                self.scraped_data.extend(products)
                page_count += 1
                
                # Apply rate limiting
                await asyncio.sleep(self.anti_bot.get_random_delay())
            
            logger.info(f"Scraping completed. Total products: {len(self.scraped_data)}")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            if self.browser:
                await self.browser.close()
        
        return self.scraped_data
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method (sync wrapper)"""
        return asyncio.run(self.scrape_async())