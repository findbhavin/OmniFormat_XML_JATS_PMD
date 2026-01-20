# PMC nlm-style-5.47 Bundle Directory

This directory is intended to contain the official PMC Style Checker XSLT bundle (version 5.47).

## Download Instructions

To obtain the official bundle, run:

```bash
./tools/fetch_pmc_style.sh
```

Or manually download from:
- **URL**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- **Official Site**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/

## Expected Contents

After extraction, this directory should contain:
- `nlm-stylechecker.xsl` - Main style checker XSLT (or similar versioned file)
- Supporting XSLT files and dependencies
- LICENSE file (Public Domain - US Government Work)
- README or documentation files

## Integration

The MasterPipeline.py will automatically detect and use XSLT files from this directory when performing PMC style checking during JATS XML conversion.

## Requirements

To use the style checker, you need `xsltproc` installed:

```bash
# Ubuntu/Debian
sudo apt-get install xsltproc

# macOS
brew install libxslt

# Alpine Linux (Docker)
apk add libxslt
```

## Manual Usage

Once the bundle is downloaded, you can run the style checker manually:

```bash
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl output/article.xml > pmc_style_report.html 2> pmc_style_error.log
```

## Notes

- The bundle is not included in the repository due to size considerations
- The fetch script handles idempotent downloads
- If download fails, manual extraction is straightforward
- All files from the official bundle maintain their original structure and licensing
