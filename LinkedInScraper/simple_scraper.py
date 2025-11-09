"""
Simple LinkedIn Profile Scraper
Creates CSV with profile URLs and extracts basic information
"""

import time
import random
import os
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd


def load_profile_urls(filename: str = "profile_urls.txt") -> List[str]:
    """Load profile URLs from file"""
    urls = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and 'linkedin.com/in/' in line:
                    if not line.startswith('http'):
                        line = 'https://' + line
                    urls.append(line)
    return urls


def extract_basic_info(driver, url: str) -> Dict[str, str]:
    """Extract basic information from LinkedIn profile"""
    profile_data = {
        'url': url,
        'name': 'Not found',
        'headline': 'Not found',
        'location': 'Not found',
        'about': 'Not found',
        'experience': 'Not found',
        'education': 'Not found',
        'skills': 'Not found',
        'connections': 'Not found'
    }
    
    try:
        # Get page title
        title = driver.title
        if title and "|" in title:
            profile_data['name'] = title.split("|")[0].strip()
        
        # Try to extract name from page
        try:
            name_selectors = [
                "h1.text-heading-xlarge",
                "h1.break-words",
                "h1",
                ".top-card-layout__title"
            ]
            for selector in name_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text and text not in ["Join LinkedIn", "Sign in"]:
                        profile_data['name'] = text
                        break
                except:
                    continue
        except:
            pass
        
        # Try headline
        try:
            headline = driver.find_element(By.CSS_SELECTOR, ".text-body-medium")
            profile_data['headline'] = headline.text.strip()
        except:
            pass
        
    except Exception as e:
        print(f"Error extracting data: {str(e)[:50]}")
    
    return profile_data


def main():
    print("=" * 80)
    print("LinkedIn Profile Scraper - Simple Version")
    print("=" * 80)
    print()
    
    # Load URLs
    urls = load_profile_urls("profile_urls.txt")
    if not urls:
        print("No URLs found in profile_urls.txt")
        return
    
    print(f"Found {len(urls)} profile URLs")
    print("Setting up browser...")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    scraped_data = []
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(5)
        
        print("\nBrowser opened. You can login to LinkedIn if needed.")
        print("Starting to scrape profiles in 5 seconds...")
        time.sleep(5)
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                
                # Extract data
                data = extract_basic_info(driver, url)
                scraped_data.append(data)
                
                print(f"  ✓ Extracted: {data['name']}")
                
            except Exception as e:
                # Still add URL to CSV even if scraping failed
                scraped_data.append({
                    'url': url,
                    'name': 'Error accessing',
                    'headline': 'Not found',
                    'location': 'Not found',
                    'about': 'Not found',
                    'experience': 'Not found',
                    'education': 'Not found',
                    'skills': 'Not found',
                    'connections': 'Not found'
                })
                print(f"  ✗ Error: {str(e)[:50]}")
            
            # Delay between requests
            if i < len(urls):
                delay = random.uniform(2, 4)
                time.sleep(delay)
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")
    
    # Save to CSV
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        df.to_csv("linkedin_profiles.csv", index=False, encoding='utf-8-sig')
        print(f"\n CSV file created: linkedin_profiles.csv")
        print(f"   Total profiles: {len(scraped_data)}")
        print(f"\nPreview:")
        print(df[['url', 'name', 'headline']].head(10).to_string())
    else:
        print("\nNo data to save.")


if __name__ == "__main__":
    main()


