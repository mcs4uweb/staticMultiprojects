#!/bin/bash

# RockAuto Scraper Setup Script

echo "========================================"
echo "RockAuto Scraper Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --break-system-packages

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Quick Start:"
    echo "  1. Search for a part:"
    echo "     python rockauto_scraper.py --part \"AC252709\""
    echo ""
    echo "  2. Run examples:"
    echo "     python example_usage.py"
    echo ""
    echo "  3. View help:"
    echo "     python rockauto_scraper.py --help"
    echo ""
else
    echo ""
    echo "❌ Installation failed"
    echo "Try installing packages individually:"
    echo "  pip install selenium --break-system-packages"
    echo "  pip install webdriver-manager --break-system-packages"
    echo "  pip install beautifulsoup4 --break-system-packages"
    echo "  pip install requests --break-system-packages"
fi