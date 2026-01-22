"""
Unit tests for DTD compliance row filtering.

Tests the specific fix for:
1. Replacing 'class' attribute with 'data-dtd-compliance' attribute
2. Filtering DTD compliance rows from HTML output
"""

import pytest
from lxml import etree
from MasterPipeline import HighFidelityConverter
import tempfile
import os


class TestDTDComplianceMarking:
    """Test that DTD compliance rows are properly marked and then stripped."""
    
    def test_post_process_xml_adds_data_attribute(self):
        """Test that _post_process_xml adds tbody for DTD compliance and strips data-* attributes."""
        # Create a minimal XML with a table that has thead but no tbody
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE article PUBLIC "-//NLM//DTD JATS (Z39.96) Journal Publishing DTD v1.3 20210610//EN" "JATS-journalpublishing1-3.dtd">
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article">
  <body>
    <table-wrap>
      <table>
        <thead>
          <tr>
            <th>Header 1</th>
            <th>Header 2</th>
          </tr>
        </thead>
      </table>
    </table-wrap>
  </body>
</article>"""
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = f.name
        
        try:
            # Create converter instance with a dummy docx path
            converter = HighFidelityConverter('/tmp/dummy.docx')
            converter.xml_path = xml_path
            
            # Run post-processing
            converter._post_process_xml()
            
            # Parse the result
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(xml_path, parser)
            root = tree.getroot()
            
            # Find the added tbody and its tr
            tables = root.findall('.//table')
            assert len(tables) > 0, "Should have at least one table"
            
            table = tables[0]
            tbody = table.find('tbody')
            
            # tbody should exist (added for DTD compliance)
            assert tbody is not None, "tbody should be added for DTD compliance"
            
            # Check the tr in tbody
            tbody_rows = tbody.findall('.//tr')
            if len(tbody_rows) > 0:
                # Verify that data-* attributes have been stripped
                tr = tbody_rows[0]
                data_attrs = [attr for attr in tr.attrib if attr.startswith('data-')]
                assert len(data_attrs) == 0, \
                    f"DTD compliance row should have all data-* attributes stripped, found: {data_attrs}"
                
                # Should NOT have class attribute
                assert tr.get('class') is None, \
                    "DTD compliance row should NOT have 'class' attribute (not allowed by DTD)"
                
        finally:
            # Cleanup
            if os.path.exists(xml_path):
                os.unlink(xml_path)


class TestDTDComplianceFiltering:
    """Test that DTD compliance rows are filtered from HTML."""
    
    def test_rebuild_table_section_filters_compliance_rows(self):
        """Test that _rebuild_table_section filters out rows with data-dtd-compliance."""
        # Create XML table with a compliance row
        xml_content = """<tbody>
  <tr data-dtd-compliance="true">
    <td></td>
  </tr>
  <tr>
    <td>Real content</td>
  </tr>
</tbody>"""
        
        parser = etree.XMLParser(remove_blank_text=True)
        xml_tbody = etree.fromstring(xml_content, parser)
        
        # Create HTML tbody element
        html_tbody = etree.Element('tbody')
        
        # Create converter instance
        converter = HighFidelityConverter('/tmp/dummy.docx')
        
        # Call the method
        converter._rebuild_table_section(xml_tbody, html_tbody)
        
        # Check results
        html_rows = html_tbody.findall('.//tr')
        
        # Should only have 1 row (the real content, not the compliance row)
        assert len(html_rows) == 1, \
            f"Expected 1 row in HTML, got {len(html_rows)}"
        
        # The remaining row should have the real content
        cells = html_rows[0].findall('.//td')
        assert len(cells) == 1, "Should have 1 cell"
        assert cells[0].text == 'Real content', "Should have the real content cell"
    
    def test_rebuild_table_section_filters_empty_single_cell_rows(self):
        """Test that _rebuild_table_section filters out empty single-cell rows."""
        # Create XML table with an empty single-cell row
        xml_content = """<tbody>
  <tr>
    <td></td>
  </tr>
  <tr>
    <td>Real content</td>
  </tr>
</tbody>"""
        
        parser = etree.XMLParser(remove_blank_text=True)
        xml_tbody = etree.fromstring(xml_content, parser)
        
        # Create HTML tbody element
        html_tbody = etree.Element('tbody')
        
        # Create converter instance
        converter = HighFidelityConverter('/tmp/dummy.docx')
        
        # Call the method
        converter._rebuild_table_section(xml_tbody, html_tbody)
        
        # Check results
        html_rows = html_tbody.findall('.//tr')
        
        # Should only have 1 row (the real content, not the empty row)
        assert len(html_rows) == 1, \
            f"Expected 1 row in HTML, got {len(html_rows)}"
        
        # The remaining row should have the real content
        cells = html_rows[0].findall('.//td')
        assert len(cells) == 1, "Should have 1 cell"
        assert cells[0].text == 'Real content', "Should have the real content cell"
    
    def test_rebuild_table_section_keeps_multi_cell_empty_rows(self):
        """Test that _rebuild_table_section keeps empty rows with multiple cells."""
        # Create XML table with an empty multi-cell row (not a compliance row)
        xml_content = """<tbody>
  <tr>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>Content 1</td>
    <td>Content 2</td>
  </tr>
</tbody>"""
        
        parser = etree.XMLParser(remove_blank_text=True)
        xml_tbody = etree.fromstring(xml_content, parser)
        
        # Create HTML tbody element
        html_tbody = etree.Element('tbody')
        
        # Create converter instance
        converter = HighFidelityConverter('/tmp/dummy.docx')
        
        # Call the method
        converter._rebuild_table_section(xml_tbody, html_tbody)
        
        # Check results
        html_rows = html_tbody.findall('.//tr')
        
        # Should have both rows (empty multi-cell rows might be intentional)
        assert len(html_rows) == 2, \
            f"Expected 2 rows in HTML, got {len(html_rows)}"
    
    def test_rebuild_table_section_keeps_single_cell_with_content(self):
        """Test that _rebuild_table_section keeps single-cell rows with content."""
        # Create XML table with a single-cell row with content
        xml_content = """<tbody>
  <tr>
    <td>Single cell with content</td>
  </tr>
  <tr>
    <td>Another row</td>
  </tr>
</tbody>"""
        
        parser = etree.XMLParser(remove_blank_text=True)
        xml_tbody = etree.fromstring(xml_content, parser)
        
        # Create HTML tbody element
        html_tbody = etree.Element('tbody')
        
        # Create converter instance
        converter = HighFidelityConverter('/tmp/dummy.docx')
        
        # Call the method
        converter._rebuild_table_section(xml_tbody, html_tbody)
        
        # Check results
        html_rows = html_tbody.findall('.//tr')
        
        # Should have both rows
        assert len(html_rows) == 2, \
            f"Expected 2 rows in HTML, got {len(html_rows)}"
        
        # First row should have the single cell with content
        cells = html_rows[0].findall('.//td')
        assert len(cells) == 1, "Should have 1 cell"
        assert cells[0].text == 'Single cell with content', "Should have the content"
