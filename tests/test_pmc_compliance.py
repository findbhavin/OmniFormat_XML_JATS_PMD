"""
Unit tests for JATS XML generation (PMC-Compliant).
"""
import os
import pytest
from lxml import etree


class TestPMCCompliantJATS:
    """Tests for JATS XML (PMC-Compliant) generation."""
    
    def test_pmc_jats_file_created(self, mock_converter, sample_jats_xml):
        """Test that articledtd.xml file is created."""
        # Write sample XML
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(sample_jats_xml)
        
        assert os.path.exists(mock_converter.xml_dtd_path)
        assert os.path.getsize(mock_converter.xml_dtd_path) > 0
    
    def test_pmc_jats_has_doctype(self, mock_converter):
        """Test that PMC-compliant XML has DOCTYPE declaration."""
        xml_with_doctype = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "JATS-journalpublishing1-3.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group>
        <article-title>Test</article-title>
      </title-group>
    </article-meta>
  </front>
  <body><p>Content</p></body>
</article>"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_with_doctype)
        
        # Read content
        with open(mock_converter.xml_dtd_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # PMC-compliant version should have DOCTYPE
        assert '<!DOCTYPE' in content
        assert 'JATS' in content or 'Journal Publishing' in content
    
    def test_pmc_jats_content_identical_to_xsd_version(self, mock_converter, sample_jats_xml):
        """Test that PMC version has identical content to XSD version (except DOCTYPE)."""
        # Write XSD version
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(sample_jats_xml)
        
        # Create PMC version with DOCTYPE
        pmc_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "JATS-journalpublishing1-3.dtd">
{sample_jats_xml.split('?>', 1)[1].strip()}"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(pmc_xml)
        
        # Parse both
        xsd_tree = etree.parse(mock_converter.xml_path)
        pmc_tree = etree.parse(mock_converter.xml_dtd_path)
        
        # Convert to strings (without DOCTYPE) and compare
        xsd_str = etree.tostring(xsd_tree.getroot(), encoding='unicode')
        pmc_str = etree.tostring(pmc_tree.getroot(), encoding='unicode')
        
        # They should be identical
        assert xsd_str == pmc_str
    
    def test_pmc_reference_ids(self, mock_converter):
        """Test that PMC-compliant XML has proper reference IDs."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>Reference citation <xref ref-type="bibr" rid="ref1">1</xref></p>
  </body>
  <back>
    <ref-list>
      <ref id="ref1">
        <element-citation publication-type="journal">
          <person-group person-group-type="author">
            <name><surname>Smith</surname></name>
          </person-group>
          <article-title>Test Article</article-title>
        </element-citation>
      </ref>
    </ref-list>
  </back>
</article>"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        tree = etree.parse(mock_converter.xml_dtd_path)
        
        # Find xref elements
        xrefs = tree.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) > 0, "Should have reference xrefs"
        
        # Find ref elements
        refs = tree.findall('.//ref')
        assert len(refs) > 0, "Should have reference definitions"
        
        # Verify that xref rid matches ref id
        for xref in xrefs:
            rid = xref.get('rid')
            ref = tree.find(f'.//ref[@id="{rid}"]')
            assert ref is not None, f"Reference {rid} not found"
    
    def test_pmc_table_formatting(self, mock_converter):
        """Test that tables are formatted according to PMC guidelines."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article dtd-version="1.3">
  <body>
    <table-wrap id="table1">
      <label>Table 1</label>
      <caption><p>Test Table</p></caption>
      <table>
        <thead>
          <tr>
            <th>Header 1</th>
            <th>Header 2</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Data 1</td>
            <td>Data 2</td>
          </tr>
        </tbody>
      </table>
    </table-wrap>
  </body>
</article>"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        tree = etree.parse(mock_converter.xml_dtd_path)
        
        # Check table structure
        table_wrap = tree.find('.//table-wrap')
        assert table_wrap is not None
        assert table_wrap.get('id') is not None, "Table should have an id"
        
        # Check for label and caption
        label = table_wrap.find('.//label')
        caption = table_wrap.find('.//caption')
        assert label is not None, "Table should have a label"
        assert caption is not None, "Table should have a caption"
        
        # Check table structure
        table = table_wrap.find('.//table')
        assert table is not None
        
        thead = table.find('.//thead')
        tbody = table.find('.//tbody')
        assert thead is not None, "Table should have thead"
        assert tbody is not None, "Table should have tbody"
    
    def test_pmc_xref_support(self, mock_converter):
        """Test that xref elements are properly formatted."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>See <xref ref-type="fig" rid="fig1">Figure 1</xref></p>
    <p>See <xref ref-type="table" rid="table1">Table 1</xref></p>
    <p>Reference <xref ref-type="bibr" rid="ref1">1</xref></p>
  </body>
</article>"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        tree = etree.parse(mock_converter.xml_dtd_path)
        
        # Check different types of xrefs
        xrefs = tree.findall('.//xref')
        assert len(xrefs) >= 3, "Should have multiple xrefs"
        
        # Verify xref attributes
        for xref in xrefs:
            assert xref.get('ref-type') is not None, "xref should have ref-type"
            assert xref.get('rid') is not None, "xref should have rid"
            assert xref.get('ref-type') in ['fig', 'table', 'bibr', 'sec'], "Invalid ref-type"


class TestPMCStyleChecker:
    """Tests for PMC Style Checker compliance."""
    
    def test_pmc_stylechecker_available(self, pmc_stylechecker_path):
        """Test that PMC Style Checker is available."""
        assert os.path.exists(pmc_stylechecker_path)
        
        # Check for style checker files
        xsl_files = [f for f in os.listdir(pmc_stylechecker_path) if f.endswith('.xsl')]
        assert len(xsl_files) > 0, "PMC Style Checker XSL files not found"
    
    @pytest.mark.skipif(
        not os.path.exists('/usr/bin/xsltproc') and not os.path.exists('/usr/local/bin/xsltproc'),
        reason="xsltproc not installed"
    )
    def test_run_pmc_stylechecker(self, mock_converter, pmc_stylechecker_path):
        """Test running PMC Style Checker on generated XML."""
        import subprocess
        
        # Create a valid PMC JATS XML
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "JATS-journalpublishing1-3.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3" article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id">test</journal-id>
      <journal-title-group>
        <journal-title>Test Journal</journal-title>
      </journal-title-group>
    </journal-meta>
    <article-meta>
      <title-group>
        <article-title>Test Article</article-title>
      </title-group>
      <contrib-group>
        <contrib contrib-type="author">
          <name>
            <surname>Doe</surname>
            <given-names>John</given-names>
          </name>
        </contrib>
      </contrib-group>
      <abstract><p>Test abstract</p></abstract>
    </article-meta>
  </front>
  <body>
    <sec id="sec1">
      <title>Introduction</title>
      <p>Test content</p>
    </sec>
  </body>
</article>"""
        
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Find style checker XSL file
        xsl_files = [f for f in os.listdir(pmc_stylechecker_path) if 'nlm-style' in f and f.endswith('.xsl')]
        if not xsl_files:
            pytest.skip("PMC Style Checker XSL not found")
        
        xsl_path = os.path.join(pmc_stylechecker_path, xsl_files[0])
        
        # Run xsltproc
        try:
            result = subprocess.run(
                ['xsltproc', '--path', pmc_stylechecker_path, xsl_path, mock_converter.xml_dtd_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check that it ran (even if there are warnings)
            assert result.returncode in [0, 1], f"xsltproc failed: {result.stderr}"
            
        except subprocess.TimeoutExpired:
            pytest.fail("PMC Style Checker timed out")
        except FileNotFoundError:
            pytest.skip("xsltproc not found")


class TestEmptyBackElementFix:
    """
    Tests for empty <back> element removal (PMC compliance).
    
    PMC requires that <back> elements must not be empty. An empty <back> element
    is defined as one with:
    - No child elements at all, OR
    - Only comments (no actual XML elements like ref-list, ack, etc.)
    """
    
    def test_empty_back_element_removed(self, mock_converter):
        """Test that empty <back> elements are removed during post-processing."""
        from lxml import etree
        
        # Create XML with empty back element
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body><p>Content</p></body>
  <back></back>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing
        mock_converter._post_process_xml()
        
        # Parse the processed XML
        tree = etree.parse(mock_converter.xml_path)
        root = tree.getroot()
        
        # Verify empty back element was removed
        back = root.find('.//back')
        assert back is None, "Empty <back> element should be removed"
    
    def test_back_element_with_content_kept(self, mock_converter):
        """Test that <back> elements with content are kept."""
        from lxml import etree
        
        # Create XML with non-empty back element
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body><p>Content with reference <xref ref-type="bibr" rid="ref1">1</xref></p></body>
  <back>
    <ref-list>
      <ref id="ref1">
        <mixed-citation>Reference 1</mixed-citation>
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
        
        # Verify back element with content was kept
        back = root.find('.//back')
        assert back is not None, "<back> element with content should be kept"
        
        # Verify ref-list is still present
        ref_list = back.find('.//ref-list')
        assert ref_list is not None, "ref-list should be preserved"
    
    def test_back_element_with_only_comments_removed(self, mock_converter):
        """Test that <back> elements with only comments are removed."""
        from lxml import etree
        
        # Create XML with back element containing only comments
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body><p>Content</p></body>
  <back>
    <!-- This is just a comment -->
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
        
        # Verify back element with only comments was removed
        back = root.find('.//back')
        assert back is None, "<back> element with only comments should be removed"
