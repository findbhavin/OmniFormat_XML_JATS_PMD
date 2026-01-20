# PMC Style Checker Compliance Checklist

This document outlines how OmniJAX complies with PMC Style Checker requirements.

## Official PMC Resources

- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- **JATS 1.4 Publishing DTD**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/

## Required Article Structure

### 1. Root Element ✓

**PMC Requirement**: Article element with proper attributes and namespaces

**Implementation**:
```xml
<article dtd-version="1.4"
         article-type="research-article"
         xmlns:xlink="http://www.w3.org/1999/xlink"
         xmlns:mml="http://www.w3.org/1998/Math/MathML">
```

**Code Location**: `MasterPipeline._post_process_xml()`

**Validation**: `MasterPipeline._validate_pmc_requirements()` - Check #1, #2, #3

### 2. Front Matter ✓

**PMC Requirement**: Complete journal and article metadata

**Required Elements**:
- `<journal-meta>`: Journal identification
- `<article-meta>`: Article identification and metadata
- `<article-id pub-id-type="doi">`: Digital Object Identifier (MANDATORY)
- `<title-group>`: Article title
- `<contrib-group>`: Author information
- `<aff>`: Affiliations with IDs
- `<pub-date>`: Publication date
- `<abstract>`: Article abstract (highly recommended)

**Implementation**: AI repair and post-processing ensure these elements

**Code Location**:
- `MasterPipeline._fix_with_ai()` - Prompt section 2
- `MasterPipeline._validate_pmc_requirements()` - Check #4

### 3. Author Formatting ✓

**PMC Requirement**: Proper author-affiliation linking

**Structure**:
```xml
<contrib-group>
  <contrib contrib-type="author">
    <name>
      <surname>Smith</surname>
      <given-names>John</given-names>
    </name>
    <xref ref-type="aff" rid="aff1">
      <sup>1</sup>
    </xref>
  </contrib>
</contrib-group>
<aff id="aff1">
  <label>1</label>
  <institution>University Name</institution>
  <country>USA</country>
</aff>
```

**Implementation**: AI repair converts author notations

**Code Location**: `MasterPipeline._fix_with_ai()` - Prompt section 3

**Validation**: `MasterPipeline._validate_pmc_requirements()` - Check #4

### 4. Table Formatting ✓

**PMC Requirement**: Tables with proper positioning and caption placement

**Critical Rules**:
1. `position` attribute must be "float" or "anchor" (NOT "top")
2. Caption must be FIRST child of table-wrap
3. Use `<label>` for table numbers
4. Minimize colspan/rowspan usage

**Structure**:
```xml
<table-wrap id="tbl1" position="float">
  <label>Table 1</label>
  <caption>
    <title>Study Results</title>
  </caption>
  <table>
    <thead>...</thead>
    <tbody>...</tbody>
  </table>
</table-wrap>
```

**Implementation**:
- Post-processing changes "top" to "float"
- AI repair ensures proper structure

**Code Location**:
- `MasterPipeline._post_process_xml()` - Lines 602-606
- `MasterPipeline._fix_with_ai()` - Prompt section 4

**Validation**: `MasterPipeline._validate_pmc_requirements()` - Check #6

### 5. Figure Formatting ✓

**PMC Requirement**: Figures with proper elements and graphic references

**Required Elements**:
- `<fig>` with unique `id` attribute
- `<label>` for figure number
- `<caption>` with title and description
- `<graphic>` with XLink namespace

**Structure**:
```xml
<fig id="fig1">
  <label>Figure 1</label>
  <caption>
    <title>Study Design</title>
    <p>Description of the figure.</p>
  </caption>
  <graphic xlink:href="media/figure1.png"/>
</fig>
```

**Implementation**: AI repair and validation checks

**Code Location**:
- `MasterPipeline._fix_with_ai()` - Prompt section 5
- `MasterPipeline._validate_pmc_requirements()` - Check #7

### 6. Body Structure ✓

**PMC Requirement**: Proper section hierarchy with IDs

**Required**:
- `<sec>` elements with `id` attributes
- `<title>` for each section
- Proper nesting

**Structure**:
```xml
<body>
  <sec id="sec1">
    <title>Introduction</title>
    <p>Content...</p>
  </sec>
  <sec id="sec2">
    <title>Methods</title>
    <p>Content...</p>
  </sec>
</body>
```

**Implementation**: AI repair adds section IDs

**Code Location**:
- `MasterPipeline._fix_with_ai()` - Prompt section 8
- `MasterPipeline._validate_pmc_requirements()` - Check #5

### 7. References ✓

**PMC Requirement**: Proper reference structure with unique IDs

**Required Elements**:
- `<ref-list>` in `<back>` section
- Each `<ref>` with unique `id`
- Proper citation elements

**Structure**:
```xml
<back>
  <ref-list>
    <ref id="ref1">
      <element-citation publication-type="journal">
        <person-group person-group-type="author">
          <name><surname>Smith</surname></name>
        </person-group>
        <article-title>Title</article-title>
        <source>Journal Name</source>
        <year>2020</year>
      </element-citation>
    </ref>
  </ref-list>
</back>
```

