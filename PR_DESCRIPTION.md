# Add official PMC nlm-style-5.47 XSLT bundle and integrate into PMC style-check pipeline; fix validation-report kwarg mismatch

## Summary

This PR adds support for the official PMC Style Checker XSLT bundle (nlm-style-5.47) and fixes a TypeError-causing kwarg mismatch in the validation pipeline. The integration uses `xsltproc` subprocess execution (as documented in the repo) and provides comprehensive error handling.

## Changes Made

### 1. Official PMC nlm-style-5.47 Bundle Integration

**Directory Structure:**
- Created `pmc-stylechecker/nlm-style-5.47/` directory for the official bundle
- Added comprehensive README with download and usage instructions
- Bundle is downloaded via `./tools/fetch_pmc_style.sh` script

**Key Features:**
- Idempotent download/extraction script
- Preserves LICENSE and attribution from official bundle
- Supports both curl and wget
- Basic file size sanity checking
- Lists all extracted files for verification

### 2. MasterPipeline.py Fixes

#### Kwarg Mismatch Fix (Fixes TypeError)
**Problem:** Code was passing `pmc_style_check` kwarg but `_generate_validation_report` expected `pmc_stylechecker`

**Solution:**
- Fixed all 4 call sites in exception handlers (XMLSchemaError, XMLSyntaxError, general Exception, XSD-missing branch)
- Changed `pmc_style_check=` to `pmc_stylechecker=`

#### Backward-Compatible Alias Support
**Added to `_generate_validation_report`:**
```python
def _generate_validation_report(self, xml_doc, passed, error_msg=None, 
                                pmc_passed=None, pmc_stylechecker=None, **kwargs):
    # Accept old kwarg name and coerce to new name
    if 'pmc_style_check' in kwargs and pmc_stylechecker is None:
        pmc_stylechecker = kwargs['pmc_style_check']
```

#### XSLT Processor Integration
**Replaced lxml XSLT with xsltproc subprocess:**

**XSLT File Search Order (Prefers Official Bundle):**
1. `pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl` (preferred if present)
2. Other `.xsl` files in `nlm-style-5.47/` directory (sorted by version)
3. Repo root: `nlm-style-5-0.xsl`, `nlm-style-3-0.xsl`, `nlm-stylechecker.xsl`
4. `pmc-stylechecker/pmc_style_checker.xsl` (simplified fallback)

**Result Dictionary Includes:**
- `xslt_stdout`: Full transformation output
- `xslt_stderr`: Any errors/warnings from xsltproc
- `returncode`: Exit code from xsltproc process
- `xslt_used`: Which XSLT file was selected
- `xslt_full_path`: Full path to XSLT file
- `processor`: "xsltproc" indicator
- `available`: False if xsltproc not found
- Error counts and parsed warnings/errors

**Defensive Behavior:**
- Checks for xsltproc availability before running
- Returns `available=False` with installation instructions if not found
- 60-second timeout on XSLT transformation
- Handles subprocess failures gracefully
- **Does not abort conversion on XSLT failure**

### 3. tools/fetch_pmc_style.sh Updates

**New Features:**
- Downloads from: `https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz`
- Idempotent: Checks if already downloaded before re-fetching
- Supports both `curl` and `wget`
- Extracts to `pmc-stylechecker/nlm-style-5.47/` preserving structure
- Verifies key files exist (nlm-stylechecker.xsl, LICENSE, README)
- Lists extracted files with count
- Provides clear installation instructions on failure

**Usage:**
```bash
./tools/fetch_pmc_style.sh
```

### 4. Documentation Updates

#### pmc-stylechecker/README.md
- Added nlm-style-5.47 bundle download instructions
- Manual xsltproc usage examples
- XSLT 1.0 vs 2.0 compatibility notes
- Saxon processor recommendation for XSLT 2.0 needs
- Automated integration details
- xsltproc installation instructions for Ubuntu/macOS/Alpine
- Troubleshooting section
- Bundle refresh instructions

#### MERGE_RESOLUTION_SUMMARY.md
- Added "Recent Updates" section documenting this PR
- Bundle refresh instructions
- Links to documentation

