# RockAuto.com Price Scraper

A Python-based web scraper for extracting product pricing and information from RockAuto.com.

## ⚠️ Important Legal Notice

**Before using this scraper:**
1. Review RockAuto's Terms of Service and robots.txt
2. Use responsibly with appropriate rate limiting
3. This tool is for educational/personal use only
4. Consider using RockAuto's official API if available
5. Respect website resources - don't overload their servers

## Features

- ✅ Search by part number
- ✅ Extract product details (price, brand, availability, etc.)
- ✅ Batch processing for multiple parts
- ✅ JSON export of results
- ✅ Rate limiting to be respectful of server resources
- ✅ Headless browser support
- ✅ Error handling and retries

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed

### Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt --break-system-packages

# Or install individually:
pip install selenium webdriver-manager beautifulsoup4 requests --break-system-packages
```

The scraper will automatically download and manage the Chrome WebDriver.

## Usage

### Command Line Interface

#### Search by Part Number
```bash
python rockauto_scraper.py --part "AC252709" --output results.json
```

#### Search with Custom Delay (be respectful!)
```bash
python rockauto_scraper.py --part "WIX51515" --delay 5 --headless
```

#### Show Browser Window (for debugging)
```bash
python rockauto_scraper.py --part "BOSCH3330"
```

### Python API

#### Basic Usage
```python
from rockauto_scraper import RockAutoScraper

# Create scraper instance
with RockAutoScraper(headless=True, delay=2) as scraper:
    # Search for a part
    results = scraper.search_by_part_number("AC252709")
    
    # Print results
    for product in results:
        print(f"Part: {product['part_number']}")
        print(f"Price: {product['price']}")
        print(f"Brand: {product['brand']}")
        print()
```

#### Batch Processing
```python
from rockauto_scraper import RockAutoScraper
import json

part_numbers = ["AC252709", "WIX51515", "BOSCH3330"]
all_results = {}

with RockAutoScraper(headless=True, delay=3) as scraper:
    for part_num in part_numbers:
        results = scraper.search_by_part_number(part_num)
        all_results[part_num] = results

# Save results
with open('results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
```

#### Price Comparison
```python
from rockauto_scraper import RockAutoScraper

with RockAutoScraper() as scraper:
    results = scraper.search_by_part_number("51515")
    
    # Sort by price
    sorted_results = sorted(
        results,
        key=lambda x: float(x['price'].replace('$', '').replace(',', ''))
    )
    
    for product in sorted_results:
        print(f"{product['price']} - {product['brand']}")
```

## Command Line Arguments

| Argument | Description | Required | Default |
|----------|-------------|----------|---------|
| `--part` | Part number to search | Yes* | - |
| `--year` | Vehicle year | No** | - |
| `--make` | Vehicle make | No** | - |
| `--model` | Vehicle model | No** | - |
| `--headless` | Run without browser window | No | False |
| `--output` | Output JSON file path | No | rockauto_results.json |
| `--delay` | Delay between requests (seconds) | No | 2 |

\* Either `--part` or vehicle information (year/make/model) must be provided
\** Vehicle search is partially implemented

## Output Format

Results are returned as a list of dictionaries:

```json
[
  {
    "part_number": "AC252709",
    "description": "Engine Oil Filter",
    "brand": "AC Delco",
    "price": "$8.99",
    "core_charge": "N/A",
    "availability": "In Stock"
  }
]
```

## Examples

Run the example script to see different use cases:

```bash
python example_usage.py
```

This includes:
1. Simple part number search
2. Batch processing multiple parts
3. Price comparison across brands

## Troubleshooting

### Chrome/ChromeDriver Issues
If you encounter WebDriver issues:
```bash
# Update webdriver-manager
pip install --upgrade webdriver-manager --break-system-packages
```

### Timeout Errors
Increase the delay parameter:
```python
scraper = RockAutoScraper(delay=5)  # 5 seconds between requests
```

### Element Not Found
RockAuto may update their website structure. You may need to:
1. Update CSS selectors in `_extract_single_product()`
2. Check the actual HTML structure using browser DevTools
3. Adjust wait times in the code

### Rate Limiting
If you're getting blocked:
1. Increase the delay parameter (minimum 2-3 seconds recommended)
2. Use residential proxies (not included in this script)
3. Reduce request frequency

## Ethical Considerations

- ✅ Use reasonable rate limiting (2-5 seconds between requests)
- ✅ Identify your bot with appropriate User-Agent
- ✅ Check robots.txt before scraping
- ✅ Don't scrape during peak hours
- ❌ Don't create excessive load on their servers
- ❌ Don't use for commercial purposes without permission
- ❌ Don't redistribute scraped data

## Technical Notes

### Class Selectors May Need Updates

RockAuto may change their HTML structure. The following selectors are used:

- `.listing-inline` - Product container
- `.listing-inline-part-number` - Part number
- `.listing-inline-title` - Description
- `.listing-inline-brand` - Manufacturer
- `.listing-inline-price` - Price
- `.listing-inline-core` - Core charge
- `.listing-inline-availability` - Stock status

If scraping fails, inspect the page HTML and update these selectors in the code.

### Alternative: Use Existing Services

Consider using established scraping services instead:
- **Apify**: Has pre-built RockAuto scraper
- **Oxylabs**: E-commerce scraping API with RockAuto support
- **ScrapeHero**: Auto parts data extraction service

## Limitations

- Vehicle search by year/make/model is not fully implemented
- Does not handle pagination automatically
- Cannot handle CAPTCHAs (use proxies or services if needed)
- Requires active Chrome browser
- May break if RockAuto updates their site structure

## Future Improvements

- [ ] Implement full vehicle search functionality
- [ ] Add pagination support for multiple result pages
- [ ] Add proxy rotation support
- [ ] Implement CAPTCHA handling
- [ ] Add more detailed product information extraction
- [ ] Support for other browsers (Firefox, Edge)
- [ ] Add caching to avoid redundant requests
- [ ] Better error recovery and retry logic

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is for educational purposes only. Use at your own risk and ensure compliance with RockAuto's Terms of Service.

## Disclaimer

This tool is not affiliated with, authorized, maintained, sponsored or endorsed by RockAuto LLC or any of its affiliates or subsidiaries. Use of this tool is at your own risk.