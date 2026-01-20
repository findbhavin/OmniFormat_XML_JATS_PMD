# PMC Style Checker Integration

This directory contains the PMC Style Checker XSLT bundle for validating JATS XML files.

## About PMC Style Checker

The PMC Style Checker is an XSLT-based tool provided by the National Library of Medicine (NLM) to validate JATS XML files against PMC submission requirements.

- **Official Site**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **Version**: nlm-style-5.47 (or later)
- **License**: Public domain (US Government work)

## Installation

Run the fetch script to download the PMC Style Checker:

```bash
./tools/fetch_pmc_style.sh
```

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

- `nlm-stylechecker.xsl` - Main XSLT stylesheet for PMC style checking (downloaded by fetch script)
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
