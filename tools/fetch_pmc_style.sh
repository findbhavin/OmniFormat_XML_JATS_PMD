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
TEMP_DIR="/tmp/pmc_style_download_$$"
BUNDLE_URL="https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz"
BUNDLE_FILE="nlm-style-5.47.tar.gz"

echo "==================================================================="
echo "PMC Style Checker XSLT Bundle Downloader (nlm-style-5.47)"
echo "==================================================================="
echo ""
echo "Target directory: $PMC_STYLE_DIR"
echo "Bundle URL: $BUNDLE_URL"
echo ""

# Check if already downloaded
if [ -f "$PMC_STYLE_DIR/nlm-stylechecker.xsl" ]; then
    echo "✅ nlm-stylechecker.xsl already exists in $PMC_STYLE_DIR"
    echo ""
    echo "Existing files:"
    ls -lh "$PMC_STYLE_DIR" 2>/dev/null || echo "  (directory exists but cannot list files)"
    echo ""
    echo "To re-download, remove the directory first:"
    echo "  rm -rf '$PMC_STYLE_DIR'"
    echo "  ./tools/fetch_pmc_style.sh"
    echo ""
    exit 0
fi

# Check if curl or wget is available
if command -v curl &> /dev/null; then
    DOWNLOADER="curl"
    echo "✓ Using curl for download"
elif command -v wget &> /dev/null; then
    DOWNLOADER="wget"
    echo "✓ Using wget for download"
else
    echo "❌ Error: Neither curl nor wget is installed"
    echo "   Please install curl or wget and try again"
    exit 1
fi

# Check if tar is available
if ! command -v tar &> /dev/null; then
    echo "❌ Error: tar is not installed"
    echo "   Please install tar and try again"
    exit 1
fi

# Create directories
mkdir -p "$NLM_547_DIR"
mkdir -p "$TEMP_DIR"

# Download the bundle
echo "📥 Downloading PMC Style Checker bundle..."
echo ""

cd "$TEMP_DIR"

if [ "$DOWNLOADER" = "curl" ]; then
    if curl -L -o "$BUNDLE_FILE" "$BUNDLE_URL"; then
        echo "✅ Downloaded $BUNDLE_FILE"
    else
        echo "❌ Download failed"
        echo ""
        echo "Manual download instructions:"
        echo "1. Visit: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/"
        echo "2. Download: $BUNDLE_URL"
        echo "3. Extract: tar -xzf $BUNDLE_FILE"
        echo "4. Copy all files to: $PMC_STYLE_DIR"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
else
    if wget -O "$BUNDLE_FILE" "$BUNDLE_URL"; then
        echo "✅ Downloaded $BUNDLE_FILE"
    else
        echo "❌ Download failed"
        echo ""
        echo "Manual download instructions:"
        echo "1. Visit: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/"
        echo "2. Download: $BUNDLE_URL"
        echo "3. Extract: tar -xzf $BUNDLE_FILE"
        echo "4. Copy all files to: $PMC_STYLE_DIR"
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Extract the bundle
echo ""
echo "📦 Extracting bundle..."
echo ""

if tar -xzf "$BUNDLE_FILE"; then
    echo "✅ Extracted $BUNDLE_FILE"
else
    echo "❌ Extraction failed"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Find the extracted directory (may vary in structure)
EXTRACTED_DIR=""
for dir in nlm-style-5.47 nlm-stylechecker nlm-style*/; do
    if [ -d "$dir" ]; then
        EXTRACTED_DIR="$dir"
        break
    fi
done

if [ -z "$EXTRACTED_DIR" ]; then
    # Files might be extracted directly to current directory
    echo "⚠️  Could not find extracted directory, checking current directory..."
    if [ -f "nlm-stylechecker.xsl" ]; then
        echo "✅ Found nlm-stylechecker.xsl in current directory"
        EXTRACTED_DIR="."
    else
        echo "❌ Could not locate extracted files"
        echo "   Contents of $TEMP_DIR:"
        ls -la
        rm -rf "$TEMP_DIR"
        exit 1
    fi
fi

# Copy files to target directory
echo ""
echo "📂 Installing files to $PMC_STYLE_DIR..."
echo ""

cp -r "$EXTRACTED_DIR"/* "$PMC_STYLE_DIR/"

# List installed files
echo "✅ Installed files:"
ls -lh "$PMC_STYLE_DIR"
echo ""

# Count files
FILE_COUNT=$(find "$PMC_STYLE_DIR" -type f | wc -l)
echo "Total files installed: $FILE_COUNT"
echo ""

# Cleanup
cd "$REPO_ROOT"
rm -rf "$TEMP_DIR"
echo "✅ Cleanup complete"
echo ""

echo "==================================================================="
echo "PMC Style Checker bundle installed successfully!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "1. Ensure xsltproc is installed:"
echo "   Ubuntu/Debian: sudo apt-get install xsltproc"
echo "   macOS: brew install libxslt"
echo "   Alpine: apk add libxslt"
echo ""
echo "2. Verify installation:"
echo "   which xsltproc"
echo ""
echo "3. Test manually:"
echo "   xsltproc $PMC_STYLE_DIR/nlm-stylechecker.xsl output/article.xml > pmc_report.html"
echo ""
echo "4. Run a conversion - PMC style checker will run automatically"
echo "==================================================================="
echo ""
echo "The MasterPipeline will automatically detect and use these files."
echo ""
