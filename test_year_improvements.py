#!/usr/bin/env python3
"""
Run improved scraper to demonstrate year extraction improvements
"""

from aristohk_scraper import AristoHKScraper
import json

def test_year_improvements():
    """Test year extraction improvements on multiple products"""
    
    scraper = AristoHKScraper(delay=1.0)
    
    print("Testing improved year extraction on multiple products...")
    print("=" * 60)
    
    try:
        # Test with Rolex products first (they had the most null years)
        print("Scraping Rolex products to test year improvements...")
        products = scraper.scrape_all(start_page=1, end_page=1, specific_brand='rolex')
        
        if products:
            print(f"✓ Successfully scraped {len(products)} Rolex products")
            
            # Analyze year extraction results
            years_found = sum(1 for p in products if p.get('year'))
            years_null = sum(1 for p in products if p.get('year') is None)
            years_2025 = sum(1 for p in products if p.get('year') == 2025)
            
            print(f"\nYEAR EXTRACTION RESULTS:")
            print(f"Products with valid years: {years_found}/{len(products)} ({years_found/len(products)*100:.1f}%)")
            print(f"Products with null years: {years_null}/{len(products)} ({years_null/len(products)*100:.1f}%)")
            print(f"Products with 2025 (problematic): {years_2025}/{len(products)} ({years_2025/len(products)*100:.1f}%)")
            
            # Show some examples
            print(f"\nSAMPLE RESULTS:")
            print("-" * 40)
            for i, product in enumerate(products[:8]):  # Show first 8
                year_status = "✅" if product.get('year') else "⚠️"
                print(f"{i+1}. {product.get('reference')} - Year: {product.get('year')} {year_status}")
            
            # Save results
            scraper.save_to_json(products, 'improved_year_rolex.json')
            print(f"\n✓ Saved results to improved_year_rolex.json")
            
            # Find products that now have years (that likely had null before)
            products_with_years = [p for p in products if p.get('year')]
            if products_with_years:
                print(f"\nEXAMPLES OF IMPROVED YEAR EXTRACTION:")
                print("-" * 50)
                for i, p in enumerate(products_with_years[:5]):
                    print(f"{i+1}. {p.get('reference')} - {p.get('year')} - URL: {p.get('product_url')}")
                    
        else:
            print("❌ No products were scraped")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    test_year_improvements()