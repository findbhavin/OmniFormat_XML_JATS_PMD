#!/bin/bash
#
# fetch_pmc_style.sh
# Downloads the PMC Style Checker XSLT bundle (nlm-style-5.47)
# 
# Usage: ./tools/fetch_pmc_style.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PMC_STYLE_DIR="$REPO_ROOT/pmc-stylechecker/nlm-style-5.47"
TEMP_DIR="/tmp/pmc_style_download"
BUNDLE_URL="https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz"
BUNDLE_FILE="nlm-style-5.47.tar.gz"

echo "==================================================================="
echo "PMC Style Checker XSLT Bundle Downloader (nlm-style-5.47)"
echo "==================================================================="
echo ""

# Check if tar is available
if ! command -v tar &> /dev/null; then
    echo "❌ Error: tar is not installed"
    echo "   Please install tar and try again"
    exit 1
fi

# Check if curl or wget is available
DOWNLOADER=""
if command -v curl &> /dev/null; then
    DOWNLOADER="curl"
elif command -v wget &> /dev/null; then
    DOWNLOADER="wget"
else
    echo "❌ Error: Neither curl nor wget is installed"
    echo "   Please install curl or wget and try again"
    exit 1
fi

# Check if already downloaded
if [ -d "$PMC_STYLE_DIR" ] && [ -f "$PMC_STYLE_DIR/nlm-stylechecker.xsl" ]; then
    echo "✅ nlm-style-5.47 bundle already exists at $PMC_STYLE_DIR"
    echo ""
    echo "Files in bundle:"
    find "$PMC_STYLE_DIR" -type f | head -20
    echo ""
    echo "To re-download, remove the directory first:"
    echo "   rm -rf $PMC_STYLE_DIR"
    exit 0
fi

# Create directories
mkdir -p "$PMC_STYLE_DIR"
mkdir -p "$TEMP_DIR"

echo "📥 Downloading PMC Style Checker bundle from PMC..."
echo "   Source: $BUNDLE_URL"
echo ""

# Download the bundle
cd "$TEMP_DIR"
if [ "$DOWNLOADER" = "curl" ]; then
    echo "Using curl to download..."
    if curl -L -o "$BUNDLE_FILE" "$BUNDLE_URL"; then
        echo "✅ Downloaded $BUNDLE_FILE"
    else
        echo "❌ Failed to download bundle"
        echo ""
        echo "Manual download instructions:"
        echo "1. Visit: $BUNDLE_URL"
        echo "2. Save to: $TEMP_DIR/$BUNDLE_FILE"
        echo "3. Run this script again"
        exit 1
    fi
else
    echo "Using wget to download..."
    if wget -O "$BUNDLE_FILE" "$BUNDLE_URL"; then
        echo "✅ Downloaded $BUNDLE_FILE"
    else
        echo "❌ Failed to download bundle"
        echo ""
        echo "Manual download instructions:"
        echo "1. Visit: $BUNDLE_URL"
        echo "2. Save to: $TEMP_DIR/$BUNDLE_FILE"
        echo "3. Run this script again"
        exit 1
    fi
fi

# Optional: Verify file size (basic sanity check)
FILE_SIZE=$(stat -f%z "$BUNDLE_FILE" 2>/dev/null || stat -c%s "$BUNDLE_FILE" 2>/dev/null)
if [ "$FILE_SIZE" -lt 10000 ]; then
    echo "⚠️  Warning: Downloaded file seems too small ($FILE_SIZE bytes)"
    echo "   The download may have failed or the URL may be incorrect"
fi

echo ""
echo "📦 Extracting bundle to $PMC_STYLE_DIR..."
tar -xzf "$BUNDLE_FILE"

# Find the extracted directory (may be nlm-style-5.47 or similar)
EXTRACTED_DIR=$(find . -maxdepth 1 -type d -name "nlm-style*" | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "⚠️  Warning: Could not find extracted directory"
    echo "   Attempting to extract directly to target..."
    tar -xzf "$BUNDLE_FILE" -C "$PMC_STYLE_DIR"
else
    echo "Found extracted directory: $EXTRACTED_DIR"
    # Move contents preserving directory structure
    cp -r "$EXTRACTED_DIR"/* "$PMC_STYLE_DIR/" || cp -r "$EXTRACTED_DIR"/. "$PMC_STYLE_DIR/"
fi

echo "✅ Extraction complete!"
echo ""

# List extracted files
echo "📄 Extracted files:"
find "$PMC_STYLE_DIR" -type f | head -20
FILE_COUNT=$(find "$PMC_STYLE_DIR" -type f | wc -l)
echo ""
echo "Total files: $FILE_COUNT"

# Verify key files exist
echo ""
echo "🔍 Verifying key files..."
if [ -f "$PMC_STYLE_DIR/nlm-stylechecker.xsl" ]; then
    echo "✅ nlm-stylechecker.xsl found"
elif [ -f "$PMC_STYLE_DIR/nlm-style-5-0.xsl" ]; then
    echo "✅ nlm-style-5-0.xsl found"
else
    echo "⚠️  Warning: No known XSLT files found in expected locations"
    echo "   Please verify the bundle contents manually"
fi

# Check for LICENSE/README
if [ -f "$PMC_STYLE_DIR/LICENSE" ] || [ -f "$PMC_STYLE_DIR/LICENSE.txt" ]; then
    echo "✅ LICENSE file found"
fi
if [ -f "$PMC_STYLE_DIR/README" ] || [ -f "$PMC_STYLE_DIR/README.md" ] || [ -f "$PMC_STYLE_DIR/README.txt" ]; then
    echo "✅ README file found"
fi

# Cleanup
cd "$REPO_ROOT"
rm -rf "$TEMP_DIR"

echo ""
echo "==================================================================="
echo "✅ PMC Style Checker setup complete!"
echo ""
echo "📁 Installation directory: $PMC_STYLE_DIR"
echo ""
echo "Next steps:"
echo "1. Ensure xsltproc is installed:"
echo "      which xsltproc"
echo "   Or install:"
echo "      apt-get install xsltproc (Ubuntu/Debian)"
echo "      brew install libxslt (macOS)"
echo "      apk add libxslt (Alpine)"
echo ""
echo "2. Test manually:"
echo "      xsltproc $PMC_STYLE_DIR/nlm-stylechecker.xsl output/article.xml > pmc_report.html"
echo ""
echo "3. Run a conversion and check validation_report.json for pmc_stylechecker results"
echo "==================================================================="
