# Testing Guide for PMC Style Checker Integration

This document provides manual verification steps for the PMC nlm-style-5.47 bundle integration and TypeError fix.

## Prerequisites

Before testing, ensure you have:
- Python 3.7+ with lxml installed
- pandoc installed
- Either curl or wget available
- tar command available
- (Optional) xsltproc installed for best results

## Test 1: Verify TypeError Fix

### Objective
Confirm that the kwarg mismatch `pmc_style_check` has been replaced with `pmc_stylechecker`.

### Steps
```bash
cd /home/runner/work/OmniFormat_XML_JATS_PMD/OmniFormat_XML_JATS_PMD

# Verify no incorrect kwarg usage
grep -n "pmc_style_check=" MasterPipeline.py
# Expected: No results (or only in comments)

# Verify correct kwarg usage
grep -n "pmc_stylechecker=" MasterPipeline.py
# Expected: Lines 330, 357, 364, 371, 378, 760
```

### Expected Result
✅ All calls to `_generate_validation_report()` use the correct kwarg name `pmc_stylechecker`

## Test 2: Verify Script Syntax

### Objective
Ensure the fetch script has valid bash syntax.

### Steps
```bash
# Check syntax
bash -n tools/fetch_pmc_style.sh

# Verify executable permissions
ls -l tools/fetch_pmc_style.sh
# Expected: -rwxr-xr-x or similar (executable)
```

### Expected Result
✅ No syntax errors reported

## Test 3: Download and Install Official Bundle

### Objective
Download and extract the official nlm-style-5.47 bundle.

### Steps
```bash
# Run the fetch script
./tools/fetch_pmc_style.sh

# Verify files were created
ls -la pmc-stylechecker/nlm-style-5.47/

# Expected files:
# - nlm-stylechecker.xsl (or similar .xsl files)
# - Any LICENSE or documentation files from the bundle
# - README.md (already exists)
```

### Expected Result
✅ Multiple .xsl files extracted to pmc-stylechecker/nlm-style-5.47/
✅ Script completes with success message
✅ File count displayed

### Troubleshooting
If download fails:
- Network may be restricted
- Archive URL may have changed
- Manual installation instructions are provided
- INSTALLATION_REQUIRED.txt file created with guidance

## Test 4: Verify Python Module Compilation

### Objective
Ensure MasterPipeline.py compiles without syntax errors.

### Steps
```bash
# Compile check
python3 -m py_compile MasterPipeline.py

# Expected: No output = success
```

### Expected Result
✅ No compilation errors

## Test 5: Test Style Checker Detection

### Objective
Verify that MasterPipeline correctly detects XSLT files.

### Steps
```bash
# Create a test script
cat > test_detection.py << 'EOF'
import os
import sys

# Simulate the detection logic
pmc_dir = "pmc-stylechecker"
xslt_candidates = [
    os.path.join(pmc_dir, "nlm-style-5.47", "nlm-stylechecker.xsl"),
    os.path.join(pmc_dir, "nlm-style-5-0.xsl"),
    os.path.join(pmc_dir, "nlm-style-3-0.xsl"),
    os.path.join(pmc_dir, "nlm-stylechecker.xsl"),
    os.path.join(pmc_dir, "pmc_style_checker.xsl")
]

print("Checking XSLT candidates in priority order:")
for i, candidate in enumerate(xslt_candidates, 1):
    exists = os.path.exists(candidate)
    status = "✓ FOUND" if exists else "✗ Not found"
    print(f"{i}. {status}: {candidate}")
    if exists:
        print(f"   → This file will be used")
        break

# Check nlm-style-5.47 directory
nlm_547_dir = os.path.join(pmc_dir, "nlm-style-5.47")
if os.path.exists(nlm_547_dir):
    xsl_files = [f for f in os.listdir(nlm_547_dir) 
                 if f.endswith('.xsl') and not f.startswith('PLACEHOLDER')]
    print(f"\nAdditional .xsl files in nlm-style-5.47/: {len(xsl_files)}")
    for xsl in xsl_files:
        print(f"  - {xsl}")
EOF

python3 test_detection.py
rm test_detection.py
```

### Expected Result
✅ Detection logic identifies available XSLT files
✅ Priority order is respected (nlm-style-5.47 first)

## Test 6: Run Full Conversion (Optional)

### Objective
Test the entire pipeline with a real DOCX file.

### Prerequisites
- lxml, pandoc, weasyprint installed
- A sample DOCX file available

