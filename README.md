# OmniJAX - Document Converter for Scientific Publications

## What is OmniJAX?

OmniJAX is a tool that converts your Microsoft Word documents into professional formats required for publishing scientific articles in academic journals and digital libraries. Think of it as a translator that takes your familiar Word document and converts it into specialized formats that publishers need, while ensuring everything meets strict formatting standards.

**In simple terms:** Upload your Word document → Get publication-ready files that meet journal requirements.

## Who Should Use This Tool?

- **Researchers & Authors**: Submit manuscripts to journals without worrying about complex formatting requirements
- **Publishers**: Convert submitted manuscripts to standardized formats for your digital library
- **Academic Institutions**: Prepare research papers and dissertations for institutional repositories
- **Students**: Format thesis and research papers according to publication standards

## Glossary - Understanding the Technical Terms

Before diving into the details, here are the key terms you'll encounter:

| Term | Simple Explanation |
|------|-------------------|
| **JATS** (Journal Article Tag Suite) | A standardized format for scientific articles. Think of it like HTML but specifically designed for research papers. It ensures your article can be properly displayed and searched in digital libraries. |
| **PMC** (PubMed Central) | A free digital library run by the US National Institutes of Health that hosts biomedical and life sciences research. It requires articles to be submitted in specific formats. |
| **XML** (eXtensible Markup Language) | A structured format for organizing information, similar to HTML. It uses tags like `<title>` and `<author>` to mark up different parts of your document. |
| **DTD** (Document Type Definition) | A set of rules that define what's allowed in an XML document, like a grammar book for documents. |
| **XSD** (XML Schema Definition) | Another way to define rules for XML documents, more modern than DTD. |
| **Validation** | The process of checking if your document follows all the required rules and standards. |
| **Metadata** | Information about your article (like title, authors, publication date) that helps people find and cite it. |

## Why Use OmniJAX?

### For Non-Technical Users
- ✅ **Easy to Use**: Simply upload your Word document and download the converted files
- ✅ **No Formatting Expertise Needed**: The tool automatically handles complex formatting requirements
- ✅ **Time Saving**: No manual reformatting or learning complex XML editors
- ✅ **Error Prevention**: Automatic validation ensures your submission meets journal requirements
- ✅ **Multiple Outputs**: Get several versions of your document for different purposes

### For Technical Users
- ✅ **Standards Compliant**: Full JATS 1.4 and PMC compliance
- ✅ **Automated Validation**: Built-in validation against official schemas
- ✅ **Extensible Pipeline**: Modular Python architecture for customization
- ✅ **Multiple Output Formats**: XML and HTML generation
- ✅ **API Access**: RESTful API for integration with other systems

## Quick Start Guide

### Step 1: Access the Tool

**Using the Web Interface** (Easiest for most users):
1. Open your web browser
2. Navigate to the OmniJAX website (URL provided by your administrator)
3. You'll see a simple upload interface

**Using the Command Line** (For technical users):
```bash
python app.py
# Then open http://localhost:8080 in your browser
```

### Step 2: Upload Your Document

1. Click the "Choose File" button or drag-and-drop your Word document onto the page
2. Supported format: Microsoft Word (.docx) files
3. Maximum file size: 50 MB
4. Click "Convert & Download Package"

### Step 3: Monitor Progress

The tool will show you a progress bar with updates like:
- "Processing document..." (0-20%)
- "Converting to JATS XML..." (20-40%)
- "Generating HTML..." (40-80%)
- "Validating output..." (80-100%)

This usually takes 30 seconds to 2 minutes depending on document size.

### Step 4: Download Your Results

Once complete (100%), click "Download Package" to get a ZIP file containing:

#### What You Get (For Non-Technical Users)
- 📄 **article.html** - HTML version for viewing in your browser
- 📄 **README.txt** - Explains what each file is for

