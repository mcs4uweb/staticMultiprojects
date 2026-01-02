# RockAuto Scraper Configuration
# Copy this file to config.py and customize as needed

# Browser settings
HEADLESS = True  # Run browser in headless mode (no window)
BROWSER_DELAY = 2  # Delay between requests in seconds (be respectful!)

# Output settings
DEFAULT_OUTPUT_FILE = "rockauto_results.json"
SAVE_SCREENSHOTS = False  # Save screenshots on errors
SCREENSHOT_DIR = "screenshots"

# Scraping behavior
MAX_RETRIES = 3  # Number of retries on failure
TIMEOUT = 10  # Timeout for page loads in seconds
IMPLICIT_WAIT = 10  # Implicit wait time in seconds

# User Agent (customize if needed)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# CSS Selectors (update these if RockAuto changes their HTML structure)
SELECTORS = {
    'search_box': 'catalog',  # name attribute
    'product_container': 'listing-inline',  # class name
    'part_number': 'listing-inline-part-number',
    'description': 'listing-inline-title',
    'brand': 'listing-inline-brand',
    'price': 'listing-inline-price',
    'core_charge': 'listing-inline-core',
    'availability': 'listing-inline-availability',
}

# Rate limiting (IMPORTANT: Be respectful!)
# Minimum delay between requests to avoid overloading the server
MIN_DELAY = 2  # seconds
MAX_DELAY = 5  # seconds
USE_RANDOM_DELAY = True  # Use random delays between MIN and MAX

# Proxy settings (optional - for advanced users)
USE_PROXY = False
PROXY_SERVER = None  # Format: "http://username:password@proxy_ip:port"
PROXY_LIST = []  # List of proxies to rotate through

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "rockauto_scraper.log"
ENABLE_FILE_LOGGING = True

# Advanced options
CACHE_RESULTS = True  # Cache results to avoid duplicate requests
CACHE_EXPIRY = 3600  # Cache expiry time in seconds (1 hour)
CACHE_DIR = ".cache"