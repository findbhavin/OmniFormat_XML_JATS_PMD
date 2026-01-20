# PMC Style Checker Integration

This directory contains XSLT files for PMC (PubMed Central) style checking.

## Files

- `pmc_style_checker.xsl` - Simplified PMC style checker for basic compliance validation

## Official PMC Style Checker

For complete and official PMC validation, please use the online PMC Style Checker:
- URL: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- Download: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz

## Purpose

This simplified version performs basic PMC compliance checks including:
- DTD version verification
- Article type validation
- DOI presence check
- Article title verification
- Abstract presence check
- Table-wrap positioning validation
- Figure and reference counting

## Usage

The style checker is automatically run during the JATS validation phase of the conversion pipeline. Results are included in the `validation_report.json` file.

## Integration

The XSLT transformation is applied to the generated JATS XML file using Python's lxml library with XSLT support.

## Note

This is a basic implementation for preliminary checks. For final PMC submission validation, always use the official PMC Style Checker tool.
