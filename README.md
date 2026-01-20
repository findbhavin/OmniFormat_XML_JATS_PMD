# OmniJAX - JATS 1.4 Publishing DTD Converter

Professional DOCX to JATS XML and dual-PDF conversion pipeline with full PMC/NLM compliance.

## Official Standards Compliance

- **JATS 1.4 Publishing DTD**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

## Features

1. **JATS 1.4 Publishing DTD Compliance**
   - Validates against official NLM XSD schemas
   - Full PMC/NLM Style Checker compatibility
   - Proper namespace declarations (XLink, MathML)
   - MathML 2.0/3.0 support

2. **PMC-Specific Validation**
   - Automated PMC requirements checking
   - DOI and metadata validation
   - Author affiliation structure verification
   - Table positioning (float/anchor)
   - Figure and caption compliance
   - Reference formatting validation

3. **Dual PDF Generation**
   - PDF from JATS XML (semantic, PMC-ready)
   - Direct DOCX→PDF (format preserving)

4. **AI-Powered Content Repair**
   - Fixes truncated headers
   - Ensures PMC metadata requirements
   - Validates accessibility compliance
   - Proper author formatting with affiliations
   - Special character encoding

5. **Automatic Features**
   - Table captions with proper positioning
   - Media extraction to `/media` folder
   - Superscript/subscript preservation
   - Section ID generation
   - Comprehensive validation reporting

## Project Structure

```
.
├── MasterPipeline.py           # Main conversion pipeline with JATS 1.4 compliance
├── app.py                      # Flask web application
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
├── JATS-journalpublishing-*.xsd # JATS schema files
├── templates/
│   ├── index.html             # Upload interface
│   └── style.css              # PMC-compliant PDF styling
├── standard-modules/          # JATS XSD modules
│   ├── mathml2/              # MathML 2.0 schema
│   ├── xlink.xsd             # XLink schema
│   └── xml.xsd               # XML namespace schema
└── tools/
    └── safe_render.py         # Validation and rendering tool
```

## JATS 1.4 and PMC Compliance Features

### Required Elements for PMC Submission

The converter ensures all PMC-required elements are present:

1. **Article Root**
   - `dtd-version="1.4"`
   - `article-type` attribute
   - XLink namespace: `xmlns:xlink="http://www.w3.org/1999/xlink"`
   - MathML namespace: `xmlns:mml="http://www.w3.org/1998/Math/MathML"`

2. **Front Matter**
   - `<journal-meta>` with journal information
   - `<article-meta>` with:
     - DOI (`<article-id pub-id-type="doi">`)
     - Article title
     - Author contributions with proper affiliations
     - Abstract
     - Publication date
     - Keywords

3. **Body Structure**
   - Properly nested `<sec>` elements with IDs
   - Section titles
   - Proper table and figure formatting

4. **Back Matter**
   - References with unique IDs
   - Acknowledgments
   - Author contributions
   - Funding information

### PMC Validation Checks

The pipeline performs comprehensive PMC compliance checks:

- DTD version validation
- Required metadata presence
- Author affiliation structure
- Table positioning and caption placement
- Figure elements and captions
- Reference formatting
- Section ID attributes
- Special character encoding

### Table Formatting

Tables are formatted according to PMC requirements:
- `position="float"` or `position="anchor"` (not "top")
- Caption as first child element
- Proper label for table numbers
- Minimal use of colspan/rowspan

### Figure Formatting

Figures include:
- Unique ID attributes
- Label elements for figure numbers
- Caption elements with descriptions
- Proper graphic references with XLink namespace

## Output Package

Each conversion generates a complete package:

1. **article.xml** - JATS 1.4 Publishing DTD XML
2. **published_article.pdf** - PDF from JATS XML
3. **direct_from_word.pdf** - Direct DOCX conversion
4. **article.html** - HTML version
5. **media/** - All extracted images
6. **validation_report.json** - Detailed validation report with:
   - JATS schema validation results
   - PMC compliance check results
   - Critical issues and warnings
   - Document structure analysis
   - PMC submission checklist
7. **README.txt** - Package documentation

## Validation Report

The validation report includes:

```json
{
  "jats_validation": {
    "status": "PASS/FAIL",
    "target_version": "JATS 1.4",
    "official_schema": "https://public.nlm.nih.gov/projects/jats/publishing/1.4/"
  },
  "pmc_compliance": {
    "status": "PASS/WARNING",
    "reference": "https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/",
    "details": {
      "critical_issues": [],
      "warnings": [],
      "issues_count": 0,
      "warnings_count": 0
    }
  },
  "document_structure": {
    "dtd_version": "1.4",
    "article_type": "research-article",
    "table_count": 5,
    "figure_count": 3,
    "reference_count": 25
  },
  "pmc_submission_checklist": [
    "Validate with PMC Style Checker",
    "Ensure all figures have alt text",
    "Verify references are properly formatted",
    ...
  ]
}
```

## Usage

1. Upload DOCX file through web interface
2. System converts to JATS 1.4 XML
3. AI-powered repair fixes common issues
4. PMC compliance validation runs automatically
5. Download complete package

## PMC Submission Workflow

1. Convert document using OmniJAX
2. Review `validation_report.json`
3. Fix any critical issues identified
4. Validate using PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
5. Review warnings and recommendations
6. Submit to PMC

## Technical Requirements

- Python 3.11+
- Pandoc 3.x with JATS support
- WeasyPrint for PDF generation
- lxml for XML processing
- Google Vertex AI (optional, for AI repair)

## References

- **JATS Official Site**: https://jats.nlm.nih.gov/
- **JATS 1.4 Publishing DTD**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- **NLM PMC**: https://pmc.ncbi.nlm.nih.gov/

## License

Proprietary - OmniJAX Professional JATS Converter
