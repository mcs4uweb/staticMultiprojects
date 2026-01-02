"""
Simple example usage of RockAuto scraper
"""

from rockauto_scraper import RockAutoScraper
import json


def example_part_number_search():
    """Example: Search by part number"""
    print("=" * 60)
    print("Example 1: Search by Part Number")
    print("=" * 60)
    
    with RockAutoScraper(headless=False, delay=2) as scraper:
        # Search for a specific part number
        results = scraper.search_by_part_number("AC252709")
        
        if results:
            print(f"\nFound {len(results)} products:\n")
            for i, product in enumerate(results, 1):
                print(f"Product {i}:")
                print(f"  Part Number: {product.get('part_number', 'N/A')}")
                print(f"  Description: {product.get('description', 'N/A')}")
                print(f"  Brand: {product.get('brand', 'N/A')}")
                print(f"  Price: {product.get('price', 'N/A')}")
                print(f"  Core Charge: {product.get('core_charge', 'N/A')}")
                print(f"  Availability: {product.get('availability', 'N/A')}")
                print()
        else:
            print("No results found")


def example_batch_search():
    """Example: Search multiple part numbers"""
    print("=" * 60)
    print("Example 2: Batch Part Number Search")
    print("=" * 60)
    
    part_numbers = [
        "AC252709",
        "WIX51515",
        "BOSCH3330"
    ]
    
    all_results = {}
    
    with RockAutoScraper(headless=True, delay=3) as scraper:
        for part_num in part_numbers:
            print(f"\nSearching for: {part_num}")
            results = scraper.search_by_part_number(part_num)
            all_results[part_num] = results
            
            if results:
                print(f"  Found {len(results)} products")
            else:
                print(f"  No results found")
    
    # Save all results
    with open('batch_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nBatch results saved to batch_results.json")


def example_price_comparison():
    """Example: Compare prices for the same part from different brands"""
    print("=" * 60)
    print("Example 3: Price Comparison")
    print("=" * 60)
    
    with RockAutoScraper(headless=True, delay=2) as scraper:
        results = scraper.search_by_part_number("51515")  # Generic part number
        
        if results:
            # Sort by price (assuming price format like "$12.99")
            try:
                sorted_results = sorted(
                    results,
                    key=lambda x: float(x.get('price', '0').replace('$', '').replace(',', ''))
                )
                
                print(f"\nFound {len(sorted_results)} products, sorted by price:\n")
                for product in sorted_results:
                    price = product.get('price', 'N/A')
                    brand = product.get('brand', 'N/A')
                    part_num = product.get('part_number', 'N/A')
                    print(f"  {price:10} - {brand:20} - Part# {part_num}")
                    
            except Exception as e:
                print(f"Error sorting prices: {e}")
                print("Results (unsorted):")
                for product in results:
                    print(f"  {product.get('price', 'N/A')} - {product.get('brand', 'N/A')}")
        else:
            print("No results found")


if __name__ == "__main__":
    print("\nRockAuto Scraper Examples")
    print("=" * 60)
    
    # Choose which example to run
    print("\nSelect an example:")
    print("1. Search by part number")
    print("2. Batch search multiple parts")
    print("3. Price comparison")
    print("0. Run all examples")
    
    choice = input("\nEnter choice (0-3): ").strip()
    
    if choice == "1":
        example_part_number_search()
    elif choice == "2":
        example_batch_search()
    elif choice == "3":
        example_price_comparison()
    elif choice == "0":
        example_part_number_search()
        print("\n" + "=" * 60 + "\n")
        example_batch_search()
        print("\n" + "=" * 60 + "\n")
        example_price_comparison()
    else:
        print("Invalid choice")