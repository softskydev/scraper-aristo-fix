#!/usr/bin/env python3
"""
Test scraping a few products to validate improvements
"""

import json
from aristohk_scraper import AristoHKScraper

def test_few_products():
    """Test scraping a few products from different brands"""
    
    scraper = AristoHKScraper()
    
    # Test URLs from the original response.json 
    test_urls = [
        "https://aristohk.com/richard-mille/rm-65-01-mc-laren/22475",  # Richard Mille
        "https://aristohk.com/richard-mille/rm-11-03-mclaren/14695",   # Another Richard Mille  
        "https://aristohk.com/rolex/126500-ln-0002/18692",            # Rolex (should remain unchanged)
    ]
    
    products = []
    
    print("Testing scraping with improvements:")
    print("-" * 50)
    
    for url in test_urls:
        print(f"Scraping: {url}")
        try:
            product = scraper.extract_product_details(url)
            if product:
                products.append(product)
                print(f"✓ Brand: {product.get('brand')}")
                print(f"✓ Reference: {product.get('reference')}")
                print(f"✓ Year: {product.get('year')}")
                print(f"✓ Price HKD: {product.get('price_hkd')}")
                print()
            else:
                print("✗ Failed to extract product details")
                print()
        except Exception as e:
            print(f"✗ Error: {e}")
            print()
    
    # Save test results
    if products:
        with open('/app/test_results.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(products)} test results to test_results.json")
    
    return products

if __name__ == "__main__":
    test_few_products()