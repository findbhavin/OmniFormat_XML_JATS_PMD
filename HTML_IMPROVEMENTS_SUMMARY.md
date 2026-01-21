# HTML Creation Process Improvements

## Summary

This update addresses two critical issues in the HTML generation process:

1. **Dynamic Article Title Extraction**: Previously hardcoded as "Article Title", the HTML title now dynamically extracts the actual article type from the Word document.
2. **Complete Table Column Preservation**: Fixed an issue where tables in HTML were missing columns due to Pandoc's JATS-to-HTML conversion bug.

## Changes Made

### 1. Article Type Extraction

**File**: `MasterPipeline.py`

**New Method**: `_extract_article_type_from_docx()`
- Reads the Word document using `python-docx` library
- Scans the first 5 paragraphs for uppercase text (article type indicator)
- Returns the article type string or None if not found
- Handles edge cases: missing file, no uppercase text, exceptions

**Modified Method**: `_post_process_xml()`
- Now calls `_extract_article_type_from_docx()` when adding title-group
- Uses extracted article type instead of hardcoded "Article Title"
- Falls back to "Article Title" if extraction fails

### 2. Table Column Preservation

**File**: `MasterPipeline.py`

**Modified Method**: `_post_process_html()`
- Enhanced to fix table structures in addition to reference anchors
- Compares HTML table columns with JATS XML source
- Triggers reconstruction when HTML has fewer columns than XML

**New Method**: `_fix_html_table_structure(xml_table, html_table)`
- Detects tables with missing columns in HTML
- Clears incorrect HTML table structure
- Rebuilds thead and tbody from JATS XML source

**New Method**: `_rebuild_table_section(xml_section, html_section)`
- Helper method to reduce code duplication
- Processes table rows and cells from XML to HTML
- Handles text content, child elements, and attributes (e.g., colspan)
- Optimizes tail text handling

**New Method**: `_convert_xml_to_html_element(xml_elem)`
- Recursively converts JATS XML elements to HTML elements
- Maps JATS tags to HTML tags (e.g., bold → strong, italic → em)
- Preserves text content, attributes, and child elements

## Dependencies

- **python-docx**: Added import `from docx import Document` for reading Word document structure

## Testing Results

### Test Document
- File: `10. Uma Phalswal 5599 SYSMETA.docx`
- Article Type: "SYSTEMATIC REVIEW/META ANALYSIS"
- Contains 5 tables with varying column counts

### Before Changes
- HTML Title: "Article Title" (hardcoded)
- Table 2: 1 column (should be 13)
- Table 3: 1 column (should be 12)
- Table 4: 1 column (should be 11)
- Table 5: 1 column (should be 3)

### After Changes
- ✅ HTML Title: "SYSTEMATIC REVIEW/META ANALYSIS" (extracted)
- ✅ Table 2: 13 columns (all preserved)
- ✅ Table 3: 12 columns (all preserved)
- ✅ Table 4: 11 columns (all preserved)
- ✅ Table 5: 3 columns (all preserved)

### Edge Cases Tested
- ✅ Missing DOCX file: Returns None gracefully
- ✅ No uppercase text in paragraphs: Returns None with warning
- ✅ Exception handling: Catches and logs errors without crashing

## Code Quality

### Code Review
- All code review suggestions addressed:
  - ✅ Magic numbers replaced with named constants
  - ✅ Code duplication eliminated via helper methods
  - ✅ Repeated list() calls optimized

### Security Scan
- ✅ CodeQL analysis: 0 security vulnerabilities found

## Table Formatting

The existing CSS (`templates/style.css`) already provides professional table styling:
- Alternating row colors for readability
- Header highlighting with blue background
- Proper borders and padding
- Responsive design with hover effects
- Print-optimized styles

No changes to CSS were needed as the styling is already professional and meets requirements.

## Impact

- **User Experience**: Article titles now accurately reflect the document type
- **Data Integrity**: All table columns are preserved, no data loss
- **Professional Appearance**: Tables maintain their structure and professional styling
- **Reliability**: Robust error handling for edge cases
- **Maintainability**: Code is well-organized with named constants and helper methods

## Technical Notes

### Pandoc JATS-to-HTML Conversion Bug
Pandoc (tested with version 3.1.9) has a known issue where it incorrectly converts JATS tables with certain structures:
- Tables with `<colgroup>` elements may lose column structure
- Each cell can be converted into a separate row instead of columns
- This affects the visual presentation and data readability

**Solution**: Post-process the HTML by comparing with the source JATS XML and reconstructing tables when column counts don't match.

### Article Type Detection Logic
The article type is typically:
- Located in the first paragraph of the Word document
- Formatted in UPPERCASE (e.g., "SYSTEMATIC REVIEW/META ANALYSIS", "ORIGINAL RESEARCH ARTICLE")
- Often placed in a text box on the first page
- Used as a document classification indicator

**Solution**: Scan first 5 paragraphs for uppercase text longer than 5 characters.

## Future Enhancements

Potential improvements for future consideration:
1. Support for article types in different locations (e.g., headers, specific text boxes)
2. Internationalization support for non-English article types
3. Configurable article type detection patterns
4. Enhanced table structure validation
5. Performance optimization for large documents with many tables

## Backward Compatibility

These changes are backward compatible:
- Existing functionality is preserved
- Fallback to "Article Title" if extraction fails
- No breaking changes to API or file formats
- Works with existing JATS XML and CSS files
