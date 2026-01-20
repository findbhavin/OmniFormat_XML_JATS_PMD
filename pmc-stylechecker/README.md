# PMC Style Checker Integration

This directory contains XSLT files for PMC (PubMed Central) style checking.

## Official NLM Style Checker 5.47 Bundle

As of this release, the repository now includes support for the official PMC Style Checker XSLT bundle (nlm-style-5.47).

### Installation

To install the official nlm-style-5.47 bundle, run:

```bash
./tools/fetch_pmc_style.sh
```

This will download and extract files into `pmc-stylechecker/nlm-style-5.47/` from:
- **Source URL**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz

### Manual Installation

If the automatic script fails (e.g., network restrictions):

1. Download the archive from the URL above
2. Extract the tar.gz file
3. Copy all `.xsl` files to `pmc-stylechecker/nlm-style-5.47/`
4. Preserve the directory structure from the archive
5. Keep any LICENSE or documentation files

## Files

- `nlm-style-5.47/` - Official NLM Style Checker 5.47 bundle (installed via fetch script)
- `pmc_style_checker.xsl` - Simplified PMC style checker for basic compliance validation (fallback)

## About PMC Style Checker

The PMC Style Checker is an XSLT-based validation tool provided by the National Library of Medicine (NLM) that checks JATS XML files for compliance with PMC submission requirements.

- **Official Documentation**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **Version**: 5.47
- **License**: Public domain (US Government work)

## Purpose

The style checker performs comprehensive PMC compliance checks including:
- DTD version verification
- Article type validation
- DOI presence check
- Article title verification
- Abstract presence check
- Table-wrap positioning validation
- Figure and reference structure
- Author and affiliation formatting
- And many more PMC-specific requirements

## Usage

### Automatic Integration

The style checker is automatically run during the JATS validation phase of the conversion pipeline. Results are included in the `validation_report.json` file.

### Manual Usage with xsltproc

You can run the style checker manually on any JATS XML file:

```bash
# Using the official nlm-style-5.47 bundle
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl article.xml > pmc_style_report.html

# Using the simplified checker (fallback)
xsltproc pmc-stylechecker/pmc_style_checker.xsl article.xml > pmc_style_report.html
```

### Requirements

- **xsltproc**: Recommended for best compatibility (XSLT 1.0)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install xsltproc
  
  # macOS
  brew install libxslt
  
  # Alpine Linux (Docker)
  apk add libxslt
  ```

- **Saxon**: Alternative for XSLT 2.0 features (if needed)
  ```bash
  # Download from https://www.saxonica.com/
  java -jar saxon.jar -s:article.xml -xsl:nlm-stylechecker.xsl -o:report.html
  ```

## Integration Details

The XSLT transformation is applied in `MasterPipeline.py`:

- **Method**: `_run_pmc_stylechecker()`
- **Search Order**:
  1. `nlm-style-5.47/nlm-stylechecker.xsl` (official bundle - highest priority)
  2. `nlm-style-5-0.xsl` (legacy official)
  3. `nlm-style-3-0.xsl` (legacy official)
  4. `nlm-stylechecker.xsl` (legacy official)
  5. `pmc_style_checker.xsl` (simplified fallback)
- **Processor**: Uses `xsltproc` if available, falls back to Python's `lxml`
- **Defensive**: If xsltproc or XSLT file is missing, conversion continues with a warning
- **Output**: HTML report saved to output directory, results parsed and included in validation_report.json
- **Error Handling**: Captures stderr and includes it in the result dictionary

## XSLT Compatibility Notes

- **XSLT 1.0**: Fully supported by both xsltproc and lxml
- **XSLT 2.0**: Requires Saxon processor
- The official NLM Style Checker uses XSLT 1.0, so xsltproc is recommended
- If you encounter compatibility issues, try using Saxon instead

## Running Locally

To test the style checker locally on your JATS XML:

```bash
# 1. Ensure you have xsltproc installed
which xsltproc

# 2. Install the official bundle (if not already done)
./tools/fetch_pmc_style.sh

# 3. Run the checker on your XML file
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl your_article.xml > report.html

# 4. Open the report in a browser
open report.html  # macOS
xdg-open report.html  # Linux
```

## Troubleshooting

**Style check not running?**
- Check if xsltproc is installed: `which xsltproc`
- Check if XSLT file exists: `ls -l pmc-stylechecker/nlm-style-5.47/`
- Check conversion logs for warnings
- Run `./tools/fetch_pmc_style.sh` to install

**Download failed?**
- Manual download is available from the PMC website
- Check network connectivity and proxy settings
- Placeholder file provides installation instructions

**Style check errors?**
- Review the generated `pmc_style_report.html` in the output package
- Check `validation_report.json` for error counts and details
- Consult PMC tagging guidelines for specific requirements

**xsltproc not found?**
- The pipeline falls back to lxml if xsltproc is not available
- For best results, install xsltproc (see Requirements section)

## Note

This is the official implementation for comprehensive PMC compliance checking. For final PMC submission validation, always verify with the online PMC Style Checker tool at https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

## References

- PMC Style Checker Online: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- JATS Standard: https://jats.nlm.nih.gov/
- NLM DTD Repository: https://dtd.nlm.nih.gov/

