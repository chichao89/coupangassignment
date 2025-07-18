# Web Automation Framework Makefile

.PHONY: help install test clean run-example run-books run-quotes setup-dev lint format

help:
	@echo "Available commands:"
	@echo "  install      - Install all dependencies"
	@echo "  setup-dev    - Setup development environment"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean up temporary files"
	@echo "  run-example  - Run example scraper (books)"
	@echo "  run-books    - Scrape books.toscrape.com"
	@echo "  run-quotes   - Scrape quotes.toscrape.com"

install:
	pip install -r requirements.txt
	python install_playwright.py

setup-dev: install
	pip install pytest pytest-cov black flake8 mypy
	pip install -e .

test:
	python -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ tests/ main.py --max-line-length=100 --ignore=E203,W503
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ main.py config/ --line-length=100

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -f scraper.log

run-example:
	python main.py example books_toscrape --max-products 20 --verbose

run-books:
	python main.py example books_toscrape --max-products 100 --output-format json

run-quotes:
	python main.py example quotes_toscrape --max-products 50 --output-format csv

# Custom scraper examples
run-custom-books:
	python main.py custom http://books.toscrape.com/ \
		--product-selector "article.product_pod" \
		--fields "title:h3 a" "price:.price_color" "availability:.availability" \
		--scraper-type requests \
		--max-products 30

# Development tasks
dev-setup: setup-dev
	cp .env.example .env
	mkdir -p output logs

# Docker commands (if you add Docker later)
docker-build:
	docker build -t web-automation-framework .

docker-run:
	docker run --rm -v $(PWD)/output:/app/output web-automation-framework

# Performance testing
benchmark:
	@echo "Running performance benchmarks..."
	time python main.py example books_toscrape --max-products 50 --scraper-type requests
	time python main.py example books_toscrape --max-products 20 --scraper-type selenium