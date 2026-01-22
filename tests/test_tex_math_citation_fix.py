"""
Unit tests for tex-math citation conversion fix.

Tests the conversion of problematic tex-math elements containing citation
superscripts to proper PMC-compliant xref elements.
"""
import os
import pytest
from lxml import etree


class TestTexMathCitationFix:
    """Tests for tex-math citation conversion to xref elements."""
    
    def test_single_citation_conversion(self, mock_converter):
        """Test conversion of single citation tex-math to xref."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">^{5}</tex-math> with citation.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was removed
        tex_math = root.find('.//tex-math')
        assert tex_math is None, "tex-math should be removed"
        
        # Verify xref was created
        xref = root.find('.//xref[@ref-type="bibr"]')
        assert xref is not None, "xref should be created"
        assert xref.get('rid') == 'ref5', "xref rid should be ref5"
        assert xref.text == '5', "xref text should be 5"
        
        # Verify xref is in sup element
        sup = root.find('.//sup')
        assert sup is not None, "sup element should exist"
        assert sup.find('.//xref') is not None, "xref should be in sup"
        
        # Verify ref was created in ref-list
        ref = root.find('.//ref[@id="ref5"]')
        assert ref is not None, "ref element should be created"
    
    def test_multiple_citations_conversion(self, mock_converter):
        """Test conversion of multiple citations tex-math to xref."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">^{5,6}</tex-math> with citations.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was removed
        tex_math = root.find('.//tex-math')
        assert tex_math is None, "tex-math should be removed"
        
        # Verify multiple xrefs were created
        xrefs = root.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) == 2, "Two xrefs should be created"
        
        # Verify xref attributes
        assert xrefs[0].get('rid') == 'ref5', "First xref rid should be ref5"
        assert xrefs[0].text == '5', "First xref text should be 5"
        assert xrefs[1].get('rid') == 'ref6', "Second xref rid should be ref6"
        assert xrefs[1].text == '6', "Second xref text should be 6"
        
        # Verify refs were created
        ref5 = root.find('.//ref[@id="ref5"]')
        ref6 = root.find('.//ref[@id="ref6"]')
        assert ref5 is not None, "ref5 should be created"
        assert ref6 is not None, "ref6 should be created"
    
    def test_range_citations_conversion(self, mock_converter):
        """Test conversion of range citations tex-math to xref."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">^{1-3}</tex-math> with range.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was removed
        tex_math = root.find('.//tex-math')
        assert tex_math is None, "tex-math should be removed"
        
        # Verify xrefs were created for range
        xrefs = root.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) == 3, "Three xrefs should be created for range 1-3"
        
        # Verify xref attributes
        assert xrefs[0].get('rid') == 'ref1', "First xref rid should be ref1"
        assert xrefs[1].get('rid') == 'ref2', "Second xref rid should be ref2"
        assert xrefs[2].get('rid') == 'ref3', "Third xref rid should be ref3"
    
    def test_leading_punctuation_preserved(self, mock_converter):
        """Test that leading punctuation is preserved."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">.^{5,6}</tex-math> with punctuation.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was removed
        tex_math = root.find('.//tex-math')
        assert tex_math is None, "tex-math should be removed"
        
        # Verify punctuation is preserved in text before sup
        p = root.find('.//p')
        # The leading punctuation should be added to the text before the sup
        assert '.' in etree.tostring(p, encoding='unicode'), "Leading punctuation should be preserved"
    
    def test_valid_math_not_converted(self, mock_converter):
        """Test that valid tex-math with actual math is not converted."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">E = mc^2</tex-math> with formula.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was NOT removed (it's valid math)
        tex_math = root.find('.//tex-math')
        assert tex_math is not None, "Valid tex-math should be kept"
        assert tex_math.text == 'E = mc^2', "tex-math content should be unchanged"
    
    def test_complete_latex_document_not_converted(self, mock_converter):
        """Test that complete LaTeX documents in tex-math are not converted."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>This is a test<tex-math id="texmath1">\\documentclass{article}\\begin{document}x^2\\end{document}</tex-math> with doc.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tex-math was NOT removed (it's a complete document)
        tex_math = root.find('.//tex-math')
        assert tex_math is not None, "Complete LaTeX document should be kept"
    
    def test_multiple_tex_math_elements(self, mock_converter):
        """Test conversion of multiple tex-math elements."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>First citation<tex-math id="texmath1">^{1}</tex-math> and second<tex-math id="texmath2">^{2,3}</tex-math> here.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify all citation tex-math were removed
        tex_math = root.findall('.//tex-math')
        assert len(tex_math) == 0, "All citation tex-math should be removed"
        
        # Verify xrefs were created
        xrefs = root.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) == 3, "Three xrefs should be created (1, 2, 3)"
        
        # Verify refs were created
        for i in range(1, 4):
            ref = root.find(f'.//ref[@id="ref{i}"]')
            assert ref is not None, f"ref{i} should be created"
    
    def test_existing_refs_not_duplicated(self, mock_converter):
        """Test that existing refs are not duplicated."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>Citation<tex-math id="texmath1">^{5}</tex-math> here.</p>
  </body>
  <back>
    <ref-list>
      <ref id="ref5">
        <mixed-citation>Existing Reference 5</mixed-citation>
      </ref>
    </ref-list>
  </back>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify ref5 exists and was not duplicated
        refs = root.findall('.//ref[@id="ref5"]')
        assert len(refs) == 1, "ref5 should not be duplicated"
        
        # Verify the existing ref content is preserved
        mixed_citation = refs[0].find('.//mixed-citation')
        assert 'Existing Reference 5' in mixed_citation.text, "Existing ref content should be preserved"
    
    def test_tail_text_preserved(self, mock_converter):
        """Test that tail text after tex-math is preserved."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>Citation<tex-math id="texmath1">^{5}</tex-math> with tail text.</p>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify tail text is preserved
        p = root.find('.//p')
        p_text = ''.join(p.itertext())
        assert 'with tail text' in p_text, "Tail text should be preserved"
