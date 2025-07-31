#!/usr/bin/env python3
"""
Run improved scraper to generate updated response.json
"""

from aristohk_scraper import AristoHKScraper
import json

def run_improved_scraper():
    """Run the improved scraper and save results"""
    
    # Initialize scraper with a small delay to be respectful
    scraper = AristoHKScraper(delay=1.0)
    
    print("Starting improved scraping of aristohk.com...")
    print("This will focus on Richard Mille products first to validate improvements")
    
    # First, let's scrape just Richard Mille to see the improvements
    try:
        print("Scraping Richard Mille products...")
        products = scraper.scrape_all(start_page=1, end_page=2, specific_brand='richard-mille')
        
        if products:
            print(f"✓ Successfully scraped {len(products)} Richard Mille products")
            
            # Show sample of improvements
            print("\nSample of improved Richard Mille extractions:")
            print("-" * 60)
            
            for i, product in enumerate(products[:5]):  # Show first 5
                print(f"{i+1}. {product.get('reference')} - Year: {product.get('year')} - Price: HK${product.get('price_hkd')}")
            
            # Save the improved results
            scraper.save_to_json(products, 'improved_richard_mille.json')
            print(f"\n✓ Saved to improved_richard_mille.json")
            
            # Count how many have proper RM references
            proper_rm_refs = sum(1 for p in products if p.get('reference', '').startswith('RM') and len(p.get('reference', '')) > 3)
            print(f"✓ {proper_rm_refs}/{len(products)} products have proper RM references")
            
            # Count how many have reasonable years (not 2025)
            reasonable_years = sum(1 for p in products if p.get('year') and p.get('year') != 2025)
            print(f"✓ {reasonable_years}/{len(products)} products have reasonable years (not 2025)")
            
        else:
            print("✗ No products were scraped")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    run_improved_scraper()