### Steps
```bash
# Create a test script
cat > test_conversion.py << 'EOF'
from MasterPipeline import HighFidelityConverter
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python3 test_conversion.py <docx_file>")
    sys.exit(1)

docx_path = sys.argv[1]
if not os.path.exists(docx_path):
    print(f"Error: File not found: {docx_path}")
    sys.exit(1)

print(f"Testing conversion with: {docx_path}")
try:
    converter = HighFidelityConverter(docx_path)
    output_dir = converter.run_pipeline()
    print(f"\n✅ Conversion completed successfully")
    print(f"Output directory: {output_dir}")
    
    # Check for validation report
    validation_report = os.path.join(output_dir, "validation_report.json")
    if os.path.exists(validation_report):
        import json
        with open(validation_report) as f:
            report = json.load(f)
        
        print("\nPMC Style Checker Status:")
        pmc_checker = report.get("pmc_style_checker", {})
        print(f"  Available: {pmc_checker.get('available', False)}")
        print(f"  XSLT Used: {pmc_checker.get('xslt_used', 'N/A')}")
        print(f"  Processor: {pmc_checker.get('processor', 'N/A')}")
        print(f"  Status: {pmc_checker.get('status', 'N/A')}")
        
except Exception as e:
    print(f"❌ Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Run with a test DOCX file (replace with actual file)
# python3 test_conversion.py sample.docx

# Clean up
rm test_conversion.py
```

### Expected Result
✅ Conversion completes without TypeError
✅ validation_report.json contains pmc_style_checker section
✅ XSLT path is logged
✅ Processor type is indicated (xsltproc or lxml)

## Test 7: Verify Documentation

### Objective
Ensure all documentation is accurate and helpful.

### Steps
```bash
# Check README files
cat pmc-stylechecker/README.md | grep -i "nlm-style-5.47"
# Expected: Multiple references to nlm-style-5.47

cat pmc-stylechecker/nlm-style-5.47/README.md
# Expected: Installation instructions, source URL, etc.

cat MERGE_RESOLUTION_SUMMARY.md | grep -A 10 "Official PMC"
# Expected: Update section about PMC bundle integration
```

### Expected Result
✅ All documentation is present and references nlm-style-5.47
✅ Installation instructions are clear
✅ Source URLs are provided

## Test 8: Verify Graceful Degradation

### Objective
Ensure pipeline continues when style checker is unavailable.

### Steps
```bash
# Temporarily rename the nlm-style-5.47 directory
mv pmc-stylechecker/nlm-style-5.47 pmc-stylechecker/nlm-style-5.47.backup

# Also rename the fallback checker
mv pmc-stylechecker/pmc_style_checker.xsl pmc-stylechecker/pmc_style_checker.xsl.backup

# Run a test conversion (should complete with warnings)
# python3 test_conversion.py sample.docx

# Restore the files
mv pmc-stylechecker/nlm-style-5.47.backup pmc-stylechecker/nlm-style-5.47
mv pmc-stylechecker/pmc_style_checker.xsl.backup pmc-stylechecker/pmc_style_checker.xsl
```

### Expected Result
✅ Conversion completes without crashing
✅ Warning logged about missing style checker
✅ validation_report.json shows style checker as unavailable

## Test 9: Test xsltproc vs lxml

### Objective
Verify both processor paths work correctly.

### With xsltproc (if available)
```bash
# Check if xsltproc is installed
which xsltproc

# Run conversion - should use xsltproc
# Check logs for "Running PMC Style Checker with xsltproc"
```

### Without xsltproc
```bash
# Temporarily make xsltproc unavailable
# (Or just check the lxml fallback in the code)

# Run conversion - should fall back to lxml
# Check logs for "using lxml XSLT processor"
```

### Expected Result
✅ xsltproc is used when available
✅ Falls back to lxml gracefully
✅ Results include processor information

## Summary Checklist

After completing all tests:

- [ ] TypeError fix verified (no `pmc_style_check=` usage)
- [ ] Fetch script has valid syntax
- [ ] Official bundle can be downloaded (or manual instructions provided)
- [ ] MasterPipeline.py compiles without errors
- [ ] XSLT detection works in priority order
- [ ] Full conversion works without TypeError
- [ ] Documentation is complete and accurate
- [ ] Pipeline degrades gracefully when style checker unavailable
- [ ] Both xsltproc and lxml processors work

## Notes for Reviewer

Since the automatic download may fail in restricted network environments:
1. The fetch script provides comprehensive manual installation instructions
2. A placeholder file guides users to run the fetch script
3. The pipeline continues working without the official bundle (uses fallback)
4. All changes are defensive and non-breaking

The main critical fix is the **TypeError** which was preventing the pipeline from completing. This is now fixed in all exception paths.

## Manual Installation Steps (If Needed)

If you need to manually install the bundle:

```bash
# 1. Download the archive
curl -L -O https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz

# 2. Extract
tar -xzf nlm-style-5.47.tar.gz

# 3. Find and copy .xsl files
find . -name "*.xsl" -exec cp {} pmc-stylechecker/nlm-style-5.47/ \;

# 4. Copy any LICENSE files
find . -name "LICENSE*" -exec cp {} pmc-stylechecker/nlm-style-5.47/ \;

# 5. Verify
ls -la pmc-stylechecker/nlm-style-5.47/
```
