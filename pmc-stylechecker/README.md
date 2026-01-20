# PMC Style Checker Integration

This directory contains XSLT files for PMC (PubMed Central) style checking.

## Official PMC nlm-style-5.47 Bundle

**As of this version**, the official PMC Style Checker XSLT bundle (nlm-style-5.47) has been integrated into this repository. 

### Download and Setup

To download and extract the official bundle:

```bash
./tools/fetch_pmc_style.sh
```

This will:
- Download the official bundle from: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- Extract files to `pmc-stylechecker/nlm-style-5.47/`
- Preserve the original directory structure and LICENSE attribution
- Check idempotently (won't re-download if already present)

### Manual Download

If the script fails or you prefer manual download:
1. Visit: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
2. Download and extract the archive
3. Copy contents to `pmc-stylechecker/nlm-style-5.47/`

## Files in This Directory

- `pmc_style_checker.xsl` - Simplified PMC style checker for basic compliance validation (fallback)
- `nlm-style-5.47/` - Official PMC Style Checker XSLT bundle (downloaded via fetch_pmc_style.sh)
- `README.md` - This file

## Requirements

The style checker requires **xsltproc** (an XSLT 1.0 processor):

```bash
# Ubuntu/Debian
sudo apt-get install xsltproc

# macOS
brew install libxslt

# Alpine Linux (Docker)
apk add libxslt
```

## XSLT Processor Compatibility

- **XSLT 1.0**: The official PMC stylesheets are designed for XSLT 1.0 processors like `xsltproc`
- **XSLT 2.0**: If you need XSLT 2.0 features, consider using **Saxon** processor:
  ```bash
  # Example with Saxon-HE (Java-based)
  java -jar saxon-he.jar -s:article.xml -xsl:nlm-stylechecker.xsl -o:report.html
  ```
- **Recommendation**: Use `xsltproc` for best compatibility with official PMC stylesheets

## Manual Usage

Run the style checker manually on any JATS XML file:

```bash
# Using xsltproc (recommended)
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl output/article.xml > pmc_style_report.html 2> pmc_style_error.log

# Or use the simplified checker
xsltproc pmc-stylechecker/pmc_style_checker.xsl output/article.xml > pmc_style_report.html
```

## Purpose

The official PMC style checker performs comprehensive compliance checks including:
- DTD version verification
- Article structure validation
- Metadata completeness checks
- Reference formatting validation
- Figure and table compliance
- And many more PMC-specific requirements

The simplified `pmc_style_checker.xsl` performs basic checks and is used as a fallback:
- DTD version verification
- Article type validation
- DOI presence check
- Article title verification
- Abstract presence check
- Table-wrap positioning validation
- Figure and reference structure
- Author and affiliation formatting
- And many more PMC-specific requirements

## Automated Integration

The style checker is automatically run during the JATS validation phase of the conversion pipeline:

1. **XSLT File Selection**: MasterPipeline.py searches for XSLT files in this order:
   - `nlm-style-5.47/nlm-stylechecker.xsl` (preferred - official)
   - `nlm-style-5.47/*.xsl` (highest version number)
   - Repo root: `nlm-style-5-0.xsl`, `nlm-style-3-0.xsl`, `nlm-stylechecker.xsl`
   - `pmc_style_checker.xsl` (simplified fallback)

2. **Execution**: Uses `xsltproc` subprocess with captured stdout/stderr

3. **Results**: Included in `validation_report.json` under the `pmc_stylechecker` key with:
   - `xslt_stdout`: XSLT transformation output
   - `xslt_stderr`: Any errors or warnings
   - `returncode`: Exit code from xsltproc
   - `xslt_used`: Which XSLT file was used
   - `status`: Overall status (PASS/FAIL/ERROR)

4. **Defensive Behavior**: If xsltproc is not found or XSLT fails, conversion continues with a warning

## Online PMC Style Checker

For interactive validation and the most up-to-date checks:
- **URL**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- **Documentation**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/

## Refreshing the Bundle

To update to a newer version when PMC releases updates:

1. Remove the old bundle:
   ```bash
   rm -rf pmc-stylechecker/nlm-style-5.47
   ```

2. Update the URL in `tools/fetch_pmc_style.sh` if needed

3. Run the fetch script:
   ```bash
   ./tools/fetch_pmc_style.sh
   ```

## Note

For final PMC submission validation, always verify using the official online PMC Style Checker tool. This local integration is for development and preliminary checking.