**Implementation**: AI repair and validation

**Code Location**:
- `MasterPipeline._fix_with_ai()` - Prompt section 6
- `MasterPipeline._validate_pmc_requirements()` - Check #8

### 8. Special Characters ✓

**PMC Requirement**: Proper XML entity encoding

**Entities**:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&apos;`

**Unicode Examples**:
- ₹ (Rupee) → `&#x20B9;`
- ± (Plus-minus) → `&#xB1;`
- ≥ (Greater-equal) → `&#x2265;`
- ≤ (Less-equal) → `&#x2264;`

**Implementation**: Rule-based and AI repair

**Code Location**:
- `MasterPipeline._fix_with_rules()` - Lines 196-203
- `MasterPipeline._fix_with_ai()` - Prompt section 7

## Validation Process

### Automated Checks

The system performs these checks automatically:

1. **Schema Validation**: Against JATS XSD
2. **DTD Version**: Ensures 1.3 or 1.4
3. **Namespaces**: Validates XLink and MathML
4. **Metadata**: Checks required elements
5. **Structure**: Validates hierarchy
6. **Tables**: Checks positioning and captions
7. **Figures**: Validates elements
8. **References**: Checks IDs

### Validation Report

Each conversion generates `validation_report.json` with:

```json
{
  "pmc_compliance": {
    "status": "PASS/WARNING",
    "details": {
      "critical_issues": [],
      "warnings": [],
      "issues_count": 0,
      "warnings_count": 0
    }
  }
}
```

### Manual Verification Steps

After conversion:

1. ✓ Review `validation_report.json`
2. ✓ Check critical issues (fix immediately)
3. ✓ Review warnings (address before submission)
4. ✓ Upload XML to PMC Style Checker
5. ✓ Fix any additional issues found
6. ✓ Re-validate until clean

## Common PMC Issues and Fixes

### Issue 1: Table Position "top"

**Problem**: `<table-wrap position="top">` not PMC compliant

**Fix**: Automatically changed to `position="float"`

**Code**: `MasterPipeline._post_process_xml()` line 604-606

### Issue 2: Missing Namespaces

**Problem**: XLink or MathML namespace not declared

**Fix**: Automatically added in post-processing

**Code**: `MasterPipeline._post_process_xml()` lines 611-620

### Issue 3: Missing Section IDs

**Problem**: `<sec>` elements without `id` attributes

**Fix**: AI repair adds IDs, validation warns

**Code**:
- AI repair: `MasterPipeline._fix_with_ai()`
- Validation: `MasterPipeline._validate_pmc_requirements()` check #5

### Issue 4: Missing DOI

**Problem**: No `<article-id pub-id-type="doi">`

**Fix**: Validation warns (requires manual addition)

**Code**: `MasterPipeline._validate_pmc_requirements()` check #4

### Issue 5: Improper Author Formatting

**Problem**: Authors not properly linked to affiliations

**Fix**: AI repair converts to proper structure

**Code**: `MasterPipeline._fix_with_ai()` prompt section 3

## PMC Submission Checklist

Before submitting to PMC:

- [ ] Run conversion through OmniJAX
- [ ] Review `validation_report.json`
- [ ] Fix all critical issues
- [ ] Validate with PMC Style Checker
- [ ] Verify DOI is present and correct
- [ ] Check all author affiliations are linked
- [ ] Verify all figures have captions and alt text
- [ ] Confirm references are properly formatted
- [ ] Check table structure and captions
- [ ] Validate special characters
- [ ] Review mathematical notation
- [ ] Verify abstract is present
- [ ] Check publication date
- [ ] Confirm journal metadata
- [ ] Review funding information (if applicable)

## Testing Your XML

### Using PMC Style Checker

1. Go to: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
2. Upload your `article.xml` file
3. Review results
4. Fix any errors or warnings
5. Re-upload until clean

### Common Validation Errors

1. **Missing required elements**: Add them manually or re-run conversion
2. **Invalid namespace**: Fixed automatically by OmniJAX
3. **Table positioning**: Fixed automatically
4. **Missing IDs**: Add manually or rely on AI repair
5. **Invalid references**: May require manual formatting

## Support and Resources

### Documentation

- JATS Tag Library: https://jats.nlm.nih.gov/
- PMC Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/
- PMC FAQs: https://pmc.ncbi.nlm.nih.gov/about/faq/

### Tools

- PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- JATS XML Validator: Various online validators available

### Getting Help

1. Review validation_report.json
2. Check PMC tagging guidelines
3. Use PMC Style Checker
4. Consult JATS documentation
5. Review examples in PMC

---

**Last Updated**: 2026-01-20
**Compliance Level**: JATS 1.4 Publishing DTD + PMC Requirements
**Validation**: Automated + Manual Verification Recommended
