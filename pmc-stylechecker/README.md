# PMC Style Checker Integration

This directory contains XSLT files for PMC (PubMed Central) style checking.

## Official nlm-style-5.47 Bundle

The official PMC nlm-style-5.47 XSLT bundle has been integrated into this repository.

- **Source**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- **Location**: `pmc-stylechecker/nlm-style-5.47/`
- **Version**: nlm-style-5.47
- **License**: Public domain (US Government work)

### Downloading the Bundle

To download and extract the official bundle, run:

```bash
./tools/fetch_pmc_style.sh
```

This script will:
1. Download the bundle from the official NCBI CDN
2. Extract all files to `pmc-stylechecker/nlm-style-5.47/`
3. Preserve the directory structure and all files (XSLT, README, LICENSE, etc.)
4. List all extracted files

The script is idempotent - it will skip downloading if files already exist.

### Manual Download

If automatic download fails or is not available:

1. Download from: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
2. Extract: `tar -xzf nlm-style-5.47.tar.gz`
3. Copy all files to `pmc-stylechecker/nlm-style-5.47/`

## Files

- `nlm-style-5.47/` - Official PMC style checker bundle (version 5.47)
  - `nlm-stylechecker.xsl` - Main XSLT stylesheet
  - Supporting XSLT files and documentation
  - README, LICENSE, and attribution files
- `pmc_style_checker.xsl` - Simplified PMC style checker for basic compliance validation (custom)
- `README.md` - This file

### Download and Setup

For complete and official PMC validation, the pipeline now uses the official nlm-style-5.47 bundle.

- **Online Tool**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- **XSLT Version**: XSLT 1.0
- **Documentation**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/

## Purpose

The PMC Style Checker performs comprehensive PMC compliance checks including:
- DTD version verification
- Article type validation
- DOI presence check
- Article title verification
- Abstract presence check
- Table-wrap positioning validation
- Figure and reference counting
- Many other PMC-specific requirements

To update to a newer version when PMC releases updates:

1. Remove the old bundle:
   ```bash
   rm -rf pmc-stylechecker/nlm-style-5.47
   ```

### Running Manually with xsltproc

You can run the style checker manually on any JATS XML file:

```bash
# Basic usage
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl output/article.xml > pmc_style_report.html 2> pmc_style_error.log

# View the HTML report
open pmc_style_report.html  # macOS
xdg-open pmc_style_report.html  # Linux
```

### Requirements

The style checker requires **xsltproc** to be installed:

```bash
# Ubuntu/Debian
sudo apt-get install xsltproc

# macOS
brew install libxslt

# Alpine Linux (Docker)
apk add libxslt

# Verify installation
which xsltproc
xsltproc --version
```

## Integration

The XSLT transformation is applied to the generated JATS XML file using xsltproc via subprocess in `MasterPipeline.py`.

### Processing Order

The pipeline uses the following XSLT file search order:
1. `pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl` (preferred)
2. Other .xsl files in `pmc-stylechecker/nlm-style-5.47/` (by discovery order)
3. `pmc-stylechecker/nlm-style-5-0.xsl` (fallback)
4. `pmc-stylechecker/nlm-style-3-0.xsl` (fallback)
5. `pmc-stylechecker/nlm-stylechecker.xsl` (fallback)
6. `pmc-stylechecker/pmc_style_checker.xsl` (custom simplified checker, final fallback)

### Defensive Behavior

- If xsltproc is not installed, the pipeline continues with a warning
- If XSLT files are missing, the pipeline continues with a warning
- XSLT transformation failures do not abort the conversion
- All diagnostic output (stdout/stderr) is captured and included in validation_report.json

## XSLT Compatibility Notes

### XSLT 1.0 vs XSLT 2.0

The official PMC style checker uses **XSLT 1.0**, which is compatible with xsltproc.

- **xsltproc**: Supports XSLT 1.0 only (included with libxslt)
- **Saxon**: Supports XSLT 2.0 and 3.0 (commercial/open-source editions)

### When to Use Saxon

Saxon is recommended if you need:
- XSLT 2.0+ features
- XPath 2.0+ expressions
- Better performance on large documents
- Advanced XML processing capabilities

#### Saxon Installation

```bash
# Download Saxon-HE (Home Edition, open source)
# Visit: https://www.saxonica.com/download/download_page.xml

# Example usage with Saxon
java -jar saxon-he.jar -xsl:pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl -s:article.xml -o:pmc_report.html
```

However, for the official PMC style checker (nlm-style-5.47), **xsltproc is sufficient** as it uses XSLT 1.0.

## Verification

After downloading the bundle, verify the installation:

```bash
# 1. Check xsltproc is available
which xsltproc

# 2. Check XSLT files exist
ls -l pmc-stylechecker/nlm-style-5.47/

# 3. Run a test conversion
# (Follow the main README.md for conversion instructions)

# 4. Check validation_report.json
cat output_files/validation_report.json | grep -A 20 pmc_stylechecker
```

The validation report should include:
- `pmc_stylechecker.available: true`
- `pmc_stylechecker.xslt_used: "nlm-stylechecker.xsl"`
- `pmc_stylechecker.xslt_stdout: "..."`
- `pmc_stylechecker.xslt_stderr: "..."`
- `pmc_stylechecker.returncode: 0`

## Troubleshooting

### xsltproc not found

```
Error: xsltproc not found
```

**Solution**: Install libxslt package (see Requirements section above)

### XSLT files not found

```
Warning: PMC Style Checker XSLT not found
```

**Solution**: Run `./tools/fetch_pmc_style.sh` to download the bundle

### XSLT transformation errors

Check the validation_report.json for:
- `xslt_stderr`: Contains error messages from xsltproc
- `returncode`: Non-zero indicates failure

Review the pmc_style_report.html (if generated) for detailed diagnostics.

## Note

This is the official PMC implementation for comprehensive PMC validation. The custom simplified checker (`pmc_style_checker.xsl`) is retained as a fallback for basic preliminary checks.

For final PMC submission validation, always verify with the official online tool: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

## References

- PMC Style Checker: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
- JATS Standard: https://jats.nlm.nih.gov/
- xsltproc Documentation: http://xmlsoft.org/XSLT/xsltproc.html
- Saxon XSLT Processor: https://www.saxonica.com/
