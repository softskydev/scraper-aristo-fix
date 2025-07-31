#!/usr/bin/env python3
"""
Aristohk.com Web Scraper
Scrapes all watch products from aristohk.com and outputs to structured JSON.

Usage:
    python aristohk_scraper.py --all --output watches.json
    python aristohk_scraper.py --pages 1-5 --output limited_watches.json
    python aristohk_scraper.py --brand rolex --output rolex_watches.json
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import argparse
import re
import sys
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Set
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AristoHKScraper:
    def __init__(self, base_url: str = "https://aristohk.com", delay: float = 0.5):
        """Initialize the scraper with base URL and request delay."""
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_products: List[Dict] = []
        self.visited_urls: Set[str] = set()
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Get a web page with retry logic."""
        for attempt in range(retries):
            try:
                if self.delay > 0:
                    time.sleep(self.delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                logger.info(f"Successfully fetched: {url}")
                return soup
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def discover_brands(self) -> List[Dict[str, str]]:
        """Discover all brands available on the website."""
        logger.info("Discovering brands...")
        
        soup = self.get_page(self.base_url)
        if not soup:
            logger.error("Failed to load homepage")
            return []
        
        brands = []
        
        # Find main feature brands
        feature_brand_links = soup.find_all('a', href=re.compile(r'^/(rolex|audemars-piguet|patek-philippe|richard-mille)$'))
        for link in feature_brand_links:
            href = link.get('href')
            if href and href.startswith('/'):
                brand_name = href[1:].replace('-', ' ').upper()
                brands.append({
                    'name': brand_name,
                    'url': urljoin(self.base_url, href),
                    'slug': href[1:]
                })
        
        # Find other brands in footer or navigation
        other_brand_links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z-]+$'))
        for link in other_brand_links:
            href = link.get('href')
            if href and href.startswith('/') and len(href.split('/')) == 2:
                brand_slug = href[1:]
                # Skip non-brand pages
                skip_pages = [
                    'about-us', 'contact-us', 'articles', 'account', 'sell-watches',
                    'prepaid-consignment', 'mega-sale', 'pre-owned', 'new-watch',
                    'blog', 'faqs'
                ]
                if brand_slug not in skip_pages and brand_slug not in [b['slug'] for b in brands]:
                    brand_name = brand_slug.replace('-', ' ').upper()
                    brands.append({
                        'name': brand_name,
                        'url': urljoin(self.base_url, href),
                        'slug': brand_slug
                    })
        
        # Additional known brands that might be missed
        known_brands = [
            'cartier', 'hublot', 'iwc', 'jaeger-lecoultre', 'longines', 'omega',
            'tudor', 'vacheron-constantin', 'alange-soehne', 'baume-mercier',
            'blancpain', 'breguet', 'bulgari', 'chanel', 'chopard', 'f-p-journe',
            'girard-perregaux', 'glashutte', 'h-moser-cie', 'hyt', 'jacob-and-co',
            'mb-f', 'montblanc', 'panerai', 'parmigiani-fleurier', 'piaget',
            'roger-dubuis', 'tag-heuer', 'van-cleef-arpels', 'zenith'
        ]
        
        for brand_slug in known_brands:
            if brand_slug not in [b['slug'] for b in brands]:
                brand_name = brand_slug.replace('-', ' ').upper()
                brands.append({
                    'name': brand_name,
                    'url': urljoin(self.base_url, brand_slug),
                    'slug': brand_slug
                })
        
        logger.info(f"Discovered {len(brands)} brands")
        return brands
    
    def get_total_pages(self, brand_url: str) -> int:
        """Get the total number of pages for a brand."""
        soup = self.get_page(brand_url)
        if not soup:
            return 1
        
        # Look for pagination
        pagination = soup.find('div', class_='pagination') or soup.find('nav', class_='pagination')
        if not pagination:
            # Try to find pagination links
            page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
            if page_links:
                max_page = 1
                for link in page_links:
                    href = link.get('href', '')
                    match = re.search(r'page=(\d+)', href)
                    if match:
                        max_page = max(max_page, int(match.group(1)))
                return max_page
            
            # Look for specific pagination numbers
            page_numbers = soup.find_all(text=re.compile(r'^\d+$'))
            if page_numbers:
                try:
                    return max([int(num.strip()) for num in page_numbers if num.strip().isdigit()])
                except:
                    pass
        
        return 1
    
    def extract_product_urls(self, brand_url: str, page: int = 1) -> List[str]:
        """Extract product URLs from a brand page."""
        page_url = f"{brand_url}?page={page}" if page > 1 else brand_url
        
        soup = self.get_page(page_url)
        if not soup:
            return []
        
        product_urls = []
        
        # Find product links - they usually follow the pattern /{brand}/{series}/{model}/{id}
        # First try specific pattern
        product_links = soup.find_all('a', href=re.compile(r'^/[^/]+/[^/]+/[^/]+/\d+$'))
        
        # If no products found, try broader patterns
        if not product_links:
            # Try alternative patterns
            product_links = soup.find_all('a', href=re.compile(r'^/[^/]+/[^/]+/\d+$'))
        
        if not product_links:
            # Try even broader pattern for any watch product links
            product_links = soup.find_all('a', href=re.compile(r'/\d+$'))
        
        # Debug: print all links found
        all_links = soup.find_all('a', href=True)
        logger.info(f"Total links found on page: {len(all_links)}")
        
        # Filter for product-like links
        potential_products = []
        for link in all_links:
            href = link.get('href')
            if href and ('/' in href) and (href.endswith(tuple(str(i) for i in range(10)))):
                # Check if it looks like a product URL
                if len(href.split('/')) >= 3:
                    potential_products.append(href)
        
        logger.info(f"Potential product URLs found: {len(potential_products)}")
        
        for link in product_links:
            href = link.get('href')
            if href and href not in self.visited_urls:
                full_url = urljoin(self.base_url, href)
                product_urls.append(full_url)
                self.visited_urls.add(href)
        
        # If still no products, add potential ones
        if not product_urls:
            for href in potential_products[:10]:  # Limit to first 10 for testing
                if href not in self.visited_urls:
                    full_url = urljoin(self.base_url, href)
                    product_urls.append(full_url)
                    self.visited_urls.add(href)
        
        logger.info(f"Found {len(product_urls)} product URLs on page {page}")
        return product_urls
    
    def extract_product_details(self, product_url: str) -> Optional[Dict]:
        """Extract product details from a product page."""
        soup = self.get_page(product_url)
        if not soup:
            return None
        
        try:
            # Extract basic information
            brand = "Unknown"
            reference = "Unknown"
            description = "Unknown"
            price_hk = None
            condition = ""
            year = None
            completeness = ""
            
            # Extract brand from URL
            url_parts = urlparse(product_url).path.split('/')
            if len(url_parts) >= 2:
                brand = url_parts[1].replace('-', ' ').title()
                if brand.lower() == 'audemars piguet':
                    brand = 'AUDEMARS PIGUET'
                elif brand.lower() == 'patek philippe':
                    brand = 'PATEK PHILIPPE'
                elif brand.lower() == 'richard mille':
                    brand = 'RICHARD MILLE'
                else:
                    brand = brand.upper()
            
            # Extract reference/model from URL - Special handling for Richard Mille
            if brand.upper() == 'RICHARD MILLE' and len(url_parts) >= 3:
                # For Richard Mille, extract model code from URL slug
                # Convert "/rm-65-01-mc-laren/" to "RM65-01"
                model_slug = url_parts[2]  # e.g., "rm-65-01-mc-laren"
                if model_slug.startswith('rm-'):
                    # Extract the model number part (e.g., "65-01" from "rm-65-01-mc-laren")
                    model_match = re.search(r'rm-(\d+(?:-\d+)*)', model_slug.lower())
                    if model_match:
                        model_number = model_match.group(1).replace('-', '-')  # Keep hyphens
                        reference = f"RM{model_number}"
                    else:
                        reference = model_slug.upper().replace('-', '')
                else:
                    reference = model_slug.upper().replace('-', '')
            elif len(url_parts) >= 4:
                reference = url_parts[3].upper().replace('-', '')
            
            # For non-Richard Mille brands, use existing logic
            if brand.upper() != 'RICHARD MILLE':
                # Try to find reference in page title or H1
                title = soup.find('title')
                if title:
                    title_text = title.get_text()
                    # Extract model from title like "ROLEX | DAYTONA 126500LN-0002"
                    if '|' in title_text:
                        parts = title_text.split('|')
                        if len(parts) >= 2:
                            model_part = parts[1].strip()
                            # Extract the model number
                            model_match = re.search(r'([A-Z0-9\-]+)$', model_part)
                            if model_match:
                                reference = model_match.group(1)
                
                # Try H1 for more accurate reference
                h1 = soup.find('h1')
                if h1:
                    h1_text = h1.get_text().strip()
                    # Extract reference from H1 like "ROLEX 126500LN-0002"
                    parts = h1_text.split()
                    if len(parts) >= 2:
                        reference = parts[-1]  # Take the last part as reference
            
            # Extract price - look for the main product price more accurately
            all_text = soup.get_text()
            
            # Try to find price near the product reference or brand name
            price_hk = None
            
            # Look for price patterns in the first part of the page (main product area)
            main_content = all_text[:1500]  # Focus on main product content
            
            # Find HK$ pattern and extract numbers after it
            hk_indices = []
            for i, char in enumerate(main_content):
                if main_content[i:i+3] == 'HK$':
                    hk_indices.append(i)
            
            # Extract the first meaningful price from main content
            for idx in hk_indices:
                price_text = main_content[idx+3:idx+20]
                number_match = re.match(r'([\d,]+)', price_text)
                if number_match:
                    price_str = number_match.group(1)
                    try:
                        price_num = int(price_str.replace(',', ''))
                        if price_num > 10000:  # Main product prices are usually substantial
                            # Check if this price is followed by "Ask Price" in close proximity
                            surrounding_text = main_content[max(0, idx-50):idx+100]
                            if not re.search(r'Ask Price', surrounding_text, re.I):
                                price_hk = price_num
                                break
                    except ValueError:
                        continue
            
            # If no price found or if Ask Price is the main price indication
            if price_hk is None:
                # Check if "Ask Price" is specifically mentioned for this product
                ask_price_pattern = re.search(r'Ask Price', main_content, re.I)
                if ask_price_pattern:
                    price_hk = None  # Explicitly set to None for "Ask Price" products
            
            # Extract condition - check main content first
            main_content = all_text[:1500]
            if re.search(r'HOT', main_content, re.I):
                condition = "New"
            elif re.search(r'Pre-owned', main_content, re.I):
                condition = "Pre-owned"
            else:
                condition = "New"  # Default assumption
            
            # Extract year from Release Year field specifically
            year = None
            
            # Look for "Release Year" field specifically in the product details (most accurate)
            release_year_pattern = r'Release Year[:\s]*(\d{4})'
            year_match = re.search(release_year_pattern, all_text, re.I)
            if year_match:
                try:
                    potential_year = int(year_match.group(1))
                    # Validate year is reasonable (between 1950 and current year + 2)
                    if 1950 <= potential_year <= 2027:
                        year = potential_year
                except ValueError:
                    pass
            
            # If no Release Year found, try other common year patterns
            if year is None:
                year_patterns = [
                    r'released in (\d{4})',           # "released in 2023"
                    r'introduced in (\d{4})',         # "introduced in 2020"  
                    r'(\d{4})\s*release',             # "2023 release"
                    r'(\d{4})\s*model',               # "2020 model"
                    r'launched in (\d{4})',           # "launched in 2021"
                    r'(\d{4})\s*edition',             # "2022 edition"
                    r'production[:\s]*(\d{4})',       # "production: 2019"
                    r'year[:\s]*(\d{4})',             # "year: 2018"
                ]
                
                for pattern in year_patterns:
                    year_match = re.search(pattern, all_text, re.I)
                    if year_match:
                        try:
                            potential_year = int(year_match.group(1))
                            if 1950 <= potential_year <= 2027:
                                year = potential_year
                                break
                        except ValueError:
                            continue
            
            # If still no year found, leave as None (don't guess or use current year)
            
            # Extract completeness from Accessories information
            completeness_parts = []
            
            # Look for "With Box" pattern
            if re.search(r'With Box', all_text, re.I):
                completeness_parts.append("With Box")
            
            # Look for "With Paper" or "With Papers" pattern  
            if re.search(r'With Papers?', all_text, re.I):
                completeness_parts.append("With Papers")
            
            # Look for "Original" accessories patterns
            if re.search(r'Original.*box', all_text, re.I):
                if "With Box" not in completeness_parts:
                    completeness_parts.append("With Box")
            
            if re.search(r'Original.*certificate', all_text, re.I):
                if "With Papers" not in completeness_parts:
                    completeness_parts.append("With Papers")
            
            # Join completeness parts
            completeness = ", ".join(completeness_parts) if completeness_parts else ""
            
            # Create description
            description = f"{brand} {reference}"
            
            # Create product dictionary
            product = {
                "brand": brand,
                "reference": reference,
                "description": description,
                "condition": condition,
                "product_url": product_url,
                "price_usd": None,
                "price_idr": None,
                "price_hkd": price_hk,
                "year": year,
                "completeness": completeness,
                "scraped_from": "aristohk.com",
                "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "product_type": "watches",
                "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            }
            
            logger.info(f"Extracted: {brand} {reference} - HK${price_hk}")
            return product
            
        except Exception as e:
            logger.error(f"Error extracting product details from {product_url}: {e}")
            return None
    
    def scrape_brand(self, brand: Dict[str, str], start_page: int = 1, end_page: int = None) -> List[Dict]:
        """Scrape all products from a specific brand."""
        logger.info(f"Scraping brand: {brand['name']}")
        
        brand_products = []
        
        # Get total pages if end_page is not specified
        if end_page is None:
            total_pages = self.get_total_pages(brand['url'])
            end_page = total_pages
        
        logger.info(f"Scraping pages {start_page} to {end_page} for {brand['name']}")
        
        for page in range(start_page, end_page + 1):
            logger.info(f"Scraping {brand['name']} page {page}")
            
            # Get product URLs from this page
            product_urls = self.extract_product_urls(brand['url'], page)
            
            if not product_urls:
                logger.info(f"No products found on page {page}, stopping")
                break
            
            # Extract details for each product
            for product_url in product_urls:
                product = self.extract_product_details(product_url)
                if product:
                    brand_products.append(product)
        
        logger.info(f"Scraped {len(brand_products)} products from {brand['name']}")
        return brand_products
    
    def scrape_all(self, start_page: int = 1, end_page: int = None, specific_brand: str = None) -> List[Dict]:
        """Scrape all products from the website."""
        logger.info("Starting comprehensive scraping...")
        
        # Discover all brands
        brands = self.discover_brands()
        
        if specific_brand:
            brands = [b for b in brands if b['slug'].lower() == specific_brand.lower()]
            if not brands:
                logger.error(f"Brand '{specific_brand}' not found")
                return []
        
        all_products = []
        
        for brand in brands:
            try:
                brand_products = self.scrape_brand(brand, start_page, end_page)
                all_products.extend(brand_products)
                
                logger.info(f"Total products scraped so far: {len(all_products)}")
                
            except Exception as e:
                logger.error(f"Error scraping brand {brand['name']}: {e}")
                continue
        
        logger.info(f"Scraping completed! Total products: {len(all_products)}")
        return all_products
    
    def save_to_json(self, products: List[Dict], filename: str):
        """Save products to JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(products)} products to {filename}")
        except Exception as e:
            logger.error(f"Error saving to {filename}: {e}")


def parse_page_range(page_range: str) -> tuple:
    """Parse page range string like '1-5' or '10-20'."""
    if '-' in page_range:
        start, end = page_range.split('-')
        return int(start), int(end)
    else:
        page = int(page_range)
        return page, page


def main():
    parser = argparse.ArgumentParser(description='Scrape aristohk.com for watch products')
    parser.add_argument('--all', action='store_true', help='Scrape all products from all brands')
    parser.add_argument('--pages', type=str, help='Page range to scrape (e.g., "1-5" or "10")')
    parser.add_argument('--brand', type=str, help='Specific brand to scrape (e.g., "rolex")')
    parser.add_argument('--output', type=str, default='aristohk_products.json', help='Output JSON filename')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all and not args.pages and not args.brand:
        print("Error: You must specify either --all, --pages, or --brand")
        sys.exit(1)
    
    # Initialize scraper
    scraper = AristoHKScraper(delay=args.delay)
    
    # Determine page range
    start_page, end_page = 1, None
    if args.pages:
        start_page, end_page = parse_page_range(args.pages)
    
    # Start scraping
    try:
        products = scraper.scrape_all(start_page, end_page, args.brand)
        
        # Save results
        scraper.save_to_json(products, args.output)
        
        print(f"\nScraping completed successfully!")
        print(f"Total products scraped: {len(products)}")
        print(f"Results saved to: {args.output}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        if scraper.scraped_products:
            scraper.save_to_json(scraper.scraped_products, f"partial_{args.output}")
            print(f"Partial results saved to: partial_{args.output}")
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()