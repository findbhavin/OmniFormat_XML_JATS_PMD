#!/usr/bin/env python3
"""
add_doctype.py - Add DOCTYPE declaration to JATS XML files

This utility script adds DOCTYPE declarations to JATS XML files for compatibility
with the PMC Style Checker, which requires DTD references. The script reads an
existing XML file and writes a new file with the DOCTYPE declaration intact.

Usage:
    python tools/add_doctype.py input.xml -o articledtd.xml -v 1.4
    python tools/add_doctype.py article.xml --output articledtd.xml --version 1.3

The script supports JATS versions 1.0 through 1.4 and validates the input XML
before adding the DOCTYPE declaration.
"""

import argparse
import sys
import os
from lxml import etree
from typing import Optional


# Official JATS Publishing DTD DOCTYPE declarations
# Source: https://jats.nlm.nih.gov/publishing/
DOCTYPE_DECLARATIONS = {
    "1.4": '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.4 20240930//EN" "https://jats.nlm.nih.gov/publishing/1.4/JATS-journalpublishing1-4.dtd">',
    "1.3": '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "https://jats.nlm.nih.gov/publishing/1.3/JATS-journalpublishing1-3.dtd">',
    "1.2": '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.2 20190208//EN" "https://jats.nlm.nih.gov/publishing/1.2/JATS-journalpublishing1-2.dtd">',
    "1.1": '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.1 20151215//EN" "https://jats.nlm.nih.gov/publishing/1.1/JATS-journalpublishing1-1.dtd">',
    "1.0": '<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.0 20120330//EN" "https://jats.nlm.nih.gov/publishing/1.0/JATS-journalpublishing1.dtd">',
}


def validate_xml(xml_path: str) -> bool:
    """
    Validate that the input XML file is well-formed.
    
    Args:
        xml_path: Path to the XML file to validate
        
    Returns:
        True if XML is well-formed, False otherwise
    """
    try:
        etree.parse(xml_path)
        return True
    except etree.XMLSyntaxError as e:
        print(f"Error: Input XML is not well-formed: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error reading XML file: {e}", file=sys.stderr)
        return False


def add_doctype_declaration(
    input_path: str,
    output_path: str,
    jats_version: str = "1.4"
) -> bool:
    """
    Add DOCTYPE declaration to JATS XML file.
    
    This function reads an XML file, adds the appropriate DOCTYPE declaration
    based on the JATS version, and writes the result to a new file. The DOCTYPE
    declaration is required for PMC Style Checker validation.
    
    Args:
        input_path: Path to input XML file (without DOCTYPE)
        output_path: Path to output XML file (with DOCTYPE)
        jats_version: JATS version (1.0-1.4), defaults to 1.4
        
    Returns:
        True if successful, False otherwise
    """
    # Validate JATS version
    if jats_version not in DOCTYPE_DECLARATIONS:
        print(f"Error: Unsupported JATS version '{jats_version}'", file=sys.stderr)
        print(f"Supported versions: {', '.join(DOCTYPE_DECLARATIONS.keys())}", file=sys.stderr)
        return False
    
    # Validate input file exists
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return False
    
    # Validate XML is well-formed
    if not validate_xml(input_path):
        return False
    
    try:
        # Parse the input XML
        tree = etree.parse(input_path)
        root = tree.getroot()
        
        # Verify root element is <article>
        if root.tag != "article":
            print(f"Warning: Root element is '{root.tag}', expected 'article'", file=sys.stderr)
            print("DOCTYPE will still be added, but may not be appropriate.", file=sys.stderr)
        
        # Read the XML content as string
        xml_content = etree.tostring(
            tree,
            pretty_print=True,
            xml_declaration=True,
            encoding='utf-8'
        ).decode('utf-8')
        
        # Split the XML declaration and content
        lines = xml_content.split('\n')
        xml_declaration_line = None
        content_start_idx = 0
        
        for idx, line in enumerate(lines):
            if line.strip().startswith('<?xml'):
                xml_declaration_line = line
                content_start_idx = idx + 1
                break
        
        # Get the DOCTYPE declaration for the specified version
        doctype = DOCTYPE_DECLARATIONS[jats_version]
        
        # Construct the output with DOCTYPE
        output_lines = []
        if xml_declaration_line:
            output_lines.append(xml_declaration_line)
        output_lines.append(doctype)
        output_lines.extend(lines[content_start_idx:])
        
        output_content = '\n'.join(output_lines)
        
        # Write to output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"✅ Successfully created {output_path} with JATS {jats_version} DOCTYPE declaration")
        return True
        
    except Exception as e:
        print(f"Error processing XML: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description='Add DOCTYPE declaration to JATS XML files for PMC Style Checker compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add DOCTYPE to article.xml and save as articledtd.xml (JATS 1.4)
  python tools/add_doctype.py article.xml
  
  # Specify custom output path
  python tools/add_doctype.py article.xml -o output/article_with_dtd.xml
  
  # Specify JATS version 1.3
  python tools/add_doctype.py article.xml -v 1.3
  
  # Full example with all options
  python tools/add_doctype.py input/article.xml --output output/articledtd.xml --version 1.4

Supported JATS versions: 1.0, 1.1, 1.2, 1.3, 1.4
        """
    )
    
    parser.add_argument(
        'input',
        help='Input XML file path (without DOCTYPE declaration)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Output XML file path (with DOCTYPE declaration). Default: articledtd.xml in same directory as input'
    )
    
    parser.add_argument(
        '-v', '--version',
        default='1.4',
        choices=['1.0', '1.1', '1.2', '1.3', '1.4'],
        help='JATS version (default: 1.4)'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output is None:
        input_dir = os.path.dirname(args.input) or '.'
        args.output = os.path.join(input_dir, 'articledtd.xml')
    
    # Process the file
    success = add_doctype_declaration(args.input, args.output, args.version)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
