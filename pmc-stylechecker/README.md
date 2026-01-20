# PMC Style Checker Integration

This directory contains the PMC Style Checker XSLT files for validating JATS XML compliance.

## Installation

Due to network restrictions, the PMC Style Checker files need to be manually downloaded and extracted:

1. Download the style checker package:
   ```bash
   wget https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
   ```

2. Extract the files:
   ```bash
   tar -xzf nlm-style-5.47.tar.gz
   mv nlm-style-5.47/* pmc-stylechecker/
   ```

## Files Required

The main XSLT file is `nlm-style-3-0.xsl` or `nlm-style-5-0.xsl` which performs the validation checks.

## Usage

The style checker is automatically integrated into the conversion pipeline when the XSLT files are present. Results are included in the `validation_report.json` file.

## Reference

- PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
- Download Link: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
