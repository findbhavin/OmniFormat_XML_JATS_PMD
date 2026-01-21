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
   - xsi:schemaLocation injection for external validators
   - MathML 2.0/3.0 support

2. **PMC-Specific Validation**
   - Automated PMC requirements checking
   - Integrated PMC Style Checker XSLT validation
   - DOI and metadata validation
   - Author affiliation structure verification
   - Table positioning (float/anchor)
   - Figure and caption compliance
   - Reference formatting validation

3. **Enhanced Professional PDF Styling**
   - **Professional Table Styles**: Enhanced borders, colors, and spacing for better readability
     - Alternating row colors for improved visual clarity
     - Professional header styling with subtle blue accents
     - Optimized padding and spacing for clean presentation
     - Smaller table font size (10pt) for better content fit
   - **Optimized Margins**: Further reduced left/right margins (0.5in) for better space utilization
   - **Enhanced Font Handling**: CSS variables for consistent font usage across document
     - Primary font stack: Liberation Serif, Times New Roman, DejaVu Serif
     - Header font stack: Liberation Sans, Arial, Helvetica
   - **Enhanced Image Handling**: Proper sizing and alignment with automatic aspect ratio preservation
   - **Compliance Text Highlighting**: Visual indicators for DTD/PMC compliance additions

4. **Asynchronous Conversion with Progress Tracking**
   - Real-time progress updates during conversion
   - Non-blocking file uploads
   - Status polling via REST API
   - Separate download endpoint for completed conversions
   - Modern drag-and-drop UI with progress bar

5. **Dual PDF Generation**
   - PDF from JATS XML (semantic, PMC-ready)
   - Direct DOCX→PDF (format preserving)

6. **AI-Powered Content Repair and Formatting**
   - Fixes truncated headers
   - Ensures PMC metadata requirements
   - Validates accessibility compliance
   - Proper author formatting with affiliations
   - Special character encoding
   - Professional content formatting for consistency
   - **Compliance Text Marking**: AI-added content for compliance is automatically marked

7. **Automatic Features**
   - Table captions with proper positioning
   - Media extraction to `/media` folder
   - Superscript/subscript preservation
   - Section ID generation
   - Comprehensive validation reporting

## Project Structure

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
│   └── style.css              # PMC-compliant PDF styling
├── standard-modules/          # JATS XSD modules
│   ├── mathml2/              # MathML 2.0 schema
│   ├── xlink.xsd             # XLink schema
│   └── xml.xsd               # XML namespace schema
└── tools/
    ├── safe_render.py         # Validation and rendering tool
    ├── add_doctype.py         # DOCTYPE declaration utility for PMC validation
    └── direct_pdf_converter.py # Direct PDF conversion utility
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

### Figure Formatting

Figures include enhanced sizing and alignment:
- Unique ID attributes
- Label elements for figure numbers
- Caption elements with descriptions
- Proper graphic references with XLink namespace
- **Enhanced Sizing**: Maximum width of 90% to prevent oversizing, maximum height of 500pt to prevent page overflow
- **Aspect Ratio Preservation**: `object-fit: contain` ensures proper proportions
- **Professional Alignment**: Centered with optimized margins for clean presentation

## Compliance Text Highlighting

### Overview
To ensure transparency and facilitate review, any text or elements added by the AI system specifically for DTD/PMC compliance are automatically highlighted in the generated PDF output.

