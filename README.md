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
   - Upload `article.xml` to https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/
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
