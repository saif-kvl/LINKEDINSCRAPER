#!/usr/bin/env python
"""
Setup script for LinkedIn Scraper
This script helps set up the environment and install dependencies
"""

import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_chrome():
    """Check if Chrome is installed"""
    print("\n🌐 Checking for Chrome browser...")
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            return True
    
    print("⚠️  Chrome not found in common locations")
    print("Please make sure Chrome is installed")
    return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        print("\n📝 Creating .env file...")
        env_content = """# LinkedIn Credentials (Optional - you can login manually)
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=

# Proxy Settings (Optional)
USE_PROXY=False

# Note: Add proxy list to config.py if needed
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created")
        print("⚠️  Please edit .env file to add your credentials (optional)")
    else:
        print("✅ .env file already exists")

def main():
    print("=" * 60)
    print("LinkedIn Scraper - Setup Script")
    print("=" * 60)
    print()
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Setup incomplete. Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Check Chrome
    check_chrome()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit profile_urls.txt and add LinkedIn profile URLs")
    print("2. (Optional) Edit .env file to add LinkedIn credentials")
    print("3. (Optional) Edit config.py to customize settings")
    print("4. Run: python linkedin_scraper.py")
    print("\n⚠️  Remember: LinkedIn scraping may violate Terms of Service")
    print("   Use this tool responsibly and at your own risk")

if __name__ == "__main__":
    main()

