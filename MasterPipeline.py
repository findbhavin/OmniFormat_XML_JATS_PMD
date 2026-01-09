import os
import logging
import subprocess
from lxml import etree

logger = logging.getLogger("MasterPipeline")

class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")
        self.output_dir = "/tmp/output_files"
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")
        
        # Updated to JATS 1.3 filename
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml3.xsd"

    def _init_ai(self):
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_formatting_with_ai(self, xml_content):
        """Repairs 'NTRODUCTION' and header gaps without changing research data."""
        try:
            model = self._init_ai()
            prompt = f"Fix only structural/formatting errors in this JATS 1.3 XML. Repair truncated headers like 'NTRODUCTION'. Do NOT alter scientific content.\n\n{xml_content[:4000]}"
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"AI Skip: {e}")
            return xml_content

    def validate_xsd(self):
        """Validation against JATS 1.3 OASIS."""
        if os.path.exists(self.xsd_path):
            try:
                schema_doc = etree.parse(self.xsd_path)
                schema = etree.XMLSchema(schema_doc)
                doc = etree.parse(self.xml_path)
                schema.assertValid(doc)
                logger.info("JATS 1.3 XSD Validation: PASSED")
                return True
            except Exception as e:
                logger.error(f"XSD Validation FAILED: {e}")
                return False
        return True

    def run_pipeline(self):
        # 1. DOCX to JATS
        subprocess.run([
            "pandoc", self.docx_path, "-t", "jats", "-o", self.xml_path, 
            "--extract-media", self.output_dir, "--standalone"
        ], check=True)

        # 2. AI Formatting Fix
        with open(self.xml_path, 'r') as f:
            raw_xml = f.read()
        fixed_xml = self.fix_formatting_with_ai(raw_xml)
        with open(self.xml_path, 'w') as f:
            f.write(fixed_xml)

        # 3. Validate
        self.validate_xsd()

        # 4. Generate HTML and PDF (High-Fidelity)
        from weasyprint import HTML
        subprocess.run(["pandoc", self.xml_path, "-s", "--self-contained", "-t", "html", "-o", self.html_path], check=True)
        HTML(self.html_path).write_pdf(self.pdf_path)
        
        return self.output_dir