# How to Run the Web Automation Framework

This guide shows you **exactly** how to run the web automation framework with the real website: `https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer`

## 🚀 Quick Start (3 Steps)

### 1. Install Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Install browser dependencies for JavaScript handling
python install_playwright.py
```

### 2. Run with Your Target Website
```bash
# Scrape the specific Electric Bike Company product
python main.py custom "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --product-selector "main, .product-details, .product-info" \
  --fields "name:h1" "price:.price" "description:.description" \
  --scraper-type selenium \
  --max-products 1
```

### 3. View Results
```bash
# Results will be saved to output/ directory
ls output/
cat output/scraped_data_*.json
```

## 📋 Detailed Explanation

### Understanding the Target Website

The Electric Bike Company website (`https://electricbikecompany.com`) is a **modern React/Next.js application** with:

- **Dynamic Content**: JavaScript-rendered product information
- **JSON Data**: Product data embedded in `__NEXT_DATA__` script tags
- **Modern Selectors**: Uses data attributes and React patterns
- **Anti-Bot Measures**: Rate limiting and bot detection

### Code Architecture Explanation

#### 1. **Configuration System** (`config/settings.py`)
```python
# Centralized settings for all scrapers
settings.MIN_DELAY = 2.0        # Respectful delays
settings.MAX_DELAY = 5.0
settings.HEADLESS = True        # Run browsers invisibly
settings.PAGE_LOAD_TIMEOUT = 45 # Wait for React apps
```

#### 2. **Anti-Bot Protection** (`src/utils/anti_bot.py`)
```python
# Handles website protection mechanisms
class AntiBot:
    def get_user_agent(self):
        # Rotates realistic browser signatures
    
    def apply_rate_limiting(self):
        # Intelligent delays between requests
    
    def detect_captcha(self, page_source):
        # Identifies CAPTCHA challenges
```

#### 3. **Multiple Scraper Engines**

**For Static Sites** - `RequestsScraper`:
```python
# Fast, lightweight HTTP requests
python main.py custom <url> --scraper-type requests
```

**For JavaScript Sites** - `SeleniumScraper`:
```python
# Full browser automation with Chrome
python main.py custom <url> --scraper-type selenium
```

**For Modern SPAs** - `PlaywrightScraper`:
```python
# Async browser automation, better performance
python main.py custom <url> --scraper-type playwright
```

## 🎯 Running with Electric Bike Company

### Method 1: Using the Custom Command

```bash
# Basic scraping
python main.py custom "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --product-selector "main" \
  --fields "name:h1" "price:.price" \
  --scraper-type selenium

# Advanced scraping with more fields
python main.py custom "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --product-selector ".product-details, main, body" \
  --fields \
    "name:h1, .product-title" \
    "price:.price, .product-price" \
    "description:.description, .product-description, p" \
    "sku:.sku" \
    "images:img" \
  --scraper-type selenium \
  --verbose \
  --output-format json
```

### Method 2: Using the Specialized EBC Scraper

```bash
# Run the specialized Electric Bike Company scraper
python examples/electric_bike_company_scraper.py \
  --url "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --verbose

# Scrape a category page
python examples/electric_bike_company_scraper.py \
  --category "https://electricbikecompany.com/shop/categories/model-j" \
  --max-products 10
```

### Method 3: Programming Interface

```python
# Create and run scraper programmatically
from src.scrapers.selenium_scraper import SeleniumScraper
from src.utils.anti_bot import AntiBot

# Configure for Electric Bike Company
anti_bot = AntiBot(min_delay=2.0, max_delay=5.0, rotate_user_agents=True)

scraper = SeleniumScraper(
    target_url="https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer",
    product_selector="main, .product-details",
    field_selectors={
        "name": "h1, .product-title",
        "price": ".price, .product-price", 
        "description": ".description, p",
        "sku": ".sku",
        "availability": ".stock-status"
    },
    anti_bot=anti_bot
)

# Run scraping
products = scraper.scrape()
output_file = scraper.save_data("ebc_product.json")

print(f"Scraped {len(products)} products")
print(f"Saved to: {output_file}")
```

## 🔧 Advanced Configuration

### Handling Different Website Types

#### For E-commerce Sites (like EBC):
```bash
--scraper-type selenium \
--fields "name:h1" "price:.price" "image:img" "description:p" \
--min-delay 2.0 \
--max-delay 5.0
```

#### For Product Catalogs:
```bash
--scraper-type requests \
--fields "title:.title" "price:.cost" "link:a" \
--min-delay 1.0
```

