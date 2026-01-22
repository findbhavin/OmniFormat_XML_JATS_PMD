"""
Test DTD validation fixes in MasterPipeline.py

This test verifies that the _post_process_xml method correctly handles:
1. tex-math elements without id attributes
2. mml:math elements without id attributes
3. xref elements pointing to named-content instead of ref elements
"""

import os
import sys
import tempfile
import shutil
from lxml import etree

# Add parent directory to path to import MasterPipeline
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MasterPipeline import HighFidelityConverter


def create_test_xml_with_issues():
    """Create a test XML file with DTD validation issues."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" 
         xmlns:mml="http://www.w3.org/1998/Math/MathML"
         article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id">test-journal</journal-id>
      <journal-title-group>
        <journal-title>Test Journal</journal-title>
      </journal-title-group>
      <issn pub-type="epub">0000-0000</issn>
      <publisher>
        <publisher-name>Test Publisher</publisher-name>
      </publisher>
    </journal-meta>
    <article-meta>
      <title-group>
        <article-title>Test Article</article-title>
      </title-group>
      <pub-date date-type="pub" publication-format="electronic">
        <year>2026</year>
      </pub-date>
      <elocation-id>e001</elocation-id>
    </article-meta>
  </front>
  <body>
    <sec>
      <title>Introduction</title>
      <p>This is a test with a formula: <inline-formula><tex-math><![CDATA[E = mc^2]]></tex-math></inline-formula></p>
      <p>Another formula with MathML: <inline-formula><mml:math><mml:mrow><mml:mi>x</mml:mi><mml:mo>=</mml:mo><mml:mn>5</mml:mn></mml:mrow></mml:math></inline-formula></p>
      <p>Reference citation here<xref alt="1" rid="Ref1" ref-type="bibr"><sup>1</sup></xref> and another<xref alt="2" rid="Ref2" ref-type="bibr"><sup>2</sup></xref>.</p>
    </sec>
  </body>
  <back>
    <p><named-content id="Ref1" content-type="anchor"/>Monteiro CA, et al. Ultra-processed foods and human health. Lancet. 2025.</p>
    <p><named-content id="Ref2" content-type="anchor"/>Smith J, et al. Research methods. Nature. 2024.</p>
  </back>
</article>
"""
    return xml_content


