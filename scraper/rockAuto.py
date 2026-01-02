"""
RockAuto.com Product Price Scraper
Scrapes product information including prices from RockAuto.com

Usage:
    python rockauto_scraper.py --part "AC Delco 252-709" --year 2015 --make Toyota --model Camry
    
Requirements:
    pip install selenium webdriver-manager beautifulsoup4 requests --break-system-packages
"""

import argparse
import time
import json
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


class RockAutoScraper:
    """Scraper for RockAuto.com auto parts pricing"""
    
    def __init__(self, headless: bool = True, delay: int = 2):
        """
        Initialize the scraper
        
        Args:
            headless: Run browser in headless mode
            delay: Delay between requests in seconds (be respectful!)
        """
        self.delay = delay
        self.base_url = "https://www.rockauto.com"
        self.driver = self._setup_driver(headless)
        
    def _setup_driver(self, headless: bool) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add options to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Suppress logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        return driver
    
    def search_by_part_number(self, part_number: str) -> List[Dict]:
        """
        Search for a specific part number
        
        Args:
            part_number: The part number to search for
            
        Returns:
            List of product dictionaries with pricing information
        """
        print(f"Searching for part number: {part_number}")
        
        try:
            # Navigate to homepage
            self.driver.get(self.base_url)
            time.sleep(self.delay)
            
            # Find and fill search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "catalog"))
            )
            search_box.clear()
            search_box.send_keys(part_number)
            search_box.submit()
            
            # Wait for results to load
            time.sleep(self.delay)
            
            # Extract product information
            products = self._extract_products()
            
            return products
            
        except TimeoutException:
            print("Timeout waiting for search results")
            return []
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def search_by_vehicle(self, year: int, make: str, model: str, 
                         category: Optional[str] = None) -> Dict:
        """
        Search by vehicle information
        
        Args:
            year: Vehicle year
            make: Vehicle make (e.g., "Toyota")
            model: Vehicle model (e.g., "Camry")
            category: Optional part category (e.g., "Brakes")
            
        Returns:
            Dictionary with vehicle parts information
        """
        print(f"Searching for: {year} {make} {model}")
        
        try:
            self.driver.get(self.base_url)
            time.sleep(self.delay)
            
            # Click on vehicle selector
            # Note: This is simplified - actual implementation may need
            # to handle dropdowns and dynamic loading
            
            # You would need to interact with the year/make/model selectors
            # This requires analyzing the actual page structure
            
            print("Vehicle search requires specific selector implementation")
            print("Please use part number search for now")
            
            return {}
            
        except Exception as e:
            print(f"Error during vehicle search: {e}")
            return {}
    
    def _extract_products(self) -> List[Dict]:
        """
        Extract product information from the current page
        
        Returns:
            List of product dictionaries
        """
        products = []
        
        try:
            # Wait for product listings to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "listing-inline"))
            )
            
            # Find all product listings
            product_elements = self.driver.find_elements(By.CLASS_NAME, "listing-inline")
            
            for element in product_elements:
                try:
                    product_data = self._extract_single_product(element)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    print(f"Error extracting product: {e}")
                    continue
            
        except TimeoutException:
            print("No products found or page took too long to load")
        except Exception as e:
            print(f"Error extracting products: {e}")
        
        return products
    
    def _extract_single_product(self, element) -> Optional[Dict]:
        """
        Extract data from a single product element
        
        Args:
            element: Selenium WebElement containing product data
            
        Returns:
            Dictionary with product information
        """
        try:
            product = {}
            
            # Extract part number (may need adjustment based on actual page structure)
            try:
                product['part_number'] = element.find_element(
                    By.CLASS_NAME, "listing-inline-part-number"
                ).text.strip()
            except NoSuchElementException:
                product['part_number'] = "N/A"
            
            # Extract description
            try:
                product['description'] = element.find_element(
                    By.CLASS_NAME, "listing-inline-title"
                ).text.strip()
            except NoSuchElementException:
                product['description'] = "N/A"
            
            # Extract brand/manufacturer
            try:
                product['brand'] = element.find_element(
                    By.CLASS_NAME, "listing-inline-brand"
                ).text.strip()
            except NoSuchElementException:
                product['brand'] = "N/A"
            
            # Extract price
            try:
                price_element = element.find_element(By.CLASS_NAME, "listing-inline-price")
                product['price'] = price_element.text.strip()
            except NoSuchElementException:
                product['price'] = "N/A"
            
            # Extract core charge if applicable
            try:
                core_element = element.find_element(By.CLASS_NAME, "listing-inline-core")
                product['core_charge'] = core_element.text.strip()
            except NoSuchElementException:
                product['core_charge'] = "N/A"
            
            # Extract availability
            try:
                product['availability'] = element.find_element(
                    By.CLASS_NAME, "listing-inline-availability"
                ).text.strip()
            except NoSuchElementException:
                product['availability'] = "N/A"
            
            return product
            
        except Exception as e:
            print(f"Error extracting single product: {e}")
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description='Scrape product prices from RockAuto.com'
    )
    parser.add_argument(
        '--part',
        type=str,
        help='Part number to search for'
    )
    parser.add_argument(
        '--year',
        type=int,
        help='Vehicle year'
    )
    parser.add_argument(
        '--make',
        type=str,
        help='Vehicle make'
    )
    parser.add_argument(
        '--model',
        type=str,
        help='Vehicle model'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no browser window)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='rockauto_results.json',
        help='Output JSON file (default: rockauto_results.json)'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=2,
        help='Delay between requests in seconds (default: 2)'
    )
    
    args = parser.parse_args()
    
    # Validate input
    if not args.part and not (args.year and args.make and args.model):
        parser.error("Either --part or (--year, --make, --model) must be provided")
    
    # Run scraper
    with RockAutoScraper(headless=args.headless, delay=args.delay) as scraper:
        if args.part:
            results = scraper.search_by_part_number(args.part)
        else:
            results = scraper.search_by_vehicle(args.year, args.make, args.model)
        
        # Display results
        print(f"\nFound {len(results)} products:")
        for i, product in enumerate(results, 1):
            print(f"\n--- Product {i} ---")
            for key, value in product.items():
                print(f"{key}: {value}")
        
        # Save to JSON
        if results:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()