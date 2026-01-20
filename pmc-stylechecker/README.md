# PMC Style Checker Integration

This directory contains XSLT files for PMC (PubMed Central) style checking.

## Files

### Official PMC Style Checker Bundle

- **nlm-style-5.47/** - Official PMC Style Checker XSLT bundle (version 5.47)
  - Contains the complete official PMC style checker from NLM
  - Download URL: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
  - To install: Run `./tools/fetch_pmc_style.sh`

### Simplified Checker

- **pmc_style_checker.xsl** - Simplified PMC style checker for basic compliance validation (fallback)

## Official PMC Style Checker (nlm-style-5.47)

The official PMC Style Checker is the authoritative XSLT-based tool provided by the National Library of Medicine (NLM) to validate JATS XML files against PMC submission requirements.

### Installation

To download and install the official bundle:

```bash
./tools/fetch_pmc_style.sh
```

Or manually:

```bash
cd pmc-stylechecker
curl -L -o nlm-style-5.47.tar.gz https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
tar -xzf nlm-style-5.47.tar.gz
```

### About the Bundle

- **Version**: 5.47
- **License**: Public domain (U.S. Government work)
- **Official Site**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **Documentation**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/

## Requirements

The PMC Style Checker requires **xsltproc** (XSLT 1.0 processor) to be installed:

```bash
# Ubuntu/Debian
sudo apt-get install xsltproc libxslt1-dev

# macOS
brew install libxslt

# Alpine Linux (Docker)
apk add libxslt
```

For XSLT 2.0 features (if needed), you may also use **Saxon**:

```bash
# Download Saxon HE (Home Edition)
# https://www.saxonica.com/download/download_page.xml
```

## Purpose

The PMC Style Checker performs comprehensive compliance checks including:
- DTD version verification
- Article type validation
- DOI presence check
- Article title verification
- Abstract presence check
- Table-wrap positioning validation
- Figure and reference counting
- Author affiliation validation
- Citation format checking
- And many more PMC-specific requirements

The simplified `pmc_style_checker.xsl` provides basic checks as a fallback.

## Usage

The style checker is automatically run during the JATS validation phase of the conversion pipeline. Results are included in the `validation_report.json` file and `pmc_style_report.html` (if generated).

### Automatic Integration

The conversion pipeline will automatically:
1. Look for the official nlm-style-5.47 bundle first (highest priority)
2. Fall back to legacy official files if present
3. Use the simplified checker as last resort

### Manual Usage

You can run the PMC Style Checker manually on any JATS XML file:

```bash
# Using xsltproc (XSLT 1.0)
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl article.xml > pmc_style_report.html

# Using Saxon (XSLT 2.0)
java -jar saxon.jar -s:article.xml -xsl:pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl -o:pmc_style_report.html
```

## Integration Details

The style checker is called in `MasterPipeline.py`:

- **Method**: `_run_pmc_stylechecker()`
- **Behavior**: Defensive - if XSLT files are missing, conversion continues with a warning
- **Output**: Results dictionary with errors, warnings, and status
- **Reports**: HTML report saved to output directory (when applicable)
- **Logging**: Detailed logs include XSLT used, error counts, and warnings

## XSLT 1.0 vs 2.0 Compatibility

The official PMC Style Checker is designed for **XSLT 1.0** and works best with **xsltproc**.

- **xsltproc**: Fully compatible (XSLT 1.0)
- **lxml (Python)**: Fully compatible (XSLT 1.0 via libxslt)
- **Saxon HE**: Compatible (supports XSLT 1.0 and 2.0)

If you encounter compatibility issues, ensure you're using xsltproc or a compatible XSLT 1.0 processor.

## Troubleshooting

**Style check not running?**
- Check if XSLT files exist: `ls -l pmc-stylechecker/nlm-style-5.47/`
- Check if xsltproc is installed: `which xsltproc`
- Check conversion logs for warnings

**Bundle not installed?**
- Run: `./tools/fetch_pmc_style.sh`
- Check internet connectivity
- Try manual download from PMC website

**XSLT transformation errors?**
- Verify XML is well-formed: `xmllint --noout article.xml`
- Check for XSLT 2.0 features (use Saxon if needed)
- Review error logs in `validation_report.json`

## References

- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
- **PMC Style Checker**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **JATS Standard**: https://jats.nlm.nih.gov/
- **Download Bundle**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz

## Note

This is the official PMC Style Checker implementation. For final PMC submission validation, always use the latest version available from the official PMC website, and consider using the online PMC Style Checker tool for the most up-to-date validation rules.
