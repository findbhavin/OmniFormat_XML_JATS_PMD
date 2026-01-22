# HTML Table DTD Validation Fix - Documentation

## Overview

This document describes the fix implemented to resolve HTML table DTD validation errors in the OmniFormat XML/JATS/PMD conversion pipeline.

## Problem Statement

The conversion pipeline was generating HTML tables that violated the JATS DTD structure requirements. Specifically:

1. **Incorrect element order**: `<colgroup>` elements appeared AFTER `<thead>`, violating the DTD requirement that column definitions must come first
2. **Missing tbody elements**: Tables with `<thead>` but no `<tbody>` were invalid according to DTD rules

### DTD Requirement

The JATS DTD specifies table structure as:
```
((col* | colgroup*), ((thead?, tfoot?, tbody+) | tr+))
```

This means:
- First: Zero or more `<col>` OR `<colgroup>` elements
- Then EITHER:
  - Optional `<thead>`, optional `<tfoot>`, and one or more `<tbody>` elements
  - OR direct `<tr>` elements

**Critical rule**: If `<thead>` or `<tfoot>` exists, at least one `<tbody>` MUST also exist.

## Solution

### 1. Table Element Reordering (MasterPipeline.py lines 962-1015)

Added logic to reorder table child elements to match DTD requirements:

```python
# Collect all table children by type
col_elements = []
colgroup_elements = []
thead_element = None
tfoot_element = None
tbody_elements_list = []
tr_elements_list = []

# Clear table and rebuild in correct order
# 1. col/colgroup first
# 2. thead
# 3. tfoot  
# 4. tbody
# 5. tr elements
```

**Effect**: Ensures `<colgroup>` always appears before `<thead>`, regardless of source document structure.

### 2. tbody Requirement Enforcement (MasterPipeline.py lines 1030-1064)

Modified tbody handling to always add tbody when thead exists:

```python
if remaining_tbody_count == 0:
    tbody = etree.Element('tbody')
    tr = etree.SubElement(tbody, 'tr')
    td = etree.SubElement(tr, 'td')
    td.text = None  # Empty content
    tr.set('class', 'dtd-compliance-row')  # Hidden via CSS
    
    # Insert after thead
    table.insert(insert_index, tbody)
```

**Effect**: 
- All tables with `<thead>` now have required `<tbody>`
- Empty rows are hidden using CSS class (not inline styles)
- Visual appearance is preserved

### 3. CSS Class for Hidden Rows (templates/style.css)

Added CSS rule to hide DTD compliance rows:

```css
/* Hide DTD compliance rows (added for table structure validation) */
tr.dtd-compliance-row {
    display: none;
    visibility: hidden;
}
```

**Benefits**:
- Consistent styling across application
- Easy to maintain and modify
- Better than inline styles per code review feedback

### 4. HTML Table Reconstruction (MasterPipeline.py lines 1688-1793)

Updated HTML table rebuilding to maintain correct DTD order:

```python
# Rebuild in DTD-compliant order
# 1. col and colgroup elements
for xml_col in xml_table.findall('./col'):
    html_table.append(html_col)
    
for xml_colgroup in xml_table.findall('./colgroup'):
    html_table.append(html_colgroup)

# 2. thead
if xml_thead is not None:
    html_table.append(html_thead)

# 3. tbody
if xml_tbody is not None:
    html_table.append(html_tbody)
```

## Before/After Examples

### Example 1: Wrong Element Order

**BEFORE** (Invalid):
```xml
<table>
  <thead>
    <tr><th>Header</th></tr>
  </thead>
  <colgroup>
    <col width="100%"/>
  </colgroup>
  <!-- Missing tbody! -->
</table>
```

**AFTER** (Valid):
```xml
<table>
  <colgroup>
    <col width="100%"/>
  </colgroup>
  <thead>
    <tr><th>Header</th></tr>
  </thead>
  <tbody>
    <tr class="dtd-compliance-row">
      <td></td>
    </tr>
  </tbody>
</table>
```

### Example 2: Informational Table (all content in thead)

**BEFORE** (Invalid):
```xml
<table>
  <colgroup>
    <col width="50%"/>
    <col width="50%"/>
  </colgroup>
  <thead>
    <tr><th colspan="2">Article Info</th></tr>
    <tr><th>Author:</th><th>John Doe</th></tr>
    <tr><th>Date:</th><th>2026-01-22</th></tr>
  </thead>
  <!-- No tbody - DTD violation! -->
</table>
```

