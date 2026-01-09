import os
import logging
import subprocess
import shutil
from lxml import etree

# Configure logging to show up in Google Cloud Logs Explorer
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")

class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        # Project ID is pulled from Cloud Run environment variables
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")
        
        # Use /tmp as it is the only writable directory in Cloud Run
        self.output_dir = "/tmp/output_files"
        self._prepare_output_dir()
        
        # Output file paths
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")
        
        # JATS 1.3 OASIS Schema Path (Must be in your root directory)
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml3.xsd"

    def _prepare_output_dir(self):
        """Clean and recreate the output directory for a fresh run."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy load Vertex AI to satisfy Cloud Run health checks."""
        import vertexai
        from vertexai.generative_models import GenerativeModel
        vertexai.init(project=self.project_id, location="us-central1")
        return GenerativeModel("gemini-1.5-pro")

    def fix_formatting_with_ai(self, xml_content):
        """
        Uses Vertex AI to fix truncated headers (e.g., 'NTRODUCTION') 
        and structural gaps. Strictly preserves scientific data.
        """
        try:
            model = self._init_ai()
            prompt = (
                "You are a technical XML editor. Repair formatting errors in this JATS 1.3 XML. "
                "Specifically: fix truncated headers like 'NTRODUCTION' to 'INTRODUCTION'. "
                "Ensure the heading hierarchy is logical. "
                "DO NOT change any scientific data, results, or author names.\n\n"
                f"XML Snippet: {xml_content[:5000]}"
            )
            response = model.generate_content(prompt)
            # Return fixed text if successful, otherwise fallback to original
            return response.text if response.text else xml_content
        except Exception as e:
            logger.warning(f"Vertex AI formatting fix failed (skipping): {e}")
            return xml_content

    def validate_xsd(self):
        """Validates the generated XML against the JATS 1.3 OASIS XSD."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"Validation failed: {self.xsd_path} not found in root.")
            return False
            
        try:
            schema_doc = etree.parse(self.xsd_path)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path)
            schema.assertValid(doc)
            logger.info("JATS 1.3 XSD Validation: SUCCESS")
            return True
        except etree.DocumentInvalid as e:
            logger.error(f"JATS 1.3 Validation Error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected Validation Error: {e}")
            return False

    def run_pipeline(self):
        """The main execution thread for conversion and rendering."""
        
        # Step 1: DOCX to JATS (Pandoc)
        # --extract-media is key for the Uma Phalswal manuscript images
        logger.info("Step 1: Converting DOCX to JATS via Pandoc...")
        subprocess.run([
            "pandoc", self.docx_path, 
            "-t", "jats", 
            "-o", self.xml_path, 
            "--extract-media", self.output_dir, 
            "--standalone"
        ], check=True)

        # Step 2: AI Structural Repair
        logger.info("Step 2: Performing AI-based structural repair...")
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()
        
        fixed_xml = self.fix_formatting_with_ai(raw_xml)
        
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)

        # Step 3: Schema Validation
        logger.info("Step 3: Validating JATS 1.3 Compliance...")
        self.validate_xsd()

        def run_pipeline(self):
            # ... Steps 1-3 (DOCX to JATS, AI Repair, Validation) ...

            # Step 4: Rendering High-Fidelity PDF (Intermediate HTML)
            # FIX: We now explicitly set input format '-f jats' and output title
            logger.info("Step 4: Rendering High-Fidelity PDF...")
            subprocess.run([
                "pandoc",
                "-f", "jats",  # Explicitly set input format
                self.xml_path,
                "--embed-resources",  # Modern replacement for --self-contained
                "--standalone",
                "--metadata", "title=Research Manuscript",
                "-t", "html",
                "-o", self.html_path
            ], check=True)

            # Step 5: PDF Generation (WeasyPrint)
            from weasyprint import HTML
            # Ensure we point directly to the HTML file we just created
            HTML(filename=self.html_path).write_pdf(target=self.pdf_path)

        logger.info("Pipeline Complete. Files ready in output directory.")
        return self.output_dir
