# Web Automation Framework

A comprehensive web scraping framework designed for extracting structured data from websites while handling modern challenges like anti-bot detection, pagination, and dynamic content.

## 🚀 Features

- **Multi-Engine Support**: Choose from Requests, Selenium, or Playwright based on your needs
- **Advanced Anti-Bot Protection**: User agent rotation, rate limiting, proxy support, and CAPTCHA detection
- **Intelligent Pagination**: Automatically handles different pagination styles (buttons, links, URL patterns)
- **Dynamic Content Handling**: Full JavaScript execution and AJAX request management
- **Configurable Output**: Export data in JSON or CSV format with comprehensive metadata
- **Robust Error Handling**: Retry mechanisms, exponential backoff, and graceful failure recovery
- **Production Ready**: Comprehensive logging, statistics, and monitoring capabilities

## 📋 Requirements

- Python 3.8+
- Chrome/Chromium browser (for Selenium/Playwright)
- Internet connection

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd web-automation-framework
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Browser Dependencies (for Selenium/Playwright)
```bash
# For Playwright (recommended for modern sites)
python install_playwright.py

# For Selenium (alternative)
# Chrome/Chromium will be downloaded automatically by undetected-chromedriver
```

### 4. Verify Installation
```bash
python main.py example --list
```

## 🎯 Quick Start

### Example 1: Scrape Books (Static Site)
```bash
# Scrape books using fast requests-based scraper
python main.py example books_toscrape --max-products 100
```

### Example 2: Scrape Quotes (Static Site)  
```bash
# Scrape quotes with pagination
python main.py example quotes_toscrape --max-products 50 --output-format csv
```

### Example 3: Custom Scraper for Any Site
```bash
# Scrape a custom e-commerce site
python main.py custom https://example-shop.com/products \
  --product-selector ".product-item" \
  --fields "name:.product-title" "price:.price" "image:.product-img img" \
  --scraper-type selenium \
  --max-products 100
```

## 📖 Usage Guide

### Command Line Interface

#### Basic Commands
```bash
# List available example scrapers
python main.py example --list

# Run example scraper
python main.py example <site_name> [options]

# Run custom scraper
python main.py custom <url> --product-selector <selector> [options]
```

#### Global Options
- `--verbose, -v`: Enable debug logging
- `--output-format {json,csv}`: Output format (default: json)
- `--headless`: Run browser in headless mode (default: True)
- `--max-pages <int>`: Maximum pages to scrape (default: 10)

#### Custom Scraper Options
- `--product-selector <css>`: CSS selector for product containers (required)
- `--fields <name:selector>`: Field definitions (e.g., "name:.title" "price:.cost")
- `--scraper-type {requests,selenium,playwright}`: Scraper engine (default: requests)
- `--max-products <int>`: Maximum products to scrape
- `--min-delay <float>`: Minimum delay between requests (default: 1.0)
- `--max-delay <float>`: Maximum delay between requests (default: 5.0)
- `--no-user-agent-rotation`: Disable user agent rotation

### Programming Interface

#### Basic Usage
```python
from src.scrapers.selenium_scraper import SeleniumScraper
from src.utils.anti_bot import AntiBot

# Configure anti-bot measures
anti_bot = AntiBot(
    min_delay=1.0,
    max_delay=3.0,
    rotate_user_agents=True
)

# Create scraper
scraper = SeleniumScraper(
    target_url="https://example.com/products",
    product_selector=".product",
    field_selectors={
        "name": ".product-name",
        "price": ".price",
        "description": ".description"
    },
    anti_bot=anti_bot
)

# Run scraping
data = scraper.scrape()

# Save results
output_file = scraper.save_data()
print(f"Scraped {len(data)} products to {output_file}")
```

#### Advanced Configuration
```python
from config.settings import settings

# Customize settings
settings.HEADLESS = False  # Show browser
settings.MAX_PAGES = 5     # Limit pages
settings.OUTPUT_FORMAT = "csv"
settings.REQUEST_TIMEOUT = 60

# Use with proxy rotation
anti_bot = AntiBot(
    proxy_list=[
        "proxy1.example.com:8080",
        "proxy2.example.com:8080"
    ]
)
```

## 🏗️ Architecture

### Core Components

#### Scrapers
- **RequestsScraper**: Fast, lightweight for static content
- **SeleniumScraper**: Full browser automation with stealth features
- **PlaywrightScraper**: Modern async browser automation

#### Anti-Bot Protection
- Dynamic user agent rotation
- Intelligent rate limiting with exponential backoff
- Proxy rotation support
- CAPTCHA detection and handling
- Session management

#### Data Processing
- Flexible field extraction with CSS selectors
- Automatic URL resolution (relative to absolute)
- Metadata enrichment (timestamps, page numbers)
- Data validation and quality checks

