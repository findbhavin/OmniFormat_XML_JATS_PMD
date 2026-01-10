import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")

class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")
        self.output_dir = "/tmp/output_files"
        self._prepare_environment()

        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")
        self.direct_pdf_path = os.path.join(self.output_dir, "direct_from_word.pdf")

        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"
        self.css_path = "templates/style.css"

    def _prepare_environment(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_content_with_ai(self, xml_content):
        """Fixes 'NTRODUCTION' and other truncation errors."""
        try:
            model = self._init_ai()
            prompt = (
                "You are an academic XML editor. Repair truncated headers "
                "(e.g., 'NTRODUCTION' to 'INTRODUCTION') in this JATS XML. "
                "Keep all scientific data and author names exactly as they are. "
                "Return only the raw XML text.\n\n"
                f"XML Source: {xml_content[:5000]}"
            )
            response = model.generate_content(prompt)
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped: {e}")
            return xml_content

    def validate_jats(self):
        try:
            schema = etree.XMLSchema(etree.parse(self.xsd_path))
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS Validation: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"JATS Validation FAILED: {e}")
            return False

    def run_pipeline(self):
        # Step 1: DOCX to JATS (Req 1: Captions top, Req 3: Media folder)
        logger.info("Step 1: JATS XML Generation")
        subprocess.run([
            "pandoc", self.docx_path, "-t", "jats", "-o", self.xml_path,
            "--extract-media", self.output_dir, "--standalone", "--mathml",
            "--table-captions=top"
        ], check=True)

        # Step 2: AI Structural Repair
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # Step 3: Schema Validation
        self.validate_jats()

        # Step 4 & 5: JATS PDF Rendering
        subprocess.run([
            "pandoc", "-f", "jats", self.xml_path, "--standalone",
            "--css", self.css_path, "-t", "html", "-o", self.html_path
        ], check=True)
        from weasyprint import HTML
        HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(target=self.pdf_path)

        # Step 6: Direct DOCX to PDF Conversion (Requirement 2)
        logger.info("Step 6: Direct PDF conversion")
        temp_direct_html = os.path.join(self.output_dir, "temp_direct.html")
        subprocess.run(["pandoc", self.docx_path, "-s", "--css", self.css_path, "-o", temp_direct_html], check=True)
        HTML(filename=temp_direct_html).write_pdf(target=self.direct_pdf_path)

        return self.output_dir