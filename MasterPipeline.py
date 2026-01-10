import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree

# Configure detailed logging for Google Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Working directory (/tmp is the only writable area in Cloud Run)
        self.output_dir = "/tmp/output_files"
        self._prepare_environment()

        # Define Output Paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")

        # Requirement (2): Direct PDF Path
        self.direct_pdf_path = os.path.join(self.output_dir, "direct_from_word.pdf")

        # Configuration Paths
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"
        self.css_path = "templates/style.css"

    def _prepare_environment(self):
        """Cleans and recreates the output directory."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy loads Vertex AI."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_content_with_ai(self, xml_content):
        """
        AI Repair: Fixes truncated headers (e.g., 'NTRODUCTION').
        Restored full prompt for maximum accuracy.
        """
        try:
            model = self._init_ai()
            prompt = (
                "You are an academic XML editor. Repair truncated headers "
                "(e.g., 'NTRODUCTION' to 'INTRODUCTION') in this JATS XML. "
                "Do not change any scientific data, authors, or references. "
                "Return only the valid XML.\n\n"
                f"XML Source: {xml_content[:5000]}"
            )
            response = model.generate_content(prompt)
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped due to error: {e}")
            return xml_content

    def validate_jats_compliance(self):
        """Requirement (4): Validates against JATS 1.3 OASIS XSD."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"XSD Driver {self.xsd_path} not found in root.")
            return False
        try:
            # lxml automatically resolves imports in 'standard-modules/'
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS Validation: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"JATS Validation Failed: {e}")
            return False

    def run_pipeline(self):
        """Executes the full 6-step conversion pipeline."""

        # STEP 1: DOCX to JATS XML
        # Requirement (1): --table-captions=top
        # Requirement (3): --extract-media creates 'media/' folder
        logger.info("Step 1: Converting DOCX to JATS XML...")
        subprocess.run([
            "pandoc", self.docx_path,
            "-t", "jats",
            "-o", self.xml_path,
            "--extract-media", self.output_dir,
            "--standalone",
            "--mathml",
            "--table-captions=top"
        ], check=True)

        # STEP 2: AI Repair
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # STEP 3: Validation
        self.validate_jats_compliance()

        # STEP 4: Intermediate HTML (for JATS PDF)
        # Requirement (4): Uses templates/style.css
        logger.info("Step 4: Generating intermediate HTML...")
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path,
            "--embed-resources",
            "--standalone",
            "--css", self.css_path,
            "-t", "html",
            "-o", self.html_path
        ], check=True)

        # STEP 5: Render JATS-Derived PDF
        logger.info("Step 5: Rendering JATS PDF via WeasyPrint...")
        from weasyprint import HTML
        HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(target=self.pdf_path)

        # STEP 6: Direct DOCX to PDF Conversion (Requirement 2)
        # Uses a temporary HTML bridge to keep Word formatting
        logger.info("Step 6: Executing Direct DOCX to PDF conversion...")
        temp_direct_html = os.path.join(self.output_dir, "temp_direct.html")
        subprocess.run([
            "pandoc", self.docx_path, "-s", "--css", self.css_path, "-o", temp_direct_html
        ], check=True)
        HTML(filename=temp_direct_html).write_pdf(target=self.direct_pdf_path)

        return self.output_dir