# LinkedIn Profile Scraper

## ⚠️ IMPORTANT WARNINGS

**This tool is for educational purposes only.**

- **Terms of Service**: LinkedIn's Terms of Service prohibit automated scraping
- **Legal Risks**: May violate laws like GDPR, CFAA, etc.
- **Account Risk**: Your LinkedIn account may be banned
- **Use Responsibly**: Only use with proper authorization and compliance

## Features

- ✅ Selenium-based web scraping with Chrome driver
- ✅ Random user agent rotation
- ✅ Proxy rotation support (residential proxies)
- ✅ LinkedIn login automation
- ✅ Manual login fallback option
- ✅ Anti-detection measures (random delays, browser fingerprinting evasion)
- ✅ CSV export of profile data
- ✅ Extracts: Name, Headline, Location, About, Experience, Education, Skills, Connections

## Installation

### Quick Setup (Recommended)

Run the setup script:
```bash
python setup.py
```

This will:
- Check Python version
- Install all dependencies
- Check for Chrome browser
- Create `.env` file

### Manual Setup

1. **Install Python 3.8+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome Browser** (if not already installed)

4. **Set up environment variables (optional):**
   - Run `python setup.py` to create `.env` file, or
   - Create `.env` file manually and add your LinkedIn credentials (optional - you can login manually)

## Usage

### Basic Usage

1. **Add profile URLs** using one of these methods:
   
   **Method 1: Use profile_urls.txt (Recommended)**
   - Edit `profile_urls.txt`
   - Add one LinkedIn profile URL per line
   - Example:
     ```
     https://www.linkedin.com/in/profile-1/
     https://www.linkedin.com/in/profile-2/
     https://www.linkedin.com/in/profile-3/
     ```
   
   **Method 2: Use config.py**
   - Edit `config.py`
   - Add URLs to the `PROFILE_URLS` list:
     ```python
     PROFILE_URLS = [
         "https://www.linkedin.com/in/profile-1/",
         "https://www.linkedin.com/in/profile-2/",
     ]
     ```

2. **Run the scraper:**
   ```bash
   python linkedin_scraper.py
   ```
   
   Or use the quick start script:
   ```bash
   python run_scraper.py
   ```

3. **Login:**
   - If credentials are in `.env`, it will attempt automatic login
   - Otherwise, login manually in the opened browser window
   - Press Enter after logging in

4. **Wait for scraping to complete:**
   - The scraper will visit each profile with random delays
   - Data will be saved to `linkedin_profiles.csv`

### Using Proxies

1. **Add proxies to the code:**
   ```python
   PROXY_LIST = [
       "123.45.67.89:8080",
       "user:pass@98.76.54.32:3128",
   ]
   ```

2. **Enable proxy usage:**
   - Set `USE_PROXY=True` in `.env`, or
   - Modify `USE_PROXY = True` in the code

### Alternative: Login via Google

If LinkedIn blocks direct access, you can modify the code to:
1. Search for LinkedIn on Google
2. Click the first result to access LinkedIn
3. This may help bypass some restrictions

## Configuration

### Delay Settings

Modify the delay range in `scrape_profiles()`:
```python
scraped_data = scraper.scrape_profiles(PROFILE_URLS, delay_range=(5, 10))
```

### Headless Mode

To run without opening a browser window:
```python
scraper.driver = scraper.setup_driver(headless=True)
```

## Output

The scraper saves data to `linkedin_profiles.csv` with the following columns:
- `url`: Profile URL
- `name`: Full name
- `headline`: Professional headline
- `location`: Location
- `about`: About section
- `experience`: Work experience
- `education`: Education history
- `skills`: Skills list
- `connections`: Connection count (if visible)

## Troubleshooting

### Login Issues

- LinkedIn may require CAPTCHA or 2FA verification
- Complete verification manually if prompted
- Consider using a test account

### Scraping Fails

- LinkedIn may block automated access
- Try increasing delays between requests
- Use residential proxies
- Rotate user agents more frequently
- Limit the number of profiles per session

### Element Not Found Errors

- LinkedIn's HTML structure may change
- Update CSS selectors in `scrape_profile()` method
- Some profiles may have different layouts

## Legal and Ethical Considerations

1. **Respect Terms of Service**: Be aware that this violates LinkedIn's ToS
2. **Get Consent**: Only scrape publicly available data with proper authorization
3. **Rate Limiting**: Don't overload LinkedIn's servers
4. **Data Privacy**: Comply with GDPR and other privacy regulations
5. **Use Test Accounts**: Consider using test accounts to avoid risking your main account

## Limitations

- LinkedIn actively blocks automated scraping
- May require manual intervention for CAPTCHA/2FA
- Profile structure may vary, causing extraction failures
- Some data may require being logged in and connected
- Rate limiting may trigger blocks

## Alternative Approaches

If direct scraping doesn't work, consider:
1. **LinkedIn API**: Official API (requires approval, limited access)
2. **Third-party APIs**: Services like LinkedIn data providers (may have costs)
3. **Public Data Sources**: Other sites that aggregate LinkedIn data
4. **Manual Collection**: For small datasets

## Support

This is an educational project. Use at your own risk.

## License

This project is for educational purposes only. Use responsibly and in compliance with all applicable laws and terms of service.

