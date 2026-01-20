# Official PMC nlm-style-5.47 Bundle

This directory should contain the official PMC Style Checker XSLT files from the nlm-style-5.47 bundle.

## Installation

To download and install the official PMC Style Checker bundle, run:

```bash
./tools/fetch_pmc_style.sh
```

Or manually download and extract:

```bash
cd pmc-stylechecker
curl -L -o nlm-style-5.47.tar.gz https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
tar -xzf nlm-style-5.47.tar.gz
```

## Expected Files

The nlm-style-5.47 bundle typically contains:
- `nlm-stylechecker.xsl` - Main style checker XSLT
- Supporting XSLT files and modules
- Documentation and license files

## Source

- **Official URL**: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- **PMC Style Checker**: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- **Version**: 5.47

## License

The PMC Style Checker is a public domain work of the U.S. Government (National Library of Medicine).

## Usage

Once installed, the conversion pipeline will automatically detect and use the official PMC Style Checker XSLT files from this directory.
