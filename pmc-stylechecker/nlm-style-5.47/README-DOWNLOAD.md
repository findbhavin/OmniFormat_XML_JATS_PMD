# NLM Style 5.47 Bundle

This directory should contain the official PMC nlm-style-5.47 XSLT bundle.

## Download Instructions

Due to network restrictions, the bundle must be downloaded manually:

1. Download from: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
2. Extract the archive: `tar -xzf nlm-style-5.47.tar.gz`
3. Copy all files from the extracted directory to this location
4. The main XSLT file should be: `nlm-stylechecker.xsl`

## Alternative: Use fetch_pmc_style.sh

Run the provided script:
```bash
cd /home/runner/work/OmniFormat_XML_JATS_PMD/OmniFormat_XML_JATS_PMD
./tools/fetch_pmc_style.sh
```

This script will download and extract the bundle automatically if network access is available.

## Expected Contents

- nlm-stylechecker.xsl (main XSLT file)
- Supporting XSLT files
- README
- LICENSE
- Other documentation files