#### What You Get (For Technical Users)
- 📄 **article.xml** - JATS XML for schema validation (XSD-compliant)
- 📄 **articledtd.xml** - JATS XML for PMC submission (DTD-compliant)
- 📄 **article.html** - HTML version with embedded images
- 📁 **media/** - All extracted images from your document
- 📄 **validation_report.json** - Detailed validation results
- 📄 **README.txt** - Package documentation

## Visual Workflow

```
┌─────────────────────┐
│  Your Word Document │
│    (article.docx)   │
└──────────┬──────────┘
           │
           │ Upload to OmniJAX
           ▼
┌──────────────────────┐
│   OmniJAX Converter  │
│                      │
│  • Reads content     │
│  • Structures data   │
│  • Applies standards │
│  • Validates format  │
└──────────┬───────────┘
           │
           │ Generates multiple outputs
           ▼
┌──────────────────────────────────────────────┐
│           Publication-Ready Files             │
├──────────────────────────────────────────────┤
│                                               │
│  ├─ article.html (For viewing)               │
│  │  Web-ready HTML version                   │
│  │                                            │
│  ├─ article.xml (For validation)             │
│  │  Technical format for quality checks      │
│  │                                            │
│  ├─ articledtd.xml (For PMC submission)      │
│  │  Format required by PubMed Central        │
│  │                                            │
│  └─ validation_report.json (Quality report)  │
│     Shows what passed and what needs review  │
│                                               │
└───────────────────────────────────────────────┘
```

## Common Use Cases

### Use Case 1: Submitting to PubMed Central (PMC)
**Goal**: Submit your biomedical research article to PMC

**Steps**:
1. Upload your Word manuscript to OmniJAX
2. Download the converted package
3. Review the `validation_report.json` to see if any issues were found
4. Upload `articledtd.xml` to the [PMC Style Checker](https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/)
5. If validation passes, submit to PMC
6. If there are warnings, review and fix them in your original Word document, then re-convert

### Use Case 2: Creating HTML for Web Viewing
**Goal**: Get a web-ready HTML version of your article

**Steps**:
1. Upload your Word document to OmniJAX
2. Download the converted package
3. Use `article.html` - this has professional styling with proper tables, figures, and formatting
4. This HTML follows publication standards and looks great in any web browser

### Use Case 3: Preparing for Journal Submission
**Goal**: Submit to a journal that requires JATS XML format

**Steps**:
1. Upload your manuscript to OmniJAX
2. Download the package
3. Submit `article.xml` to your journal's submission system
4. Include `article.html` as a preview version
5. The journal can validate your XML against their requirements

## Features Overview

### What OmniJAX Does Automatically

#### 1. **Document Structure Analysis**
The tool reads your Word document and identifies:
- Title and authors
- Abstract and keywords
- Main sections (Introduction, Methods, Results, etc.)
- Tables and figures
- References
- Acknowledgments

#### 2. **Format Conversion**
Converts your document into multiple professional formats:
- **JATS XML**: The standard format for scientific articles
- **HTML**: Web-friendly version with images

#### 3. **Quality Checking**
Automatically validates that your converted document:
- Meets JATS 1.4 standards (the current version of the scientific article format)
- Follows PMC requirements (if you're submitting to PubMed Central)
- Has proper structure (sections, metadata, citations)
- Contains all required elements

#### 4. **Smart Formatting**
The tool enhances your document with:
- Professional table styling (borders, colors, spacing)
- Proper figure sizing and alignment
- Correct reference formatting
- Standardized metadata (author info, publication details)

#### 5. **Transparency Highlighting**
Any content added by the tool for compliance is highlighted in yellow with a 📋 icon, so you can:
- See exactly what was added versus what was in your original document
- Review and update these sections with your specific information
- Understand why certain elements were added

### What Makes OmniJAX Special

#### Smart Content Repair
If your document is missing required elements (like an abstract or specific metadata), OmniJAX can:
- Detect what's missing
- Add placeholder content that meets requirements
- Highlight these additions so you can review them
- Ensure your document passes validation

#### Multiple Output Versions
Different users need different things:
- **Researchers**: Get validated JATS XML
- **Publishers**: Get validated JATS XML
- **Reviewers**: Get easy-to-read HTML versions
- **Archives**: Get properly structured XML for long-term preservation

#### Real-Time Progress Tracking
Watch the conversion happen:
- See exactly what step is running
- Know how long it will take
- Get immediate feedback if something goes wrong

## Understanding Your Output Files

### For Non-Technical Users - Which File Should I Use?

| File Name | What It's For | When to Use It |
|-----------|---------------|----------------|
| `article.html` | HTML version for viewing | Viewing in a web browser, sharing online |
| `article.xml` | Technical XML file | For journal submissions |
| `validation_report.json` | Quality check results | See if there are any issues to fix |
| `README.txt` | File descriptions | Learn what each file does |

### For Technical Users - File Specifications

| File Name | Format | Purpose | Standards |
|-----------|--------|---------|-----------|
| `article.xml` | JATS XML 1.4 | Schema validation, XSD tools | No DOCTYPE, includes xsi:schemaLocation |
| `articledtd.xml` | JATS XML 1.4 | PMC submission, DTD validation | Includes DOCTYPE declaration |
| `article.html` | HTML5 | Web display | W3C compliant |
| `media/` | Images | Extracted figures | Referenced from HTML/XML |
| `validation_report.json` | JSON | Validation results | JATS/PMC compliance report |

## Advanced Usage

### For Developers: Using the API

OmniJAX provides a RESTful API for integration with other systems:

#### Start a Conversion
```bash
curl -X POST -F "file=@document.docx" http://localhost:8080/convert
```

Response:
```json
{
  "conversion_id": "20260120_103000_abcd1234",
  "status": "queued",
  "message": "Conversion started"
}
```

#### Check Progress
```bash
curl http://localhost:8080/status/20260120_103000_abcd1234
```

Response:
```json
{
  "status": "processing",
  "progress": 40,
  "message": "Validating JATS XML",
  "filename": "document.docx"
}
```

#### Download Results
```bash
curl -O http://localhost:8080/download/20260120_103000_abcd1234
```

### For Programmers: Using the Python Library

```python
from MasterPipeline import HighFidelityConverter

# Initialize with your Word document
converter = HighFidelityConverter('path/to/document.docx')

# Run the complete conversion
converter.run()

# All outputs are saved in the output directory
print(f"Files generated in: {converter.output_dir}")
```

#### Step-by-Step Processing

```python
from MasterPipeline import HighFidelityConverter

converter = HighFidelityConverter('document.docx')

# Step 1: Convert to JATS XML
converter.convert_to_jats()  # Creates article.xml

# Step 2: Validate the XML
converter.validate_jats()     # Checks against JATS schema

# Step 3: Add PMC compliance
converter.add_doctype()       # Creates articledtd.xml

# Step 4: Generate HTML
converter.convert_to_html()   # Creates article.html + media/

# Step 5: Generate HTML
converter.convert_to_html()    # Creates article.html

# Step 6: Run all validations
converter.validate_all()      # Creates validation_report.json
```

## Troubleshooting Common Issues

### Issue 1: "Conversion Failed" Error
**Possible Causes:**
- Word document is corrupted
- File is too large (>50 MB)
- Document contains unsupported elements

**Solutions:**
1. Try opening and re-saving your Word document
2. Reduce file size by compressing images
3. Remove any embedded objects that might cause issues
4. Check the error message for specific details

### Issue 2: "Validation Warnings" in Report
**What It Means:**
Your document converted successfully, but some elements don't perfectly match publication standards.

**Solutions:**
1. Open `validation_report.json` to see specific warnings
2. Most warnings are minor and don't prevent submission
3. For critical issues, update your Word document and re-convert
4. Consult your target journal's submission guidelines

### Issue 3: Yellow Highlighted Content in HTML
**What It Means:**
The tool added these elements to meet formatting requirements.

**Solutions:**
1. Review each highlighted section
2. Replace placeholder text with your actual information
3. If an element isn't needed, note it in your submission
4. This is normal and helps ensure compliance

### Issue 4: Progress Bar Stuck
**Possible Causes:**
- Very large document taking time to process
- Server is busy
- Network connection issue

**Solutions:**
1. Wait a few more minutes (large documents can take 2-5 minutes)
2. Refresh the page and check if conversion completed
3. Try uploading again
4. Check your internet connection

### Issue 5: Downloaded ZIP File is Empty
**Possible Causes:**
- Conversion hasn't finished yet
- Download interrupted

**Solutions:**
1. Wait for progress to reach 100% before downloading
2. Try downloading again
3. Check your downloads folder for previous attempts
4. Disable download managers that might interfere

## Technical Requirements

### For Running OmniJAX Yourself

If you want to install and run OmniJAX on your own system:

**System Requirements:**
- Operating System: Linux, macOS, or Windows with WSL2
- RAM: At least 4GB (8GB recommended)
- Disk Space: 2GB free
- Internet connection for initial setup

**Software Requirements:**
- Python 3.11 or newer
- Pandoc 3.x (document converter)
- Python 3.11+
- Pandoc (document converter)

**Detailed Setup:**
See [SETUP.md](SETUP.md) for complete installation instructions.

## Understanding Validation Reports

When you convert a document, OmniJAX generates a `validation_report.json` file. Here's what it tells you:

### Report Structure (Simplified)

```json
{
  "jats_validation": {
    "status": "PASS",
    "message": "Your XML meets JATS 1.4 standards ✓"
  },
  "pmc_compliance": {
    "status": "PASS",
    "message": "Ready for PMC submission ✓",
    "warnings": [
      "Consider adding keywords for better searchability"
    ]
  },
  "document_structure": {
    "tables": 3,
    "figures": 5,
    "references": 25,
    "sections": 6
  }
}
```

### What Each Status Means

- **PASS**: Everything is good! Your document meets all requirements.
- **WARNING**: Document converted successfully, but there are suggestions for improvement. Usually safe to proceed.
- **FAIL**: There are critical issues that need to be fixed before submission.

### Common Warnings (And What to Do)

| Warning | What It Means | Action Needed |
|---------|---------------|---------------|
| "Missing keywords" | Your article should have keywords for searchability | Add keywords to your Word document |
| "Author affiliation incomplete" | Author institution info is partial | Add full institution details |
| "Figure caption needs alt text" | Figures need descriptions for accessibility | Add descriptive captions |
| "Reference formatting inconsistent" | Citations aren't uniform | Check reference list formatting |
| "DOI placeholder detected" | Article needs a real DOI | Get DOI from publisher or leave for now |

## Submitting to Publishers

### PMC (PubMed Central) Submission Workflow

1. **Convert your document** with OmniJAX
2. **Review validation report** - Open `validation_report.json` and check for any critical issues
3. **Test with PMC Style Checker**:
   - Go to: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
   - Upload `articledtd.xml` (not article.xml)
   - Review results
4. **Fix any errors** in your original Word document and re-convert
5. **Submit to PMC** using their online system
6. **Include**:
   - `articledtd.xml` (the XML file)
   - Media files from the `media/` folder if applicable

### General Journal Submission

Different journals have different requirements:

1. **Check journal guidelines** - See what format they want (XML or HTML)
2. **Use the appropriate file**:
   - JATS XML required? → Use `article.xml`
   - HTML preferred? → Use `article.html`
   - PMC/NLM compliance needed? → Use `articledtd.xml`
3. **Include supplementary materials**:
   - Upload images from `media/` folder if requested
   - Attach `validation_report.json` if journal wants proof of validation

## Frequently Asked Questions (FAQ)

### General Questions

**Q: Is OmniJAX free to use?**
A: OmniJAX is open-source software. Your institution or organization may provide access, or you can install it on your own server.

**Q: What types of documents work best?**
A: Research articles, review papers, case studies, and technical reports. The document should have a clear structure with sections like Introduction, Methods, Results, etc.

**Q: Can I convert multiple documents at once?**
A: Currently, you need to convert one document at a time. For batch processing, use the API or Python library.

**Q: How long does conversion take?**
A: Usually 30 seconds to 2 minutes, depending on document size and complexity. Large documents with many images may take up to 5 minutes.

**Q: Is my document data kept private?**
A: Check with your system administrator. In a self-hosted setup, all data stays on your server.

### Compatibility Questions

**Q: Does it work with older Word formats (.doc)?**
A: OmniJAX requires .docx format (Word 2007 and newer). To convert .doc files:
1. Open in Microsoft Word
2. Save As → Word Document (.docx)
3. Then use OmniJAX

**Q: Can I convert Google Docs?**
A: Yes, but you need to download first:
1. In Google Docs: File → Download → Microsoft Word (.docx)
2. Upload the downloaded .docx file to OmniJAX

**Q: What about LibreOffice or OpenOffice documents?**
A: Save your document as .docx format first, then use OmniJAX.

### Output Questions

**Q: What's the difference between article.xml and articledtd.xml?**
A: Both have the same content, but:
- `article.xml` - For general XML validation and modern tools
- `articledtd.xml` - Required for PMC Style Checker and PMC submission

**Q: Can I edit the XML files?**
A: Yes, but you'll need an XML editor. For most users, it's easier to edit the Word document and re-convert.

### Problem-Solving Questions

**Q: The HTML doesn't look right. What should I do?**
A: 
1. Check if the original Word document looks correct
2. If the Word doc looks wrong, fix formatting there first
3. Re-upload and convert again
4. If issues persist, check if your Word doc has unusual formatting

**Q: Validation failed. Can I still submit?**
A: Depends on the error:
- **Warnings**: Usually okay to proceed, but review them
- **Critical errors**: Need to fix before submission
- Check your target journal's requirements

**Q: Why is some text highlighted in yellow?**
A: This shows content that OmniJAX added to meet formatting standards. Review and update these sections with your actual information.

## Getting Help

### Documentation Resources
- **This README**: Overview and user guide
- **SETUP.md**: Installation instructions
- **TESTING_GUIDE.md**: For developers and testers

### External Resources
- **JATS Website**: https://jats.nlm.nih.gov/ - Learn about the JATS standard
- **PMC Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/ - PMC formatting requirements
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/ - Validate your XML

### Support
For technical support:
1. Check the troubleshooting section above
2. Review the validation report for specific errors
3. Contact your system administrator
4. For development issues, check the project repository

## Contributing and Development

Interested in improving OmniJAX or adapting it for your needs?

### For Developers
- **Repository**: View the source code and contribute
- **Testing**: See TESTING_GUIDE.md for how to run tests
- **Architecture**: The tool is built in Python with a modular pipeline

### Feature Requests
If you need additional features:
1. Check if there's an existing issue
2. Create a new feature request with use case
3. Consider contributing code if you have the skills

---

## Technical Details Section

*The following sections contain detailed technical information for advanced users, developers, and system administrators.*

### Official Standards Compliance

- **JATS 1.4 Publishing DTD**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

### Detailed Feature List

#### 1. JATS 1.4 Publishing DTD Compliance
- Validates against official NLM XSD schemas
- Full PMC/NLM Style Checker compatibility
- Proper namespace declarations (XLink, MathML)
- xsi:schemaLocation injection for external validators
- MathML 2.0/3.0 support

#### 2. PMC-Specific Validation
- Automated PMC requirements checking
- Integrated PMC Style Checker XSLT validation
- DOI and metadata validation
- Author affiliation structure verification
- Table positioning (float/anchor)
- Figure and caption compliance
- Reference formatting validation

#### 3. Enhanced Professional HTML Styling
- **Professional Table Styles**: Enhanced borders, colors, and spacing for better readability
  - Alternating row colors for improved visual clarity
  - Professional header styling with subtle blue accents
  - Optimized padding and spacing for clean presentation
  - Smaller table font size (10pt) for better content fit
- **Optimized Margins**: Reduced left/right margins (0.5in) for better space utilization
- **Enhanced Font Handling**: CSS variables for consistent font usage across document
  - Primary font stack: Liberation Serif, Times New Roman, DejaVu Serif
  - Header font stack: Liberation Sans, Arial, Helvetica
- **Enhanced Image Handling**: Proper sizing and alignment with automatic aspect ratio preservation
- **Compliance Text Highlighting**: Visual indicators for DTD/PMC compliance additions

#### 4. Asynchronous Conversion with Progress Tracking
- Real-time progress updates during conversion
- Non-blocking file uploads
- Status polling via REST API
- Separate download endpoint for completed conversions
- Modern drag-and-drop UI with progress bar

#### 5. AI-Powered Content Repair and Formatting
- Fixes truncated headers
- Ensures PMC metadata requirements
- Validates accessibility compliance
- Proper author formatting with affiliations
- Special character encoding
- Professional content formatting for consistency
- **Compliance Text Marking**: AI-added content for compliance is automatically marked

#### 7. Automatic Features
- Table captions with proper positioning
- Media extraction to `/media` folder
- Superscript/subscript preservation
- Section ID generation
- Comprehensive validation reporting

### Project Structure

```
.
├── MasterPipeline.py           # Main conversion pipeline with JATS 1.4 compliance
├── app.py                      # Flask web application with async endpoints
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
├── JATS-journalpublishing-*.xsd # JATS schema files
├── pmc-stylechecker/           # PMC Style Checker XSLT files
│   └── README.md              # Installation instructions
├── templates/
│   ├── index.html             # Modern async upload interface
│   └── style.css              # PMC-compliant HTML styling
├── standard-modules/          # JATS XSD modules
│   ├── mathml2/              # MathML 2.0 schema
│   ├── xlink.xsd             # XLink schema
│   └── xml.xsd               # XML namespace schema
└── tools/
    ├── safe_render.py         # Validation and rendering tool
    └── add_doctype.py         # DOCTYPE declaration utility for PMC validation
```

### JATS 1.4 and PMC Compliance Features

#### Required Elements for PMC Submission

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

#### PMC Validation Checks

The pipeline performs comprehensive PMC compliance checks:

- DTD version validation
- Required metadata presence
- Author affiliation structure
- Table positioning and caption placement
- Figure elements and captions
- Reference formatting
- Section ID attributes
- Special character encoding

#### Table Formatting

Tables are formatted according to PMC requirements with enhanced professional styling:

**PMC Compliance:**
- `position="float"` or `position="anchor"` (not "top")
- Caption as first child element
- Proper label for table numbers
- Minimal use of colspan/rowspan

**Enhanced Professional Styling:**
- Professional borders (#666) with subtle box shadows for depth
- Header row styling with light blue background (#e8f0f7) and accent border (#4a90d9)
- Alternating row colors (#f9f9f9) for improved readability
- Hover effects for interactive viewing
- Optimized padding (8px-10px) and tighter line-height (1.3) for clean presentation
- Smaller table font size (10pt) for better content fit
- Word-wrap handling for long content
- All styling preserves PMC/DTD compliance and does not alter content

#### Figure Formatting

Figures include enhanced sizing and alignment:
- Unique ID attributes
- Label elements for figure numbers
- Caption elements with descriptions
- Proper graphic references with XLink namespace
- **Enhanced Sizing**: Maximum width of 90% to prevent oversizing, maximum height of 500pt to prevent page overflow
- **Aspect Ratio Preservation**: `object-fit: contain` ensures proper proportions
- **Professional Alignment**: Centered with optimized margins for clean presentation

### Compliance Text Highlighting

#### Overview
To ensure transparency and facilitate review, any text or elements added by the AI system specifically for DTD/PMC compliance are automatically highlighted in the generated HTML output.

#### How It Works
1. **AI Marking**: When the AI repair system adds content for compliance (e.g., mandatory DOI elements, journal metadata), it marks them with `data-compliance="true"` attribute
2. **Visual Highlighting**: Marked content appears with:
   - Light yellow background (#fff9e6)
   - Orange left border (3px, #ff9900)
   - Compliance icon (📋) prefix

#### Examples of Highlighted Content
Compliance text may include:
- Journal metadata elements added for PMC requirements
- DOI placeholders when not present in source document
- Abstract sections added for compliance
- Required front matter elements
- Structural elements needed for DTD validation

#### Reviewing Highlighted Content
When reviewing the generated HTML:
- ✅ **Yellow highlighted sections** = Content added for DTD/PMC compliance
- ⚠️ **Original content** = Remains unhighlighted and unmodified
- 📋 Icon indicates compliance-related additions

This feature allows you to:
1. Easily identify what was added versus what was in the original document
2. Review compliance additions before final submission
3. Update highlighted sections with actual document-specific information
4. Maintain transparency in the conversion process

### Output Package Details

Each conversion generates a complete package with enhanced professional styling:

1. **article.xml** - JATS 1.4 Publishing DTD XML with xsi:schemaLocation (without DOCTYPE for XSD validation)
2. **articledtd.xml** - JATS 1.4 Publishing DTD XML with DOCTYPE declaration (for PMC Style Checker validation)
3. **article.html** - HTML version with enhanced styling:
   - **Optimized Margins**: 0.75in vertical, 0.65in horizontal for better space utilization
   - **Professional Tables**: Enhanced borders, colors, and spacing
   - **Enhanced Images**: Proper sizing with max-width 90%, max-height 500pt, aspect ratio preservation
   - **Compliance Highlighting**: Yellow background for compliance-added text
4. **media/** - All extracted images
5. **validation_report.json** - Detailed validation report with:
   - JATS schema validation results
   - PMC compliance check results
   - PMC Style Checker results (if available)
   - Critical issues and warnings
   - Document structure analysis
   - PMC submission checklist
8. **README.txt** - Package documentation

### Validation Report Format

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
  "pmc_stylechecker": {
    "available": true,
    "status": "PASS/FAIL",
    "xslt_used": "nlm-style-5-0.xsl",
    "error_count": 0,
    "warning_count": 0,
    "errors": [],
    "warnings": []
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

### Running Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_jats_generation.py -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Validation and Compliance Checking

```bash
# Validate JATS XML against XSD schema
python -c "
from MasterPipeline import HighFidelityConverter
converter = HighFidelityConverter('document.docx')
converter.convert_to_jats()
converter.validate_jats()
"

# Run PMC Style Checker
cd pmc-stylechecker
xsltproc --path . nlm-style-5-0.xsl ../path/to/articledtd.xml

# Validate HTML with W3C standards (requires external tool)
# Install: npm install -g html-validator-cli
html-validator path/to/article.html
```

### Pipeline Outputs Explained

The pipeline generates 5 main output types:

1. **JATS XML (XSD-Compliant)**: `article.xml`
   - Validates against JATS 1.4 XSD schema
   - No DOCTYPE declaration (optimized for schema validation)
   - Contains xsi:schemaLocation for external validators
   - Used for: Schema-based validation, XSD tools

2. **JATS XML (PMC-Compliant)**: `articledtd.xml`
   - Identical content to article.xml
   - Includes DOCTYPE declaration for PMC Style Checker
   - Compatible with DTD-based validators
   - Used for: PMC Style Checker, PMC submission

3. **HTML with Embedded Media**: `article.html` + `media/`
   - Semantic HTML5 output
   - Images embedded from media/ folder
   - CSS styling applied
   - W3C HTML5 compliant

3. **HTML for Display**: `article.html`
   - W3C HTML5 compliant
   - Professional styling
   - Embedded images
   - Responsive design

### Validation Workflow

```bash
# 1. Generate all outputs
python -c "
from MasterPipeline import HighFidelityConverter
converter = HighFidelityConverter('document.docx')
converter.run()
"

# 2. Review validation report
cat /tmp/output_files/validation_report.json

# 3. Check XSD validation
# Look for: jats_validation.status = "PASS"

# 4. Check PMC compliance
# Look for: pmc_compliance.status = "PASS" or "WARNING"

# 5. Run PMC Style Checker manually (if needed)
cd pmc-stylechecker
xsltproc --path . nlm-style-5-0.xsl /tmp/output_files/articledtd.xml

# 6. Review outputs
ls -lah /tmp/output_files/
```

### Async Conversion Progress UI

#### New Features (v1.4)

##### Asynchronous Conversion with Progress Tracking

The web interface now supports asynchronous conversions with real-time progress updates:

**Features:**
- **Drag-and-drop file upload** with visual feedback
- **Real-time progress bar** showing conversion status
- **Status polling** for long-running conversions
- **Download link** appears when conversion completes
- **Error handling** with detailed error messages

**API Endpoints:**
- `POST /convert` - Upload file, returns HTTP 202 with conversion_id
- `GET /status/<conversion_id>` - Poll conversion status
- `GET /download/<conversion_id>` - Download completed package

**Example Usage:**
```javascript
// Upload file
const formData = new FormData();
formData.append('file', file);
const response = await fetch('/convert', {
    method: 'POST',
    body: formData,
    headers: {'Accept': 'application/json'}
});
const { conversion_id } = await response.json();

// Poll status
const statusResponse = await fetch(`/status/${conversion_id}`);
const status = await statusResponse.json();
// status includes: status, progress, message, etc.

// Download result when complete
window.location.href = `/download/${conversion_id}`;
```

##### Schema Resolution for External Validators

Generated JATS XML now includes `xsi:schemaLocation` attribute pointing to the public JATS XSD:

```xml
<article xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jats.nlm.nih.gov/publishing/1.3/ https://jats.nlm.nih.gov/publishing/1.3/xsd/JATS-journalpublishing1-3.xsd"
         dtd-version="1.4"
         article-type="research-article">
```

This allows external PMC Style Checker and other validators to resolve the schema without "DTD not found" errors.

##### PMC Style-Check Integration

The pipeline now integrates the PMC Style Checker XSLT bundle (nlm-style-5.47):

**Setup:**
```bash
# Download PMC style checker
./tools/fetch_pmc_style.sh

# Ensure xsltproc is installed
sudo apt-get install xsltproc  # Ubuntu/Debian
brew install libxslt           # macOS
apk add libxslt                # Alpine/Docker
```

**Output Files:**
- `pmc_style_report.html` - Detailed style check report with errors and warnings
- `validation_report.json` - Includes PMC style check results:
  ```json
  {
    "pmc_style_check": {
      "status": "completed",
      "report_file": "pmc_style_report.html",
      "errors_count": 0,
      "warnings_count": 5,
      "summary": "0 errors, 5 warnings"
    }
  }
  ```

**Defensive Design:**
- If `xsltproc` is not installed, conversion continues with warning
- If PMC style checker is not downloaded, conversion continues with warning
- Pipeline never fails due to missing optional tools

### Deployment Notes

#### Single-Instance Deployment (Current)

The current implementation uses an in-memory progress store, suitable for:
- Development environments
- Single-server deployments
- Low to moderate traffic

**Limitations:**
- Progress state lost on server restart
- Not suitable for multi-instance deployments
- Not suitable for load-balanced environments

#### Multi-Instance Deployment (Recommended for Production)

For production deployments with multiple instances or load balancing:

**Option 1: Redis-based Progress Store**
```python
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Store progress
redis_client.setex(
    f"conversion:{conversion_id}",
    3600,  # 1 hour TTL
    json.dumps(progress_data)
)

# Retrieve progress
progress_json = redis_client.get(f"conversion:{conversion_id}")
progress_data = json.loads(progress_json) if progress_json else None
```

**Option 2: Job Queue System (Celery, RQ, etc.)**
```python
from celery import Celery

app = Celery('omnijax', broker='redis://localhost:6379/0')

@app.task(bind=True)
def convert_document(self, docx_path, conversion_id):
    # Update progress via self.update_state()
    self.update_state(state='PROGRESS', meta={'progress': 50})
    # ... conversion logic ...
```

**Option 3: Database-backed Progress Store**
```python
# Using SQLAlchemy or similar ORM
class ConversionJob(db.Model):
    id = db.Column(db.String, primary_key=True)
    status = db.Column(db.String)
    progress = db.Column(db.Integer)
    message = db.Column(db.String)
    created_at = db.Column(db.DateTime)
```

**Cloud Run Considerations:**
- Use Cloud Tasks or Pub/Sub for background jobs
- Store progress in Cloud Firestore or Cloud SQL
- Use Cloud Storage for output files
- Set appropriate timeouts for long-running conversions

### Testing Async Features

To test the new async UI and PMC style check:

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open browser to http://localhost:8080**

3. **Upload a DOCX file:**
   - Drag and drop or click to select
   - Watch progress bar update in real-time
   - Download package when complete

4. **Check output package:**
   - `pmc_style_report.html` - Style check results (if xsltproc available)
   - `validation_report.json` - Includes pmc_style_check section
   - `article.xml` - Now includes xsi:schemaLocation for external validators

5. **Validate with external PMC Style Checker:**
   - Upload `articledtd.xml` to https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
   - articledtd.xml includes DOCTYPE declaration required by PMC Style Checker
   - Should not see "DTD not found" errors
   - Should validate successfully

### Troubleshooting Technical Issues

**Progress bar not updating:**
- Check browser console for JavaScript errors
- Verify `/status/<conversion_id>` endpoint is accessible
- Check server logs for conversion errors

**PMC style check not running:**
- Verify xsltproc is installed: `which xsltproc`
- Verify XSLT file exists: `ls -l tools/pmc_style/nlm-stylechecker.xsl`
- Run `./tools/fetch_pmc_style.sh` if missing
- Check server logs for warnings

**External validator errors:**
- Verify `xsi:schemaLocation` is in article.xml
- Check that namespace declarations are present
- Validate XML is well-formed: `xmllint --noout article.xml`

### DOCTYPE Utility Script

The `tools/add_doctype.py` utility script can be used to add DOCTYPE declarations to existing JATS XML files:

```bash
# Add DOCTYPE to article.xml and save as articledtd.xml (JATS 1.4)
python tools/add_doctype.py article.xml

# Specify custom output path
python tools/add_doctype.py article.xml -o output/article_with_dtd.xml

# Specify JATS version 1.3
python tools/add_doctype.py article.xml -v 1.3

# Full example with all options
python tools/add_doctype.py input/article.xml --output output/articledtd.xml --version 1.4
```

**When to use:**
- When you need to validate an existing XML file with PMC Style Checker
- When you have article.xml without DOCTYPE and need to add it
- When you need a specific JATS version DOCTYPE (supports 1.0-1.4)

**Note:** The MasterPipeline automatically generates both article.xml (without DOCTYPE) and articledtd.xml (with DOCTYPE) during conversion, so you typically don't need to run this script manually.

### References

- **JATS Official Site**: https://jats.nlm.nih.gov/
- **JATS 1.4 Publishing DTD**: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
- **PMC Tagging Guidelines**: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
- **PMC Style Checker**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
- **NLM PMC**: https://pmc.ncbi.nlm.nih.gov/

## Roadmap

This project is actively maintained and improved. Recent updates include:

- **Documentation Enhancement**: Removed legacy PDF generation references to better reflect current capabilities
- **Validation Reports**: Added comprehensive validation report files to output packages for better transparency
- **UI Improvements**: Enhanced table formatting with zebra striping for improved readability
- **User Experience**: Streamlined documentation to focus on current features

Future enhancements may include additional output formats, enhanced validation capabilities, and improved AI-powered content repair features.

## License

Proprietary - OmniJAX Professional JATS Converter

---

**Document Version**: 2.0 - Improved for accessibility
**Last Updated**: January 2024
**Target Audience**: Non-technical and technical users
