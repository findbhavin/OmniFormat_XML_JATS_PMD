import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree

# Configure structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Cloud Run uses /tmp as the only writable partition
        self.output_dir = "/tmp/output_files"
        self._prepare_environment()

        # Define asset paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")

        # ALIGNMENT: Explicitly uses your JATS 1.3 Driver Filename
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"

    def _prepare_environment(self):
        """Ensures a clean workspace for every conversion."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy load Vertex AI to prevent health-check timeouts."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_content_with_ai(self, xml_content):
        """Uses Gemini to fix 'NTRODUCTION' and header truncations."""
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
            logger.warning(f"AI Repair skipped due to: {e}")
            return xml_content

    def validate_jats_compliance(self):
        """Validates against JATS 1.3 OASIS using the local schema tree."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"CRITICAL: Driver file {self.xsd_path} not found in root.")
            return False
        try:
            # lxml automatically follows relative paths in 'standard-modules/'
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS 1.3 OASIS Validation: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"JATS 1.3 OASIS Validation: FAILED: {e}")
            return False

    def run_pipeline(self):
        """Full execution: DOCX -> JATS -> HTML -> PDF."""

        # 1. Extraction: DOCX to JATS XML + Media Folder
        logger.info("Executing Pandoc: DOCX to JATS conversion...")
        subprocess.run([
            "pandoc", self.docx_path,
            "-t", "jats",
            "-o", self.xml_path,
            "--extract-media", self.output_dir,  # Extracts images to output_dir/media
            "--standalone"
        ], check=True)

        # 2. AI Enhancement
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # 3. Schema Check
        self.validate_jats_compliance()

        # 4. Rendering: JATS to Standalone HTML (with embedded base64 images)
        logger.info("Executing Pandoc: JATS to Standalone HTML...")
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path,
            "--embed-resources",
            "--standalone",
            "--metadata", "title=Scientific Article",
            "-t", "html",
            "-o", self.html_path
        ], check=True)

        # 5. High-Fidelity PDF Generation (via WeasyPrint)
        logger.info("Rendering PDF from JATS source...")
        from weasyprint import HTML
        # Passing base_url allows WeasyPrint to find extracted images
        HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(target=self.pdf_path)

        return self.output_dir