#!/bin/bash
# Helper script to publish Code Sage to PyPI

set -e  # Exit on error

echo "🚀 Code Sage PyPI Publishing Script"
echo "===================================="
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Run this script from the project root."
    exit 1
fi

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install/upgrade required tools
echo "📦 Installing/upgrading publishing tools..."
pip install --upgrade pip setuptools wheel twine build

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Build the package
echo ""
echo "🔨 Building package..."
python -m build

# Check the package
echo ""
echo "✅ Checking package..."
twine check dist/*

# Show what will be uploaded
echo ""
echo "📦 Package contents:"
ls -lh dist/

# Ask which repository to upload to
echo ""
echo "Where do you want to upload?"
echo "1) TestPyPI (test.pypi.org) - Recommended for first time"
echo "2) PyPI (pypi.org) - Production"
echo "3) Cancel"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📤 Uploading to TestPyPI..."
        echo "You'll need a TestPyPI account: https://test.pypi.org/account/register/"
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Upload successful!"
        echo "Test installation with:"
        echo "pip install --index-url https://test.pypi.org/simple/ code-sage"
        ;;
    2)
        echo ""
        echo "📤 Uploading to PyPI..."
        echo "You'll need a PyPI account: https://pypi.org/account/register/"
        read -p "Are you sure? This is PRODUCTION! (yes/N) " confirm
        if [ "$confirm" = "yes" ]; then
            twine upload dist/*
            echo ""
            echo "🎉 Upload successful!"
            echo "Your package is now live at: https://pypi.org/project/code-sage/"
            echo ""
            echo "Install with:"
            echo "pip install code-sage"
        else
            echo "❌ Upload cancelled."
        fi
        ;;
    3)
        echo "❌ Upload cancelled."
        exit 0
        ;;
    *)
        echo "❌ Invalid choice."
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
