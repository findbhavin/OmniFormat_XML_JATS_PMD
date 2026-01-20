#!/usr/bin/env python3
"""
Direct DOCX to PDF Converter
=============================

Standalone script for direct conversion from DOCX to PDF without using JATS XML.
This is a simplified conversion that preserves Word formatting.

Usage:
    python tools/direct_pdf_converter.py input.docx output.pdf
    
Features:
- Direct DOCX to PDF conversion
- Preserves Word formatting
- No JATS XML intermediate step
- Faster than full JATS pipeline
- Suitable for quick PDF generation

Author: OmniJAX Team
Date: 2026-01-20
"""

import os
import sys
import logging
import argparse
import subprocess
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if required tools are installed."""
    required_tools = ['pandoc']
    missing = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool, '--version'], 
                         capture_output=True, 
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(tool)
    
    if missing:
        logger.error(f"Missing required tools: {', '.join(missing)}")
        logger.error("Please install:")
        for tool in missing:
            if tool == 'pandoc':
                logger.error("  - Pandoc: https://pandoc.org/installing.html")
        return False
    
    # Check for WeasyPrint
    try:
        import weasyprint
        logger.info("WeasyPrint available")
    except ImportError:
        logger.error("WeasyPrint not installed. Install with: pip install weasyprint")
        return False
    
    return True


def convert_docx_to_pdf(docx_path, pdf_path, css_path=None):
    """
    Convert DOCX to PDF directly without JATS XML.
    
    Args:
        docx_path: Path to input DOCX file
        pdf_path: Path to output PDF file
        css_path: Optional path to CSS file for styling
    
    Returns:
        bool: True if conversion successful, False otherwise
    """
    try:
        # Validate input file
        if not os.path.exists(docx_path):
            logger.error(f"Input file not found: {docx_path}")
            return False
        
        if not docx_path.lower().endswith('.docx'):
            logger.error("Input file must be a .docx file")
            return False
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.html', 
            delete=False
        ) as temp_html:
            temp_html_path = temp_html.name
        
        try:
            # Step 1: Convert DOCX to HTML using Pandoc
            logger.info("Converting DOCX to HTML...")
            pandoc_cmd = [
                'pandoc',
                docx_path,
                '-s',  # Standalone HTML
                '--self-contained',  # Embed resources
                '-o', temp_html_path
            ]
            
            if css_path and os.path.exists(css_path):
                pandoc_cmd.extend(['--css', css_path])
                logger.info(f"Using CSS: {css_path}")
            
            subprocess.run(pandoc_cmd, check=True, capture_output=True)
            logger.info("✓ HTML generated")
            
            # Step 2: Convert HTML to PDF using WeasyPrint
            logger.info("Converting HTML to PDF...")
            from weasyprint import HTML, CSS
            
            html_doc = HTML(filename=temp_html_path)
            
            # Apply additional CSS if provided
            stylesheets = []
            if css_path and os.path.exists(css_path):
                stylesheets.append(CSS(filename=css_path))
            
            html_doc.write_pdf(
                target=pdf_path,
                stylesheets=stylesheets if stylesheets else None
            )
            
            logger.info("✓ PDF generated")
            
            # Verify output
            if os.path.exists(pdf_path):
                size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
                logger.info(f"✓ Success! PDF created: {size_mb:.2f} MB")
                return True
            else:
                logger.error("PDF file was not created")
                return False
                
        finally:
            # Clean up temporary HTML file
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {e.stderr.decode()}")
        return False
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_pdf(pdf_path):
    """
    Perform basic validation on the generated PDF.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        dict: Validation results
    """
    results = {
        'exists': False,
        'size_bytes': 0,
        'size_mb': 0,
        'readable': False,
        'valid': False
    }
    
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.warning(f"PDF file not found: {pdf_path}")
            return results
        
        results['exists'] = True
        results['size_bytes'] = os.path.getsize(pdf_path)
        results['size_mb'] = results['size_bytes'] / (1024 * 1024)
        
        # Check if file is readable
        try:
            with open(pdf_path, 'rb') as f:
                # Read first few bytes to check PDF header
                header = f.read(4)
                if header == b'%PDF':
                    results['readable'] = True
                    results['valid'] = True
                    logger.info("✓ PDF validation passed")
                else:
                    logger.warning("File does not have PDF header")
        except Exception as e:
            logger.warning(f"Could not read PDF: {e}")
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
    
    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert DOCX to PDF directly without JATS XML',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.docx output.pdf
  %(prog)s document.docx output.pdf --css custom.css
  %(prog)s document.docx output.pdf --validate
        """
    )
    
    parser.add_argument(
        'input',
        help='Input DOCX file path'
    )
    
    parser.add_argument(
        'output',
        help='Output PDF file path'
    )
    
    parser.add_argument(
        '--css',
        help='Optional CSS file for styling',
        default=None
    )
    
    parser.add_argument(
        '--validate',
        help='Validate the generated PDF',
        action='store_true'
    )
    
    parser.add_argument(
        '--verbose',
        help='Enable verbose logging',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check dependencies
    logger.info("Checking dependencies...")
    if not check_dependencies():
        logger.error("Missing required dependencies")
        return 1
    
    # Convert DOCX to PDF
    logger.info(f"Converting: {args.input} -> {args.output}")
    success = convert_docx_to_pdf(args.input, args.output, args.css)
    
    if not success:
        logger.error("Conversion failed")
        return 1
    
    # Validate if requested
    if args.validate:
        logger.info("Validating PDF...")
        validation = validate_pdf(args.output)
        logger.info(f"Validation results:")
        logger.info(f"  Exists: {validation['exists']}")
        logger.info(f"  Size: {validation['size_mb']:.2f} MB")
        logger.info(f"  Valid PDF: {validation['valid']}")
        
        if not validation['valid']:
            return 1
    
    logger.info("Conversion completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
