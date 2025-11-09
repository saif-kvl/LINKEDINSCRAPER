#!/usr/bin/env python
"""
Quick start script for LinkedIn Scraper
This script provides an easy way to run the scraper with common configurations
"""

import os
import sys

def main():
    print("LinkedIn Profile Scraper - Quick Start")
    print("=" * 50)
    print()
    
    # Check if profile URLs exist
    if os.path.exists("profile_urls.txt"):
        with open("profile_urls.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            if urls:
                print(f"Found {len(urls)} URLs in profile_urls.txt")
            else:
                print("No URLs found in profile_urls.txt")
                print("Please add LinkedIn profile URLs to profile_urls.txt")
                return
    else:
        print("profile_urls.txt not found.")
        print("Please create profile_urls.txt and add LinkedIn profile URLs (one per line)")
        return
    
    # Run the scraper
    print("\nStarting scraper...")
    print("Make sure you have:")
    print("1. Installed all dependencies: pip install -r requirements.txt")
    print("2. Chrome browser installed")
    print("3. Added profile URLs to profile_urls.txt or config.py")
    print()
    
    input("Press Enter to continue...")
    
    # Import and run the main scraper
    try:
        from linkedin_scraper import main as scraper_main
        scraper_main()
    except ImportError as e:
        print(f"Error importing scraper: {e}")
        print("Make sure linkedin_scraper.py is in the same directory")
    except Exception as e:
        print(f"Error running scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

