#!/usr/bin/env python3
"""
Web Automation Framework - Demonstration Script
This script demonstrates the framework capabilities without requiring external dependencies
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urljoin

class MockResponse:
    """Mock HTTP response for demonstration"""
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code
        self.headers = {}

class DemoAntiBot:
    """Demonstration anti-bot utilities"""
    
    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.request_count = 0
    
    def get_user_agent(self) -> str:
        """Get a demo user agent"""
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    def apply_rate_limiting(self):
        """Apply demo rate limiting"""
        delay = (self.min_delay + self.max_delay) / 2
        print(f"⏳ Applying rate limiting: {delay:.1f}s delay")
        time.sleep(0.1)  # Short delay for demo
        self.request_count += 1
    
    def detect_captcha(self, page_source: str) -> bool:
        """Detect CAPTCHA in demo content"""
        return "captcha" in page_source.lower()

class DemoScraper:
    """Demonstration scraper class"""
    
    def __init__(self, target_url: str, product_selector: str, field_selectors: Dict[str, str]):
        self.target_url = target_url
        self.product_selector = product_selector
        self.field_selectors = field_selectors
        self.anti_bot = DemoAntiBot()
        self.scraped_data: List[Dict[str, Any]] = []
        self.current_page = 1
    
    def extract_product_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract product data from HTML (simulated)"""
        products = []
        
        # Simulate finding products with regex (simplified for demo)
        if "books.toscrape.com" in self.target_url:
            # Demo data for books site
            demo_products = [
                {
                    "title": "A Light in the Attic",
                    "price": "£51.77",
                    "availability": "In stock",
                    "rating": "Three",
                    "image": "http://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"
                },
                {
                    "title": "Tipping the Velvet",
                    "price": "£53.74",
                    "availability": "In stock", 
                    "rating": "One",
                    "image": "http://books.toscrape.com/media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg"
                },
                {
                    "title": "Soumission",
                    "price": "£50.10",
                    "availability": "In stock",
                    "rating": "One", 
                    "image": "http://books.toscrape.com/media/cache/3e/ef/3eef99c9d9adef34639f510662022830.jpg"
                }
            ]
        elif "quotes.toscrape.com" in self.target_url:
            # Demo data for quotes site
                         demo_products = [
                 {
                     "text": "The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.",
                     "author": "Albert Einstein",
                     "tags": "change,deep-thoughts,thinking,world"
                 },
                 {
                     "text": "It is our choices, Harry, that show what we truly are, far more than our abilities.",
                     "author": "J.K. Rowling",
                     "tags": "abilities,choices"
                 },
                 {
                     "text": "There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle.",
                     "author": "Albert Einstein", 
                     "tags": "inspirational,life,live,miracle,miracles"
                 }
             ]
        else:
            # Generic demo data
            demo_products = [
                {
                    "name": "Product 1",
                    "price": "$19.99",
                    "description": "High quality product"
                },
                {
                    "name": "Product 2", 
                    "price": "$29.99",
                    "description": "Premium product"
                }
            ]
        
        # Add metadata to products
        for i, product in enumerate(demo_products[:min(len(demo_products), 5)]):  # Limit to 5 for demo
            product['page_number'] = self.current_page
            product['scraped_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
            product['source_url'] = self.target_url
            products.append(product)
        
        print(f"📦 Extracted {len(products)} products from page {self.current_page}")
        return products
    
    def handle_pagination(self) -> bool:
        """Handle pagination (simulated)"""
        # Simulate pagination for demo
        if self.current_page < 3:  # Demo: stop after 3 pages
            self.current_page += 1
            print(f"🔄 Navigating to page {self.current_page}")
            return True
        return False
    
    def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method"""
        print(f"🚀 Starting demo scrape of {self.target_url}")
        print(f"🎯 Product selector: {self.product_selector}")
        print(f"🏷️  Field selectors: {self.field_selectors}")
        print("-" * 60)
        
        # Simulate first page
        products = self.extract_product_data("")
        self.scraped_data.extend(products)
        self.anti_bot.apply_rate_limiting()
        
        # Simulate pagination
        page_count = 1
        while page_count < 3:  # Demo: limit to 3 pages
            if not self.handle_pagination():
                break
            
            products = self.extract_product_data("")
            self.scraped_data.extend(products)
            self.anti_bot.apply_rate_limiting()
            page_count += 1
        
        print(f"✅ Demo scraping completed! Total products: {len(self.scraped_data)}")
        return self.scraped_data
    
    def save_data(self, filename: str = None) -> str:
        """Save scraped data to file"""
        if not self.scraped_data:
            print("⚠️  No data to save")
            return ""
        
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = filename or f"demo_scraped_data_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Data saved to {filepath}")
        return str(filepath)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            "total_products": len(self.scraped_data),
            "target_url": self.target_url,
            "pages_scraped": self.current_page,
            "anti_bot_requests": self.anti_bot.request_count,
            "unique_fields": list(set().union(*(d.keys() for d in self.scraped_data))) if self.scraped_data else []
        }

def demo_books_scraper():
    """Demonstrate scraping books.toscrape.com"""
    print("📚 DEMO: Books.toscrape.com Scraper")
    print("=" * 60)
    
    scraper = DemoScraper(
        target_url="http://books.toscrape.com/",
        product_selector="article.product_pod",
        field_selectors={
            "title": "h3 a",
            "price": "p.price_color",
            "availability": "p.instock.availability",
            "rating": ".star-rating",
            "image": ".image_container img"
        }
    )
    
    # Run scraping
    data = scraper.scrape()
    
    # Save results
    output_file = scraper.save_data("books_demo.json")
    
    # Show statistics
    stats = scraper.get_stats()
    print(f"\n📊 SCRAPING STATISTICS:")
    print(f"   • Products scraped: {stats['total_products']}")
    print(f"   • Pages processed: {stats['pages_scraped']}")
    print(f"   • Requests made: {stats['anti_bot_requests']}")
    print(f"   • Fields extracted: {', '.join(stats['unique_fields'])}")
    
    return data, output_file

def demo_quotes_scraper():
    """Demonstrate scraping quotes.toscrape.com"""
    print("\n💬 DEMO: Quotes.toscrape.com Scraper")
    print("=" * 60)
    
    scraper = DemoScraper(
        target_url="http://quotes.toscrape.com/",
        product_selector=".quote",
        field_selectors={
            "text": ".text",
            "author": ".author",
            "tags": ".tags a"
        }
    )
    
    # Run scraping
    data = scraper.scrape()
    
    # Save results
    output_file = scraper.save_data("quotes_demo.json")
    
    # Show statistics
    stats = scraper.get_stats()
    print(f"\n📊 SCRAPING STATISTICS:")
    print(f"   • Quotes scraped: {stats['total_products']}")
    print(f"   • Pages processed: {stats['pages_scraped']}")
    print(f"   • Requests made: {stats['anti_bot_requests']}")
    print(f"   • Fields extracted: {', '.join(stats['unique_fields'])}")
    
    return data, output_file

def demo_anti_bot_features():
    """Demonstrate anti-bot capabilities"""
    print("\n🛡️  DEMO: Anti-Bot Features")
    print("=" * 60)
    
    anti_bot = DemoAntiBot()
    
    print(f"🔄 User Agent: {anti_bot.get_user_agent()[:50]}...")
    print(f"⏱️  Rate Limiting: {anti_bot.min_delay}-{anti_bot.max_delay}s delays")
    
    # Demo CAPTCHA detection
    normal_content = "<html><body>Welcome to our site</body></html>"
    captcha_content = "<html><body>Please solve this CAPTCHA</body></html>"
    
    print(f"🔍 CAPTCHA Detection:")
    print(f"   • Normal content: {anti_bot.detect_captcha(normal_content)}")
    print(f"   • CAPTCHA content: {anti_bot.detect_captcha(captcha_content)}")

def demo_framework_architecture():
    """Demonstrate framework architecture and features"""
    print("🏗️  WEB AUTOMATION FRAMEWORK ARCHITECTURE")
    print("=" * 80)
    
    print("""
📁 Project Structure:
├── config/                 # Configuration management
│   └── settings.py        # Centralized settings with Pydantic
├── src/
│   ├── scrapers/          # Scraper implementations
│   │   ├── base_scraper.py      # Abstract base class
│   │   ├── requests_scraper.py  # Fast, lightweight scraper
│   │   ├── selenium_scraper.py  # Full browser automation
│   │   └── playwright_scraper.py # Modern async automation
│   ├── utils/             # Utility modules
│   │   └── anti_bot.py    # Anti-bot detection & mitigation
│   └── examples/          # Pre-configured site examples
│       └── ecommerce_scraper.py
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation
├── main.py               # CLI entry point
└── requirements.txt      # Dependencies

🚀 Key Features:
✅ Multi-Engine Support (Requests, Selenium, Playwright)
✅ Advanced Anti-Bot Protection
✅ Intelligent Pagination Handling  
✅ Dynamic Content Support
✅ Configurable Output (JSON/CSV)
✅ Robust Error Handling
✅ Comprehensive Logging
✅ Production-Ready Design
""")

def main():
    """Main demonstration function"""
    print("🕷️  WEB AUTOMATION FRAMEWORK DEMONSTRATION")
    print("=" * 80)
    print("This demo shows the framework capabilities without external dependencies")
    print()
    
    # Show architecture
    demo_framework_architecture()
    
    # Demo anti-bot features
    demo_anti_bot_features()
    
    # Demo scrapers
    books_data, books_file = demo_books_scraper()
    quotes_data, quotes_file = demo_quotes_scraper()
    
    print(f"\n🎉 DEMONSTRATION COMPLETED!")
    print("=" * 60)
    print(f"📚 Books data: {books_file}")
    print(f"💬 Quotes data: {quotes_file}")
    print(f"\n📖 To use the full framework:")
    print(f"   1. Install dependencies: pip install -r requirements.txt")
    print(f"   2. Run real scraper: python main.py example books_toscrape")
    print(f"   3. Custom scraping: python main.py custom <url> --product-selector '.product'")
    print(f"\n📚 Documentation: docs/REPORT.md")
    print(f"🧪 Tests: python -m pytest tests/")

if __name__ == "__main__":
    main()