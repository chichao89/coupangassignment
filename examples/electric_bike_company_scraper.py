#!/usr/bin/env python3
"""
Electric Bike Company Scraper - Real World Example
This demonstrates scraping the actual https://electricbikecompany.com website
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.selenium_scraper import SeleniumScraper
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings
import logging
import json

logger = logging.getLogger(__name__)

# Electric Bike Company website configuration
EBC_CONFIG = {
    "base_url": "https://electricbikecompany.com",
    "shop_url": "https://electricbikecompany.com/shop/categories/e-bikes",
    
    # Main product grid selector (this is a React/Next.js app)
    "product_selector": '[data-testid="product-card"], .product-item, .product-card',
    
    # Field selectors for product information
    "field_selectors": {
        "name": "h2, h3, .product-title, .product-name, [data-testid='product-title']",
        "price": ".price, .product-price, [data-testid='price']",
        "description": ".product-description, .description, p",
        "image": "img",
        "link": "a",
        "sku": ".sku, [data-testid='sku']",
        "availability": ".availability, .stock-status, [data-testid='availability']"
    },
    
    # Pagination selectors
    "pagination_selectors": [
        "[aria-label*='Next']",
        ".next, .pagination-next",
        "[data-testid='next-page']",
        "a:contains('Next')",
        "button:contains('Next')"
    ],
    
    # Category pages to scrape
    "category_urls": [
        "https://electricbikecompany.com/shop/categories/e-bikes",
        "https://electricbikecompany.com/shop/categories/model-j",
        "https://electricbikecompany.com/shop/categories/model-r", 
        "https://electricbikecompany.com/shop/categories/model-c",
        "https://electricbikecompany.com/shop/categories/model-s",
        "https://electricbikecompany.com/shop/categories/parts-accessories"
    ]
}

class ElectricBikeCompanyScraper:
    """Specialized scraper for Electric Bike Company website"""
    
    def __init__(self, scraper_type="selenium", max_products=50):
        self.scraper_type = scraper_type
        self.max_products = max_products
        
        # Configure anti-bot measures for this specific site
        self.anti_bot = AntiBot(
            min_delay=2.0,  # Be respectful to EBC servers
            max_delay=5.0,
            rotate_user_agents=True
        )
        
        # Update settings for this site
        settings.HEADLESS = True  # Use headless mode
        settings.PAGE_LOAD_TIMEOUT = 45  # Longer timeout for React apps
        settings.MAX_PAGES = 5  # Limit pages for demo
        
    def create_scraper(self, target_url):
        """Create appropriate scraper for EBC website"""
        if self.scraper_type == "playwright":
            return PlaywrightScraper(
                target_url=target_url,
                product_selector=EBC_CONFIG["product_selector"],
                field_selectors=EBC_CONFIG["field_selectors"],
                anti_bot=self.anti_bot
            )
        else:  # Default to Selenium for React apps
            return SeleniumScraper(
                target_url=target_url,
                product_selector=EBC_CONFIG["product_selector"],
                field_selectors=EBC_CONFIG["field_selectors"],
                anti_bot=self.anti_bot,
                use_undetected=True  # Use undetected Chrome for better success
            )
    
    def scrape_category(self, category_url):
        """Scrape a specific category page"""
        logger.info(f"Starting scrape of category: {category_url}")
        
        scraper = self.create_scraper(category_url)
        
        try:
            products = scraper.scrape()
            logger.info(f"Scraped {len(products)} products from {category_url}")
            return products
        except Exception as e:
            logger.error(f"Failed to scrape {category_url}: {e}")
            return []
    
    def scrape_all_categories(self):
        """Scrape all configured categories"""
        all_products = []
        
        for category_url in EBC_CONFIG["category_urls"]:
            if len(all_products) >= self.max_products:
                break
                
            products = self.scrape_category(category_url)
            all_products.extend(products)
            
            # Limit total products
            if len(all_products) > self.max_products:
                all_products = all_products[:self.max_products]
                break
        
        return all_products
    
    def scrape_single_product(self, product_url):
        """Scrape a single product page for detailed information"""
        logger.info(f"Scraping single product: {product_url}")
        
        # For single product pages, we need different selectors
        product_selectors = {
            "name": "h1, .product-title",
            "price": ".price, .product-price",
            "description": ".product-description, .description",
            "features": ".features li, .specs li",
            "images": ".product-gallery img, .product-images img",
            "sku": ".sku",
            "availability": ".stock-status, .availability"
        }
        
        scraper = self.create_scraper(product_url)
        scraper.field_selectors = product_selectors
        scraper.product_selector = ".product-details, .product-info, main"
        
        try:
            products = scraper.scrape()
            return products[0] if products else {}
        except Exception as e:
            logger.error(f"Failed to scrape product {product_url}: {e}")
            return {}

def demonstrate_ebc_scraping():
    """Demonstrate scraping Electric Bike Company website"""
    print("🚲 ELECTRIC BIKE COMPANY WEBSITE SCRAPER")
    print("=" * 60)
    print("Target: https://electricbikecompany.com")
    print("This demonstrates real-world scraping with our framework")
    print()
    
    # Create scraper instance
    ebc_scraper = ElectricBikeCompanyScraper(
        scraper_type="selenium",  # Use Selenium for React/JS-heavy site
        max_products=20  # Limit for demo
    )
    
    # Example 1: Scrape the specific product page provided
    print("📋 Example 1: Scraping Specific Product")
    print("-" * 40)
    product_url = "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer"
    product_data = ebc_scraper.scrape_single_product(product_url)
    
    if product_data:
        print(f"✅ Successfully scraped product:")
        print(f"   • Name: {product_data.get('name', 'N/A')}")
        print(f"   • Price: {product_data.get('price', 'N/A')}")
        print(f"   • Description: {product_data.get('description', 'N/A')[:100]}...")
    else:
        print("❌ Failed to scrape product")
    
    print()
    
    # Example 2: Scrape product category
    print("📋 Example 2: Scraping Product Category")
    print("-" * 40)
    category_products = ebc_scraper.scrape_category(
        "https://electricbikecompany.com/shop/categories/model-j"
    )
    
    print(f"✅ Scraped {len(category_products)} products from Model J category")
    for i, product in enumerate(category_products[:3]):  # Show first 3
        print(f"   {i+1}. {product.get('name', 'Unknown')}")
    
    # Save results
    import json
    from pathlib import Path
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save single product
    if product_data:
        with open(output_dir / "ebc_single_product.json", 'w') as f:
            json.dump(product_data, f, indent=2)
    
    # Save category products  
    if category_products:
        with open(output_dir / "ebc_category_products.json", 'w') as f:
            json.dump(category_products, f, indent=2)
    
    print(f"\n💾 Results saved to output/ directory")
    print(f"📊 Total products processed: {len(category_products) + (1 if product_data else 0)}")

def main():
    """Main function for running EBC scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Electric Bike Company Website Scraper")
    parser.add_argument("--url", default="https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer",
                       help="Specific product URL to scrape")
    parser.add_argument("--category", help="Category URL to scrape")
    parser.add_argument("--scraper-type", choices=["selenium", "playwright"], default="selenium",
                       help="Scraper engine to use")
    parser.add_argument("--max-products", type=int, default=20,
                       help="Maximum products to scrape")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        if args.category:
            # Scrape specific category
            ebc_scraper = ElectricBikeCompanyScraper(args.scraper_type, args.max_products)
            products = ebc_scraper.scrape_category(args.category)
            print(f"✅ Scraped {len(products)} products from category")
            
        elif args.url:
            # Scrape specific product
            ebc_scraper = ElectricBikeCompanyScraper(args.scraper_type, args.max_products)
            product = ebc_scraper.scrape_single_product(args.url)
            if product:
                print(f"✅ Successfully scraped product: {product.get('name', 'Unknown')}")
            else:
                print("❌ Failed to scrape product")
        else:
            # Run full demonstration
            demonstrate_ebc_scraping()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())