### How It Works
1. **AI Marking**: When the AI repair system adds content for compliance (e.g., mandatory DOI elements, journal metadata), it marks them with `data-compliance="true"` attribute
2. **Visual Highlighting**: Marked content appears with:
   - Light yellow background (#fff9e6 / #ffeecc in print)
   - Orange left border (3px, #ff9900)
   - Compliance icon (📋) prefix
   - Special print color adjustment to ensure visibility in printed PDFs

### Examples of Highlighted Content
Compliance text may include:
- Journal metadata elements added for PMC requirements
- DOI placeholders when not present in source document
- Abstract sections added for compliance
- Required front matter elements
- Structural elements needed for DTD validation

### Reviewing Highlighted Content
When reviewing the generated PDF:
- ✅ **Yellow highlighted sections** = Content added for DTD/PMC compliance
- ⚠️ **Original content** = Remains unhighlighted and unmodified
- 📋 Icon indicates compliance-related additions

This feature allows you to:
1. Easily identify what was added versus what was in the original document
2. Review compliance additions before final submission
3. Update highlighted sections with actual document-specific information
4. Maintain transparency in the conversion process

## Output Package

Each conversion generates a complete package with enhanced professional styling:

1. **article.xml** - JATS 1.4 Publishing DTD XML with xsi:schemaLocation (without DOCTYPE for XSD validation)
2. **articledtd.xml** - JATS 1.4 Publishing DTD XML with DOCTYPE declaration (for PMC Style Checker validation)
3. **published_article.pdf** - PDF from JATS XML with enhanced styling:
   - **Optimized Margins**: 0.75in vertical, 0.65in horizontal (reduced from 1in for better space utilization)
   - **Professional Tables**: Enhanced borders, colors, and spacing
   - **Enhanced Images**: Proper sizing with max-width 90%, max-height 500pt, aspect ratio preservation
   - **Compliance Highlighting**: Yellow background for compliance-added text
   - **Print-Optimized**: Special color adjustments for print output
4. **direct_from_word.pdf** - Direct DOCX conversion
5. **article.html** - HTML version
6. **media/** - All extracted images
7. **validation_report.json** - Detailed validation report with:
   - JATS schema validation results
   - PMC compliance check results
   - PMC Style Checker results (if available)
   - Critical issues and warnings
   - Document structure analysis
   - PMC submission checklist
8. **README.txt** - Package documentation

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

## Usage

### Web Interface

1. **Upload File**
   - Navigate to the web interface
   - Click or drag-and-drop a DOCX file (max 50 MB)
   - Click "Convert & Download Package"

2. **Monitor Progress**
   - Real-time progress bar shows conversion status
   - Progress updates from 0% to 100%
   - Status messages indicate current step

3. **Download Results**
   - Once conversion completes (100%), click "Download Package"
   - Receive complete ZIP package with all outputs

### API Endpoints

#### POST /convert
Start asynchronous conversion
```bash
curl -X POST -F "file=@document.docx" http://localhost:8080/convert
```
Returns:
```json
{
  "conversion_id": "20260120_103000_abcd1234",
  "status": "queued",
  "message": "Conversion started"
}
```

#### GET /status/<conversion_id>
Check conversion status
```bash
curl http://localhost:8080/status/20260120_103000_abcd1234
```
Returns:
```json
{
  "status": "processing",
  "progress": 40,
  "message": "Validating JATS XML",
  "filename": "document.docx"
}
```

#### GET /download/<conversion_id>
Download completed conversion
```bash
curl -O http://localhost:8080/download/20260120_103000_abcd1234
```

#### GET /health
Health check endpoint
```bash
curl http://localhost:8080/health
```

## Running the Enhanced Output Pipeline

### Quick Start

For detailed environment setup instructions, see [SETUP.md](SETUP.md).

#### 1. Command-Line Pipeline Execution

Run the complete pipeline programmatically:

```python
from MasterPipeline import HighFidelityConverter

# Initialize converter with DOCX file
converter = HighFidelityConverter('path/to/document.docx')

# Run the complete pipeline
# This generates all outputs:
# - article.xml (XSD-compliant JATS XML)
# - articledtd.xml (PMC-compliant JATS XML with DOCTYPE)
# - published_article.pdf (PDF from JATS XML)
# - direct_from_word.pdf (Direct DOCX to PDF)
# - article.html (HTML with embedded media)
# - media/ (extracted images)
# - validation_report.json (validation results)
converter.run()

print(f"All outputs generated in: {converter.output_dir}")
```

#### 2. Step-by-Step Pipeline Execution

Run individual pipeline steps:

```python
from MasterPipeline import HighFidelityConverter

converter = HighFidelityConverter('document.docx')

# Step 1: Generate XSD-compliant JATS XML
converter.convert_to_jats()  # Creates article.xml
converter.validate_jats()     # Validates against XSD schema

# Step 2: Generate PMC-compliant JATS XML
converter.add_doctype()      # Creates articledtd.xml with DOCTYPE

# Step 3: Generate HTML with embedded media
converter.convert_to_html()  # Creates article.html + media/

# Step 4: Generate PDF from JATS XML
converter.convert_to_pdf()   # Creates published_article.pdf

# Step 5: Generate direct DOCX to PDF
converter.direct_pdf()       # Creates direct_from_word.pdf

# Step 6: Run validations
converter.validate_all()     # Creates validation_report.json
```

#### 3. Running Tests

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

#### 4. Validation and Compliance Checking

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

4. **Direct DOCX to PDF**: `direct_from_word.pdf`
   - Preserves original DOCX fonts
   - Maintains superscripts/subscripts
   - Table formatting preserved
   - Created via LibreOffice/Pandoc

5. **PDF from HTML/JATS**: `published_article.pdf`
   - Generated from JATS XML via WeasyPrint
   - PMC-compliant styling
   - Professional table formatting
   - Enhanced margins and spacing

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

## PMC Submission Workflow

1. Convert document using OmniJAX
2. Review `validation_report.json`
3. Fix any critical issues identified
4. **Use articledtd.xml for PMC Style Checker validation**: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
   - articledtd.xml includes the DOCTYPE declaration required by PMC Style Checker
   - Upload this file to avoid "Validation failed: no DTD found" errors
5. **Use article.xml for XSD validation** and other schema-based validators
   - article.xml is optimized for XSD validation (without DOCTYPE declaration)
6. Review warnings and recommendations
7. Submit to PMC

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

## Async Conversion Progress UI

### New Features (v1.4)

#### Asynchronous Conversion with Progress Tracking

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

#### Schema Resolution for External Validators

Generated JATS XML now includes `xsi:schemaLocation` attribute pointing to the public JATS XSD:

```xml
<article xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="https://jats.nlm.nih.gov/publishing/1.3/ https://jats.nlm.nih.gov/publishing/1.3/xsd/JATS-journalpublishing1-3.xsd"
         dtd-version="1.4"
         article-type="research-article">
```

This allows external PMC Style Checker and other validators to resolve the schema without "DTD not found" errors.

#### PMC Style-Check Integration

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

### Testing

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

### Troubleshooting

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

## DOCTYPE Utility Script

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
