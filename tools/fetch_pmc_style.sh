#!/bin/bash
#
# fetch_pmc_style.sh
# Downloads the PMC Style Checker XSLT bundle (nlm-style-5.47)
# 
# Usage: ./tools/fetch_pmc_style.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PMC_STYLE_DIR="$SCRIPT_DIR/pmc_style"
TEMP_DIR="/tmp/pmc_style_download"

echo "==================================================================="
echo "PMC Style Checker XSLT Bundle Downloader"
echo "==================================================================="
echo ""

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo "❌ Error: curl is not installed"
    echo "   Please install curl and try again"
    exit 1
fi

# Check if unzip is available (if needed)
if ! command -v unzip &> /dev/null; then
    echo "⚠️  Warning: unzip is not installed"
    echo "   You may need to manually extract the downloaded files"
fi

# Create directories
mkdir -p "$PMC_STYLE_DIR"
mkdir -p "$TEMP_DIR"

echo "📥 Downloading PMC Style Checker (nlm-style-5.47)..."
echo ""

# PMC Style Checker is available from:
# https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
# The XSLT is part of the nlm-stylechecker package

# Download the style checker XSLT
STYLE_XSL_URL="https://dtd.nlm.nih.gov/tools/nlm-stylechecker/nlm-stylechecker.xsl"

echo "Downloading nlm-stylechecker.xsl..."
if curl -L -o "$PMC_STYLE_DIR/nlm-stylechecker.xsl" "$STYLE_XSL_URL" 2>/dev/null; then
    echo "✅ Downloaded nlm-stylechecker.xsl"
else
    echo "⚠️  Failed to download from primary URL"
    echo "   Creating placeholder file with instructions..."
    
    cat > "$PMC_STYLE_DIR/nlm-stylechecker.xsl" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!--
  PMC Style Checker XSLT Placeholder
  
  To use the PMC Style Checker:
  
  1. Download the official nlm-stylechecker from:
     https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
     
  2. Extract the nlm-stylechecker.xsl file
  
  3. Place it in this directory: tools/pmc_style/
  
  4. The conversion pipeline will automatically use it
  
  Note: The style checker requires xsltproc to be installed.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  
  <xsl:template match="/">
    <html>
      <head>
        <title>PMC Style Checker Not Available</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
          .message { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
          h1 { color: #d93025; }
          code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
        </style>
      </head>
      <body>
        <div class="message">
          <h1>⚠️ PMC Style Checker Not Available</h1>
          <p>The PMC Style Checker XSLT is not properly installed.</p>
          <h2>To install:</h2>
          <ol>
            <li>Visit <a href="https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/">PMC Style Checker</a></li>
            <li>Download the nlm-stylechecker XSLT files</li>
            <li>Place <code>nlm-stylechecker.xsl</code> in <code>tools/pmc_style/</code></li>
            <li>Run your conversion again</li>
          </ol>
          <p><strong>Note:</strong> The style checker requires <code>xsltproc</code> to be installed.</p>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
EOF
    echo "📝 Created placeholder file with installation instructions"
fi

# Create README
cat > "$PMC_STYLE_DIR/README.md" << 'EOF'
# PMC Style Checker Integration

This directory contains the PMC Style Checker XSLT bundle for validating JATS XML files.

## About PMC Style Checker

The PMC Style Checker is an XSLT-based tool provided by the National Library of Medicine (NLM) to validate JATS XML files against PMC submission requirements.

- **Official Site**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **Version**: nlm-style-5.47 (or later)
- **License**: Public domain (US Government work)

## Usage

The style checker is automatically integrated into the OmniJAX conversion pipeline. When a DOCX file is converted:

1. JATS XML is generated
2. XSD validation is performed
3. PMC style checker runs (if available)
4. Results are included in `validation_report.json`
5. HTML report is generated as `pmc_style_report.html`

## Requirements

- **xsltproc**: The XSLT processor must be installed
  ```bash
  # Ubuntu/Debian
  sudo apt-get install xsltproc
  
  # macOS
  brew install libxslt
  
  # Alpine Linux (Docker)
  apk add libxslt
  ```

## Files

- `nlm-stylechecker.xsl` - Main XSLT stylesheet for PMC style checking
- `README.md` - This file

## Manual Download

If the automatic download fails:

1. Visit https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
2. Download the nlm-stylechecker package
3. Extract `nlm-stylechecker.xsl`
4. Place it in this directory

## Running Style Check Manually

You can run the style checker manually on any JATS XML file:

```bash
xsltproc tools/pmc_style/nlm-stylechecker.xsl article.xml > style_report.html
```

## Integration Details

The style checker is called in `MasterPipeline.py`:

- Method: `_run_pmc_style_check()`
- Defensive: If xsltproc or XSLT file is missing, conversion continues with a warning
- Output: HTML report saved to output directory
- Results: Parsed and included in validation_report.json

## Troubleshooting

**Style check not running?**
- Check if xsltproc is installed: `which xsltproc`
- Check if XSLT file exists: `ls -l tools/pmc_style/nlm-stylechecker.xsl`
- Check conversion logs for warnings

**Download failed?**
- Manual download from PMC website is always available
- Placeholder file is created with instructions

**Style check errors?**
- Review the generated `pmc_style_report.html` in the output package
- Check `validation_report.json` for error counts and details

## References

- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
- PMC Style Checker: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- JATS Standard: https://jats.nlm.nih.gov/
EOF

echo ""
echo "✅ PMC Style Checker setup complete!"
echo ""
echo "📁 Installation directory: $PMC_STYLE_DIR"
echo "📄 Files:"
ls -lh "$PMC_STYLE_DIR"
echo ""
echo "==================================================================="
echo "Next steps:"
echo "1. Ensure xsltproc is installed: which xsltproc"
echo "2. Run a conversion and check for pmc_style_report.html"
echo "3. Review validation_report.json for style check results"
echo "==================================================================="