**AFTER** (Valid):
```xml
<table>
  <colgroup>
    <col width="50%"/>
    <col width="50%"/>
  </colgroup>
  <thead>
    <tr><th colspan="2">Article Info</th></tr>
    <tr><th>Author:</th><th>John Doe</th></tr>
    <tr><th>Date:</th><th>2026-01-22</th></tr>
  </thead>
  <tbody>
    <tr class="dtd-compliance-row">
      <td></td>
    </tr>
  </tbody>
</table>
```

Note: The hidden row in tbody is not visible to users due to CSS.

## Testing Results

### Validation Tests

✅ All 5 tables in `Output files/article.xml` now pass DTD validation
✅ All tables in `examples/outputs/article.xml` pass validation
✅ Visual appearance preserved - no extra visible rows
✅ Correct element order in all tables: colgroup → thead → tbody

### Test Script

Created comprehensive validation script (`/tmp/validate_table_structure.py`) that checks:
- Element order matches DTD requirements
- tbody exists when thead/tfoot present
- Runs against both example and production output files

### Code Quality

✅ Code review completed - all comments addressed
✅ Security scan (CodeQL) - no vulnerabilities found
✅ Import test successful
✅ Python syntax valid

## Impact

### Files Modified

1. **MasterPipeline.py** (3 sections)
   - Lines 962-1015: Table element reordering
   - Lines 1030-1064: tbody requirement enforcement  
   - Lines 1688-1793: HTML table reconstruction

2. **templates/style.css** (1 addition)
   - Added `.dtd-compliance-row` CSS rule

3. **Output files/article.xml** (fixed)
   - 4 tables corrected to add tbody with hidden rows
   - 1 table already valid, no changes needed

### Backward Compatibility

✅ No breaking changes
✅ Existing tables without issues remain unchanged
✅ Only adds tbody when necessary (thead/tfoot present)
✅ Visual appearance preserved via CSS

## Key Design Decisions

### 1. CSS Class vs Inline Styles

**Decision**: Use CSS class `dtd-compliance-row` instead of inline `style="display: none;"`

**Rationale**:
- Better maintainability
- Consistent with best practices
- Easier to modify styling globally
- Recommended by code review

### 2. Empty Cell Content

**Decision**: Use `td.text = None` instead of `td.text = ''`

**Rationale**:
- More explicit for intentionally empty content
- Avoids potential rendering inconsistencies
- Recommended by code review

### 3. Always Add tbody When thead Exists

**Decision**: Remove condition that skipped tbody for tables with multiple thead rows

**Rationale**:
- DTD strictly requires tbody when thead exists
- Previous logic violated DTD to avoid "blank rows in HTML"
- New approach: add tbody but hide the row with CSS
- Result: DTD compliance AND preserved visual appearance

## Maintenance Notes

### Adding More Hidden Row Styles

If you need to modify how hidden rows appear (e.g., for debugging), edit `templates/style.css`:

```css
/* Example: Show hidden rows with reduced opacity for debugging */
tr.dtd-compliance-row {
    opacity: 0.1;  /* Instead of display: none */
}
```

### Extending to Other Table Types

If you encounter other table structures that need special handling:

1. Add new CSS class in `templates/style.css`
2. Set the class in `MasterPipeline.py` tbody creation
3. Update this documentation

## Related Files

- `MasterPipeline.py` - Main conversion pipeline
- `templates/style.css` - Stylesheet with CSS rules
- `tools/add_doctype.py` - DTD DOCTYPE declaration tool
- `pmc-stylechecker/pmc_style_checker.xsl` - PMC validation tool

## References

- JATS Publishing DTD v1.3: https://jats.nlm.nih.gov/publishing/1.3/
- HTML5 Table Specification: https://html.spec.whatwg.org/multipage/tables.html
- PMC Style Checker: https://www.ncbi.nlm.nih.gov/pmc/pub/stylechecker/

## Summary

This fix ensures all generated tables comply with JATS DTD structure requirements by:

1. ✅ Reordering table elements to match DTD specification
2. ✅ Adding required tbody when thead exists
3. ✅ Preserving visual appearance using CSS
4. ✅ Following code review best practices
5. ✅ Maintaining backward compatibility

All tables now pass DTD validation while maintaining their original appearance in HTML output.
