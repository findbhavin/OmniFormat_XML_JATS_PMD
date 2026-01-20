"""
tools/safe_render.py

Validate a generated JATS XML file against the provided JATS XSD and only produce HTML when the XML is valid (unless --force is used).
This prevents producing incorrect HTML/PDF files from invalid XML.

Usage:
  python tools/safe_render.py --xml /tmp/output_files/article.xml --xsd JATS-journalpublishing-oasis-article1-3-mathml2.xsd --css templates/style.css

If validation fails a validation_report.json will be written alongside the XML and the script exits with non-zero status (unless --force is used).
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import subprocess
import sys
from lxml import etree, html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("safe_render")

def validate_xml_against_xsd(xml_path: str, xsd_path: str):
    """Validate xml_path against xsd_path using lxml.XMLSchema.
    Returns (valid: bool, errors: list).
    """
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"XML file not found: {xml_path}")
    if not os.path.exists(xsd_path):
        raise FileNotFoundError(f"XSD file not found: {xsd_path}")

    xml_doc = etree.parse(xml_path)
    xsd_doc = etree.parse(xsd_path)
    schema = etree.XMLSchema(xsd_doc)
    valid = schema.validate(xml_doc)
    errors = []
    if not valid:
        for entry in schema.error_log:
            errors.append({
                "line": entry.line,
                "column": getattr(entry, 'column', None),
                "message": entry.message,
                "domain_name": entry.domain_name,
                "type": entry.type_name
            })
    return valid, errors

def write_validation_report(output_dir: str, valid: bool, errors: list, xml_path: str, xsd_path: str):
    report = {
        "jats_validation": {
            "status": "PASS" if valid else "FAIL",
            "schema_used": os.path.basename(xsd_path),
            "xml": os.path.basename(xml_path)
        },
        "errors": errors
    }
    report_path = os.path.join(output_dir, "validation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote validation report to {report_path}")
    return report_path

def convert_jats_to_html(xml_path: str, html_path: str, css_path: str | None = None):
    """Convert JATS XML to HTML using pandoc. Raises subprocess.CalledProcessError on failure."""
    cmd = ["pandoc", "-f", "jats", "-t", "html5", xml_path, "-o", html_path, "--standalone", "--section-divs"]
    if css_path and os.path.exists(css_path):
        cmd.extend(["--css", css_path])
    logger.info("Running pandoc to generate HTML: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Verify the HTML is at least parseable
    with open(html_path, "rb") as f:
        content = f.read()
    try:
        html.fromstring(content)
        logger.info("HTML is well-formed and parseable")
        return True, None
    except Exception as e:
        logger.error("Generated HTML is not parseable: %s", e)
        return False, str(e)

def write_fallback_html(html_path: str, message: str):
    logger.info("Writing fallback HTML to %s", html_path)
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OmniJAX - Conversion Fallback</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>body{{font-family: Arial, Helvetica, sans-serif; padding:2rem;}}</style>
</head>
<body>
  <h1>Conversion Fallback</h1>
  <p>{message}</p>
  <p>Please check <code>validation_report.json</code> for details.</p>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser(description="Safely render JATS XML to HTML after validating against XSD")
    parser.add_argument("--xml", default="/tmp/output_files/article.xml", help="Path to generated JATS XML")
    parser.add_argument("--xsd", default="JATS-journalpublishing-oasis-article1-3-mathml2.xsd", help="Path to JATS XSD")
    parser.add_argument("--html", default="/tmp/output_files/article.html", help="Output HTML path")
    parser.add_argument("--css", default="templates/style.css", help="Optional CSS to pass to pandoc/weasyprint")
    parser.add_argument("--force", action="store_true", help="Force HTML generation even if validation fails")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(args.html))
    os.makedirs(output_dir, exist_ok=True)

    try:
        valid, errors = validate_xml_against_xsd(args.xml, args.xsd)
    except Exception as e:
        logger.exception("Validation step failed: %s", e)
        # Create minimal report and fallback HTML
        write_validation_report(output_dir, False, [{"message": str(e)}], args.xml, args.xsd)
        write_fallback_html(args.html, f"Validation step failed: {e}")
        sys.exit(2)

    report_path = write_validation_report(output_dir, valid, errors, args.xml, args.xsd)

    if not valid and not args.force:
        logger.error("XML validation failed. Aborting HTML generation. Use --force to override.")
        sys.exit(1)

    try:
        ok, parse_error = convert_jats_to_html(args.xml, args.html, args.css)
        if not ok:
            # Generated HTML is not parseable; write fallback and exit non-zero
            write_fallback_html(args.html, f"Generated HTML is not parseable: {parse_error}")
            sys.exit(3)
    except subprocess.CalledProcessError as e:
        logger.exception("Pandoc failed: %s", e)
        write_fallback_html(args.html, f"Pandoc failed to convert JATS to HTML: {e}")
        sys.exit(4)
    except Exception as e:
        logger.exception("Unexpected error while generating HTML: %s", e)
        write_fallback_html(args.html, f"Unexpected error: {e}")
        sys.exit(5)

    logger.info("HTML successfully generated at %s", args.html)
    sys.exit(0)


if __name__ == "__main__":
    main()