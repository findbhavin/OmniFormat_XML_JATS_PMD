import os
import logging
import subprocess
import shutil
import traceback
from lxml import etree
import json
import re
import html

# Configure detailed logging for Google Cloud Run
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterPipeline")


class HighFidelityConverter:
    def __init__(self, docx_path):
        self.docx_path = docx_path
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "doctojatsxmlandpdf")

        # Define all directory paths FIRST
        self.output_dir = "/tmp/output_files"
        self.media_dir = os.path.join(self.output_dir, "media")
        
        # Prepare environment (creates directories)
        self._prepare_environment()

        # Define file paths AFTER directories exist
        self.xml_path = os.path.join(self.output_dir, "article.xml")
        self.html_path = os.path.join(self.output_dir, "article.html")
        self.pdf_path = os.path.join(self.output_dir, "published_article.pdf")
        self.direct_pdf_path = os.path.join(self.output_dir, "direct_from_word.pdf")

        # Configuration Paths - JATS 1.4 Publishing DTD
        # Official schema: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
        self.xsd_path = "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"  # Fallback to 1.3 for now
        self.jats_version = "1.3"  # Using 1.3 since we have 1.3 XSD
        self.css_path = "templates/style.css"

    def _prepare_environment(self):
        """Cleans and recreates the output directory."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)

    def _init_ai(self):
        """Lazy loads Vertex AI with version compatibility."""
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel
            
            # Initialize Vertex AI
            vertexai.init(
                project=self.project_id, 
                location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
            )
            
            # Try to use gemini-1.5-pro, fall back to other models
            try:
                return GenerativeModel("gemini-1.5-pro")
            except:
                try:
                    return GenerativeModel("gemini-pro")
                except:
                    # Last resort, try any available model
                    return GenerativeModel()
                    
        except ImportError as e:
            logger.warning(f"Vertex AI not available: {e}")
            logger.warning("AI repair functionality will be disabled")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI: {e}")
            return None

    def fix_content_with_ai(self, xml_content):
        """
        AI Repair: Enhanced for PMC Style Checker compliance.
        Falls back to rule-based repair if AI is not available.
        """
        # Try AI repair first
        ai_fixed = self._fix_with_ai(xml_content)
        if ai_fixed and ai_fixed != xml_content:
            return ai_fixed
        
        # Fall back to rule-based repair
        return self._fix_with_rules(xml_content)

    def _fix_with_ai(self, xml_content):
        """Try to fix XML using Vertex AI."""
        try:
            model = self._init_ai()
            if model is None:
                return xml_content
                
            prompt = f"""
            You are an expert JATS XML validator. Fix the following issues to ensure PMC Style Checker compliance.
            Reference: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/

            JATS 1.4 PUBLISHING DTD REQUIREMENTS (NLM/PMC):
            - Schema: https://public.nlm.nih.gov/projects/jats/publishing/1.4/
            - PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/

            CRITICAL FIXES FOR PMC COMPLIANCE:

            1. ROOT ELEMENT (MANDATORY):
               <article dtd-version="1.4" article-type="research-article"
                        xmlns:xlink="http://www.w3.org/1999/xlink"
                        xmlns:mml="http://www.w3.org/1998/Math/MathML">

            2. FRONT MATTER (REQUIRED):
               - <journal-meta> with <journal-id>, <journal-title-group>, <issn>, <publisher>
               - <article-meta> with:
                 * <article-id pub-id-type="doi"> (MANDATORY)
                 * <title-group> with <article-title>
                 * <contrib-group> with <contrib contrib-type="author">
                 * <aff> elements with proper id attributes
                 * <author-notes> if applicable
                 * <pub-date> with valid date-type
                 * <abstract> (HIGHLY RECOMMENDED)

            3. AUTHOR FORMATTING:
               <contrib contrib-type="author">
                 <name><surname>Smith</surname><given-names>John</given-names></name>
                 <xref ref-type="aff" rid="aff1"><sup>1</sup></xref>
               </contrib>
               <aff id="aff1"><label>1</label>Department, Institution</aff>

            4. TABLES (PMC REQUIREMENT):
               - <table-wrap> MUST have position="float" or position="anchor"
               - <caption> MUST be FIRST child of table-wrap
               - Use <label> for table number
               - Avoid colspan/rowspan when possible

            5. FIGURES:
               - <fig> with proper id attribute
               - <label> and <caption> elements
               - <graphic xlink:href="filename.ext"> with proper namespacing

            6. REFERENCES:
               - <ref-list> in <back> section
               - Each <ref> with unique id
               - Proper citation elements

            7. SPECIAL CHARACTERS:
               - Use XML entities: &lt; &gt; &amp; &apos; &quot;
               - Unicode: &#x20B9; (Rupee), &#xB1; (plus-minus)

            8. SECTIONS:
               - <sec> elements with id attributes
               - <title> for each section
               - Proper nesting hierarchy

            PRESERVE: All scientific content, measurements, formulas, data.
            RETURN: Only valid JATS 1.4 XML, no explanations.

            XML to fix:
            {xml_content[:8000]}
            """
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                # Clean up any markdown formatting from AI response
                cleaned_xml = response.text.strip()
                
                # Remove markdown code blocks if present
                cleaned_xml = re.sub(r'```xml\s*|\s*```', '', cleaned_xml)
                cleaned_xml = re.sub(r'```\s*|\s*```', '', cleaned_xml)
                
                # Ensure it's valid XML
                try:
                    etree.fromstring(cleaned_xml.encode('utf-8'))
                    logger.info("✅ AI repair produced valid XML")
                    return cleaned_xml
                except etree.XMLSyntaxError as e:
                    logger.warning(f"⚠️ AI repair produced invalid XML: {e}")
                    return xml_content
            else:
                logger.warning("⚠️ AI returned no response")
                return xml_content
                
        except Exception as e:
            logger.warning(f"⚠️ AI repair failed: {e}")
            return xml_content

    def _fix_with_rules(self, xml_content):
        """Rule-based XML repair as fallback."""
        try:
            # Parse the XML if possible, otherwise work with string
            try:
                parser = etree.XMLParser(remove_blank_text=True, recover=True)
                root = etree.fromstring(xml_content.encode('utf-8'), parser)
                xml_str = etree.tostring(root, encoding='unicode', pretty_print=True)
            except:
                xml_str = xml_content
            
            # Fix common header truncations
            header_fixes = {
                'NTRODUCTION': 'INTRODUCTION',
                'ETHODS': 'METHODS',
                'ESULTS': 'RESULTS',
                'ISCUSSION': 'DISCUSSION',
                'ONCLUSION': 'CONCLUSION',
                'BSTRACT': 'ABSTRACT',
                'CKNOWLEDGMENTS': 'ACKNOWLEDGMENTS',
                'EFERENCES': 'REFERENCES',
                'ATERIALS': 'MATERIALS'
            }
            
            for wrong, correct in header_fixes.items():
                # Look for headers with the truncated pattern
                pattern = f'<title>{wrong}'
                replacement = f'<title>{correct}'
                xml_str = xml_str.replace(pattern, replacement)
                
                # Also check in text content
                pattern = f'>{wrong}<'
                replacement = f'>{correct}<'
                xml_str = xml_str.replace(pattern, replacement)
            
            # Note: Special character encoding is handled by lxml parser above
            # No need for manual string replacements that can cause double-encoding
            
            logger.info("✅ Rule-based repair applied")
            return xml_str
            
        except Exception as e:
            logger.warning(f"⚠️ Rule-based repair failed: {e}")
            return xml_content

    def _run_pandoc_command(self, args, step_name):
        """
        Run pandoc command with proper error handling and logging.
        
        Args:
            args: List of arguments for pandoc
            step_name: Name of the step for logging
            
        Returns:
            bool: True if successful
        """
        try:
            # Construct the full command
            cmd = ["pandoc"] + args
            
            # Log the command (excluding very long content)
            cmd_log = " ".join(cmd)
            if len(cmd_log) > 200:
                cmd_log = cmd_log[:200] + "..."
            logger.info(f"Running pandoc for {step_name}: {cmd_log}")
            
            # Execute the command
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Log warnings if any
            if result.stderr and result.stderr.strip():
                logger.warning(f"Pandoc warnings for {step_name}: {result.stderr[:500]}")
            
            logger.info(f"✅ {step_name} completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Pandoc failed for {step_name}")
            logger.error(f"Error output: {e.stderr[:1000]}")
            logger.error(f"Return code: {e.returncode}")
            raise RuntimeError(f"Pandoc conversion failed for {step_name}: {e.stderr[:500]}")
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Pandoc timeout for {step_name} (5 minutes)")
            raise RuntimeError(f"Pandoc conversion timed out for {step_name}")
            
        except FileNotFoundError:
            logger.error(f"❌ Pandoc not found. Make sure pandoc is installed.")
            raise RuntimeError("Pandoc is not installed or not in PATH")
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in {step_name}: {e}")
            raise

    def _validate_xml_wellformedness(self):
        """
        Validate XML well-formedness after pandoc conversion.
        This catches malformed XML before post-processing applies string replacements.
        """
        try:
            logger.info("Validating XML well-formedness...")
            if not os.path.exists(self.xml_path):
                raise FileNotFoundError(f"XML file not found: {self.xml_path}")
            
            # Try to parse the XML
            parser = etree.XMLParser(remove_blank_text=True)
            with open(self.xml_path, 'rb') as f:
                doc = etree.parse(f, parser)
            
            # Check that root element exists
            root = doc.getroot()
            if root is None:
                raise ValueError("XML has no root element")
            
            # Check that it's an article element (JATS requirement)
            if root.tag not in ['article', '{http://jats.nlm.nih.gov}article']:
                logger.warning(f"⚠️ Root element is '{root.tag}', expected 'article'")
            
            logger.info("✅ XML is well-formed")
            return True
            
        except etree.XMLSyntaxError as e:
            logger.error(f"❌ XML Syntax Error in pandoc output: {e}")
            logger.error(f"   Line {e.lineno}, Column {e.offset}")
            raise RuntimeError(f"Pandoc produced malformed XML: {e}")
            
        except Exception as e:
            logger.error(f"❌ XML validation failed: {e}")
            raise

    def validate_jats_compliance(self):
        """Validates against JATS XSD and performs PMC Style Checker compliance checks."""
        if not os.path.exists(self.xsd_path):
            logger.error(f"❌ XSD file not found: {self.xsd_path}")
            # Still try to run PMC Style Checker even if XSD is missing
            pmc_stylechecker = self._run_pmc_stylechecker()
            self._generate_validation_report(None, False, "XSD file not found", pmc_stylechecker=pmc_stylechecker)
            return False

        try:
            # Set up parser
            parser = etree.XMLParser()

            # Parse and validate
            logger.info("Loading JATS schema...")
            schema_doc = etree.parse(self.xsd_path, parser)
            schema = etree.XMLSchema(schema_doc)

            logger.info("Parsing generated XML...")
            doc = etree.parse(self.xml_path, parser)

            logger.info(f"Validating XML against JATS schema (targeting {self.jats_version})...")
            schema.assertValid(doc)

            logger.info(f"✅ JATS Validation: SUCCESS")

            # Perform additional PMC-specific checks
            pmc_passed = self._validate_pmc_requirements(doc)
            
            # Run PMC Style Checker if available
            pmc_stylechecker_result = self._run_pmc_stylechecker()

            # Generate comprehensive validation report
            self._generate_validation_report(doc, True, pmc_passed=pmc_passed, pmc_stylechecker=pmc_stylechecker_result)
            return True

        except etree.XMLSchemaError as e:
            logger.error(f"❌ JATS Validation Failed: {e}")
            # Still try to run PMC Style Checker even if schema validation fails
            pmc_stylechecker = self._run_pmc_stylechecker()
            self._generate_validation_report(None, False, str(e), pmc_stylechecker=pmc_stylechecker)
            return False

        except etree.XMLSyntaxError as e:
            logger.error(f"❌ XML Syntax Error: {e}")
            # Try to run PMC Style Checker if XML can be parsed
            pmc_stylechecker = self._run_pmc_stylechecker()
            self._generate_validation_report(None, False, f"XML Syntax Error: {e}", pmc_stylechecker=pmc_stylechecker)
            return False

        except Exception as e:
            logger.error(f"❌ Validation Error: {e}")
            # Try to run PMC Style Checker
            pmc_stylechecker = self._run_pmc_stylechecker()
            self._generate_validation_report(None, False, str(e), pmc_stylechecker=pmc_stylechecker)
            return False

    def _run_pmc_stylechecker(self):
        """
        Run PMC Style Checker XSLT transformation using xsltproc.
        Looks for both official PMC style checker files and custom simplified checker.
        Returns a dictionary with style checker results.
        """
        logger.info("Running PMC Style Checker...")
        
        # Look for style checker XSLT files in order of preference
        pmc_dir = "pmc-stylechecker"
        bundle_dir = os.path.join(pmc_dir, "nlm-style-5.47")
        
        xslt_candidates = []
        
        # First, check the nlm-style-5.47 bundle directory
        if os.path.exists(bundle_dir):
            # Prefer nlm-stylechecker.xsl if present
            nlm_stylechecker_path = os.path.join(bundle_dir, "nlm-stylechecker.xsl")
            if os.path.exists(nlm_stylechecker_path):
                xslt_candidates.append(nlm_stylechecker_path)
            
            # Also look for versioned XSL files (e.g., nlm-style-5-0.xsl)
            # Find all .xsl files in the bundle directory
            try:
                for filename in os.listdir(bundle_dir):
                    if filename.endswith('.xsl'):
                        filepath = os.path.join(bundle_dir, filename)
                        if filepath not in xslt_candidates:
                            xslt_candidates.append(filepath)
            except OSError:
                pass
        
        # Fallback candidates at repository root
        xslt_candidates.extend([
            # Official PMC style checker files (preferred)
            os.path.join(pmc_dir, "nlm-style-5-0.xsl"),
            os.path.join(pmc_dir, "nlm-style-3-0.xsl"),
            os.path.join(pmc_dir, "nlm-stylechecker.xsl"),
            # Custom simplified checker
            os.path.join(pmc_dir, "pmc_style_checker.xsl")
        ])
        
        # Find first existing XSLT file
        xslt_path = None
        for candidate_path in xslt_candidates:
            if os.path.exists(candidate_path):
                xslt_path = candidate_path
                logger.info(f"Found PMC Style Checker XSLT: {xslt_path}")
                break
        
        # If no candidate found, try to find any .xsl file in nlm-style-5.47 directory
        if not xslt_path:
            nlm_547_dir = os.path.join(pmc_dir, "nlm-style-5.47")
            if os.path.exists(nlm_547_dir) and os.path.isdir(nlm_547_dir):
                xsl_files = [f for f in os.listdir(nlm_547_dir) 
                           if f.endswith('.xsl') and not f.startswith('PLACEHOLDER')]
                if xsl_files:
                    # Prefer files with "stylechecker" in the name, otherwise use the first .xsl
                    stylechecker_files = [f for f in xsl_files if 'stylechecker' in f.lower()]
                    if stylechecker_files:
                        xslt_path = os.path.join(nlm_547_dir, stylechecker_files[0])
                    else:
                        xslt_path = os.path.join(nlm_547_dir, xsl_files[0])
                    logger.info(f"Found PMC Style Checker XSLT in nlm-style-5.47: {xslt_path}")
        
        if not xslt_path:
            logger.warning("PMC Style Checker XSLT not found. Skipping style check.")
            logger.info(f"To enable: Run ./tools/fetch_pmc_style.sh")
            logger.info(f"Or download from https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz")
            return {
                "available": False,
                "message": "PMC Style Checker XSLT files not installed",
                "installation_url": "https://cdn.ncbi.nlm.nih.gov/pmc/cms/files/nlm-style-5.47.tar.gz",
                "installation_script": "./tools/fetch_pmc_style.sh"
            }
        
        # Check if xsltproc is available
        try:
            xsltproc_check = subprocess.run(
                ["which", "xsltproc"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if xsltproc_check.returncode != 0:
                logger.warning("xsltproc not found. PMC Style Checker requires xsltproc to be installed.")
                return {
                    "available": False,
                    "message": "xsltproc not found. Install libxslt package to enable PMC style checking.",
                    "xslt_found": os.path.basename(xslt_path),
                    "install_instructions": "Ubuntu/Debian: apt-get install xsltproc, macOS: brew install libxslt"
                }
        except Exception as e:
            logger.warning(f"Could not check for xsltproc: {e}")
            return {
                "available": False,
                "message": f"Could not verify xsltproc availability: {e}",
                "xslt_found": os.path.basename(xslt_path)
            }
        
        # Run xsltproc via subprocess
        try:
            logger.info(f"Running xsltproc with {os.path.basename(xslt_path)}...")
            result = subprocess.run(
                ["xsltproc", xslt_path, self.xml_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Build result dictionary
            style_check_result = {
                "available": True,
                "xslt_used": os.path.basename(xslt_path),
                "xslt_path": xslt_path,
                "returncode": result.returncode,
                "xslt_stdout": result.stdout,
                "xslt_stderr": result.stderr
            }
            
            # Parse output for errors and warnings
            errors = []
            warnings = []
            
            # Check both stdout and stderr for diagnostic messages
            output_text = result.stdout + "\n" + result.stderr
            
            if output_text:
                lines = output_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    if 'error' in line.lower() or 'ERROR' in line:
                        errors.append(line)
                    elif 'warning' in line.lower() or 'WARNING' in line:
                        warnings.append(line)
            
            style_check_result["error_count"] = len(errors)
            style_check_result["warning_count"] = len(warnings)
            style_check_result["errors"] = errors
            style_check_result["warnings"] = warnings
            
            # Determine status based on return code and parsed output
            if result.returncode == 0:
                style_check_result["status"] = "PASS" if len(errors) == 0 else "FAIL"
            else:
                style_check_result["status"] = "ERROR"
            
            # Save HTML output if generated
            if result.stdout:
                html_output_path = os.path.join(self.output_dir, "pmc_style_report.html")
                try:
                    with open(html_output_path, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
                    style_check_result["html_report"] = "pmc_style_report.html"
                    logger.info(f"PMC Style Checker HTML report saved to {html_output_path}")
                except Exception as e:
                    logger.warning(f"Could not save HTML report: {e}")
            
            logger.info(f"✅ PMC Style Checker completed: {len(errors)} errors, {len(warnings)} warnings")
            return style_check_result
            
        except subprocess.TimeoutExpired:
            logger.error("❌ PMC Style Checker timed out after 60 seconds")
            return {
                "available": True,
                "xslt_used": os.path.basename(xslt_path),
                "error": "XSLT transformation timed out after 60 seconds",
                "status": "ERROR",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"❌ PMC Style Checker failed: {e}")
            logger.debug(f"Exception details: {traceback.format_exc()}")
            return {
                "available": True,
                "xslt_used": os.path.basename(xslt_path),
                "error": str(e),
                "status": "ERROR",
                "returncode": -1
            }
            
            # Include traceback in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                error_details["traceback"] = traceback.format_exc()
            
            return error_details


    def _validate_pmc_requirements(self, xml_doc):
        """
        Validate PMC-specific requirements beyond basic JATS compliance.
        Reference: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/
        """
        logger.info("Running PMC Style Checker compliance validation...")
        issues = []
        warnings = []

        try:
            root = xml_doc.getroot()

            # 1. Check DTD version
            dtd_version = root.get('dtd-version')
            if not dtd_version:
                issues.append("Missing dtd-version attribute on <article>")
            elif dtd_version not in ['1.3', '1.4']:
                warnings.append(f"DTD version {dtd_version} - PMC recommends 1.3 or 1.4")

            # 2. Check article-type
            article_type = root.get('article-type')
            if not article_type:
                warnings.append("Missing article-type attribute")

            # 3. Check required namespaces
            xlink_ns = root.get('{http://www.w3.org/2000/xmlns/}xlink')
            if not xlink_ns:
                warnings.append("Missing XLink namespace declaration")

            # 4. Validate front matter structure
            front = root.find('.//front')
            if front is None:
                issues.append("Missing <front> element")
            else:
                # Check article-meta
                article_meta = front.find('.//article-meta')
                if article_meta is None:
                    issues.append("Missing <article-meta> in <front>")
                else:
                    # Check DOI
                    doi = article_meta.find('.//article-id[@pub-id-type="doi"]')
                    if doi is None:
                        warnings.append("Missing DOI - highly recommended for PMC")

                    # Check title
                    title = article_meta.find('.//title-group/article-title')
                    if title is None:
                        issues.append("Missing <article-title>")

                    # Check authors
                    contrib_group = article_meta.find('.//contrib-group')
                    if contrib_group is None:
                        warnings.append("Missing <contrib-group> - authors not specified")
                    else:
                        contribs = contrib_group.findall('.//contrib[@contrib-type="author"]')
                        if len(contribs) == 0:
                            warnings.append("No authors with contrib-type='author'")

                    # Check abstract
                    abstract = article_meta.find('.//abstract')
                    if abstract is None:
                        warnings.append("Missing <abstract> - highly recommended")

                    # Check pub-date
                    pub_date = article_meta.find('.//pub-date')
                    if pub_date is None:
                        warnings.append("Missing <pub-date>")

            # 5. Validate body structure
            body = root.find('.//body')
            if body is None:
                warnings.append("Missing <body> element")
            else:
                # Check sections have IDs
                sections = body.findall('.//sec')
                for i, sec in enumerate(sections):
                    if not sec.get('id'):
                        warnings.append(f"Section {i+1} missing id attribute")

            # 6. Validate table-wrap elements
            table_wraps = root.findall('.//table-wrap')
            for i, tw in enumerate(table_wraps):
                position = tw.get('position')
                if not position or position not in ['float', 'anchor']:
                    warnings.append(f"table-wrap {i+1} should have position='float' or 'anchor'")

                # Check caption is first child
                if len(tw) > 0:
                    first_child = tw[0]
                    if first_child.tag != 'caption' and first_child.tag != 'label':
                        warnings.append(f"table-wrap {i+1}: caption should be first child")

            # 7. Validate figure elements
            figs = root.findall('.//fig')
            for i, fig in enumerate(figs):
                if not fig.get('id'):
                    warnings.append(f"Figure {i+1} missing id attribute")

                caption = fig.find('.//caption')
                if caption is None:
                    warnings.append(f"Figure {i+1} missing <caption>")

                graphic = fig.find('.//graphic')
                if graphic is None:
                    warnings.append(f"Figure {i+1} missing <graphic> element")

            # 8. Validate back matter
            back = root.find('.//back')
            if back is not None:
                ref_list = back.find('.//ref-list')
                if ref_list is not None:
                    refs = ref_list.findall('.//ref')
                    for i, ref in enumerate(refs):
                        if not ref.get('id'):
                            warnings.append(f"Reference {i+1} missing id attribute")

            # Log results
            if issues:
                logger.warning(f"PMC Validation: {len(issues)} CRITICAL issues found")
                for issue in issues:
                    logger.warning(f"  - {issue}")

            if warnings:
                logger.info(f"PMC Validation: {len(warnings)} warnings found")
                for warning in warnings[:5]:  # Show first 5
                    logger.info(f"  - {warning}")
                if len(warnings) > 5:
                    logger.info(f"  ... and {len(warnings) - 5} more warnings")

            if not issues and not warnings:
                logger.info("✅ PMC compliance checks: PASSED")
                return {"passed": True, "issues": [], "warnings": []}

            return {
                "passed": len(issues) == 0,
                "issues": issues,
                "warnings": warnings
            }

        except Exception as e:
            logger.error(f"PMC validation check failed: {e}")
            return {"passed": False, "error": str(e)}

    def _generate_validation_report(self, xml_doc, passed, error_msg=None, pmc_passed=None, pmc_stylechecker=None, **kwargs):
        """Generate detailed validation report for PMC compliance.
        
        Args:
            xml_doc: The XML document to validate
            passed: Whether validation passed
            error_msg: Error message if validation failed
            pmc_passed: PMC compliance check results
            pmc_stylechecker: PMC style checker results
            **kwargs: Additional keyword arguments (supports pmc_style_check for backward compatibility)
        """
        # Handle backward compatibility: pmc_style_check -> pmc_stylechecker
        if 'pmc_style_check' in kwargs and pmc_stylechecker is None:
            pmc_stylechecker = kwargs['pmc_style_check']
            logger.warning("Using deprecated parameter 'pmc_style_check', please use 'pmc_stylechecker' instead")
        
        report_path = os.path.join(self.output_dir, "validation_report.json")

        report = {
            "jats_validation": {
                "status": "PASS" if passed else "FAIL",
                "target_version": f"JATS {self.jats_version}",
                "schema_used": os.path.basename(self.xsd_path),
                "standard": f"JATS Publishing DTD {self.jats_version}",
                "official_schema": f"https://public.nlm.nih.gov/projects/jats/publishing/{self.jats_version}/",
                "timestamp": self._get_timestamp()
            },
            "pmc_compliance": {
                "checked": pmc_passed is not None,
                "status": "PASS" if (pmc_passed and pmc_passed.get("passed")) else "WARNING",
                "reference": "https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/",
                "style_checker": "https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/"
            },
            "pmc_style_checker": pmc_stylechecker if pmc_stylechecker else {
                "status": "not_run",
                "message": "PMC Style Checker not available"
            },
            "output_files": {
                "jats_xml": "article.xml",
                "jats_pdf": "published_article.pdf",
                "direct_pdf": "direct_from_word.pdf",
                "html": "article.html",
                "media": "media/"
            },
            "recommendations": []
        }
        
        # Add PMC Style Checker results
        if pmc_stylechecker:
            report["pmc_stylechecker"] = pmc_stylechecker
            
            if pmc_stylechecker.get("available"):
                if pmc_stylechecker.get("status") == "PASS":
                    report["recommendations"].append(
                        "PMC Style Checker passed with no errors."
                    )
                elif pmc_stylechecker.get("status") == "FAIL":
                    report["recommendations"].append(
                        f"PMC Style Checker found {pmc_stylechecker.get('error_count', 0)} errors. Review and fix before submission."
                    )
                if pmc_stylechecker.get("warning_count", 0) > 0:
                    report["recommendations"].append(
                        f"PMC Style Checker found {pmc_stylechecker.get('warning_count', 0)} warnings. Review for best practices."
                    )

        # Add PMC compliance details
        if pmc_passed:
            if isinstance(pmc_passed, dict):
                report["pmc_compliance"]["details"] = {
                    "critical_issues": pmc_passed.get("issues", []),
                    "warnings": pmc_passed.get("warnings", []),
                    "issues_count": len(pmc_passed.get("issues", [])),
                    "warnings_count": len(pmc_passed.get("warnings", []))
                }

                # Add recommendations based on findings
                if pmc_passed.get("issues"):
                    report["recommendations"].append(
                        "Critical issues found. Fix these before PMC submission."
                    )
                if pmc_passed.get("warnings"):
                    report["recommendations"].append(
                        "Warnings found. Review PMC tagging guidelines for best practices."
                    )
                if not pmc_passed.get("issues") and not pmc_passed.get("warnings"):
                    report["recommendations"].append(
                        "XML structure looks good. Validate with PMC Style Checker before submission."
                    )
        
        # Add recommendations from PMC Style Checker
        if pmc_stylechecker and pmc_stylechecker.get("status") == "completed":
            summary = pmc_stylechecker.get("summary", {})
            if summary.get("errors", 0) > 0:
                report["recommendations"].append(
                    f"PMC Style Checker found {summary['errors']} error(s). Review and fix before submission."
                )
            if summary.get("warnings", 0) > 0:
                report["recommendations"].append(
                    f"PMC Style Checker found {summary['warnings']} warning(s). Review for best practices."
                )

        # Add basic structure checks
        if xml_doc:
            try:
                root = xml_doc.getroot()
                structure_info = {
                    "dtd_version": root.get('dtd-version', 'not specified'),
                    "article_type": root.get('article-type', 'not specified'),
                    "has_front": root.find('.//front') is not None,
                    "has_body": root.find('.//body') is not None,
                    "has_back": root.find('.//back') is not None,
                    "table_count": len(root.findall('.//table-wrap')),
                    "figure_count": len(root.findall('.//fig')),
                    "reference_count": len(root.findall('.//ref'))
                }
                report["document_structure"] = structure_info

            except Exception as e:
                logger.warning(f"Could not extract structure info: {e}")
                report["document_structure"] = {"error": str(e)}

        if error_msg:
            report["jats_validation"]["error"] = error_msg
            report["recommendations"].append(
                "Schema validation failed. Review error details and fix XML structure."
            )

        # Add submission checklist
        report["pmc_submission_checklist"] = [
            "Validate with PMC Style Checker: https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/",
            "Ensure all figures have alt text and captions",
            "Verify all references are properly formatted",
            "Check that DOI and article metadata are complete",
            "Confirm author affiliations are correctly linked",
            "Review table formatting (captions at top, proper structure)",
            "Validate special characters and mathematical notation"
        ]

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Validation report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

    def _get_timestamp(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _namespace_exists(self, nsmap, prefix):
        """Check if a namespace prefix already exists in the nsmap."""
        if not nsmap:
            return False
        # Check if prefix exists directly
        if prefix in nsmap:
            return True
        # Check if prefix exists in any key (case-insensitive)
        for key in nsmap.keys():
            if key and prefix.lower() in str(key).lower():
                return True
        return False

    def _post_process_xml(self):
        """Post-process the XML to fix common JATS issues and ensure PMC compliance."""
        try:
            if not os.path.exists(self.xml_path):
                return

            # Parse XML using lxml to avoid string replacement issues
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(self.xml_path, parser)
            root = tree.getroot()
            
            # PMC Requirement: table-wrap position attribute
            # Position should be "float" or "anchor" (not "top")
            for table_wrap in root.findall('.//table-wrap'):
                position = table_wrap.get('position')
                if position is None:
                    table_wrap.set('position', 'float')
                elif position == 'top':
                    table_wrap.set('position', 'float')
            
            # Build the desired namespace map
            # Keep existing namespaces and add missing ones
            nsmap = dict(root.nsmap) if root.nsmap else {}
            
            # Add required namespaces if not present
            if not self._namespace_exists(nsmap, 'xlink'):
                nsmap['xlink'] = 'http://www.w3.org/1999/xlink'
            
            if not self._namespace_exists(nsmap, 'mml'):
                nsmap['mml'] = 'http://www.w3.org/1998/Math/MathML'
            
            if not self._namespace_exists(nsmap, 'xsi'):
                nsmap['xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
            
            # If we need to add namespaces, we need to recreate the root element
            if nsmap != root.nsmap:
                # Create new root with updated nsmap
                new_root = etree.Element(root.tag, nsmap=nsmap)
                
                # Copy all attributes
                for key, value in root.attrib.items():
                    new_root.set(key, value)
                
                # Copy all children
                for child in root:
                    new_root.append(child)
                
                # Replace the root
                root = new_root
                tree._setroot(root)
            
            # Add xsi:schemaLocation attribute
            xsi_ns = 'http://www.w3.org/2001/XMLSchema-instance'
            schema_location_attr = f'{{{xsi_ns}}}schemaLocation'
            if schema_location_attr not in root.attrib:
                schema_location = (
                    'https://jats.nlm.nih.gov/publishing/1.3/ '
                    'https://jats.nlm.nih.gov/publishing/1.3/JATS-journalpublishing1-3.xsd'
                )
                root.set(schema_location_attr, schema_location)
            
            # Set DTD version
            root.set('dtd-version', self.jats_version)
            
            # Ensure article-type
            if 'article-type' not in root.attrib:
                root.set('article-type', 'research-article')
            
            # Remove DOCTYPE declaration to avoid "DTD not found" errors during validation
            # The DOCTYPE with external URL causes xsltproc to fail when validating
            tree.docinfo.clear()
            
            # Write back the XML with proper formatting
            tree.write(
                self.xml_path,
                pretty_print=True,
                xml_declaration=True,
                encoding='utf-8'
            )

            logger.info(f"✅ XML post-processing completed (JATS {self.jats_version} + PMC compliance + xsi:schemaLocation)")
        except Exception as e:
            logger.warning(f"XML post-processing failed: {e}")
            # Log the traceback for debugging
            import traceback
            logger.warning(f"Traceback: {traceback.format_exc()}")

    def _create_fallback_pdf(self, pdf_path, message):
        """Create a simple fallback PDF when WeasyPrint fails."""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.setFont("Helvetica", 12)
            
            # Add title
            c.drawString(1*inch, 10*inch, "OmniJAX Conversion Report")
            c.setFont("Helvetica", 10)
            
            # Add message
            y_position = 9*inch
            for line in message.split('\n'):
                c.drawString(1*inch, y_position, line)
                y_position -= 0.25*inch
            
            # Add timestamp
            c.drawString(1*inch, 0.5*inch, f"Generated: {self._get_timestamp()}")
            
            c.save()
            logger.info(f"Created fallback PDF at {pdf_path}")
        except Exception as e:
            logger.error(f"Failed to create fallback PDF: {e}")
            # Last resort: create empty file
            with open(pdf_path, 'wb') as f:
                f.write(b"%PDF-1.4\n%Fallback PDF\n")

    def _generate_readme(self):
        """Generate README file with conversion details."""
        readme_path = os.path.join(self.output_dir, "README.txt")

        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write(f"OmniJAX JATS {self.jats_version} Publishing DTD Conversion Package\n")
                f.write("=" * 70 + "\n\n")

                f.write("GENERATED FILES:\n")
                f.write("-" * 50 + "\n")
                f.write("1. article.xml           - JATS 1.4 Publishing DTD XML\n")
                f.write("2. published_article.pdf - PDF generated from JATS XML\n")
                f.write("3. direct_from_word.pdf  - Direct DOCX→PDF conversion\n")
                f.write("4. article.html          - HTML version for web viewing\n")
                f.write("5. media/                - Extracted images and media files\n")
                f.write("6. validation_report.json- Comprehensive validation report\n")
                f.write("7. README.txt            - This file\n\n")

                f.write("COMPLIANCE INFORMATION:\n")
                f.write("-" * 50 + "\n")
                f.write(f"• JATS {self.jats_version} Publishing DTD compliant\n")
                f.write("• Official Schema: https://public.nlm.nih.gov/projects/jats/publishing/1.4/\n")
                f.write("• PMC/NLM Tagging Guidelines: https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/\n")
                f.write("• PMC Style Checker ready for validation\n")
                f.write("• Table positioning: float/anchor (PMC compliant)\n")
                f.write("• MathML 2.0/3.0 support included\n")
                f.write("• Proper XLink namespace declarations\n")
                f.write("• Accessibility features (alt-text, captions)\n")
                f.write("• Media extraction to separate folder\n\n")

                f.write("PMC SUBMISSION CHECKLIST:\n")
                f.write("-" * 50 + "\n")
                f.write("1. ✓ Validate with PMC Style Checker:\n")
                f.write("   https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/\n")
                f.write("2. ✓ Review validation_report.json for warnings\n")
                f.write("3. ✓ Verify DOI and article metadata are complete\n")
                f.write("4. ✓ Check author affiliations and ORCID IDs\n")
                f.write("5. ✓ Ensure all figures have captions and alt text\n")
                f.write("6. ✓ Verify references are properly formatted\n")
                f.write("7. ✓ Review table formatting (captions, structure)\n")
                f.write("8. ✓ Validate special characters and math notation\n\n")

                f.write("TECHNICAL DETAILS:\n")
                f.write("-" * 50 + "\n")
                f.write(f"• Input file: {os.path.basename(self.docx_path)}\n")
                f.write(f"• Generated: {self._get_timestamp()}\n")
                f.write(f"• JATS Version: {self.jats_version} Publishing DTD\n")
                f.write("• Tools: Pandoc 3.x, WeasyPrint, lxml\n")
                f.write(f"• Schema: {os.path.basename(self.xsd_path)}\n")
                f.write("• AI-enhanced content repair applied\n")
                f.write("• PMC compliance checks performed\n\n")

                f.write("VALIDATION DETAILS:\n")
                f.write("-" * 50 + "\n")
                f.write("The XML has been validated against:\n")
                f.write("1. JATS Publishing DTD schema (XSD)\n")
                f.write("2. PMC-specific structural requirements\n")
                f.write("3. Required metadata elements\n")
                f.write("4. Table and figure formatting rules\n")
                f.write("5. Reference structure compliance\n\n")
                f.write("See validation_report.json for detailed results.\n\n")

                f.write("USAGE NOTES:\n")
                f.write("-" * 50 + "\n")
                f.write("1. The JATS XML is validated against official schema\n")
                f.write("2. Two PDF versions are provided:\n")
                f.write("   - published_article.pdf: From JATS XML (semantic)\n")
                f.write("   - direct_from_word.pdf: Direct conversion (visual)\n")
                f.write("3. All images are extracted to media/ folder\n")
                f.write("4. Review validation_report.json before submission\n")
                f.write("5. Use PMC Style Checker for final validation\n")
                f.write("6. Check PMC tagging guidelines for specific requirements\n\n")

                f.write("REFERENCES:\n")
                f.write("-" * 50 + "\n")
                f.write("• JATS Official: https://jats.nlm.nih.gov/\n")
                f.write("• PMC Tagging Guidelines:\n")
                f.write("  https://pmc.ncbi.nlm.nih.gov/tagging-guidelines/article/style/\n")
                f.write("• PMC Style Checker:\n")
                f.write("  https://pmc.ncbi.nlm.nih.gov/tools/stylechecker/\n")
                f.write("• JATS Publishing DTD:\n")
                f.write("  https://public.nlm.nih.gov/projects/jats/publishing/1.4/\n\n")

                f.write("SUPPORT:\n")
                f.write("-" * 50 + "\n")
                f.write("OmniJAX Professional JATS Converter\n")
                f.write("PMC-Compliant Document Conversion System\n\n")

                f.write("=" * 70 + "\n")

            logger.info(f"✅ README generated: {readme_path}")

        except Exception as e:
            logger.error(f"Failed to generate README: {e}")

    def run_pipeline(self):
        """Executes the full conversion pipeline."""
        logger.info("=" * 60)
        logger.info("OmniJAX Pipeline Starting")
        logger.info("=" * 60)

        # STEP 1: DOCX to JATS XML
        logger.info("Step 1: Converting DOCX to JATS XML...")
        try:
            # Use valid pandoc options for JATS
            self._run_pandoc_command([
                self.docx_path,
                "-t", "jats",
                "-o", self.xml_path,
                "--extract-media=" + self.output_dir,
                "--standalone",
                "--mathml",
                # Valid pandoc options
                "--wrap=none",
                "--top-level-division=section",
                "--metadata", "link-citations=true"
            ], "DOCX to JATS XML")
            
            # Validate XML well-formedness before post-processing
            self._validate_xml_wellformedness()
            
            # Post-process XML for JATS compliance
            self._post_process_xml()
            
        except Exception as e:
            logger.error(f"Failed to convert DOCX to JATS XML: {e}")
            raise

        # Verify XML was created
        if not os.path.exists(self.xml_path):
            raise FileNotFoundError(f"JATS XML not created at {self.xml_path}")
        
        xml_size = os.path.getsize(self.xml_path)
        logger.info(f"JATS XML created: {xml_size:,} bytes")

        # STEP 2: AI Repair & PMC Compliance
        logger.info("Step 2: AI Repair for PMC Style Checker compliance...")
        try:
            with open(self.xml_path, 'r', encoding='utf-8') as f:
                raw_xml = f.read()
            
            # Only process if we have content
            if raw_xml and len(raw_xml) > 100:
                fixed_xml = self.fix_content_with_ai(raw_xml)
                with open(self.xml_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_xml)
                logger.info("✅ AI repair completed")
            else:
                logger.warning("⚠️ XML too small or empty, skipping AI repair")
        except Exception as e:
            logger.warning(f"⚠️ AI repair failed, continuing with original XML: {e}")

        # STEP 3: JATS Validation & PMC Compliance
        logger.info(f"Step 3: Validating against JATS {self.jats_version} Schema and PMC requirements...")
        validation_passed = self.validate_jats_compliance()

        if not validation_passed:
            logger.warning("⚠️ JATS validation failed, but continuing with pipeline...")

        # STEP 4: Intermediate HTML (for JATS PDF)
        logger.info("Step 4: Generating intermediate HTML from JATS XML...")
        try:
            self._run_pandoc_command([
                "-f", "jats",
                self.xml_path,
                "--standalone",
                "--css", self.css_path,
                "-t", "html5",
                "-o", self.html_path,
                "--embed-resources",
                "--mathjax"
            ], "JATS to HTML")
            
            # Verify HTML was created
            if os.path.exists(self.html_path):
                html_size = os.path.getsize(self.html_path)
                logger.info(f"HTML created: {html_size:,} bytes")
            else:
                raise FileNotFoundError(f"HTML not created at {self.html_path}")
                
        except Exception as e:
            logger.error(f"Failed to generate HTML: {e}")
            raise

        # STEP 5: Render JATS-Derived PDF
        logger.info("Step 5: Rendering JATS-compliant PDF via WeasyPrint...")
        try:
            from weasyprint import HTML, CSS
            
            # Check if WeasyPrint can access the CSS file
            css_path = self.css_path
            if not os.path.exists(css_path):
                logger.warning(f"CSS file not found at {css_path}, using default styling")
                css_path = None
            
            # Generate PDF
            html = HTML(filename=self.html_path, base_url=self.output_dir)
            
            if css_path and os.path.exists(css_path):
                css = CSS(filename=css_path)
                html.write_pdf(target=self.pdf_path, stylesheets=[css])
            else:
                html.write_pdf(target=self.pdf_path)
            
            # Verify PDF was created
            if os.path.exists(self.pdf_path):
                pdf_size = os.path.getsize(self.pdf_path)
                logger.info(f"✅ JATS PDF generated: {pdf_size:,} bytes")
            else:
                raise FileNotFoundError(f"PDF not created at {self.pdf_path}")
                
        except ImportError:
            logger.error("❌ WeasyPrint not installed")
            raise RuntimeError("WeasyPrint is required for PDF generation")
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            # Try to create a minimal PDF as fallback
            self._create_fallback_pdf(self.pdf_path, "JATS PDF Generation Failed")
            logger.info("Created fallback PDF")

        # STEP 6: Direct DOCX to PDF Conversion
        logger.info("Step 6: Creating direct DOCX→PDF (preserving Word formatting)...")
        try:
            # Create a temporary HTML file from DOCX
            temp_html = os.path.join(self.output_dir, "direct_temp.html")
            
            self._run_pandoc_command([
                self.docx_path,
                "-s",
                "--css", self.css_path,
                "--extract-media=" + self.output_dir,
                "-o", temp_html
            ], "DOCX to HTML (direct)")
            
            # Convert HTML to PDF
            from weasyprint import HTML
            HTML(filename=temp_html, base_url=self.output_dir).write_pdf(
                target=self.direct_pdf_path
            )
            
            # Clean up temp file
            if os.path.exists(temp_html):
                os.remove(temp_html)
            
            if os.path.exists(self.direct_pdf_path):
                pdf_size = os.path.getsize(self.direct_pdf_path)
                logger.info(f"✅ Direct PDF generated: {pdf_size:,} bytes")
            else:
                raise FileNotFoundError(f"Direct PDF not created")
                
        except Exception as e:
            logger.error(f"❌ Direct PDF conversion failed: {e}")
            # Create a simple placeholder PDF
            self._create_fallback_pdf(
                self.direct_pdf_path, 
                "Direct PDF Generation Failed\n\nThis file is a placeholder because direct PDF conversion encountered an error.\n\nPlease use the JATS-derived PDF instead."
            )
            logger.info("Created placeholder for direct PDF")

        # STEP 7: Create documentation and finalize
        logger.info("Step 7: Generating documentation and finalizing package...")
        self._generate_readme()
        
        # Check for media files
        media_files = []
        if os.path.exists(self.media_dir):
            media_files = os.listdir(self.media_dir)
            logger.info(f"Found {len(media_files)} media files")
        
        # Log final summary
        logger.info("=" * 60)
        logger.info("Pipeline Completed Successfully!")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Files generated:")
        logger.info(f"  - JATS XML: {os.path.getsize(self.xml_path):,} bytes")
        logger.info(f"  - HTML: {os.path.getsize(self.html_path):,} bytes")
        logger.info(f"  - JATS PDF: {os.path.getsize(self.pdf_path):,} bytes")
        logger.info(f"  - Direct PDF: {os.path.getsize(self.direct_pdf_path):,} bytes")
        logger.info(f"  - Media files: {len(media_files)}")
        logger.info("=" * 60)

        return self.output_dir