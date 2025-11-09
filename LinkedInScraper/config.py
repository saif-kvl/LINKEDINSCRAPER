"""
Configuration file for LinkedIn Scraper
Edit this file to customize your scraping settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LinkedIn Credentials (Optional)
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')

# Proxy Settings
USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'

# Proxy List (Add your proxies here)
# Format: "ip:port" or "user:pass@ip:port"
PROXY_LIST = [
    # Example: "123.45.67.89:8080",
    # Example: "user:pass@98.76.54.32:3128",
]

# Profile URLs to scrape
# Add up to 20 LinkedIn profile URLs
PROFILE_URLS = [
    # Add your profile URLs here
    # Example: "https://www.linkedin.com/in/example-profile-1/",
    # Example: "https://www.linkedin.com/in/example-profile-2/",
]

# Scraping Settings
DELAY_RANGE = (5, 10)  # Minimum and maximum delay between requests (seconds)
HEADLESS_MODE = False  # Set to True to run browser in headless mode
MAX_RETRIES = 3  # Maximum number of retries for failed profiles

# Output Settings
OUTPUT_FILE = "linkedin_profiles.csv"  # Output CSV filename

# Browser Settings
WINDOW_SIZE = "1920,1080"  # Browser window size
USER_AGENT_ROTATION = True  # Rotate user agents

# LinkedIn Settings
LOGIN_VIA_GOOGLE = False  # Set to True to access LinkedIn via Google search
GOOGLE_SEARCH_URL = "https://www.google.com/search?q=linkedin+login"  # Google search URL

