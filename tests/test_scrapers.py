#!/usr/bin/env python3
"""
Unit tests for the web scraping framework
"""

import unittest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.anti_bot import AntiBot
from src.scrapers.requests_scraper import RequestsScraper
from src.scrapers.selenium_scraper import SeleniumScraper
from src.scrapers.playwright_scraper import PlaywrightScraper

class TestAntiBot(unittest.TestCase):
    """Test anti-bot utilities"""
    
    def setUp(self):
        self.anti_bot = AntiBot(min_delay=0.1, max_delay=0.2)
    
    def test_get_random_delay(self):
        """Test random delay generation"""
        delay = self.anti_bot.get_random_delay()
        self.assertGreaterEqual(delay, 0.1)
        self.assertLessEqual(delay, 0.2)
    
    def test_get_user_agent(self):
        """Test user agent generation"""
        ua = self.anti_bot.get_user_agent()
        self.assertIsInstance(ua, str)
        self.assertIn("Mozilla", ua)
    
    def test_detect_captcha(self):
        """Test CAPTCHA detection"""
        captcha_html = "<html><body>Please solve this captcha</body></html>"
        normal_html = "<html><body>Welcome to our site</body></html>"
        
        self.assertTrue(self.anti_bot.detect_captcha(captcha_html))
        self.assertFalse(self.anti_bot.detect_captcha(normal_html))
    
    def test_proxy_rotation(self):
        """Test proxy rotation"""
        proxies = ["proxy1:8080", "proxy2:8080", "proxy3:8080"]
        anti_bot = AntiBot(proxy_list=proxies)
        
        proxy1 = anti_bot.get_proxy()
        proxy2 = anti_bot.get_proxy()
        proxy3 = anti_bot.get_proxy()
        proxy4 = anti_bot.get_proxy()  # Should wrap around
        
        self.assertNotEqual(proxy1, proxy2)
        self.assertNotEqual(proxy2, proxy3)
        self.assertEqual(proxy1, proxy4)  # Wrapped around

class TestRequestsScraper(unittest.TestCase):
    """Test requests-based scraper"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = RequestsScraper(
            target_url="http://example.com",
            product_selector=".product",
            field_selectors={"name": ".name", "price": ".price"},
            anti_bot=AntiBot(min_delay=0.1, max_delay=0.1)
        )
        self.scraper.output_dir = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_extract_product_data(self):
        """Test product data extraction"""
        html = """
        <div class="product">
            <span class="name">Product 1</span>
            <span class="price">$10.99</span>
        </div>
        <div class="product">
            <span class="name">Product 2</span>
            <span class="price">$15.99</span>
        </div>
        """
        
        products = self.scraper.extract_product_data(html)
        
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]["name"], "Product 1")
        self.assertEqual(products[0]["price"], "$10.99")
        self.assertEqual(products[1]["name"], "Product 2")
        self.assertEqual(products[1]["price"], "$15.99")
    
    def test_find_next_page_url(self):
        """Test next page URL detection"""
        from bs4 import BeautifulSoup
        
        html = """
        <div class="pagination">
            <a href="/page/1">1</a>
            <a href="/page/2" class="current">2</a>
            <a href="/page/3">3</a>
            <a href="/page/3" class="next">Next</a>
        </div>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        self.scraper.current_page = 2
        next_url = self.scraper.find_next_page_url(soup, "http://example.com/page/2")
        
        self.assertIn("/page/3", next_url)
    
    @patch('src.utils.anti_bot.AntiBot.make_request')
    def test_scrape_with_pagination(self, mock_request):
        """Test scraping with pagination"""
        # Mock first page response
        first_page_html = """
        <div class="product">
            <span class="name">Product 1</span>
            <span class="price">$10.99</span>
        </div>
        <a href="/page/2" class="next">Next</a>
        """
        
        # Mock second page response
        second_page_html = """
        <div class="product">
            <span class="name">Product 2</span>
            <span class="price">$15.99</span>
        </div>
        """
        
        # Setup mock responses
        mock_response1 = Mock()
        mock_response1.text = first_page_html
        mock_response1.status_code = 200
        
        mock_response2 = Mock()
        mock_response2.text = second_page_html
        mock_response2.status_code = 200
        
        mock_request.side_effect = [mock_response1, mock_response2]
        
        # Run scraping
        products = self.scraper.scrape()
        
        # Verify results
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0]["name"], "Product 1")
        self.assertEqual(products[1]["name"], "Product 2")