def test_dtd_fixes():
    """Test that DTD fixes are applied correctly."""
    print("\n" + "=" * 70)
    print("Testing DTD Validation Fixes")
    print("=" * 70)
    
    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="test_dtd_fixes_")
    print(f"\nTest directory: {test_dir}")
    
    try:
        # Create test XML file
        xml_path = os.path.join(test_dir, "article.xml")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(create_test_xml_with_issues())
        
        print(f"\n✓ Created test XML: {xml_path}")
        
        # Parse original XML
        parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
        tree = etree.parse(xml_path, parser)
        root = tree.getroot()
        
        # Check issues before fix
        print("\nBEFORE FIXES:")
        print("-" * 70)
        
        # Check tex-math elements
        tex_math_elements = root.findall('.//tex-math')
        print(f"tex-math elements: {len(tex_math_elements)}")
        for i, elem in enumerate(tex_math_elements, 1):
            has_id = 'id' in elem.attrib
            print(f"  tex-math {i}: has id = {has_id}")
        
        # Check mml:math elements
        mml_ns = 'http://www.w3.org/1998/Math/MathML'
        mml_math_elements = root.findall('.//{%s}math' % mml_ns)
        print(f"mml:math elements: {len(mml_math_elements)}")
        for i, elem in enumerate(mml_math_elements, 1):
            has_id = 'id' in elem.attrib
            print(f"  mml:math {i}: has id = {has_id}")
        
        # Check xref and named-content
        bibr_xrefs = root.findall('.//xref[@ref-type="bibr"]')
        print(f"xref[@ref-type='bibr'] elements: {len(bibr_xrefs)}")
        for xref in bibr_xrefs:
            rid = xref.get('rid')
            target = root.find(f".//*[@id='{rid}']") if rid else None
            target_type = target.tag if target is not None else "NOT FOUND"
            print(f"  xref rid='{rid}' -> target type: {target_type}")
        
        named_content_elements = root.findall('.//named-content[@content-type="anchor"]')
        print(f"named-content[@content-type='anchor'] elements: {len(named_content_elements)}")
        
        # Create a temporary DOCX file (required by HighFidelityConverter)
        docx_path = os.path.join(test_dir, "test.docx")
        with open(docx_path, 'w') as f:
            f.write("dummy")  # Just a placeholder
        
        # Create converter instance and set paths
        converter = HighFidelityConverter(docx_path)
        converter.xml_path = xml_path
        converter.output_dir = test_dir
        
        # Apply the post-processing fixes
        print("\nAPPLYING FIXES...")
        print("-" * 70)
        converter._post_process_xml()
        
        # Parse the fixed XML
        tree = etree.parse(xml_path, parser)
        root = tree.getroot()
        
        # Check fixes were applied
        print("\nAFTER FIXES:")
        print("-" * 70)
        
        # Check tex-math elements
        tex_math_elements = root.findall('.//tex-math')
        print(f"tex-math elements: {len(tex_math_elements)}")
        tex_math_fixed = 0
        for i, elem in enumerate(tex_math_elements, 1):
            has_id = 'id' in elem.attrib
            elem_id = elem.get('id', 'NONE')
            print(f"  tex-math {i}: has id = {has_id}, id = '{elem_id}'")
            if has_id:
                tex_math_fixed += 1
        
        # Check mml:math elements
        mml_math_elements = root.findall('.//{%s}math' % mml_ns)
        print(f"mml:math elements: {len(mml_math_elements)}")
        mml_math_fixed = 0
        for i, elem in enumerate(mml_math_elements, 1):
            has_id = 'id' in elem.attrib
            elem_id = elem.get('id', 'NONE')
            print(f"  mml:math {i}: has id = {has_id}, id = '{elem_id}'")
            if has_id:
                mml_math_fixed += 1
        
        # Check xref and ref elements
        bibr_xrefs = root.findall('.//xref[@ref-type="bibr"]')
        print(f"xref[@ref-type='bibr'] elements: {len(bibr_xrefs)}")
        xrefs_pointing_to_ref = 0
        for xref in bibr_xrefs:
            rid = xref.get('rid')
            target = root.find(f".//*[@id='{rid}']") if rid else None
            target_type = target.tag if target is not None else "NOT FOUND"
            print(f"  xref rid='{rid}' -> target type: {target_type}")
            if target_type == 'ref':
                xrefs_pointing_to_ref += 1
        
        # Check ref-list
        ref_list = root.find('.//back/ref-list')
        if ref_list is not None:
            refs = ref_list.findall('.//ref')
            print(f"ref elements in ref-list: {len(refs)}")
            for ref in refs:
                ref_id = ref.get('id', 'NONE')
                citation = ref.find('.//mixed-citation')
                citation_text = citation.text[:50] if citation is not None and citation.text else "NONE"
                print(f"  ref id='{ref_id}': {citation_text}...")
        else:
            print("ref-list: NOT FOUND")
        
        named_content_elements = root.findall('.//named-content[@content-type="anchor"]')
        print(f"named-content[@content-type='anchor'] elements: {len(named_content_elements)}")
        
        # Verify results
        print("\nVERIFICATION:")
        print("-" * 70)
        
        success = True
        
        if tex_math_fixed == len(tex_math_elements) and len(tex_math_elements) > 0:
            print("✓ All tex-math elements have id attributes")
        else:
            print(f"✗ tex-math fix incomplete: {tex_math_fixed}/{len(tex_math_elements)}")
            success = False
        
        if mml_math_fixed == len(mml_math_elements) and len(mml_math_elements) > 0:
            print("✓ All mml:math elements have id attributes")
        else:
            print(f"✗ mml:math fix incomplete: {mml_math_fixed}/{len(mml_math_elements)}")
            success = False
        
        if xrefs_pointing_to_ref == len(bibr_xrefs) and len(bibr_xrefs) > 0:
            print("✓ All bibr xrefs now point to ref elements")
        else:
            print(f"✗ xref fix incomplete: {xrefs_pointing_to_ref}/{len(bibr_xrefs)}")
            success = False
        
        if len(named_content_elements) == 0:
            print("✓ All named-content anchor elements removed")
        else:
            print(f"✗ named-content removal incomplete: {len(named_content_elements)} remaining")
            success = False
        
        if success:
            print("\n" + "=" * 70)
            print("✓ ALL TESTS PASSED")
            print("=" * 70)
            return 0
        else:
            print("\n" + "=" * 70)
            print("✗ SOME TESTS FAILED")
            print("=" * 70)
            return 1
    
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"\n✓ Cleaned up test directory")


if __name__ == '__main__':
    sys.exit(test_dtd_fixes())