### Configuration
```python
# config/settings.py
class ScraperSettings:
    MIN_DELAY: float = 1.0          # Minimum request delay
    MAX_DELAY: float = 5.0          # Maximum request delay
    MAX_RETRIES: int = 3            # Retry attempts
    HEADLESS: bool = True           # Browser headless mode
    MAX_PAGES: int = 10             # Maximum pages to scrape
    OUTPUT_FORMAT: str = "json"     # Output format
    # ... more settings
```

## 🎛️ Customization

### Adding New Sites
```python
# src/examples/ecommerce_scraper.py
SITE_CONFIGS = {
    "your_site": {
        "url": "https://yoursite.com/products",
        "product_selector": ".product-card",
        "field_selectors": {
            "title": "h2.title",
            "price": ".price-tag",
            "image": "img.product-img"
        },
        "scraper_type": "selenium"
    }
}
```

### Custom Field Extractors
```python
def extract_custom_field(element, field_name, selector):
    """Custom field extraction logic"""
    if field_name == "rating":
        stars = element.select(f"{selector} .star.filled")
        return len(stars)
    elif field_name == "discount":
        original = element.select_one(".original-price")
        current = element.select_one(".current-price")
        if original and current:
            return calculate_discount(original.text, current.text)
    # Default extraction
    return element.select_one(selector).get_text(strip=True)
```

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Test anti-bot utilities
python -m pytest tests/test_scrapers.py::TestAntiBot -v

# Test scraper functionality
python -m pytest tests/test_scrapers.py::TestRequestsScraper -v

# Test with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Manual Testing
```bash
# Test with a known working site
python main.py example books_toscrape --max-products 10 --verbose

# Test custom scraper
python main.py custom http://books.toscrape.com/ \
  --product-selector "article.product_pod" \
  --fields "title:h3 a" "price:.price_color" \
  --scraper-type requests
```

## 📊 Output Examples

### JSON Output
```json
[
  {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "availability": "In stock",
    "rating": "Three",
    "image": "http://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "page_number": 1,
    "scraped_at": "2024-01-15 10:30:45",
    "source_url": "http://books.toscrape.com/"
  }
]
```

### CSV Output
```csv
title,price,availability,rating,image,page_number,scraped_at,source_url
"A Light in the Attic","£51.77","In stock","Three","http://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",1,"2024-01-15 10:30:45","http://books.toscrape.com/"
```

## 🚨 Common Issues & Solutions

### Issue: Browser Not Found
```bash
# Install Chrome/Chromium
sudo apt-get install chromium-browser  # Ubuntu/Debian
brew install chromium                  # macOS

# Or use system Chrome
export CHROME_BIN=/usr/bin/google-chrome
```

### Issue: Playwright Installation
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
python -m playwright install
```

### Issue: Rate Limiting/Blocking
```python
# Increase delays in configuration
settings.MIN_DELAY = 3.0
settings.MAX_DELAY = 8.0

# Enable proxy rotation
anti_bot = AntiBot(proxy_list=["proxy1:8080", "proxy2:8080"])
```

### Issue: JavaScript Not Loading
```python
# Use Selenium or Playwright instead of Requests
python main.py custom <url> --scraper-type selenium

# Increase wait times
settings.PAGE_LOAD_TIMEOUT = 60
```

## 📜 Legal and Ethical Considerations

### Best Practices
- ✅ Respect robots.txt files
- ✅ Use reasonable delays between requests
- ✅ Don't overload target servers
- ✅ Respect website terms of service
- ✅ Consider reaching out for API access

### Rate Limiting
The framework includes built-in rate limiting to be respectful to target websites:
- Default 1-5 second delays between requests
- Exponential backoff on errors
- Configurable request timeouts
- Automatic detection of rate limiting responses

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/ -v
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all public methods
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

### Documentation
- [Technical Report](docs/REPORT.md) - Detailed implementation analysis
- [API Documentation](docs/api.md) - Programming interface reference
- [Examples](src/examples/) - Sample configurations and usage

### Getting Help
1. Check the [Common Issues](#-common-issues--solutions) section
2. Review the [Technical Report](docs/REPORT.md) for implementation details
3. Run with `--verbose` flag for detailed logging
4. Create an issue with reproduction steps

### Performance Tips
- Use `requests` scraper for static content (fastest)
- Use `playwright` for modern SPAs (good performance + JS support)
- Use `selenium` only when other options fail (slowest but most compatible)
- Adjust delays based on website responsiveness
- Monitor memory usage for long-running scrapes

---

**Built for Web Automation Engineers** 🕷️ **|** **Production Ready** ⚡ **|** **Extensible Architecture** 🔧