class TestSeleniumScraper(unittest.TestCase):
    """Test Selenium-based scraper"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = SeleniumScraper(
            target_url="http://example.com",
            product_selector=".product",
            field_selectors={"name": ".name", "price": ".price"},
            anti_bot=AntiBot(min_delay=0.1, max_delay=0.1)
        )
        self.scraper.output_dir = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    @patch('src.scrapers.selenium_scraper.webdriver.Chrome')
    def test_setup_driver(self, mock_chrome):
        """Test driver setup"""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        self.scraper.setup_driver()
        
        self.assertIsNotNone(self.scraper.driver)
        mock_driver.execute_script.assert_called()
        mock_driver.set_page_load_timeout.assert_called()
    
    def test_extract_product_data(self):
        """Test product data extraction"""
        html = """
        <div class="product">
            <span class="name">Product 1</span>
            <span class="price">$10.99</span>
        </div>
        """
        
        products = self.scraper.extract_product_data(html)
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Product 1")
        self.assertEqual(products[0]["price"], "$10.99")

class TestPlaywrightScraper(unittest.TestCase):
    """Test Playwright-based scraper"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = PlaywrightScraper(
            target_url="http://example.com",
            product_selector=".product",
            field_selectors={"name": ".name", "price": ".price"},
            anti_bot=AntiBot(min_delay=0.1, max_delay=0.1)
        )
        self.scraper.output_dir = Path(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_extract_product_data(self):
        """Test product data extraction"""
        html = """
        <div class="product">
            <span class="name">Product 1</span>
            <span class="price">$10.99</span>
        </div>
        """
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            products = loop.run_until_complete(
                self.scraper.extract_product_data(html)
            )
            
            self.assertEqual(len(products), 1)
            self.assertEqual(products[0]["name"], "Product 1")
            self.assertEqual(products[0]["price"], "$10.99")
        finally:
            loop.close()

class TestDataOutput(unittest.TestCase):
    """Test data output functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.scraper = RequestsScraper(
            target_url="http://example.com",
            product_selector=".product",
            field_selectors={"name": ".name", "price": ".price"},
            anti_bot=AntiBot()
        )
        self.scraper.output_dir = Path(self.temp_dir)
        
        # Add sample data
        self.scraper.scraped_data = [
            {"name": "Product 1", "price": "$10.99", "page_number": 1},
            {"name": "Product 2", "price": "$15.99", "page_number": 1}
        ]
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_json_data(self):
        """Test saving data as JSON"""
        from config.settings import settings
        settings.OUTPUT_FORMAT = "json"
        
        output_file = self.scraper.save_data("test_output.json")
        
        self.assertTrue(Path(output_file).exists())
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Product 1")
    
    def test_save_csv_data(self):
        """Test saving data as CSV"""
        from config.settings import settings
        settings.OUTPUT_FORMAT = "csv"
        
        output_file = self.scraper.save_data("test_output.csv")
        
        self.assertTrue(Path(output_file).exists())
        
        import pandas as pd
        df = pd.read_csv(output_file)
        
        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["name"], "Product 1")
    
    def test_get_stats(self):
        """Test statistics generation"""
        stats = self.scraper.get_stats()
        
        self.assertEqual(stats["total_products"], 2)
        self.assertEqual(stats["target_url"], "http://example.com")
        self.assertIn("name", stats["unique_fields"])
        self.assertIn("price", stats["unique_fields"])
    
    def test_validate_data(self):
        """Test data validation"""
        # Test with good data
        self.assertTrue(self.scraper.validate_data())
        
        # Test with empty data
        self.scraper.scraped_data = []
        self.assertFalse(self.scraper.validate_data())

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)