#### pmc-stylechecker/nlm-style-5.47/README.md
- New file documenting the bundle directory
- Download instructions
- Expected contents after extraction
- Integration notes
- Manual usage examples

## Manual Verification Steps for Reviewers

### 1. Download and Extract Bundle
```bash
# Run the fetch script
./tools/fetch_pmc_style.sh

# Verify extraction
ls -la pmc-stylechecker/nlm-style-5.47/

# Should see nlm-stylechecker.xsl and other XSLT files
find pmc-stylechecker/nlm-style-5.47 -name "*.xsl"
```

### 2. Run xsltproc Manually (Requires xsltproc and a test XML file)
```bash
# Ensure xsltproc is installed
which xsltproc

# If not installed:
# Ubuntu/Debian: sudo apt-get install xsltproc
# macOS: brew install libxslt
# Alpine: apk add libxslt

# Run manually on converted XML
xsltproc pmc-stylechecker/nlm-style-5.47/nlm-stylechecker.xsl output/article.xml > pmc_style_report.html 2> pmc_style_error.log

# Check the reports
cat pmc_style_error.log
open pmc_style_report.html  # or view in browser
```

### 3. Verify TypeError Fix
```bash
# Run a conversion
python3 app.py  # or however the service is started

# Upload a test DOCX file

# Check validation_report.json in output
cat output/validation_report.json | grep -A 20 pmc_stylechecker

# Should see:
# - "pmc_stylechecker": { "available": true/false, ... }
# - "xslt_stdout", "xslt_stderr", "returncode" if xsltproc ran
# - No TypeError in logs
```

### 4. Test Graceful Fallback
```bash
# Test without xsltproc (temporarily rename it)
sudo mv /usr/bin/xsltproc /usr/bin/xsltproc.bak

# Run conversion
# Should complete successfully with:
# - available: false
# - message about xsltproc not found
# - install_instructions in result

# Restore xsltproc
sudo mv /usr/bin/xsltproc.bak /usr/bin/xsltproc
```

## Testing Summary

### Static Analysis ✅
- [x] Python syntax validation passes
- [x] Bash script syntax validation passes
- [x] All kwarg mismatches fixed (0 instances of wrong name)
- [x] Backward-compatible alias properly implemented
- [x] xsltproc subprocess integration confirmed
- [x] xslt_stdout, xslt_stderr, returncode in results
- [x] nlm-style-5.47 directory preference confirmed
- [x] Error handling with available=False confirmed
- [x] Timeout handling present

### Integration Tests (Manual - Requires Environment)
- [ ] Bundle download and extraction successful
- [ ] xsltproc runs successfully on test XML
- [ ] validation_report.json contains pmc_stylechecker entry
- [ ] No TypeError when running conversions
- [ ] Graceful fallback when xsltproc not found
- [ ] Conversion completes even when XSLT fails

## Breaking Changes

**None.** This is backward-compatible:
- Old `pmc_style_check` kwarg still works via alias
- Conversion continues if style checker is unavailable
- All existing functionality preserved

## Dependencies

**Optional Runtime Dependency:**
- `xsltproc` (from libxslt package)
  - Ubuntu/Debian: `apt-get install xsltproc`
  - macOS: `brew install libxslt`
  - Alpine: `apk add libxslt`

**Note:** If xsltproc is not installed, the pipeline logs a warning and continues. The style checker simply returns `available: false`.

## Related Issues

Fixes TypeError in validation pipeline caused by kwarg name mismatch between caller and callee.

## References

- PMC Style Checker: https://www.ncbi.nlm.nih.gov/pmc/tools/stylechecker/
- Bundle URL: https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- JATS Standard: https://jats.nlm.nih.gov/

## Checklist

- [x] Code follows repository style
- [x] Python syntax validated
- [x] Bash script syntax validated
- [x] Documentation updated
- [x] Backward compatibility maintained
- [x] Error handling defensive (doesn't abort conversion)
- [x] Manual verification steps provided
- [x] No new runtime dependencies required (xsltproc optional)
