#!/usr/bin/env python3
"""
Generate complete improved response.json with all the improvements
"""

from aristohk_scraper import AristoHKScraper
import json

def generate_improved_response():
    """Generate a new response.json with all improvements"""
    
    print("Generating improved response.json...")
    print("This may take a while as it scrapes multiple brands")
    print("-" * 50)
    
    # Initialize scraper
    scraper = AristoHKScraper(delay=0.8)  # Reasonable delay
    
    try:
        # First scrape a limited sample to demonstrate improvements
        # You can modify this to scrape all brands if needed
        brands_to_test = ['richard-mille', 'rolex']  # Test with main brands
        
        all_products = []
        
        for brand in brands_to_test:
            print(f"Scraping {brand}...")
            try:
                products = scraper.scrape_all(start_page=1, end_page=1, specific_brand=brand)
                if products:
                    all_products.extend(products)
                    print(f"✓ Scraped {len(products)} products from {brand}")
                else:
                    print(f"⚠ No products found for {brand}")
            except Exception as e:
                print(f"✗ Error scraping {brand}: {e}")
                continue
        
        if all_products:
            # Save the improved results
            scraper.save_to_json(all_products, 'improved_response.json')
            
            print(f"\n✓ Successfully generated improved_response.json with {len(all_products)} products")
            
            # Analyze the improvements
            richard_mille_products = [p for p in all_products if p.get('brand') == 'RICHARD MILLE']
            rolex_products = [p for p in all_products if p.get('brand') == 'ROLEX']
            
            print("\nIMPROVEMENT ANALYSIS:")
            print("-" * 30)
            
            if richard_mille_products:
                proper_rm_refs = sum(1 for p in richard_mille_products 
                                   if p.get('reference', '').startswith('RM') and len(p.get('reference', '')) > 3)
                print(f"Richard Mille: {proper_rm_refs}/{len(richard_mille_products)} have proper RM references")
                
                # Show some examples
                print("Examples:")
                for i, p in enumerate(richard_mille_products[:3]):
                    print(f"  {i+1}. {p.get('reference')} (was: URL-based parsing)")
            
            if rolex_products:
                reasonable_years = sum(1 for p in rolex_products 
                                     if p.get('year') and p.get('year') != 2025)
                print(f"Rolex: {reasonable_years}/{len(rolex_products)} have reasonable years (not 2025)")
            
            # Show year distribution
            year_2025_count = sum(1 for p in all_products if p.get('year') == 2025)
            year_none_count = sum(1 for p in all_products if p.get('year') is None)
            year_reasonable_count = sum(1 for p in all_products 
                                      if p.get('year') and p.get('year') != 2025)
            
            print(f"\nYear Distribution:")
            print(f"  Reasonable years: {year_reasonable_count}/{len(all_products)}")
            print(f"  Year = None: {year_none_count}/{len(all_products)}")
            print(f"  Year = 2025: {year_2025_count}/{len(all_products)}")
            
        else:
            print("✗ No products were scraped")
            
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == "__main__":
    generate_improved_response()