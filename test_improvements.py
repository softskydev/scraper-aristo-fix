#!/usr/bin/env python3
"""
Test script to validate the improvements made to the aristohk_scraper.py
"""

import sys
import json
from aristohk_scraper import AristoHKScraper

def test_richard_mille_reference_extraction():
    """Test Richard Mille reference extraction from URLs"""
    
    scraper = AristoHKScraper()
    
    # Test cases for Richard Mille URL parsing
    test_urls = [
        "https://aristohk.com/richard-mille/rm-65-01-mc-laren/22475",
        "https://aristohk.com/richard-mille/rm-11-03-mclaren/14695", 
        "https://aristohk.com/richard-mille/rm-35-02-rafael-nadal/12345"
    ]
    
    expected_references = [
        "RM65-01",
        "RM11-03", 
        "RM35-02"
    ]
    
    print("Testing Richard Mille reference extraction:")
    print("-" * 50)
    
    for i, url in enumerate(test_urls):
        url_parts = url.split('/')
        model_slug = url_parts[4] if len(url_parts) > 4 else ""
        
        # Simulate the improved logic
        import re
        if model_slug.startswith('rm-'):
            model_match = re.search(r'rm-(\d+(?:-\d+)*)', model_slug.lower())
            if model_match:
                model_number = model_match.group(1).replace('-', '-')
                reference = f"RM{model_number}"
            else:
                reference = model_slug.upper().replace('-', '')
        else:
            reference = model_slug.upper().replace('-', '')
            
        expected = expected_references[i]
        status = "✓ PASS" if reference == expected else "✗ FAIL"
        
        print(f"URL: {url}")
        print(f"Expected: {expected}")
        print(f"Got: {reference}")
        print(f"Status: {status}")
        print()

def test_scraper_on_richard_mille():
    """Test the actual scraper on a Richard Mille product"""
    
    print("Testing actual Richard Mille product scraping:")
    print("-" * 50)
    
    scraper = AristoHKScraper()
    
    # Test with one of the Richard Mille URLs from the response
    test_url = "https://aristohk.com/richard-mille/rm-65-01-mc-laren/22475"
    
    print(f"Attempting to scrape: {test_url}")
    
    try:
        product = scraper.extract_product_details(test_url)
        
        if product:
            print("✓ Successfully scraped product")
            print(f"Brand: {product.get('brand')}")
            print(f"Reference: {product.get('reference')}")
            print(f"Year: {product.get('year')}")
            print(f"Price HKD: {product.get('price_hkd')}")
            
            # Check if reference extraction improved
            if product.get('reference') and 'RM' in product.get('reference', ''):
                if len(product.get('reference', '')) > 3:  # More than just "RM"
                    print("✓ Reference extraction looks improved!")
                else:
                    print("⚠ Reference still seems incomplete")
            else:
                print("✗ Reference extraction still has issues")
                
            # Check year
            if product.get('year') and product.get('year') != 2025:
                print(f"✓ Year extraction improved: {product.get('year')}")
            else:
                print(f"⚠ Year might still have issues: {product.get('year')}")
                
        else:
            print("✗ Failed to scrape product")
            
    except Exception as e:
        print(f"✗ Error during scraping: {e}")

if __name__ == "__main__":
    print("Testing improvements to aristohk_scraper.py")
    print("=" * 60)
    print()
    
    # Test the reference extraction logic
    test_richard_mille_reference_extraction()
    
    # Test actual scraping (this requires internet connection)
    try:
        test_scraper_on_richard_mille()
    except Exception as e:
        print(f"Note: Actual scraping test failed (might be network issue): {e}")
    
    print("\nTesting complete!")