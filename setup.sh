#!/bin/bash
# Quick Setup Script for DHS Tracker

echo "=================================="
echo "DHS Tracker - Quick Setup"
echo "=================================="
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements_full.txt

# Check ChromeDriver
echo ""
echo "Checking ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  ChromeDriver not found"
    echo ""
    echo "Please install ChromeDriver:"
    echo "  Mac:    brew install chromedriver"
    echo "  Linux:  sudo apt-get install chromium-chromedriver"
    echo "  Windows: Download from https://chromedriver.chromium.org/"
    echo ""
    read -p "Press Enter after installing ChromeDriver..."
fi
echo "✓ ChromeDriver found"

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data
mkdir -p logs
echo "✓ Directories created"

# Run initial scrape
echo ""
echo "=================================="
echo "Ready to run initial scrape!"
echo "=================================="
echo ""
echo "This will:"
echo "  1. Scrape the DHS website"
echo "  2. Create your historical database"
echo "  3. Take about 5-10 minutes"
echo ""
read -p "Run initial scrape now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting scrape..."
    python3 dhs_tracker.py --max-pages 20 --visible
    
    echo ""
    echo "=================================="
    echo "Setup Complete! 🎉"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "  1. Launch dashboard: streamlit run dashboard.py"
    echo "  2. Update data: python3 dhs_tracker.py"
    echo "  3. Read docs: README_COMPLETE.md"
    echo ""
else
    echo ""
    echo "Setup complete (without initial scrape)"
    echo ""
    echo "To run scrape later:"
    echo "  python3 dhs_tracker.py --max-pages 20"
    echo ""
    echo "To launch dashboard:"
    echo "  streamlit run dashboard.py"
    echo ""
fi
