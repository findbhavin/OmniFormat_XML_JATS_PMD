# NLM Style Checker 5.47 - Official PMC Bundle

This directory contains the official PMC Style Checker XSLT files (nlm-style-5.47).

## Installation

The files in this directory should be populated by running:

```bash
./tools/fetch_pmc_style.sh
```

This will download and extract the official nlm-style-5.47.tar.gz bundle from:
https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz

## Expected Files

After running the fetch script, this directory should contain:
- `nlm-stylechecker.xsl` - Main style checker XSLT
- Additional supporting XSLT files as included in the official bundle
- LICENSE or attribution files from the bundle

## About

The NLM Style Checker is an XSLT-based validation tool provided by the National Library of Medicine for checking JATS XML compliance with PMC submission requirements.

- **Version**: 5.47
- **Source**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- **Official Documentation**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **License**: Public domain (US Government work)

## Integration

The MasterPipeline.py automatically detects and uses these XSLT files during the JATS validation phase.

## Manual Installation

If the automatic fetch script fails, you can manually:

1. Download: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
2. Extract the archive
3. Copy all .xsl files to this directory
4. Preserve the directory structure from the archive where practical
