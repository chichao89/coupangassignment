# 🚀 Quick Start: Scraping Electric Bike Company Website

This guide shows you **exactly** how to run the web automation framework with your target website:
`https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer`

## ⚡ 30-Second Demo (No Dependencies Required)

```bash
# Run the framework demonstration (works immediately)
python3 demo.py
```

This shows you how the framework works with sample data and demonstrates all key features.

## 🎯 Real Website Scraping (With Dependencies)

### Step 1: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser support
python install_playwright.py
```

### Step 2: Scrape Your Target Website

#### Option A: Simple Command
```bash
python main.py custom "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --product-selector "main" \
  --fields "name:h1" "price:.price" "description:p" \
  --scraper-type selenium \
  --max-products 1 \
  --verbose
```

#### Option B: Advanced Configuration
```bash
python main.py custom "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --product-selector "main, .product-details, body" \
  --fields \
    "name:h1, .product-title, .product-name" \
    "price:.price, .product-price, .cost" \
    "description:.description, .product-description, p" \
    "sku:.sku, [data-sku]" \
    "availability:.stock-status, .availability" \
    "images:img" \
  --scraper-type selenium \
  --output-format json \
  --verbose
```

#### Option C: Use the Specialized EBC Scraper
```bash
python examples/electric_bike_company_scraper.py \
  --url "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer" \
  --verbose
```

### Step 3: View Results
```bash
ls output/
cat output/scraped_data_*.json
```

## 📋 Understanding the Command

### Basic Structure:
```bash
python main.py custom <URL> --product-selector <SELECTOR> --fields <FIELD_MAPPINGS>
```

### Parameters Explained:

- **URL**: The webpage to scrape
- **--product-selector**: CSS selector that identifies product containers
- **--fields**: Maps data fields to CSS selectors (format: "name:selector")
- **--scraper-type**: Engine to use (requests/selenium/playwright)
- **--max-products**: Limit number of products to scrape
- **--verbose**: Show detailed logging

### Field Mapping Format:
```bash
--fields "field_name:css_selector" "another_field:another_selector"
```

Examples:
- `"name:h1"` - Extract product name from h1 tags
- `"price:.price"` - Extract price from elements with class "price"
- `"description:p"` - Extract description from paragraph tags

## 🎛️ Choosing the Right Scraper

| Website Type | Use This | Why |
|--------------|----------|-----|
| Static HTML | `--scraper-type requests` | Fastest |
| JavaScript/React | `--scraper-type selenium` | Full browser |
| Modern SPA | `--scraper-type playwright` | Better performance |

For Electric Bike Company (React/Next.js site): **Use `selenium`**

## 🔧 Code Architecture

The framework consists of these key components:

### 1. **Main Entry Point** (`main.py`)
```python
# CLI interface that orchestrates scraping
python main.py custom <url> --options
```

### 2. **Scraper Engines** (`src/scrapers/`)
```python
# RequestsScraper: Fast HTTP requests
# SeleniumScraper: Full browser automation  
# PlaywrightScraper: Modern async automation
```

### 3. **Anti-Bot Protection** (`src/utils/anti_bot.py`)
```python
# Rate limiting, user agent rotation, CAPTCHA detection
```

### 4. **Configuration** (`config/settings.py`)
```python
# Centralized settings for delays, timeouts, etc.
```

## 🛡️ Anti-Bot Features

The framework automatically includes:

- **Rate Limiting**: 1-5 second delays between requests
- **User Agent Rotation**: Realistic browser signatures
- **CAPTCHA Detection**: Automatic identification and handling
- **Request Headers**: Natural browser-like headers
- **Retry Logic**: Exponential backoff on failures

## 📊 Expected Output

### JSON Format:
```json
[
  {
    "name": "Burley Honey Bee Bike Trailer",
    "price": "$512",
    "description": "This versatile trailer features seating for one or two children and includes a 1-Wheel Stroller Kit to convert from a bike trailer to a stroller.",
    "sku": "20009",
    "page_number": 1,
    "scraped_at": "2024-01-15 10:30:45",
    "source_url": "https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer"
  }
]
```

### CSV Format:
```csv
name,price,description,sku,page_number,scraped_at,source_url
"Burley Honey Bee Bike Trailer","$512","This versatile trailer...","20009",1,"2024-01-15 10:30:45","https://electricbikecompany.com/..."
```

## 🚨 Troubleshooting

### Common Issues:

#### 1. "Element not found"
```bash
# Try multiple selectors
--fields "name:h1, h2, .title, .product-name"
```

#### 2. "JavaScript not loading"
```bash
# Use browser automation
--scraper-type selenium
```

#### 3. "Rate limited"
```bash
# Increase delays
--min-delay 5.0 --max-delay 10.0
```

#### 4. Browser installation issues
```bash
# Reinstall browser dependencies
python install_playwright.py
```

### Debug Mode:
```bash
# Enable verbose logging to see what's happening
python main.py custom <url> --verbose

# Run with visible browser (for debugging)
# Note: Remove --headless flag in code for visual debugging
```

## 📈 Performance Tips

1. **Start with demo**: Run `python3 demo.py` first
2. **Test one product**: Use `--max-products 1` initially
3. **Use appropriate delays**: Be respectful to target servers
4. **Check selectors**: Use browser developer tools to find CSS selectors
5. **Monitor logs**: Use `--verbose` to understand the process

## 🔄 Pagination Support

The framework automatically handles:

- **Next button pagination**: Finds and clicks "Next" buttons
- **URL-based pagination**: Detects and modifies page parameters
- **Numbered pagination**: Navigates through sequential page numbers

## 📚 Additional Examples

### Scrape Multiple Pages:
```bash
python main.py custom "https://electricbikecompany.com/shop/categories/model-j" \
  --product-selector ".product-card" \
  --fields "name:.product-title" "price:.price" \
  --max-pages 3
```

### Export as CSV:
```bash
python main.py custom <url> \
  --product-selector "main" \
  --fields "name:h1" "price:.price" \
  --output-format csv
```

### Custom Configuration:
```python
# For programmatic use
from src.scrapers.selenium_scraper import SeleniumScraper
from src.utils.anti_bot import AntiBot

scraper = SeleniumScraper(
    target_url="https://electricbikecompany.com/shop/products/burley-honey-bee-bike-trailer",
    product_selector="main",
    field_selectors={"name": "h1", "price": ".price"},
    anti_bot=AntiBot(min_delay=2.0, max_delay=5.0)
)

products = scraper.scrape()
```

## ✅ Success Criteria

You'll know it's working when you see:

1. **Logs showing**: "Starting scrape of [URL]"
2. **Product extraction**: "Extracted X products from page Y"
3. **Output file**: "Data saved to output/scraped_data_[timestamp].json"
4. **Valid JSON**: Properly formatted product data

## 🎯 Next Steps

1. **Run the demo**: `python3 demo.py`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Try your website**: Use the commands above
4. **Read the docs**: Check `HOW_TO_RUN.md` for advanced usage
5. **Explore examples**: See `examples/` directory for more configurations

This framework provides enterprise-grade web scraping capabilities with built-in protection against modern anti-bot measures. The modular design makes it easy to adapt for any website structure while maintaining ethical scraping practices.