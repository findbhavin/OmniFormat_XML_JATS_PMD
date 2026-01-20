# Direct PDF Conversion Documentation

## Overview

The OmniJAX system provides **two** PDF conversion pathways:

1. **JATS XML-based PDF** (`published_article.pdf`)
   - Converts DOCX → JATS XML → HTML → PDF
   - Full PMC/NLM compliance
   - Semantic structure preserved
   - Best for journal submissions

2. **Direct PDF** (`direct_from_word.pdf`)
   - Converts DOCX → HTML → PDF (bypassing JATS XML)
   - Preserves Word formatting
   - Faster conversion
   - Best for quick document viewing

## When to Use Direct PDF Conversion

Use direct PDF conversion when:
- You need a quick PDF without JATS XML processing
- You want to preserve original Word formatting
- You don't need PMC/NLM compliance
- You're generating PDFs for internal review
- Speed is more important than semantic structure

Use JATS XML-based PDF when:
- Submitting to PMC or journals
- You need JATS 1.4 compliance
- Semantic structure is important
- You need metadata validation
- You're archiving for long-term preservation

## How It Works

### Integrated in Pipeline

When you convert a DOCX file through the main pipeline:

```python
from MasterPipeline import HighFidelityConverter

converter = HighFidelityConverter("document.docx")
output_dir = converter.run_pipeline()

# Output includes:
# - article.xml (JATS XML)
# - published_article.pdf (from JATS XML)
# - direct_from_word.pdf (direct conversion)
# - article.html (HTML version)
# - media/ (extracted images)
```

Both PDFs are automatically generated in the output package.

### Standalone Tool

For direct PDF conversion only (no JATS XML):

```bash
# Basic usage
python tools/direct_pdf_converter.py input.docx output.pdf

# With custom CSS
python tools/direct_pdf_converter.py input.docx output.pdf --css custom.css

# With validation
python tools/direct_pdf_converter.py input.docx output.pdf --validate

# Verbose output
python tools/direct_pdf_converter.py input.docx output.pdf --verbose
```

### Tool Features

The standalone `direct_pdf_converter.py` provides:

- ✓ Dependency checking (Pandoc, WeasyPrint)
- ✓ Direct DOCX to PDF conversion
- ✓ Optional CSS styling
- ✓ PDF validation
- ✓ Detailed logging
- ✓ Error handling with fallbacks

## Technical Details

### Conversion Process

1. **DOCX to HTML**
   - Uses Pandoc to convert DOCX to standalone HTML
   - Preserves formatting, tables, images
   - Self-contained HTML with embedded resources

2. **HTML to PDF**
   - Uses WeasyPrint for PDF generation
   - Applies CSS styling if provided
   - Generates high-quality PDF output

### Requirements

- Python 3.11+
- Pandoc 3.x
- WeasyPrint 61.2+

### Quality Checks

The tool performs basic validation:
- File existence check
- PDF header verification (`%PDF`)
- File size validation
- Readability test

## Comparison: Direct PDF vs JATS-derived PDF

| Feature | Direct PDF | JATS-derived PDF |
|---------|-----------|------------------|
| Speed | ⚡ Fast (seconds) | 🐌 Slower (minutes) |
| Formatting | Original Word | Standardized |
| PMC Compliance | ❌ No | ✅ Yes |
| JATS Validation | ❌ No | ✅ Yes |
| Metadata | Basic | Rich (JATS) |
| Tables | Word layout | PMC-compliant |
| Figures | As-is | With captions |
| References | As-is | Structured |
| Use Case | Quick preview | Journal submission |

## Examples

### Example 1: Quick PDF for Review

```bash
# Generate PDF quickly for internal review
python tools/direct_pdf_converter.py manuscript.docx review.pdf
```

### Example 2: Styled PDF with Validation

```bash
# Generate PDF with custom styling and validate
python tools/direct_pdf_converter.py \
  manuscript.docx \
  styled_output.pdf \
  --css templates/style.css \
  --validate \
  --verbose
```

### Example 3: Using in Python Script

```python
from pathlib import Path
import sys

# Add tools directory to path
sys.path.append('tools')

from direct_pdf_converter import convert_docx_to_pdf, validate_pdf

# Convert DOCX to PDF
success = convert_docx_to_pdf(
    'input.docx',
    'output.pdf',
    css_path='templates/style.css'
)

if success:
    # Validate the generated PDF
    results = validate_pdf('output.pdf')
    print(f"PDF valid: {results['valid']}")
    print(f"Size: {results['size_mb']:.2f} MB")
```

