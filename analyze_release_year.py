#!/usr/bin/env python3
"""
Analyze the HTML structure to find the Release Year field properly
"""

import requests
from bs4 import BeautifulSoup
import re

def analyze_release_year_structure(url):
    """Analyze how Release Year appears in the HTML structure"""
    
    print(f"Analyzing Release Year structure for: {url}")
    print("=" * 60)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for all text containing "Release Year"
        all_text = soup.get_text()
        
        print("1. SEARCHING IN ALL TEXT:")
        print("-" * 30)
        
        # Current pattern
        release_year_pattern = r'Release Year[:\s]*(\d{4})'
        year_match = re.search(release_year_pattern, all_text, re.I)
        if year_match:
            print(f"✓ Found with current pattern: {year_match.group(1)}")
            print(f"  Full match: '{year_match.group(0)}'")
        else:
            print("✗ Not found with current pattern")
        
        # Look for the context around "Release Year"
        release_year_context = []
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            if 'release year' in line.lower():
                # Get context: 2 lines before, current line, 2 lines after
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context = lines[start:end]
                release_year_context.extend(context)
        
        if release_year_context:
            print("\n2. CONTEXT AROUND 'RELEASE YEAR':")
            print("-" * 30)
            for line in release_year_context:
                line = line.strip()
                if line:
                    print(f"  '{line}'")
        
        print("\n3. LOOKING FOR STRUCTURED DATA:")
        print("-" * 30)
        
        # Look for table structures that might contain Release Year
        tables = soup.find_all(['table', 'div'], class_=True)
        for table in tables:
            text = table.get_text()
            if 'release year' in text.lower():
                print(f"Found in element: {table.name} with class: {table.get('class')}")
                print(f"Text content: {text.strip()[:200]}...")
                print()
        
        # Look for specific HTML patterns
        print("4. TESTING ALTERNATIVE PATTERNS:")
        print("-" * 30)
        
        alternative_patterns = [
            r'Release Year[:\s]*?(\d{4})',      # Non-greedy
            r'Release Year.*?(\d{4})',          # Any chars between
            r'Release\s*Year[:\s]*(\d{4})',     # With space in Release Year
            r'(?i)release\s*year[\s:]*(\d{4})', # Case insensitive with optional space/colon
        ]
        
        for pattern in alternative_patterns:
            year_match = re.search(pattern, all_text)
            if year_match:
                print(f"✓ Found with pattern '{pattern}': {year_match.group(1)}")
                print(f"  Full match: '{year_match.group(0)}'")
            else:
                print(f"✗ Not found with pattern '{pattern}'")
        
        print("\n5. ALL 4-DIGIT NUMBERS NEAR 'RELEASE YEAR':")
        print("-" * 30)
        
        # Find all occurrences of "Release Year" and look for nearby numbers
        for match in re.finditer(r'release year', all_text, re.I):
            start = max(0, match.start() - 50)
            end = min(len(all_text), match.end() + 50)
            context = all_text[start:end]
            years = re.findall(r'\d{4}', context)
            if years:
                print(f"Near 'Release Year': {years}")
                print(f"Context: '{context.strip()}'")
                print()
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test URLs from the images
    test_urls = [
        "https://aristohk.com/rolex/126231-0023/23914",  # Should have Release Year: 2018
        "https://aristohk.com/richard-mille/rm-65-01-black-carbon-tpt/18560",  # Richard Mille
    ]
    
    for url in test_urls:
        analyze_release_year_structure(url)
        print("\n" + "="*80 + "\n")