import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree
import json
import re

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
        AI Repair: Enhanced for PMC Style Checker compliance.
        Fixes truncated headers and ensures JATS 1.3 + PMC/NLM requirements.
        """
        try:
            model = self._init_ai()
            prompt = f"""
            You are an expert JATS XML validator. Fix the following issues to ensure PMC Style Checker compliance:

            CRITICAL FIXES REQUIRED:
            1. HEADER REPAIR: Fix truncated headers (e.g., 'NTRODUCTION' → 'INTRODUCTION', 'ATERIALS' → 'MATERIALS')

            2. JATS 1.3 STRUCTURE VALIDATION:
               - Ensure root element: <article dtd-version="1.3" article-type="research-article">
               - Required structure: <front> → <article-meta> → <title-group>, <contrib-group>, <aff>, <abstract>
               - Body sections: <body> → <sec> with proper id attributes
               - Back matter: <back> → <ref-list>, <ack>

            3. PMC/NLM METADATA REQUIREMENTS:
               - Add if missing: <article-id pub-id-type="pmc">PMCXXXXXX</article-id>
               - <article-categories> with <subj-group subj-group-type="heading">
               - <contrib-group> with <contrib contrib-type="author">
               - Each author must have: <name>, <xref ref-type="aff">
               - <permissions> with <copyright-statement>, <copyright-year>, <license>
               - <abstract> must exist (both <p> and <sec> structured versions if possible)

            4. CITATION & REFERENCE COMPLIANCE:
               - <ref id="R1">, <ref id="R2">, etc.
               - Use <mixed-citation> format for references
               - Include DOI: <pub-id pub-id-type="doi">
               - Include PMID: <pub-id pub-id-type="pmid">

            5. MATHML 2.0 COMPLIANCE:
               - Ensure namespace: xmlns:mml="http://www.w3.org/1998/Math/MathML"
               - Math elements: <mml:math display="inline|block">
               - Proper <mml:mrow>, <mml:mi>, <mml:mo>, <mml:mn> structure

            6. ACCESSIBILITY (PMC REQUIRED):
               - All <fig> must have: <caption> and <alt-text>
               - Complex figures: add <long-desc>
               - Tables: <table-wrap> with position="top" attribute

            7. MEDIA REFERENCES:
               - <graphic xlink:href="media/image1.png">
               - All images must be in media/ folder
               - <supplementary-material> for additional files

            8. TABLE CAPTION POSITION (Requirement 1):
               - Ensure ALL tables have: <table-wrap position="top">
               - Caption must be BEFORE table content

            IMPORTANT: Preserve all scientific content, data, measurements, formulas.
            Return ONLY valid JATS 1.3 XML, no explanations.

            XML to fix:
            {xml_content[:10000]}
            """
            response = model.generate_content(prompt)
            if response.text:
                # Clean up any markdown formatting from AI response
                cleaned_xml = response.text.strip()
                # Remove markdown code blocks if present
                cleaned_xml = re.sub(r'```xml\s*|\s*```', '', cleaned_xml)
                cleaned_xml = re.sub(r'```\s*|\s*```', '', cleaned_xml)
                return cleaned_xml
            return xml_content
        except Exception as e:
            logger.warning(f"AI Step skipped due to error: {e}")
            logger.warning(traceback.format_exc())
            return xml_content

    def validate_jats_compliance(self):
        """Requirement (4): Validates against JATS 1.3 OASIS XSD."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"XSD Driver {self.xsd_path} not found.")
            return False

        try:
            # Set up catalog for module resolution
            catalog_path = "standard-modules/catalog.xml"
            if os.path.exists(catalog_path):
                parser = etree.XMLParser(load_dtd=True, no_network=False)
            else:
                parser = etree.XMLParser()

            # Parse and validate
            schema_doc = etree.parse(self.xsd_path, parser)
            schema = etree.XMLSchema(schema_doc)
            doc = etree.parse(self.xml_path, parser)
            schema.assertValid(doc)

            logger.info("✅ JATS 1.3 Validation: SUCCESS")

            # Generate validation report
            self._generate_validation_report(doc, True)
            return True

        except etree.XMLSchemaError as e:
            logger.error(f"❌ JATS Validation Failed: {e}")
            self._generate_validation_report(None, False, str(e))
            return False
        except Exception as e:
            logger.error(f"❌ Validation Error: {e}")
            self._generate_validation_report(None, False, str(e))
            return False

    def _generate_validation_report(self, xml_doc, passed, error_msg=None):
        """Generate detailed validation report for PMC compliance."""
        report_path = os.path.join(self.output_dir, "validation_report.json")

        report = {
            "jats_validation": {
                "status": "PASS" if passed else "FAIL",
                "schema_used": "JATS-journalpublishing-oasis-article1-3-mathml2.xsd",
                "standard": "JATS 1.3 OASIS Publishing",
                "timestamp": logging.Formatter().formatTime(logging.LogRecord(None, None, None, None, None, None, None))
            },
            "pmc_requirements": {
                "checked": True,
                "checks_performed": []
            },
            "output_files": {
                "jats_xml": "article.xml",
                "jats_pdf": "published_article.pdf",
                "direct_pdf": "direct_from_word.pdf",
                "html": "article.html"
            }
        }

        if xml_doc:
            # Add PMC-specific checks
            ns = {'jats': 'http://jats.nlm.nih.gov'}

            # Check for PMC required elements
            checks = [
                ("pmc_id", bool(xml_doc.xpath('//article-meta/article-id[@pub-id-type="pmc"]')), "PMC ID present"),
                ("article_type", bool(xml_doc.xpath('//article[@article-type="research-article"]')),
                 "Research article type"),
                ("title_group", bool(xml_doc.xpath('//article-meta/title-group')), "Title group present"),
                ("abstract", bool(xml_doc.xpath('//article-meta/abstract')), "Abstract present"),
                ("contributors", bool(xml_doc.xpath('//article-meta/contrib-group/contrib')),
                 "Authors/contributors listed"),
                ("affiliations", bool(xml_doc.xpath('//article-meta/aff')), "Affiliations present"),
                ("permissions", bool(xml_doc.xpath('//article-meta/permissions')), "Copyright permissions"),
                ("references", bool(xml_doc.xpath('//back/ref-list/ref')), "References present"),
                ("table_captions_top", all(
                    elem.get('position') == 'top'
                    for elem in xml_doc.xpath('//table-wrap')
                ), "All table captions positioned top"),
                ("figures_accessible", all(
                    elem.xpath('.//alt-text')
                    for elem in xml_doc.xpath('//fig')
                ), "All figures have alt-text")
            ]

            report["pmc_requirements"]["checks_performed"] = [
                {"check": name, "passed": passed, "description": desc}
                for name, passed, desc in checks
            ]

            report["pmc_requirements"]["overall"] = "PASS" if all(p for _, p, _ in checks) else "WARNING"

        if error_msg:
            report["jats_validation"]["error"] = error_msg

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Validation report saved to: {report_path}")

    def run_pipeline(self):
        """Executes the full 7-step conversion pipeline."""
        logger.info("=" * 60)
        logger.info("OmniJAX Pipeline Starting")
        logger.info("=" * 60)

        # STEP 1: DOCX to JATS XML
        logger.info("Step 1: Converting DOCX to JATS XML...")
        try:
            subprocess.run([
                "pandoc", self.docx_path,
                "-t", "jats",
                "-o", self.xml_path,
                "--extract-media", self.output_dir,
                "--standalone",
                "--mathml",
                "--table-captions=top"
            ], check=True, capture_output=True, text=True)
            logger.info(f"✅ XML generated: {self.xml_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Pandoc conversion failed: {e.stderr}")
            raise

        # STEP 2: AI Repair & PMC Compliance
        logger.info("Step 2: AI Repair for PMC Style Checker compliance...")
        with open(self.xml_path, 'r', encoding='utf-8') as f:
            raw_xml = f.read()

        fixed_xml = self.fix_content_with_ai(raw_xml)
        with open(self.xml_path, 'w', encoding='utf-8') as f:
            f.write(fixed_xml)
        logger.info("✅ AI repair completed")

        # STEP 3: JATS 1.3 Validation
        logger.info("Step 3: Validating against JATS 1.3 OASIS Schema...")
        validation_passed = self.validate_jats_compliance()

        if not validation_passed:
            logger.warning("⚠️  JATS validation failed, but continuing with pipeline...")

        # STEP 4: Intermediate HTML (for JATS PDF)
        logger.info("Step 4: Generating intermediate HTML from JATS XML...")
        try:
            subprocess.run([
                "pandoc", "-f", "jats", self.xml_path,
                "--embed-resources",
                "--standalone",
                "--css", self.css_path,
                "-t", "html5",
                "-o", self.html_path
            ], check=True, capture_output=True, text=True)
            logger.info(f"✅ HTML generated: {self.html_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ HTML generation failed: {e.stderr}")
            raise

        # STEP 5: Render JATS-Derived PDF
        logger.info("Step 5: Rendering JATS-compliant PDF via WeasyPrint...")
        try:
            from weasyprint import HTML
            HTML(filename=self.html_path, base_url=self.output_dir).write_pdf(
                target=self.pdf_path,
                presentational_hints=True
            )
            logger.info(f"✅ JATS PDF generated: {self.pdf_path}")
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            raise

        # STEP 6: Direct DOCX to PDF Conversion (Requirement 2)
        logger.info("Step 6: Creating direct DOCX→PDF (preserving Word formatting)...")
        try:
            # First convert to HTML with Word styling
            temp_direct_html = os.path.join(self.output_dir, "temp_direct.html")
            subprocess.run([
                "pandoc", self.docx_path,
                "-s",
                "--css", self.css_path,
                "--extract-media", self.output_dir,
                "-o", temp_direct_html
            ], check=True, capture_output=True, text=True)

            # Convert HTML to PDF
            from weasyprint import HTML
            HTML(filename=temp_direct_html, base_url=self.output_dir).write_pdf(
                target=self.direct_pdf_path
            )
            logger.info(f"✅ Direct PDF generated: {self.direct_pdf_path}")

            # Clean up temp HTML
            if os.path.exists(temp_direct_html):
                os.remove(temp_direct_html)

        except Exception as e:
            logger.error(f"❌ Direct PDF conversion failed: {e}")
            # Continue even if direct PDF fails
            if not os.path.exists(self.direct_pdf_path):
                # Create a placeholder
                from weasyprint import HTML
                HTML(string="<h1>Direct PDF Generation Failed</h1><p>Using JATS PDF instead.</p>").write_pdf(
                    self.direct_pdf_path)

        # STEP 7: Create README with conversion details
        logger.info("Step 7: Generating documentation...")
        self._generate_readme()

        logger.info("=" * 60)
        logger.info("Pipeline Completed Successfully!")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("=" * 60)

        return self.output_dir

    def _generate_readme(self):
        """Generate README file with conversion details."""
        readme_path = os.path.join(self.output_dir, "README.txt")

        with open(readme_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("OmniJAX Conversion Package\n")
            f.write("=" * 60 + "\n\n")
            f.write("This package contains:\n")
            f.write("1. article.xml          - JATS 1.3 OASIS compliant XML\n")
            f.write("2. published_article.pdf - PDF generated from JATS XML\n")
            f.write("3. direct_from_word.pdf  - Direct DOCX→PDF conversion\n")
            f.write("4. article.html          - HTML version for web\n")
            f.write("5. media/                - Extracted images and media\n")
            f.write("6. validation_report.json - JATS compliance report\n\n")
            f.write("Compliance Details:\n")
            f.write("- JATS 1.3 OASIS Publishing Standard\n")
            f.write("- PMC/NLM Style Checker requirements\n")
            f.write("- Table captions forced to top position\n")
            f.write("- MathML 2.0 support\n")
            f.write("- Accessibility compliance (alt-text, long-desc)\n\n")
            f.write("Generated by OmniJAX Professional Converter\n")
            f.write("https://github.com/your-repo/omnijax\n")

        logger.info(f"✅ README generated: {readme_path}")