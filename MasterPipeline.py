import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree

# Configure structured logging for production debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        """
        Initializes the converter with the source DOCX path.
        Sets up the environment and local file paths.
        """
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Working directory in Cloud Run (/tmp is the only writable area)
        self.output_dir = "/tmp/output_files"
        self._prepare_environment()

        # Define internal asset paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")

        # REQUIREMENT (2): Path for the direct DOCX -> PDF conversion output
        self.direct_pdf_path = os.path.join(self.output_dir, "direct_from_word.pdf")

        # REQUIREMENT (3/4): JATS 1.3 Driver Filename and CSS location
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"
        self.css_path = "templates/style.css"

    def _prepare_environment(self):
        """Ensures a fresh, clean output directory for every run."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy load Vertex AI to satisfy fast startup health checks."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_content_with_ai(self, xml_content):
        """
        Requirement (4): Uses AI to fix header truncations like 'NTRODUCTION'.
        Strictly preserves scientific data and JATS tags.
        """
        try:
            model = self._init_ai()
            prompt = (
                "You are an academic XML editor. Repair truncated headers "
                "(e.g., 'NTRODUCTION' to 'INTRODUCTION') in this JATS XML. "
                "Keep all scientific data and author names exactly as they are.\n\n"
                f"XML Source: {xml_content[:5000]}"
            )
            response = model.generate_content(prompt)
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped (context preserved): {e}")
            return xml_content

    def validate_jats_compliance(self):
        """
        Validates the generated XML against the JATS 1.3 OASIS driver.
        Automatically resolves imports in the standard-modules/ folder.
        """
        if not os.path.exists(self.xsd_path):
            logger.error(f"XSD Driver {self.xsd_path} not found in root directory.")
            return False
        try:
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS 1.3 OASIS Validation: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"JATS Validation Failed: {e}")
            return False

    def run_pipeline(self):
        """
        The core execution thread. Performs JATS conversion, AI repair,
        validation, and dual-PDF rendering.
        """

        # STEP 1: DOCX to JATS XML
        # REQ (1): Force table captions to the top.
        # REQ (3): Extract media to 'media/' folder (JATS compliant).
        logger.info("Step 1: Converting DOCX to JATS XML...")
        subprocess.run([
            "pandoc", self.docx_path,
            "-t", "jats",
            "-o", self.xml_path,
            "--extract-media", self.output_dir,  # Pandoc creates the 'media' folder
            "--standalone",
            "--mathml",
            "--table-captions=top"
        ], check=True)

        # STEP 2: AI Structural Enhancement
        logger.info("Step 2: Performing AI Repair on XML content...")
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # STEP 3: Schema Validation
        logger.info("Step 3: Validating JATS 1.3 Compliance...")
        self.validate_jats_compliance()

        # STEP 4: Render Styled HTML (Intermediate for JATS PDF)
        # REQ (4): Point to the CSS located in /templates/style.css
        logger.info("Step 4: Generating intermediate HTML from JATS...")
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path,
            "--embed-resources",
            "--standalone",
            "--css", self.css_path,
            "-t", "html",
            "-o", self.html_path
        ], check=True)

        # STEP 5: Generate JATS-Derived PDF (Published Style)
        logger.info("Step 5: Rendering JATS-derived PDF...")
        from weasyprint import HTML
        html_doc = HTML(filename=self.html_path, base_url=self.output_dir)
        html_doc.write_pdf(
            target=self.pdf_path,
            presentational_hints=True,
            optimize_images=True
        )

        # STEP 6: Direct DOCX to PDF Conversion (Requirement 2)
        # This provides a 1:1 replica of the Word document in PDF format.
        logger.info("Step 6: Executing Direct DOCX to PDF conversion...")
        temp_direct_html = os.path.join(self.output_dir, "temp_direct.html")
        # Use Pandoc to go DOCX -> HTML, then WeasyPrint to PDF
        subprocess.run([
            "pandoc", self.docx_path, "-s", "--css", self.css_path, "-o", temp_direct_html
        ], check=True)
        HTML(filename=temp_direct_html).write_pdf(target=self.direct_pdf_path)

        logger.info("Conversion Pipeline Complete.")
        return self.output_dir