## Troubleshooting

### Issue: Pandoc not found

```
ERROR: Missing required tools: pandoc
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Windows
# Download from https://pandoc.org/installing.html
```

### Issue: WeasyPrint not installed

```
ERROR: WeasyPrint not installed
```

**Solution:**
```bash
pip install weasyprint

# On Ubuntu/Debian, you may also need:
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

### Issue: PDF generation failed

```
ERROR: Conversion failed: ...
```

**Common causes:**
1. Corrupted DOCX file - try opening in Word first
2. Complex formatting - simplify document
3. Large images - reduce image sizes
4. Memory issues - close other applications

**Solution:**
```bash
# Try with verbose logging to see detailed error
python tools/direct_pdf_converter.py input.docx output.pdf --verbose
```

### Issue: Invalid PDF generated

```
WARNING: File does not have PDF header
```

**Solution:**
1. Check input DOCX file is valid
2. Try with different CSS or no CSS
3. Check WeasyPrint logs for errors
4. Use `--validate` flag to see detailed validation

## Performance

### Speed Comparison

| Document Size | Direct PDF | JATS-derived PDF |
|--------------|-----------|------------------|
| 5 pages | ~2 seconds | ~30 seconds |
| 20 pages | ~5 seconds | ~90 seconds |
| 50 pages | ~15 seconds | ~240 seconds |

*Times are approximate and depend on document complexity*

### File Size

Direct PDFs are typically:
- Smaller for simple documents (less metadata)
- Larger for documents with many images (embedded differently)
- Similar size to JATS-derived PDFs overall

## Best Practices

### 1. Choose the Right Method

- **Use Direct PDF for:**
  - Internal drafts and reviews
  - Quick document sharing
  - Format preservation
  - Fast turnaround

- **Use JATS PDF for:**
  - Journal submissions
  - PMC archiving
  - Long-term preservation
  - Compliance requirements

### 2. Optimize Input Documents

- Keep formatting simple
- Optimize images before adding to DOCX
- Use standard fonts
- Avoid complex tables

### 3. Validate Output

Always validate generated PDFs:
```bash
python tools/direct_pdf_converter.py input.docx output.pdf --validate
```

### 4. Use CSS for Styling

Provide custom CSS for better output:
```bash
python tools/direct_pdf_converter.py \
  input.docx output.pdf \
  --css templates/style.css
```

## Integration with CI/CD

### Example GitHub Actions

```yaml
name: Generate PDF

on: [push]

jobs:
  pdf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: |
          sudo apt-get install pandoc
          pip install weasyprint
      
      - name: Generate PDF
        run: |
          python tools/direct_pdf_converter.py \
            document.docx \
            output.pdf \
            --validate
      
      - name: Upload PDF
        uses: actions/upload-artifact@v2
        with:
          name: generated-pdf
          path: output.pdf
```

## API Reference

### convert_docx_to_pdf()

```python
def convert_docx_to_pdf(docx_path, pdf_path, css_path=None):
    """
    Convert DOCX to PDF directly without JATS XML.
    
    Args:
        docx_path (str): Path to input DOCX file
        pdf_path (str): Path to output PDF file
        css_path (str, optional): Path to CSS file for styling
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
```

### validate_pdf()

```python
def validate_pdf(pdf_path):
    """
    Perform basic validation on the generated PDF.
    
    Args:
        pdf_path (str): Path to PDF file
    
    Returns:
        dict: Validation results with keys:
            - exists (bool): File exists
            - size_bytes (int): File size in bytes
            - size_mb (float): File size in MB
            - readable (bool): File can be read
            - valid (bool): Valid PDF format
    """
```

## Future Enhancements

Planned improvements:
- [ ] PDF/A compliance for archival
- [ ] Batch conversion support
- [ ] Progress callback for large files
- [ ] Custom metadata injection
- [ ] Watermark support
- [ ] Page numbering options
- [ ] Table of contents generation
- [ ] Bookmarks from headings

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review validation output with `--validate --verbose`
3. Check Pandoc and WeasyPrint documentation
4. Review DOCX file in Microsoft Word for compatibility

## References

- **Pandoc Documentation**: https://pandoc.org/
- **WeasyPrint Documentation**: https://weasyprint.org/
- **DOCX Format Specification**: https://docs.microsoft.com/en-us/openspecs/office_standards/
- **Main Pipeline Documentation**: See README.md

---

**Last Updated**: 2026-01-20  
**Version**: 1.0  
**Tool Location**: `tools/direct_pdf_converter.py`
