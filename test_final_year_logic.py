#!/usr/bin/env python3
"""
Test the improved year extraction logic
"""

from aristohk_scraper import AristoHKScraper

def test_improved_year_logic():
    """Test the new year extraction logic"""
    
    scraper = AristoHKScraper()
    
    print("Testing improved year extraction logic:")
    print("=" * 60)
    
    # Test with multiple URLs
    test_urls = [
        "https://aristohk.com/rolex/126500-ln-0002/18692",   # Should find "released in 2023"
        "https://aristohk.com/rolex/126610-ln-0001/25110",   # Should find "introduced in 2020" 
        "https://aristohk.com/richard-mille/rm-65-01-mc-laren/22475",  # Richard Mille test
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        print("-" * 50)
        
        try:
            product = scraper.extract_product_details(url)
            
            if product:
                print(f"✓ Brand: {product.get('brand')}")  
                print(f"✓ Reference: {product.get('reference')}")
                print(f"✓ Year: {product.get('year')}")
                print(f"✓ Price HKD: {product.get('price_hkd')}")
                
                # Check year extraction status
                if product.get('year'):
                    if product.get('year') in [2025, 2026, 2027]:
                        print(f"⚠️  Year might be problematic: {product.get('year')}")
                    else:
                        print(f"✅ SUCCESS: Valid year found: {product.get('year')}")
                else:
                    print("ℹ️  No year found (returning null - better than wrong year)")
                    
            else:
                print("❌ Failed to extract product details")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_rolex_sample():
    """Test with a sample of Rolex products"""
    
    print("\n" + "="*60)
    print("TESTING ROLEX PRODUCTS SAMPLE:")
    print("="*60)
    
    scraper = AristoHKScraper(delay=1.0)
    
    try:
        # Get a few Rolex products to test
        products = scraper.scrape_all(start_page=1, end_page=1, specific_brand='rolex')
        
        if products:
            print(f"\nTested {len(products)} Rolex products:")
            print("-" * 40)
            
            years_found = 0
            years_null = 0 
            years_problematic = 0
            
            for i, product in enumerate(products[:8], 1):  # Show first 8
                year = product.get('year')
                
                if year is None:
                    status = "NULL"
                    years_null += 1
                elif year >= 2025:
                    status = "PROBLEMATIC"
                    years_problematic += 1
                else:
                    status = "✅ VALID"
                    years_found += 1
                
                print(f"{i:2d}. {product.get('reference'):20s} | Year: {str(year):4s} | {status}")
            
            print(f"\nSUMMARY:")
            print(f"Valid years: {years_found}/{len(products[:8])} ({years_found/len(products[:8])*100:.1f}%)")
            print(f"Null years: {years_null}/{len(products[:8])} ({years_null/len(products[:8])*100:.1f}%)")  
            print(f"Problematic: {years_problematic}/{len(products[:8])} ({years_problematic/len(products[:8])*100:.1f}%)")
            
        else:
            print("No products scraped")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_improved_year_logic()
    test_rolex_sample()