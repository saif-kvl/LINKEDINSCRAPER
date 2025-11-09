"""
LinkedIn Profile Scraper

WARNING: This script is for educational purposes only.
LinkedIn's Terms of Service prohibit automated scraping.
Use at your own risk. Accounts may be banned.
Ensure compliance with applicable laws (GDPR, CFAA, etc.).
"""

import time
import random
import csv
import os
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import config, fall back to environment variables if config doesn't exist
try:
    import config
except ImportError:
    config = None


class LinkedInScraper:
    def __init__(self, use_proxy: bool = False, proxy_list: Optional[List[str]] = None):
        """
        Initialize LinkedIn Scraper
        
        Args:
            use_proxy: Whether to use proxy rotation
            proxy_list: List of proxy servers in format "ip:port" or "user:pass@ip:port"
        """
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        self.ua = UserAgent()
        self.driver = None
        self.scraped_profiles = []
        
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return self.ua.random
    
    def get_proxy(self) -> Optional[str]:
        """Get next proxy from the list (round-robin)"""
        if not self.use_proxy or not self.proxy_list:
            return None
        proxy = self.proxy_list[self.current_proxy_index % len(self.proxy_list)]
        self.current_proxy_index += 1
        return proxy
    
    def setup_driver(self, headless: bool = False) -> webdriver.Chrome:
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Random user agent
        user_agent = self.get_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Additional options to avoid detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        # Keep browser alive
        chrome_options.add_experimental_option("detach", True)
        
        # Proxy configuration
        proxy = self.get_proxy()
        if proxy:
            chrome_options.add_argument(f'--proxy-server=http://{proxy}')
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Set timeouts
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        # Execute script to remove webdriver property
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            print("Navigating to LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(random.uniform(2, 4))
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "linkedin.com/in/" in self.driver.current_url:
                print("Login successful!")
                return True
            elif "challenge" in self.driver.current_url.lower():
                print("LinkedIn is asking for verification. Please complete manually.")
                input("Press Enter after completing verification...")
                return True
            else:
                print("Login may have failed. Current URL:", self.driver.current_url)
                return False
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False
    
    def login_via_google(self, profile_url: str = None) -> bool:
        """
        Alternative login method: Open LinkedIn via Google search
        
        Args:
            profile_url: Optional LinkedIn profile URL to search for
            
        Returns:
            True if successful
        """
        try:
            if profile_url:
                # Search for the specific LinkedIn profile
                search_query = profile_url.replace("https://www.linkedin.com/in/", "").replace("/", "")
                google_url = f"https://www.google.com/search?q=site:linkedin.com/in/{search_query}"
            else:
                # Search for LinkedIn login page
                google_url = "https://www.google.com/search?q=linkedin.com/login"
            
            print(f"Opening LinkedIn via Google search: {google_url}")
            self.driver.get(google_url)
            time.sleep(random.uniform(3, 5))
            
            # Try multiple selectors for Google search results
            selectors = [
                "div.g a h3",  # Standard Google result
                "a h3",  # Alternative selector
                "div[data-ved] a h3",  # Another variant
            ]
            
            for selector in selectors:
                try:
                    search_results = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if search_results:
                        # Find LinkedIn result
                        for result in search_results:
                            parent_link = result.find_element(By.XPATH, "./ancestor::a")
                            href = parent_link.get_attribute("href")
                            if "linkedin.com" in href:
                                print(f"Clicking on LinkedIn result: {href}")
                                parent_link.click()
                                time.sleep(random.uniform(3, 5))
                                return True
                except:
                    continue
            
            print("Could not find LinkedIn result in Google search")
            return False
        except Exception as e:
            print(f"Error with Google login method: {str(e)}")
            return False
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict[str, str]]:
        """
        Scrape a single LinkedIn profile
        
        Args:
            profile_url: LinkedIn profile URL
            
        Returns:
            Dictionary with profile data or None if failed
        """
        try:
            # Check if driver is still alive
            if not self.driver:
                print(f"Driver not available for {profile_url}")
                return None
            
            # Test if session is alive with retry
            max_retries = 3
            for retry in range(max_retries):
                try:
                    self.driver.current_url  # Test if session is alive
                    break
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"Session test failed, retrying ({retry + 1}/{max_retries})...")
                        time.sleep(1)
                    else:
                        print(f"Browser session expired. Cannot scrape {profile_url}")
                        return None
            
            print(f"Scraping profile: {profile_url}")
            
            # Navigate to profile with error handling
            try:
                self.driver.get(profile_url)
                time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
            except Exception as e:
                if "target window already closed" in str(e) or "invalid session" in str(e):
                    print(f"Browser closed while navigating to {profile_url}")
                    return None
                # Try to continue anyway
                time.sleep(2)
            
            profile_data = {
                'url': profile_url,
                'name': '',
                'headline': '',
                'location': '',
                'about': '',
                'experience': '',
                'education': '',
                'skills': '',
                'connections': ''
            }
            
            # Check if we're on a login page or error page
            current_url = self.driver.current_url.lower()
            page_text = self.driver.page_source.lower()
            
            if "login" in current_url or "authwall" in current_url or "join" in page_text[:500]:
                # Try to extract what we can from the page
                try:
                    title = self.driver.title
                    if title and "linkedin" in title.lower():
                        profile_data['name'] = title.replace(" | LinkedIn", "").strip()
                except:
                    pass
                # Still continue to try to get other data
            else:
                # Extract name - try multiple selectors
                name_selectors = [
                    "h1.text-heading-xlarge",
                    "h1.break-words",
                    "h1.top-card-layout__title",
                    "h1",
                    "div.ph5 h1",
                    ".pv-text-details__left-panel h1",
                    "h1[class*='text-heading']"
                ]
                profile_data['name'] = "Not found"
                for selector in name_selectors:
                    try:
                        name_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        name_text = name_element.text.strip()
                        if name_text and name_text not in ["Join LinkedIn", "Sign in"]:
                            profile_data['name'] = name_text
                            break
                    except:
                        continue
                
                # Fallback: try to get from page title
                if profile_data['name'] == "Not found":
                    try:
                        title = self.driver.title
                        if title and "|" in title:
                            profile_data['name'] = title.split("|")[0].strip()
                    except:
                        pass
            
            # Extract headline - try multiple selectors
            headline_selectors = [
                ".text-body-medium.break-words",
                ".text-body-medium",
                ".pv-text-details__left-panel .text-body-medium",
                "div.ph5 .text-body-medium"
            ]
            profile_data['headline'] = "Not found"
            for selector in headline_selectors:
                try:
                    headline = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if headline.text.strip() and headline.text.strip() != profile_data['name']:
                        profile_data['headline'] = headline.text.strip()
                        break
                except:
                    continue
            
            # Extract location - try multiple selectors
            location_selectors = [
                ".text-body-small.inline.t-black--light.break-words",
                ".text-body-small",
                ".pv-text-details__left-panel .text-body-small",
                "span.text-body-small"
            ]
            profile_data['location'] = "Not found"
            for selector in location_selectors:
                try:
                    location = self.driver.find_element(By.CSS_SELECTOR, selector)
                    loc_text = location.text.strip()
                    if loc_text and '·' not in loc_text:  # Avoid connection count
                        profile_data['location'] = loc_text
                        break
                except:
                    continue
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            
            # Extract About section - try multiple methods
            about_selectors = [
                ("#about", ".inline-show-more-text"),
                ("#about", ".pv-about-section .pv-about__summary-text"),
                ("section[data-section='summary']", ".inline-show-more-text"),
            ]
            profile_data['about'] = "Not found"
            for section_selector, text_selector in about_selectors:
                try:
                    about_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    about_text = about_section.find_element(By.CSS_SELECTOR, text_selector)
                    if about_text.text.strip():
                        profile_data['about'] = about_text.text.strip()
                        break
                except:
                    continue
            
            # Extract Experience - try multiple selectors
            experience_selectors = [
                ("#experience", ".pvs-list__paged-list-item"),
                ("#experience", ".pv-entity__summary-info"),
                ("section[data-section='experience']", ".pvs-list__paged-list-item"),
            ]
            experiences = []
            for section_selector, item_selector in experience_selectors:
                try:
                    experience_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    experience_items = experience_section.find_elements(By.CSS_SELECTOR, item_selector)
                    for item in experience_items[:5]:  # Limit to first 5
                        try:
                            exp_text = item.text.strip()
                            if exp_text and exp_text not in experiences:
                                experiences.append(exp_text)
                        except:
                            continue
                    if experiences:
                        break
                except:
                    continue
            profile_data['experience'] = " | ".join(experiences) if experiences else "Not found"
            
            # Extract Education - try multiple selectors
            education_selectors = [
                ("#education", ".pvs-list__paged-list-item"),
                ("#education", ".pv-entity__summary-info"),
                ("section[data-section='education']", ".pvs-list__paged-list-item"),
            ]
            educations = []
            for section_selector, item_selector in education_selectors:
                try:
                    education_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    education_items = education_section.find_elements(By.CSS_SELECTOR, item_selector)
                    for item in education_items[:5]:  # Limit to first 5
                        try:
                            edu_text = item.text.strip()
                            if edu_text and edu_text not in educations:
                                educations.append(edu_text)
                        except:
                            continue
                    if educations:
                        break
                except:
                    continue
            profile_data['education'] = " | ".join(educations) if educations else "Not found"
            
            # Extract Skills - try multiple selectors
            skills_selectors = [
                ("[data-section='skills']", ".mr1.t-bold span[aria-hidden='true']"),
                ("#skills", ".pv-skill-category-entity__name"),
                ("section[data-section='skills']", ".pv-skill-entity__skill-name"),
            ]
            skills = []
            for section_selector, skill_selector in skills_selectors:
                try:
                    skills_section = self.driver.find_element(By.CSS_SELECTOR, section_selector)
                    skill_items = skills_section.find_elements(By.CSS_SELECTOR, skill_selector)
                    for skill in skill_items[:10]:  # Limit to first 10
                        try:
                            skill_text = skill.text.strip()
                            if skill_text and skill_text not in skills:
                                skills.append(skill_text)
                        except:
                            continue
                    if skills:
                        break
                except:
                    continue
            profile_data['skills'] = ", ".join(skills) if skills else "Not found"
            
            # Extract connections (if visible) - try multiple selectors
            connection_selectors = [
                ".pv-top-card-v2-ctas__connections",
                ".t-bold span[aria-hidden='true']",
                ".pv-top-card__connections",
            ]
            profile_data['connections'] = "Not found"
            for selector in connection_selectors:
                try:
                    connections = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for conn in connections:
                        conn_text = conn.text.strip()
                        if 'connection' in conn_text.lower() or any(char.isdigit() for char in conn_text):
                            profile_data['connections'] = conn_text
                            break
                    if profile_data['connections'] != "Not found":
                        break
                except:
                    continue
            
            print(f"Successfully scraped: {profile_data['name']}")
            return profile_data
            
        except TimeoutException:
            print(f"Timeout while scraping {profile_url}")
            return None
        except Exception as e:
            error_msg = str(e)
            if "target window already closed" in error_msg or "invalid session id" in error_msg or "web view not found" in error_msg:
                print(f"Browser window closed. Cannot continue scraping.")
                print("Please restart the scraper and ensure the browser window stays open.")
                return None
            print(f"Error scraping {profile_url}: {error_msg[:100]}")  # Limit error message length
            return None
    
    def scrape_profiles(self, profile_urls: List[str], delay_range: tuple = (3, 8)) -> List[Dict[str, str]]:
        """
        Scrape multiple LinkedIn profiles
        
        Args:
            profile_urls: List of LinkedIn profile URLs
            delay_range: Tuple of (min, max) delay between requests in seconds
            
        Returns:
            List of profile data dictionaries
        """
        scraped_data = []
        self.scraped_profiles = []  # Reset scraped profiles list
        
        for i, url in enumerate(profile_urls, 1):
            print(f"\n--- Scraping profile {i}/{len(profile_urls)} ---")
            
            # Check if driver is still alive before each request
            if not self.driver:
                print("Driver not available. Stopping scraping.")
                break
            try:
                self.driver.current_url  # Test if session is alive
            except:
                print("Browser session expired. Stopping scraping.")
                print(f"Successfully scraped {len(scraped_data)} profiles before session expired.")
                break
            
            profile_data = self.scrape_profile(url)
            if profile_data:
                scraped_data.append(profile_data)
                self.scraped_profiles.append(profile_data)  # Store for recovery
                # Save incrementally every 5 profiles
                if len(scraped_data) % 5 == 0:
                    print(f"\n⚠️  Saving progress: {len(scraped_data)} profiles scraped so far...")
                    self.save_to_csv(scraped_data, "linkedin_profiles.csv", append=False)
            
            # Random delay between requests
            if i < len(profile_urls):
                delay = random.uniform(delay_range[0], delay_range[1])
                print(f"Waiting {delay:.2f} seconds before next request...")
                time.sleep(delay)
        
        return scraped_data
    
    def save_to_csv(self, data: List[Dict[str, str]], filename: str = "linkedin_profiles.csv", append: bool = False):
        """Save scraped data to CSV file"""
        if not data:
            print("No data to save.")
            return
        
        df = pd.DataFrame(data)
        if append and os.path.exists(filename):
            # Append to existing file
            existing_df = pd.read_csv(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
            df = df.drop_duplicates(subset=['url'], keep='last')  # Remove duplicates
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nData saved to {filename}")
        print(f"Total profiles scraped: {len(df)}")
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("Browser closed.")


def load_profile_urls_from_file(filename: str = "profile_urls.txt") -> List[str]:
    """Load profile URLs from a text file"""
    urls = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and 'linkedin.com/in/' in line:
                    # Ensure URL has https://
                    if not line.startswith('http'):
                        line = 'https://' + line
                    urls.append(line)
    return urls


def main():
    """Main function to run the scraper"""
    
    # WARNING
    print("=" * 80)
    print("WARNING: LinkedIn scraping may violate Terms of Service.")
    print("Use this tool responsibly and at your own risk.")
    print("Ensure compliance with applicable laws and regulations.")
    print("=" * 80)
    print()
    
    # Load configuration from config.py if available, otherwise use environment variables
    if config:
        LINKEDIN_EMAIL = config.LINKEDIN_EMAIL
        LINKEDIN_PASSWORD = config.LINKEDIN_PASSWORD
        USE_PROXY = config.USE_PROXY
        PROXY_LIST = config.PROXY_LIST
        PROFILE_URLS = config.PROFILE_URLS
        DELAY_RANGE = config.DELAY_RANGE
        HEADLESS_MODE = config.HEADLESS_MODE
        OUTPUT_FILE = config.OUTPUT_FILE
        LOGIN_VIA_GOOGLE = config.LOGIN_VIA_GOOGLE
    else:
        LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL', '')
        LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD', '')
        USE_PROXY = os.getenv('USE_PROXY', 'False').lower() == 'true'
        PROXY_LIST = []
        PROFILE_URLS = []
        DELAY_RANGE = (5, 10)
        HEADLESS_MODE = False
        OUTPUT_FILE = "linkedin_profiles.csv"
        LOGIN_VIA_GOOGLE = False
    
    # Try to load URLs from file if no URLs in config
    if not PROFILE_URLS:
        PROFILE_URLS = load_profile_urls_from_file("profile_urls.txt")
    
    # If still no URLs, prompt user
    if not PROFILE_URLS:
        print("No profile URLs found!")
        print("Please either:")
        print("1. Add URLs to config.py (PROFILE_URLS list)")
        print("2. Add URLs to profile_urls.txt (one per line)")
        print("3. Or edit linkedin_scraper.py and add URLs directly")
        return
    
    print(f"Found {len(PROFILE_URLS)} profile URLs to scrape")
    
    # Initialize scraper
    scraper = LinkedInScraper(use_proxy=USE_PROXY, proxy_list=PROXY_LIST)
    
    try:
        # Setup driver
        print("Setting up Chrome driver...")
        scraper.driver = scraper.setup_driver(headless=HEADLESS_MODE)
        
        # Login
        if LOGIN_VIA_GOOGLE:
            print("\nAttempting to access LinkedIn via Google...")
            scraper.login_via_google()
            print("Waiting 10 seconds for manual login if needed...")
            time.sleep(10)  # Wait for manual login
        elif LINKEDIN_EMAIL and LINKEDIN_PASSWORD:
            print("\nAttempting to login...")
            if not scraper.login(LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
                print("Login failed. Attempting to continue anyway...")
                print("Waiting 10 seconds in case you want to login manually...")
                time.sleep(10)  # Wait for manual login
        else:
            print("\nNo credentials provided.")
            print("Attempting to scrape public profile data...")
            print("Note: Some data may be limited without login.")
            # Try to access a profile directly first to see if we can get public data
            try:
                scraper.driver.get("https://www.linkedin.com/")
                time.sleep(2)
                print("Browser is ready. Starting to scrape...")
            except Exception as e:
                print(f"Error opening browser: {e}")
                print("Please ensure Chrome is installed and try again.")
                return
        
        # Scrape profiles
        print(f"\nStarting to scrape {len(PROFILE_URLS)} profiles...")
        scraped_data = scraper.scrape_profiles(PROFILE_URLS, delay_range=DELAY_RANGE)
        
        # Save to CSV
        if scraped_data:
            scraper.save_to_csv(scraped_data, OUTPUT_FILE)
            print(f"\n Successfully scraped {len(scraped_data)} out of {len(PROFILE_URLS)} profiles")
        else:
            print("No profiles were successfully scraped.")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
        if scraper.scraped_profiles:
            scraper.save_to_csv(scraper.scraped_profiles, OUTPUT_FILE)
            print(f"Partial data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

