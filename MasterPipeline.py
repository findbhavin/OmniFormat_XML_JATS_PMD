import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree

# Configure structured logging for Google Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        """
        Initializes the converter.
        Requirement (3): media folder name and structure set for JATS compliance.
        """
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Working directory (/tmp is the only writable area on Cloud Run)
        self.output_dir = "/tmp/output_files"
        self._prepare_environment()

        # Output paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")

        # Requirement (2): Path for direct DOCX to PDF conversion
        self.direct_pdf_path = os.path.join(self.output_dir, "direct_from_word.pdf")

        # Requirement (4): Paths for XSD and CSS (moved to templates folder)
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"
        self.css_path = "templates/style.css"

    def _prepare_environment(self):
        """Ensures a fresh workspace for every conversion."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy load Vertex AI for header repair."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_content_with_ai(self, xml_content):
        """AI Repair for truncated headers (e.g., 'NTRODUCTION' fix)."""
        try:
            model = self._init_ai()
            prompt = (
                "You are an academic XML editor. Repair truncated headers "
                "(e.g., 'NTRODUCTION' to 'INTRODUCTION') in this JATS XML. "
                "Strictly keep all scientific data and JATS tags unchanged.\n\n"
                f"XML Source: {xml_content[:5000]}"
            )
            response = model.generate_content(prompt)
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped: {e}")
            return xml_content

    def validate_jats_compliance(self):
        """Requirement (4): Validates against JATS 1.3 OASIS Driver."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"XSD Driver {self.xsd_path} not found.")
            return False
        try:
            # lxml automatically follows relative paths to standard-modules/
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS 1.3 OASIS Validation: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Validation Failed: {e}")
            return False

    def run_pipeline(self):
        """Full Execution: DOCX -> JATS -> HTML -> PDF + Direct PDF."""

        # Step 1: DOCX to JATS XML
        # Requirement (1): --table-captions=top (Requires Pandoc 3.0+)
        # Requirement (3): --extract-media creates 'media/' folder
        logger.info("Step 1: JATS XML Generation and Image Extraction...")
        subprocess.run([
            "pandoc", self.docx_path,
            "-t", "jats",
            "-o", self.xml_path,
            "--extract-media", self.output_dir,  # Extract images to 'media/'
            "--standalone",
            "--mathml",
            "--table-captions=top"
        ], check=True)

        # Step 2: AI Repair (NTRODUCTION fix)
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # Step 3: XSD Validation
        self.validate_jats_compliance()

        # Step 4: Render JATS to HTML (Intermediate for PDF)
        # Requirement (4): Uses templates/style.css
        logger.info("Step 4: JATS to Intermediate HTML...")
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path,
            "--embed-resources",
            "--standalone",
            "--css", self.css_path,
            "-t", "html",
            "-o", self.html_path
        ], check=True)

        # Step 5: Generate JATS-derived PDF (Published Look)
        logger.info("Step 5: Rendering JATS PDF...")
        from weasyprint import HTML
        HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(target=self.pdf_path)

        # Step 6: Requirement (2) Direct DOCX to PDF Conversion
        # Provides a 1:1 replica of the Word document structure
        logger.info("Step 6: Executing Direct DOCX to PDF conversion...")
        temp_direct_html = os.path.join(self.output_dir, "temp_direct.html")
        subprocess.run([
            "pandoc", self.docx_path, "-s", "--css", self.css_path, "-o", temp_direct_html
        ], check=True)
        HTML(filename=temp_direct_html).write_pdf(target=self.direct_pdf_path)

        return self.output_dir