#!/usr/bin/env python3
"""
Web Automation Framework - Main Entry Point
This script provides a command-line interface for running web scrapers
with various anti-bot and pagination handling capabilities.
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.examples.ecommerce_scraper import EcommerceScraper, SITE_CONFIGS
from src.scrapers.selenium_scraper import SeleniumScraper
from src.scrapers.playwright_scraper import PlaywrightScraper
from src.scrapers.requests_scraper import RequestsScraper
from src.utils.anti_bot import AntiBot
from config.settings import settings

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('scraper.log')
        ]
    )

def run_example_scraper(args):
    """Run one of the preconfigured example scrapers"""
    print(f"🚀 Running example scraper for: {args.site}")
    print(f"📊 Target products: {args.max_products}")
    print(f"📝 Output format: {args.output_format}")
    print("-" * 50)
    
    # Update settings
    settings.OUTPUT_FORMAT = args.output_format
    settings.HEADLESS = args.headless
    settings.MAX_PAGES = args.max_pages
    
    scraper = EcommerceScraper(args.site, args.max_products)
    data, output_file = scraper.run_scraping()
    
    print(f"\n✅ Scraping completed!")
    print(f"📊 Products scraped: {len(data)}")
    print(f"📁 Output saved to: {output_file}")

def run_custom_scraper(args):
    """Run a custom scraper with user-provided configuration"""
    print(f"🚀 Running custom scraper for: {args.url}")
    print(f"🎯 Product selector: {args.product_selector}")
    print(f"📊 Max products: {args.max_products}")
    print("-" * 50)
    
    # Parse field selectors
    field_selectors = {}
    if args.fields:
        for field_def in args.fields:
            if ":" in field_def:
                field_name, selector = field_def.split(":", 1)
                field_selectors[field_name.strip()] = selector.strip()
    
    if not field_selectors:
        print("⚠️  No field selectors provided. Using default fields.")
        field_selectors = {
            "title": "h1, h2, h3, .title, .name",
            "price": ".price, .cost, .amount",
            "description": ".description, .desc, p"
        }
    
    # Setup anti-bot
    anti_bot = AntiBot(
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        rotate_user_agents=not args.no_user_agent_rotation
    )
    
    # Create scraper based on type
    if args.scraper_type == "selenium":
        scraper = SeleniumScraper(
            target_url=args.url,
            product_selector=args.product_selector,
            field_selectors=field_selectors,
            anti_bot=anti_bot
        )
    elif args.scraper_type == "playwright":
        scraper = PlaywrightScraper(
            target_url=args.url,
            product_selector=args.product_selector,
            field_selectors=field_selectors,
            anti_bot=anti_bot
        )
    else:  # requests
        scraper = RequestsScraper(
            target_url=args.url,
            product_selector=args.product_selector,
            field_selectors=field_selectors,
            anti_bot=anti_bot
        )
    
    # Update settings
    settings.OUTPUT_FORMAT = args.output_format
    settings.HEADLESS = args.headless
    settings.MAX_PAGES = args.max_pages
    
    # Run scraping
    data = scraper.scrape()
    
    # Limit results if specified
    if args.max_products and len(data) > args.max_products:
        data = data[:args.max_products]
        scraper.scraped_data = data
    
    # Save results
    output_file = scraper.save_data()
    
    # Print results
    stats = scraper.get_stats()
    print(f"\n✅ Scraping completed!")
    print(f"📊 Products scraped: {stats['total_products']}")
    print(f"📁 Output saved to: {output_file}")
    print(f"🏷️  Fields extracted: {', '.join(stats['unique_fields'])}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Web Automation Framework - Advanced Web Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run example scraper
  python main.py example books_toscrape --max-products 100

  # Run custom scraper
  python main.py custom https://example.com \
    --product-selector ".product" \
    --fields "name:.product-name" "price:.price" \
    --scraper-type selenium

  # List available example sites
  python main.py example --list
        """
    )
    
    # Global options
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--output-format", choices=["json", "csv"], default="json",
                       help="Output format (default: json)")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run browser in headless mode (default: True)")
    parser.add_argument("--max-pages", type=int, default=10,
                       help="Maximum pages to scrape (default: 10)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Example scraper command
    example_parser = subparsers.add_parser("example", help="Run preconfigured example scrapers")
    example_parser.add_argument("site", nargs="?", choices=list(SITE_CONFIGS.keys()),
                               help="Site to scrape")
    example_parser.add_argument("--list", action="store_true",
                               help="List available example sites")
    example_parser.add_argument("--max-products", type=int, default=50,
                               help="Maximum products to scrape (default: 50)")
    
    # Custom scraper command
    custom_parser = subparsers.add_parser("custom", help="Run custom scraper")
    custom_parser.add_argument("url", help="Target URL to scrape")
    custom_parser.add_argument("--product-selector", required=True,
                              help="CSS selector for product containers")
    custom_parser.add_argument("--fields", nargs="*",
                              help="Field definitions in format 'name:selector'")
    custom_parser.add_argument("--scraper-type", choices=["requests", "selenium", "playwright"],
                              default="requests", help="Scraper type (default: requests)")
    custom_parser.add_argument("--max-products", type=int,
                              help="Maximum products to scrape")
    custom_parser.add_argument("--min-delay", type=float, default=1.0,
                              help="Minimum delay between requests (default: 1.0)")
    custom_parser.add_argument("--max-delay", type=float, default=5.0,
                              help="Maximum delay between requests (default: 5.0)")
    custom_parser.add_argument("--no-user-agent-rotation", action="store_true",
                              help="Disable user agent rotation")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "example":
            if args.list:
                print("Available example sites:")
                for site, config in SITE_CONFIGS.items():
                    print(f"  • {site}: {config['url']}")
                return 0
            
            if not args.site:
                print("Error: Site name required for example command")
                example_parser.print_help()
                return 1
            
            run_example_scraper(args)
            
        elif args.command == "custom":
            run_custom_scraper(args)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())