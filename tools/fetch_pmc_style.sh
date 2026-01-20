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
PMC_STYLE_DIR="$REPO_ROOT/pmc-stylechecker"
NLM_BUNDLE_DIR="$PMC_STYLE_DIR/nlm-style-5.47"
TEMP_DIR="/tmp/pmc_style_download"

echo "==================================================================="
echo "PMC Style Checker XSLT Bundle Downloader (nlm-style-5.47)"
echo "==================================================================="
echo ""

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl is not installed"
    echo "   Please install curl and try again"
    exit 1
fi

# Check if tar is available
if ! command -v tar &> /dev/null; then
    echo "❌ Error: tar is not installed"
    echo "   Please install tar and try again"
    exit 1
fi

# Create directories
mkdir -p "$PMC_STYLE_DIR"
mkdir -p "$NLM_BUNDLE_DIR"
mkdir -p "$TEMP_DIR"

echo "📥 Downloading PMC Style Checker (nlm-style-5.47)..."
echo ""

# Official PMC Style Checker bundle URL
BUNDLE_URL="https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz"
BUNDLE_FILE="$TEMP_DIR/nlm-style-5.47.tar.gz"

echo "Downloading from: $BUNDLE_URL"
if curl -L -o "$BUNDLE_FILE" "$BUNDLE_URL" 2>&1 | grep -v "^[[:space:]]*$"; then
    echo "✅ Downloaded nlm-style-5.47.tar.gz"
    
    # Extract the bundle
    echo ""
    echo "📦 Extracting bundle..."
    cd "$TEMP_DIR"
    tar -xzf nlm-style-5.47.tar.gz
    
    # Find the extracted directory (may vary)
    if [ -d "nlm-style-5.47" ]; then
        EXTRACTED_DIR="nlm-style-5.47"
    elif [ -d "nlm-style" ]; then
        EXTRACTED_DIR="nlm-style"
    else
        # Find first directory created
        EXTRACTED_DIR=$(ls -d */ 2>/dev/null | head -1 | sed 's:/$::')
    fi
    
    if [ -z "$EXTRACTED_DIR" ]; then
        echo "⚠️  Could not find extracted directory"
        echo "   Listing files in $TEMP_DIR:"
        ls -la
        echo ""
        echo "   Please manually extract and copy files to:"
        echo "   $NLM_BUNDLE_DIR"
        exit 1
    fi
    
    echo "✅ Extracted to: $EXTRACTED_DIR"
    
    # Copy all files to the repository
    echo ""
    echo "📋 Copying files to repository..."
    cp -r "$TEMP_DIR/$EXTRACTED_DIR/"* "$NLM_BUNDLE_DIR/"
    
    echo "✅ Files copied to: $NLM_BUNDLE_DIR"
    
    # List installed files
    echo ""
    echo "📄 Installed files:"
    ls -lh "$NLM_BUNDLE_DIR"
    
    # Count XSL files
    XSL_COUNT=$(find "$NLM_BUNDLE_DIR" -name "*.xsl" | wc -l)
    echo ""
    echo "✅ Found $XSL_COUNT XSLT file(s)"
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    
else
    echo "❌ Failed to download bundle"
    echo ""
    echo "Manual installation:"
    echo "1. Visit https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/"
    echo "2. Download nlm-style-5.47.tar.gz"
    echo "3. Extract and copy files to: $NLM_BUNDLE_DIR"
    exit 1
fi

echo ""
echo "==================================================================="
echo "✅ PMC Style Checker setup complete!"
echo ""
echo "📁 Installation directory: $NLM_BUNDLE_DIR"
echo ""
echo "Next steps:"
echo "1. Ensure xsltproc is installed: which xsltproc"
echo "2. Run a conversion and check for pmc_style_report.html"
echo "3. Review validation_report.json for style check results"
echo "==================================================================="
