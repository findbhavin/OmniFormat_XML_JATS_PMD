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
NLM_547_DIR="$PMC_STYLE_DIR/nlm-style-5.47"
TEMP_DIR="/tmp/pmc_style_download"
ARCHIVE_URL="https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz"
ARCHIVE_FILE="$TEMP_DIR/nlm-style-5.47.tar.gz"

echo "==================================================================="
echo "PMC Style Checker XSLT Bundle Downloader"
echo "Official NLM Style Checker 5.47"
echo "==================================================================="
echo ""
echo "Source: $ARCHIVE_URL"
echo "Target: $NLM_547_DIR"
echo ""

# Check if curl or wget is available
DOWNLOADER=""
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

echo ""
echo "📥 Downloading PMC Style Checker (nlm-style-5.47)..."
echo ""

# Download the archive
if [ "$DOWNLOADER" = "curl" ]; then
    if curl -L -f -o "$ARCHIVE_FILE" "$ARCHIVE_URL" 2>&1; then
        echo "✅ Downloaded nlm-style-5.47.tar.gz"
    else
        DOWNLOAD_FAILED=1
    fi
elif [ "$DOWNLOADER" = "wget" ]; then
    if wget -O "$ARCHIVE_FILE" "$ARCHIVE_URL" 2>&1; then
        echo "✅ Downloaded nlm-style-5.47.tar.gz"
    else
        DOWNLOAD_FAILED=1
    fi
fi

if [ -n "$DOWNLOAD_FAILED" ]; then
    echo ""
    echo "⚠️  Failed to download from official URL"
    echo ""
    echo "This may be due to:"
    echo "  - Network connectivity issues"
    echo "  - Firewall or proxy restrictions"
    echo "  - Archive URL has changed"
    echo ""
    echo "Manual installation steps:"
    echo "1. Visit: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/"
    echo "2. Download the nlm-style-5.47.tar.gz archive"
    echo "3. Extract: tar -xzf nlm-style-5.47.tar.gz"
    echo "4. Copy all .xsl files to: $NLM_547_DIR"
    echo "5. Preserve any LICENSE or documentation files"
    echo ""
    
    # Create a helpful placeholder
    cat > "$NLM_547_DIR/INSTALLATION_REQUIRED.txt" << 'EOF'
NLM Style Checker 5.47 Installation Required

The automatic download failed. Please install manually:

1. Download from: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
2. Extract the archive: tar -xzf nlm-style-5.47.tar.gz
3. Copy all .xsl files to this directory
4. Preserve the directory structure from the archive
5. Keep any LICENSE or attribution files

After installation, this directory should contain:
- nlm-stylechecker.xsl (main XSLT file)
- Supporting XSLT files from the bundle
- LICENSE or attribution files

The pipeline will automatically detect and use these files once installed.
EOF
    
    echo "📝 Created installation instructions in: $NLM_547_DIR/INSTALLATION_REQUIRED.txt"
    exit 1
fi

# Verify the download
if [ ! -f "$ARCHIVE_FILE" ]; then
    echo "❌ Error: Downloaded file not found"
    exit 1
fi

FILE_SIZE=$(stat -f%z "$ARCHIVE_FILE" 2>/dev/null || stat -c%s "$ARCHIVE_FILE" 2>/dev/null)
echo "📦 Archive size: $FILE_SIZE bytes"

# Optional: Verify checksum (if known)
# echo "🔐 Verifying checksum..."
# EXPECTED_SHA256="..."
# ACTUAL_SHA256=$(shasum -a 256 "$ARCHIVE_FILE" | cut -d' ' -f1)
# if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
#     echo "❌ Checksum verification failed"
#     exit 1
# fi

echo ""
echo "📂 Extracting archive..."
echo ""

# Extract to temp directory first
cd "$TEMP_DIR"
if tar -xzf "$ARCHIVE_FILE" 2>&1; then
    echo "✅ Archive extracted"
else
    echo "❌ Failed to extract archive"
    exit 1
fi

# Find the extracted directory (it may have a different name)
EXTRACTED_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "nlm-style*" | head -1)

if [ -z "$EXTRACTED_DIR" ]; then
    # Try finding any directory with .xsl files
    EXTRACTED_DIR=$(find "$TEMP_DIR" -maxdepth 2 -name "*.xsl" -print | head -1 | xargs dirname)
fi

if [ -z "$EXTRACTED_DIR" ]; then
    echo "⚠️  Could not find extracted directory with .xsl files"
    echo "   Checking for .xsl files in temp directory..."
    XSL_FILES=$(find "$TEMP_DIR" -name "*.xsl" | wc -l)
    if [ "$XSL_FILES" -gt 0 ]; then
        echo "   Found $XSL_FILES .xsl files, copying them..."
        find "$TEMP_DIR" -name "*.xsl" -exec cp {} "$NLM_547_DIR/" \;
        find "$TEMP_DIR" -name "LICENSE*" -exec cp {} "$NLM_547_DIR/" \; 2>/dev/null || true
        find "$TEMP_DIR" -name "README*" -exec cp {} "$NLM_547_DIR/" \; 2>/dev/null || true
    else
        echo "❌ No .xsl files found in archive"
        exit 1
    fi
else
    echo "📁 Found extracted content in: $(basename "$EXTRACTED_DIR")"
    echo ""
    echo "📋 Copying files to $NLM_547_DIR..."
    
    # Copy all .xsl files
    find "$EXTRACTED_DIR" -name "*.xsl" -exec cp -v {} "$NLM_547_DIR/" \;
    
    # Copy LICENSE and documentation files if present
    find "$EXTRACTED_DIR" -name "LICENSE*" -exec cp -v {} "$NLM_547_DIR/" \; 2>/dev/null || true
    find "$EXTRACTED_DIR" -name "README*" -not -name "*.md" -exec cp -v {} "$NLM_547_DIR/" \; 2>/dev/null || true
    find "$EXTRACTED_DIR" -name "*.txt" -exec cp -v {} "$NLM_547_DIR/" \; 2>/dev/null || true
fi

# Clean up temp files
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# List installed files
echo ""
echo "✅ PMC Style Checker installation complete!"
echo ""
echo "📁 Installation directory: $NLM_547_DIR"
echo "📄 Installed files:"
ls -lh "$NLM_547_DIR"
echo ""

# Count .xsl files
XSL_COUNT=$(find "$NLM_547_DIR" -name "*.xsl" -not -name "PLACEHOLDER.xsl" | wc -l)
echo "📊 Total .xsl files: $XSL_COUNT"

if [ "$XSL_COUNT" -eq 0 ]; then
    echo "⚠️  Warning: No .xsl files found in installation"
    echo "   The archive may not have contained the expected files"
    echo "   Please verify manually or try downloading from:"
    echo "   https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/"
fi

echo ""
echo "==================================================================="
echo "Next steps:"
echo "1. Verify xsltproc is installed: which xsltproc"
echo "   (Install with: apt-get install xsltproc / brew install libxslt)"
echo "2. Run a conversion to test the style checker"
echo "3. Check for pmc_style_report.html in output"
echo "4. Review validation_report.json for style check results"
echo "==================================================================="
echo ""
echo "The MasterPipeline will automatically detect and use these files."
echo ""
