"""
Integration test for tex-math citation fix with PMC Style Checker.

This test verifies that the tex-math citation conversion produces
PMC-compliant XML that passes the PMC Style Checker validation.
"""
import os
import pytest
import subprocess
from lxml import etree


class TestTexMathCitationPMCCompliance:
    """Integration tests for PMC Style Checker compliance."""
    
    def test_converted_xml_structure(self, mock_converter):
        """Test that converted citations have correct XML structure."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML" dtd-version="1.3" article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id">test</journal-id>
      <journal-title-group>
        <journal-title>Test Journal</journal-title>
      </journal-title-group>
      <issn pub-type="epub">0000-0000</issn>
      <publisher>
        <publisher-name>Test Publisher</publisher-name>
      </publisher>
    </journal-meta>
    <article-meta>
      <article-categories>
        <subj-group subj-group-type="heading">
          <subject>Research Article</subject>
        </subj-group>
      </article-categories>
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
      <pub-date date-type="pub" publication-format="electronic">
        <year>2024</year>
      </pub-date>
      <elocation-id>e001</elocation-id>
      <abstract>
        <p>Test abstract.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <sec id="sec1">
      <title>Introduction</title>
      <p>Previous work<tex-math id="texmath1">^{5,6}</tex-math> showed results.</p>
    </sec>
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
        
        # Verify structure
        sup = root.find('.//sup')
        assert sup is not None, "sup element should exist"
        
        xrefs = sup.findall('.//xref')
        assert len(xrefs) == 2, "Should have 2 xref elements"
        
        # Verify xref attributes match PMC requirements
        for xref in xrefs:
            assert xref.get('ref-type') == 'bibr', "xref must have ref-type='bibr'"
            assert xref.get('rid') is not None, "xref must have rid attribute"
            assert xref.get('rid').startswith('ref'), "rid should follow ref pattern"
        
        # Verify ref elements exist
        back = root.find('.//back')
        assert back is not None, "back section should exist"
        
        ref_list = back.find('.//ref-list')
        assert ref_list is not None, "ref-list should exist"
        
        refs = ref_list.findall('.//ref')
        assert len(refs) >= 2, "Should have at least 2 ref elements"
        
        # Verify all referenced IDs exist
        for xref in xrefs:
            rid = xref.get('rid')
            ref = ref_list.find(f".//ref[@id='{rid}']")
            assert ref is not None, f"Referenced ref {rid} should exist"
    
    @pytest.mark.skipif(
        not os.path.exists('pmc-stylechecker/pmc_style_checker.xsl'),
        reason="PMC Style Checker not available"
    )
    @pytest.mark.skipif(
        not (os.path.exists('/usr/bin/xsltproc') or os.path.exists('/usr/local/bin/xsltproc')),
        reason="xsltproc not installed"
    )
    def test_pmc_stylechecker_no_texmath_errors(self, mock_converter):
        """Test that PMC Style Checker doesn't report tex-math errors after conversion."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "JATS-journalpublishing1-3.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:mml="http://www.w3.org/1998/Math/MathML" dtd-version="1.3" article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id">test</journal-id>
      <journal-title-group>
        <journal-title>Test Journal</journal-title>
      </journal-title-group>
      <issn pub-type="epub">0000-0000</issn>
      <publisher>
        <publisher-name>Test Publisher</publisher-name>
      </publisher>
    </journal-meta>
    <article-meta>
      <article-categories>
        <subj-group subj-group-type="heading">
          <subject>Research Article</subject>
        </subj-group>
      </article-categories>
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
      <pub-date date-type="pub" publication-format="electronic">
        <year>2024</year>
      </pub-date>
      <elocation-id>e001</elocation-id>
      <abstract>
        <p>Test abstract.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <sec id="sec1">
      <title>Introduction</title>
      <p>Previous work<tex-math id="texmath1">^{5,6}</tex-math> and other studies<tex-math id="texmath2">.^{1-3}</tex-math> showed results.</p>
    </sec>
  </body>
</article>"""
        
        # Write XML file
        with open(mock_converter.xml_dtd_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        # Run post-processing (using xml_path as input)
        import shutil
        shutil.copy(mock_converter.xml_dtd_path, mock_converter.xml_path)
        mock_converter._post_process_xml()
        shutil.copy(mock_converter.xml_path, mock_converter.xml_dtd_path)
        
        # Run PMC Style Checker
        xsl_path = 'pmc-stylechecker/pmc_style_checker.xsl'
        
        try:
            result = subprocess.run(
                ['xsltproc', '--path', 'pmc-stylechecker', xsl_path, mock_converter.xml_dtd_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Check for tex-math related errors
            assert 'tex-math content check' not in output.lower(), \
                "PMC Style Checker should not report tex-math content errors"
            
            # Verify no incomplete LaTeX errors
            assert 'complete latex document' not in output.lower(), \
                "Should not have incomplete LaTeX document errors"
            
            print(f"PMC Style Checker output:\n{output}")
            
        except subprocess.TimeoutExpired:
            pytest.fail("PMC Style Checker timed out")
        except FileNotFoundError:
            pytest.skip("xsltproc not found")
    
    def test_mixed_texmath_citations_and_formulas(self, mock_converter):
        """Test that citations are converted but real formulas are preserved."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>Citations<tex-math id="texmath1">^{5,6}</tex-math> and formula<tex-math id="texmath2">E = mc^2</tex-math> here.</p>
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
        
        # Verify citation was converted
        xrefs = root.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) == 2, "Citation should be converted to xrefs"
        
        # Verify formula was preserved
        tex_math = root.find('.//tex-math')
        assert tex_math is not None, "Valid tex-math should be preserved"
        assert 'mc^2' in (tex_math.text or ''), "Formula content should be unchanged"
    
    def test_problematic_line_515_pattern(self, mock_converter):
        """Test the exact pattern from the problem statement (Line 515)."""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" dtd-version="1.3">
  <front>
    <article-meta>
      <title-group><article-title>Test</article-title></title-group>
    </article-meta>
  </front>
  <body>
    <p>Text here<tex-math id="texmath4">.^{5,6}</tex-math> more text.</p>
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
        tex_math = root.find('.//tex-math[@id="texmath4"]')
        assert tex_math is None, "Problematic tex-math should be removed"
        
        # Verify xrefs were created
        xrefs = root.findall('.//xref[@ref-type="bibr"]')
        assert len(xrefs) == 2, "Should create two xrefs for 5,6"
        
        # Verify leading punctuation was preserved
        p = root.find('.//p')
        p_text = etree.tostring(p, encoding='unicode')
        assert '.' in p_text, "Leading period should be preserved"
        assert '<sup>' in p_text, "Should have sup element"
