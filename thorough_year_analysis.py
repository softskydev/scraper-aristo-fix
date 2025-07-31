#!/usr/bin/env python3
"""
Test with a specific URL that should have Release Year data
"""

import requests
from bs4 import BeautifulSoup
import re

def find_release_year_thoroughly(url):
    """Thoroughly analyze the page structure to find Release Year"""
    
    print(f"Analyzing: {url}")
    print("=" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        all_text = soup.get_text()
        
        print("FULL PAGE TEXT SAMPLE (first 3000 chars):")
        print("-" * 50)
        print(all_text[:3000])
        print("-" * 50)
        
        # Search for any occurrence of "Release" and "Year"
        print("\nSEARCHING FOR 'RELEASE' AND 'YEAR':")
        print("-" * 30)
        
        release_lines = []
        year_lines = []
        
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if 'release' in line.lower():
                release_lines.append((i, line))
            if 'year' in line.lower() and any(char.isdigit() for char in line):
                year_lines.append((i, line))
        
        print(f"Lines containing 'release': {len(release_lines)}")
        for line_num, line in release_lines[:5]:  # Show first 5
            print(f"  Line {line_num}: '{line}'")
        
        print(f"\nLines containing 'year' with numbers: {len(year_lines)}")
        for line_num, line in year_lines[:10]:  # Show first 10
            print(f"  Line {line_num}: '{line}'")
        
        # Look for table-like structures
        print("\nLOOKING FOR TABLE STRUCTURES:")
        print("-" * 30)
        
        # Find all elements that might contain structured data
        potential_data_elements = soup.find_all(['table', 'div', 'dl', 'ul'], class_=True)
        
        for elem in potential_data_elements:
            elem_text = elem.get_text()
            if any(word in elem_text.lower() for word in ['year', 'release', 'detail', 'specification']):
                print(f"Element: {elem.name}, class: {elem.get('class')}")
                print(f"Text: {elem_text.strip()[:200]}...")
                print()
                
                # Look for year patterns in this element
                years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', elem_text)
                if years:
                    print(f"  Years found in this element: {years}")
                print()
        
        # Try to find any 4-digit years and their context
        print("ALL 4-DIGIT YEARS WITH CONTEXT:")
        print("-" * 30)
        
        for match in re.finditer(r'\b(19[5-9]\d|20[0-2]\d)\b', all_text):
            year = match.group(1)
            start = max(0, match.start() - 100)
            end = min(len(all_text), match.end() + 100)
            context = all_text[start:end].strip()
            
            # Clean up context
            context = ' '.join(context.split())
            print(f"Year {year}: ...{context}...")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Let's try a URL from your original response.json that had year: 2023
    test_urls = [
        "https://aristohk.com/rolex/126500-ln-0002/18692",  # This one worked before
    ]
    
    for url in test_urls:
        find_release_year_thoroughly(url)