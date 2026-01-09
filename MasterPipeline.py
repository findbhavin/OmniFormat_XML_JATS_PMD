import os
import logging
import subprocess
import shutil
from lxml import etree

logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Cloud Run writable directory
        self.output_dir = "/tmp/output_files"
        self._prepare_dir()

        # Internal file paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")

        # Path to images folder (Pandoc will create this)
        self.media_dir = os.path.join(self.output_dir, "media")

        # Aligned to your specific JATS 1.3 Driver Filename
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"

    def _prepare_dir(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_with_ai(self, xml_content):
        """Repair formatting only (e.g., 'NTRODUCTION' fix)."""
        try:
            model = self._init_ai()
            prompt = f"Fix only structural/formatting errors in this JATS XML (e.g., 'NTRODUCTION' -> 'INTRODUCTION'). Do NOT change scientific data.\n\n{xml_content[:5000]}"
            response = model.generate_content(prompt)
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped: {e}")
            return xml_content

    def validate_jats(self):
        """Validates against the local JATS 1.3 OASIS XSD structure."""
        if not os.path.exists(self.xsd_path):
            logger.error("XSD Driver file missing from root!")
            return False
        try:
            # lxml follows imports into 'standard-modules/' automatically
            parser = etree.XMLParser(remove_blank_text=True)
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)

            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS Validation: PASSED")
            return True
        except Exception as e:
            logger.error(f"JATS Validation: FAILED: {e}")
            return False

    def run_pipeline(self):
        # 1. Convert DOCX to JATS XML + Extract Images
        logger.info("Phase 1: DOCX to JATS & Media Extraction")
        subprocess.run([
            "pandoc", self.docx_path,
            "-t", "jats",
            "-o", self.xml_path,
            "--extract-media", self.output_dir,  # Creates 'media/' folder in /tmp
            "--standalone"
        ], check=True)

        # 2. AI Structural Cleanup
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # 3. Schema Validation
        self.validate_jats()

        # 4. Generate Standalone HTML with Embedded Images
        logger.info("Phase 2: JATS to Standalone HTML")
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path,
            "--embed-resources",
            "--standalone",
            "--metadata", "title=Journal Article",
            "-t", "html",
            "-o", self.html_path
        ], check=True)

        # 5. Generate High-Fidelity PDF
        logger.info("Phase 3: HTML to PDF Rendering")
        from weasyprint import HTML
        # Explicitly passing paths to satisfy newer WeasyPrint API
        HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(target=self.pdf_path)

        return self.output_dir