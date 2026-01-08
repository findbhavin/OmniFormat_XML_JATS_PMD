import os
import subprocess
import logging
import shutil
from weasyprint import HTML, CSS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HighFidelity_JATS")

class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = os.path.abspath(docx_path)
        # Cloud Run uses /tmp for temporary file processing
        self.output_dir = os.path.join("/tmp", "jats_package")
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def convert_to_jats(self):
        """Uses Pandoc for high-fidelity JATS XML extraction."""
        xml_path = os.path.join(self.output_dir, "article.xml")
        logger.info(f"Running Pandoc conversion on: {self.docx_path}")
        # Pandoc captures full strings, preventing the 'NTRODUCTION' error
        subprocess.run(['pandoc', self.docx_path, '-t', 'jats', '-o', xml_path], check=True)
        return xml_path

    def generate_outputs(self, xml_path):
        """Uses WeasyPrint for professional CSS3 PDF rendering."""
        html_path = os.path.join(self.output_dir, "published_article.html")
        pdf_path = os.path.join(self.output_dir, "published_article.pdf")
        
        # Professional Stylesheet for Academic Journal Fidelity
        academic_css = """
            @page { size: A4; margin: 2cm; @bottom-center { content: "Page " counter(page); } }
            body { font-family: 'Liberation Serif', serif; text-align: justify; line-height: 1.6; }
            h1 { color: #003366; text-align: center; border-bottom: 2px solid #003366; }
            h2 { color: #004466; text-transform: uppercase; border-bottom: 1px solid #ccc; margin-top: 1.5em; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 9pt; }
            th, td { border: 1px solid #444; padding: 8px; vertical-align: top; }
            sup, sub { font-size: 0.75em; line-height: 0; position: relative; vertical-align: baseline; }
            sup { top: -0.5em; }
            sub { bottom: -0.25em; }
        """
        
        # Generate standalone HTML via Pandoc
        subprocess.run(['pandoc', xml_path, '-s', '--self-contained', '-o', html_path], check=True)
        
        # Render the PDF with WeasyPrint
        HTML(filename=html_path).write_pdf(pdf_path, stylesheets=[CSS(string=academic_css)])
        return html_path, pdf_path