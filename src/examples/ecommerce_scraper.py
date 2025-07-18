#!/usr/bin/env python3
"""
Example scraper for e-commerce websites
This demonstrates how to use the scraping framework with real-world configurations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.selenium_scraper import SeleniumScraper
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.scrapers.requests_scraper import RequestsScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Example configurations for different e-commerce sites
SITE_CONFIGS = {
    "books_toscrape": {
        "url": "http://books.toscrape.com/",
        "product_selector": "article.product_pod",
        "field_selectors": {
            "title": "h3 a",
            "price": "p.price_color",
            "availability": "p.instock.availability",
            "rating": ".star-rating",
            "image": ".image_container img",
            "link": "h3 a"
        },
        "scraper_type": "requests"  # Static site, no JS needed
    },
    
    "quotes_toscrape": {
        "url": "http://quotes.toscrape.com/",
        "product_selector": ".quote",
        "field_selectors": {
            "text": ".text",
            "author": ".author",
            "tags": ".tags a"
        },
        "scraper_type": "requests"
    },
    
    # Example for JS-heavy site (placeholder)
    "spa_example": {
        "url": "https://example-spa-site.com/products",
        "product_selector": ".product-card",
        "field_selectors": {
            "name": ".product-name",
            "price": ".price",
            "description": ".description",
            "image": ".product-image img",
            "brand": ".brand"
        },
        "scraper_type": "selenium"  # Needs JS execution
    }
}

class EcommerceScraper:
    """Main scraper class that orchestrates different scraping strategies"""
    
    def __init__(self, site_name: str, max_products: int = 50):
        self.site_name = site_name
        self.max_products = max_products
        self.config = SITE_CONFIGS.get(site_name)
        
        if not self.config:
            raise ValueError(f"Site '{site_name}' not configured. Available sites: {list(SITE_CONFIGS.keys())}")
        
        # Setup anti-bot measures
        self.anti_bot = AntiBot(
            min_delay=settings.MIN_DELAY,
            max_delay=settings.MAX_DELAY,
            rotate_user_agents=settings.ROTATE_USER_AGENTS
        )
    
    def create_scraper(self):
        """Create appropriate scraper based on site configuration"""
        scraper_type = self.config.get("scraper_type", "requests")
        
        if scraper_type == "selenium":
            return SeleniumScraper(
                target_url=self.config["url"],
                product_selector=self.config["product_selector"],
                field_selectors=self.config["field_selectors"],
                anti_bot=self.anti_bot
            )
        elif scraper_type == "playwright":
            return PlaywrightScraper(
                target_url=self.config["url"],
                product_selector=self.config["product_selector"],
                field_selectors=self.config["field_selectors"],
                anti_bot=self.anti_bot
            )
        else:  # Default to requests
            return RequestsScraper(
                target_url=self.config["url"],
                product_selector=self.config["product_selector"],
                field_selectors=self.config["field_selectors"],
                anti_bot=self.anti_bot
            )
    
    def run_scraping(self):
        """Execute the scraping process"""
        logger.info(f"Starting scraping for site: {self.site_name}")
        logger.info(f"Target: {self.config['url']}")
        logger.info(f"Scraper type: {self.config.get('scraper_type', 'requests')}")
        
        scraper = self.create_scraper()
        
        try:
            # Run scraping
            data = scraper.scrape()
            
            # Limit to max products if specified
            if self.max_products and len(data) > self.max_products:
                data = data[:self.max_products]
                scraper.scraped_data = data
            
            # Save results
            output_file = scraper.save_data(f"{self.site_name}_products")
            
            # Print statistics
            stats = scraper.get_stats()
            logger.info(f"Scraping completed successfully!")
            logger.info(f"Products scraped: {stats['total_products']}")
            logger.info(f"Output file: {output_file}")
            logger.info(f"Fields extracted: {stats['unique_fields']}")
            
            # Validate data quality
            scraper.validate_data()
            
            return data, output_file
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="E-commerce Web Scraper")
    parser.add_argument("site", choices=list(SITE_CONFIGS.keys()), 
                       help="Site to scrape")
    parser.add_argument("--max-products", type=int, default=50,
                       help="Maximum number of products to scrape")
    parser.add_argument("--output-format", choices=["json", "csv"], default="json",
                       help="Output format")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run browser in headless mode")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Update settings
    settings.OUTPUT_FORMAT = args.output_format
    settings.HEADLESS = args.headless
    
    try:
        # Create and run scraper
        scraper = EcommerceScraper(args.site, args.max_products)
        data, output_file = scraper.run_scraping()
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"📊 Products scraped: {len(data)}")
        print(f"📁 Output file: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())