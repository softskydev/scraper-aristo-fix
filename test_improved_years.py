#!/usr/bin/env python3
"""
Test the improved year extraction on actual products
"""

from aristohk_scraper import AristoHKScraper

def test_improved_year_extraction():
    """Test the improved year extraction logic"""
    
    scraper = AristoHKScraper()
    
    # Test URLs that previously had null years
    test_urls = [
        "https://aristohk.com/rolex/126610-ln-0001/25110",  # Should find "introduced in 2020"
        "https://aristohk.com/rolex/126500-ln-0002/18692",  # Should find "released in 2023" 
        "https://aristohk.com/richard-mille/rm-65-01-mc-laren/22475",  # Richard Mille (should still work)
    ]
    
    print("Testing improved year extraction:")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        print("-" * 40)
        
        try:
            product = scraper.extract_product_details(url)
            if product:
                print(f"✓ Brand: {product.get('brand')}")
                print(f"✓ Reference: {product.get('reference')}")
                print(f"✓ Year: {product.get('year')}")
                print(f"✓ Price HKD: {product.get('price_hkd')}")
                
                # Check if year extraction improved
                if product.get('year'):
                    print(f"✅ SUCCESS: Found year {product.get('year')}")
                else:
                    print("⚠️  Still no year found")
            else:
                print("❌ Failed to extract product details")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_improved_year_extraction()