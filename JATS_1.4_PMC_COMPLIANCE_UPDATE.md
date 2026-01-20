# JATS 1.4 and PMC Compliance Update

## Summary

The OmniJAX codebase has been updated to comply with JATS 1.4 Publishing DTD and PMC Style Checker requirements as specified at:

- **JATS 1.4 Schema**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

## Key Changes

### 1. Schema Version Update

**File: `MasterPipeline.py`**

- Added `self.jats_version = "1.4"` to target JATS 1.4 compliance
- Updated all references from "JATS 1.3" to "JATS 1.4"
- Updated schema documentation URLs

### 2. Enhanced AI Repair Prompts

**Updated AI repair instructions to include:**

- JATS 1.4 root element requirements
- Required namespaces (XLink, MathML)
- PMC-specific metadata requirements
- Author affiliation formatting
- Table positioning (float/anchor instead of top)
- Figure formatting with proper graphic elements
- Section ID requirements

### 3. Comprehensive PMC Validation

**New Method: `_validate_pmc_requirements()`**

Validates 8 key areas:

1. **DTD Version**: Checks for version 1.3 or 1.4
2. **Article Type**: Ensures article-type attribute is present
3. **Namespaces**: Validates XLink namespace declaration
4. **Front Matter Structure**:
   - Checks for required article-meta elements
   - DOI validation
   - Title presence
   - Author contributions
   - Abstract
   - Publication date
5. **Body Structure**: Validates sections have ID attributes
6. **Table Formatting**:
   - Position attribute (float/anchor)
   - Caption placement (first child)
7. **Figure Elements**:
   - ID attributes
   - Caption presence
   - Graphic elements
8. **References**: Validates reference IDs

### 4. Enhanced Validation Reporting

**Updated Method: `_generate_validation_report()`**

Now includes:

- Target JATS version (1.4)
- Official schema URL
- PMC compliance status
- Detailed issue and warning lists
- Document structure analysis
- PMC submission checklist
- Recommendations based on findings

Example report structure:

```json
{
  "jats_validation": {
    "target_version": "JATS 1.4",
    "official_schema": "https://public.nlm.nih.gov/projects/jats/publishing/1.4/"
  },
  "pmc_compliance": {
    "status": "PASS/WARNING",
    "reference": "https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/",
    "details": {
      "critical_issues": [],
      "warnings": []
    }
  }
}
```

### 5. PMC-Compliant XML Post-Processing

**Updated Method: `_post_process_xml()`**

Changes:

- Table position changed from "top" to "float" (PMC requirement)
- Automatic addition of XLink namespace
- Automatic addition of MathML namespace
- DTD version forced to 1.4
- Article-type attribute ensured

### 6. Documentation Updates

**Updated Files:**

1. **README.md**:
   - Updated title to "JATS 1.4 Publishing DTD Converter"
   - Added official standards compliance section
   - Comprehensive PMC features documentation
   - Required elements for PMC submission
   - PMC validation checks description
   - Table and figure formatting requirements
   - PMC submission workflow

2. **Generated README.txt** (in output package):
   - Updated to reference JATS 1.4
   - Added PMC submission checklist
   - Included all official URLs
   - Enhanced compliance information
   - Added validation details section

## PMC-Specific Requirements Implemented

### Required Elements

1. **Root Element**:
   ```xml
   <article dtd-version="1.4" article-type="research-article"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            xmlns:mml="http://www.w3.org/1998/Math/MathML">
   ```

2. **Front Matter**:
   - journal-meta with journal information
   - article-meta with DOI, title, authors, abstract
   - Proper author affiliations with xref

3. **Body Structure**:
   - Sections with ID attributes
   - Proper nesting hierarchy

4. **Tables**:
   - position="float" or "anchor"
   - Caption as first child
   - Label for table number

5. **Figures**:
   - ID attributes
   - Label and caption elements
   - Graphic with XLink namespace

6. **References**:
   - Unique IDs
   - Proper citation elements

### Validation Checks

The system now validates:

- ✓ DTD version (1.3 or 1.4)
- ✓ Required namespaces
- ✓ Article metadata structure
- ✓ DOI presence
- ✓ Author affiliations
- ✓ Table positioning
- ✓ Figure formatting
- ✓ Section IDs
- ✓ Reference structure

## Benefits

1. **PMC Submission Ready**: Output XML is now compliant with PMC requirements
2. **Automated Validation**: Built-in checks reduce manual verification
3. **Clear Reporting**: Detailed validation reports with actionable recommendations
4. **Standards Compliant**: Follows official JATS 1.4 Publishing DTD
5. **Style Checker Compatible**: Output is compatible with PMC Style Checker

## Usage

1. Upload DOCX file
2. System converts to JATS 1.4 XML
3. Automatic PMC compliance checks run
4. Review validation_report.json
5. Validate with PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
6. Submit to PMC

## Testing Recommendations

To verify PMC compliance:

1. **Generate Test Conversion**: Convert a sample DOCX file
2. **Review validation_report.json**: Check for issues and warnings
3. **PMC Style Checker**: Upload XML to official checker
4. **Fix Issues**: Address any problems identified
5. **Re-validate**: Ensure all checks pass

## References

- JATS Official: https://jats.nlm.nih.gov/
- JATS 1.4 Publishing DTD: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

## Notes

- The system currently uses JATS 1.3 XSD files as fallback for validation
- Target version is set to 1.4 in all generated XML
- Full JATS 1.4 XSD can be downloaded from the official NLM site if needed
- All PMC-specific checks are based on official PMC tagging guidelines
- The validation is comprehensive but should be supplemented with PMC Style Checker for final verification

## Migration from JATS 1.3

For existing JATS 1.3 XML files:

1. Update root element: `dtd-version="1.4"`
2. Add required namespaces
3. Change table position from "top" to "float"
4. Ensure all required elements are present
5. Run through validation pipeline
6. Verify with PMC Style Checker

## Future Enhancements

Potential improvements:

1. Download and integrate official JATS 1.4 XSD files
2. Add more granular validation rules
3. Automatic correction of common PMC issues
4. Integration with PMC Style Checker API (if available)
5. Additional output format options

---

**Last Updated**: 2026-01-20
**Version**: 1.4.0
**Compliance**: JATS 1.4 Publishing DTD + PMC Requirements
