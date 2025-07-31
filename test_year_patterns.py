#!/usr/bin/env python3
"""
Test year extraction patterns on actual product pages
"""

import requests
from bs4 import BeautifulSoup
import re

def test_year_extraction(url):
    """Test year extraction on a specific URL"""
    
    print(f"Testing year extraction for: {url}")
    print("-" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        all_text = soup.get_text()
        
        print("PAGE CONTENT SAMPLE (first 2000 chars):")
        print(all_text[:2000])
        print("\n" + "="*60)
        
        # Test current patterns
        print("TESTING CURRENT PATTERNS:")
        
        # Current Release Year pattern
        release_year_pattern = r'Release Year[:\s]*(\d{4})'
        year_match = re.search(release_year_pattern, all_text, re.I)
        if year_match:
            print(f"✓ Found with 'Release Year' pattern: {year_match.group(1)}")
        else:
            print("✗ No match with 'Release Year' pattern")
        
        # Current other patterns
        other_patterns = [
            r'released in (\d{4})',
            r'(\d{4})\s*release',
        ]
        
        for pattern in other_patterns:
            year_match = re.search(pattern, all_text, re.I)
            if year_match:
                print(f"✓ Found with pattern '{pattern}': {year_match.group(1)}")
            else:
                print(f"✗ No match with pattern '{pattern}'")
        
        print("\n" + "="*60)
        print("TESTING ADDITIONAL PATTERNS:")
        
        # Test more patterns that might work
        additional_patterns = [
            r'Year[:\s]*(\d{4})',  # Just "Year: 2018"
            r'(\d{4})\s*Year',     # "2018 Year" 
            r'Production[:\s]*(\d{4})',  # "Production: 2018"
            r'Made[:\s]*(\d{4})',  # "Made: 2018"
            r'Circa[:\s]*(\d{4})', # "Circa: 2018"
            r'(\d{4})\s*model',    # "2018 model"
            r'model[:\s]*(\d{4})', # "model: 2018"
        ]
        
        for pattern in additional_patterns:
            year_match = re.search(pattern, all_text, re.I)
            if year_match:
                print(f"✓ Found with additional pattern '{pattern}': {year_match.group(1)}")
        
        print("\n" + "="*60)
        print("ALL 4-DIGIT YEARS FOUND IN TEXT:")
        all_years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', all_text)
        year_counts = {}
        for year in all_years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        for year, count in sorted(year_counts.items()):
            print(f"Year {year}: appears {count} times")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with a few URLs from the original response.json
    test_urls = [
        "https://aristohk.com/rolex/126610-ln-0001/25110",  # Rolex with null year
        "https://aristohk.com/rolex/126500-ln-0002/18692",  # Rolex 
    ]
    
    for url in test_urls:
        test_year_extraction(url)
        print("\n" + "="*80 + "\n")