#### For News/Blog Sites:
```bash
--scraper-type playwright \
--fields "headline:h1" "content:.content" "date:.date" \
--max-pages 3
```

### Debugging and Troubleshooting

#### Enable Verbose Logging:
```bash
python main.py custom <url> --verbose
```

#### Test Different Selectors:
```bash
# Try multiple selectors for the same field
--fields "name:h1, .title, .product-name"
```

#### Check Browser Mode:
```bash
# Run with visible browser for debugging
python main.py custom <url> --scraper-type selenium --no-headless
```

#### Handle JavaScript Loading:
```bash
# Increase timeout for slow sites
--page-timeout 60
```

## 📊 Understanding the Output

### JSON Output Structure:
```json
[
  {
    "name": "Burley Honey Bee Bike Trailer",
    "price": "$512",
    "description": "This versatile trailer features seating for one or two children...",
    "sku": "20009",
    "page_number": 1,
    "scraped_at": "2024-01-15 10:30:45",
    "source_url": "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer"
  }
]
```

### CSV Output:
```csv
name,price,description,sku,page_number,scraped_at,source_url
"Burley Honey Bee Bike Trailer","$512","This versatile trailer...","20009",1,"2024-01-15 10:30:45","https://electricbikecompany.com/..."
```

## 🛡️ Anti-Bot Features Explained

### 1. **Rate Limiting**
```python
# Automatic delays between requests
MIN_DELAY = 2.0 seconds
MAX_DELAY = 5.0 seconds
# Exponential backoff on errors
```

### 2. **User Agent Rotation**
```python
# Realistic browser signatures
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36..."
```

### 3. **Request Headers**
```python
# Natural browser headers
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}
```

### 4. **JavaScript Execution**
```python
# Wait for dynamic content to load
await page.wait_for_load_state("networkidle")
WebDriverWait(driver, 30).until(EC.presence_of_element_located(...))
```

## 🔄 Pagination Handling

The framework automatically handles different pagination patterns:

### 1. **Next Button Detection**
```python
next_selectors = [
    "a[aria-label*='Next']",
    ".next, .pagination-next", 
    "button:contains('Next')"
]
```

### 2. **URL Pattern Analysis**
```python
# Detects and modifies page parameters
if "page=" in url:
    new_url = url.replace("page=1", "page=2")
```

### 3. **Numbered Pagination**
```python
# Finds sequential page numbers
for link in pagination_links:
    if link.text == str(current_page + 1):
        navigate_to(link.href)
```

## 📈 Performance Optimization

### Choose the Right Scraper:

| Website Type | Recommended Scraper | Speed | JS Support |
|--------------|-------------------|-------|------------|
| Static HTML | `requests` | Fast | No |
| Modern SPA | `playwright` | Medium | Full |
| Heavy JS | `selenium` | Slow | Full |

### Optimization Settings:
```python
# For speed
settings.HEADLESS = True
settings.MIN_DELAY = 1.0

# For reliability  
settings.PAGE_LOAD_TIMEOUT = 45
settings.MAX_RETRIES = 3
```

## 🚨 Common Issues and Solutions

### Issue 1: "Element not found"
```bash
# Solution: Try broader selectors
--fields "name:h1, h2, .title, .product-name"
```

### Issue 2: "JavaScript not loading"
```bash
# Solution: Use selenium or playwright
--scraper-type selenium
```

### Issue 3: "Rate limited / blocked"
```bash
# Solution: Increase delays
--min-delay 5.0 --max-delay 10.0
```

### Issue 4: "No products found"
```bash
# Solution: Check product selector
--product-selector "main, .product, .item, article"
```

## 🎯 Success Tips

1. **Start Simple**: Use basic selectors first, then add complexity
2. **Test Incrementally**: Try one page before scraping many
3. **Be Respectful**: Use appropriate delays for the target site
4. **Monitor Logs**: Use `--verbose` to understand what's happening
5. **Save Frequently**: Results are automatically saved with timestamps

## 📚 Next Steps

1. **Explore Examples**: Check `src/examples/` for more configurations
2. **Read Documentation**: See `docs/REPORT.md` for technical details
3. **Run Tests**: Execute `python -m pytest tests/` to verify setup
4. **Customize**: Modify selectors for your specific target websites

This framework provides production-ready web scraping capabilities with comprehensive anti-bot protection and intelligent pagination handling. The modular design makes it easy to adapt for any website structure.