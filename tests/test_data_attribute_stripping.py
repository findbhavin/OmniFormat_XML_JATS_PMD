"""
Unit tests for stripping data-* attributes from XML for DTD/XSD validation.

Tests the specific fix for:
1. Stripping data-compliance attributes
2. Stripping data-dtd-compliance attributes
3. Stripping any other data-* attributes
4. Ensuring clean XML for DTD/XSD validation
"""

import pytest
from lxml import etree
from MasterPipeline import HighFidelityConverter
import tempfile
import os


class TestDataAttributeStripping:
    """Test that data-* attributes are properly stripped from XML."""
    
    def test_post_process_xml_strips_data_dtd_compliance(self):
        """Test that _post_process_xml strips data-dtd-compliance attributes."""
        # Create a minimal XML with data-dtd-compliance attribute
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
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
        <tbody>
          <tr data-dtd-compliance="true">
            <td></td>
            <td></td>
          </tr>
        </tbody>
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
            converter = HighFidelityConverter(os.path.join(tempfile.gettempdir(), 'dummy.docx'))
            converter.xml_path = xml_path
            
            # Run post-processing
            converter._post_process_xml()
            
            # Parse the result
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(xml_path, parser)
            root = tree.getroot()
            
            # Find all tr elements and verify they have no data-* attributes
            for tr in root.findall('.//tr'):
                data_attrs = [attr for attr in tr.attrib if attr.startswith('data-')]
                assert len(data_attrs) == 0, \
                    f"Found data-* attributes that should have been stripped: {data_attrs}"
                
        finally:
            # Cleanup
            if os.path.exists(xml_path):
                os.unlink(xml_path)
    
    def test_post_process_xml_strips_data_compliance(self):
        """Test that _post_process_xml strips data-compliance attributes."""
        # Create a minimal XML with data-compliance attribute
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id" data-compliance="true">test-journal</journal-id>
    </journal-meta>
    <article-meta>
      <title-group>
        <article-title>Test Article</article-title>
      </title-group>
      <abstract data-compliance="true">
        <p data-compliance="true">This abstract was added for PMC compliance.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <p>Body content</p>
  </body>
</article>"""
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            xml_path = f.name
        
        try:
            # Create converter instance with a dummy docx path
            converter = HighFidelityConverter(os.path.join(tempfile.gettempdir(), 'dummy.docx'))
            converter.xml_path = xml_path
            
            # Run post-processing
            converter._post_process_xml()
            
            # Parse the result
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(xml_path, parser)
            root = tree.getroot()
            
            # Verify no elements have data-* attributes
            elements_with_data_attrs = []
            for elem in root.iter():
                data_attrs = [attr for attr in elem.attrib if attr.startswith('data-')]
                if data_attrs:
                    elements_with_data_attrs.append((elem.tag, data_attrs))
            
            assert len(elements_with_data_attrs) == 0, \
                f"Found elements with data-* attributes that should have been stripped: {elements_with_data_attrs}"
                
        finally:
            # Cleanup
            if os.path.exists(xml_path):
                os.unlink(xml_path)
    
    def test_post_process_xml_strips_all_data_attributes(self):
        """Test that _post_process_xml strips all data-* attributes."""
        # Create XML with various data-* attributes
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article">
  <body>
    <p data-custom="test" data-foo="bar" data-test="value">Test paragraph</p>
    <table-wrap>
      <table data-dtd-compliance="true" data-compliance="true">
        <tbody>
          <tr data-row-id="1" data-dtd-compliance="true">
            <td data-cell-id="a">Content</td>
          </tr>
        </tbody>
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
            converter = HighFidelityConverter(os.path.join(tempfile.gettempdir(), 'dummy.docx'))
            converter.xml_path = xml_path
            
            # Run post-processing
            converter._post_process_xml()
            
            # Parse the result
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(xml_path, parser)
            root = tree.getroot()
            
            # Count total elements and those with data-* attributes
            total_elements = sum(1 for _ in root.iter())
            elements_with_data_attrs = []
            
            for elem in root.iter():
                data_attrs = [attr for attr in elem.attrib if attr.startswith('data-')]
                if data_attrs:
                    elements_with_data_attrs.append((elem.tag, data_attrs))
            
            # Verify no elements have any data-* attributes
            assert len(elements_with_data_attrs) == 0, \
                f"Found {len(elements_with_data_attrs)} elements with data-* attributes: {elements_with_data_attrs}"
            
            # Verify we still have elements (not empty document)
            assert total_elements > 0, "Document should not be empty"
                
        finally:
            # Cleanup
            if os.path.exists(xml_path):
                os.unlink(xml_path)
    
    def test_post_process_xml_preserves_non_data_attributes(self):
        """Test that _post_process_xml preserves all non-data-* attributes."""
        # Create XML with normal attributes and data-* attributes
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" article-type="research-article" dtd-version="1.3">
  <body>
    <table-wrap id="table1" position="float">
      <table>
        <tbody>
          <tr data-dtd-compliance="true">
            <td colspan="2" rowspan="1">Content</td>
          </tr>
        </tbody>
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
            converter = HighFidelityConverter(os.path.join(tempfile.gettempdir(), 'dummy.docx'))
            converter.xml_path = xml_path
            
            # Run post-processing
            converter._post_process_xml()
            
            # Parse the result
            parser = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
            tree = etree.parse(xml_path, parser)
            root = tree.getroot()
            
            # Verify article-type and dtd-version are preserved
            assert root.get('article-type') == 'research-article', \
                "article-type attribute should be preserved"
            assert root.get('dtd-version') is not None, \
                "dtd-version attribute should be preserved"
            
            # Verify table-wrap attributes are preserved
            table_wrap = root.find('.//table-wrap')
            assert table_wrap is not None, "table-wrap should exist"
            assert table_wrap.get('id') == 'table1', \
                "id attribute should be preserved"
            assert table_wrap.get('position') == 'float', \
                "position attribute should be preserved"
            
            # Verify td attributes are preserved
            td = root.find('.//td')
            assert td is not None, "td should exist"
            assert td.get('colspan') == '2', \
                "colspan attribute should be preserved"
            assert td.get('rowspan') == '1', \
                "rowspan attribute should be preserved"
            
            # Verify no data-* attributes remain
            for elem in root.iter():
                data_attrs = [attr for attr in elem.attrib if attr.startswith('data-')]
                assert len(data_attrs) == 0, \
                    f"Found data-* attributes on {elem.tag}: {data_attrs}"
                
        finally:
            # Cleanup
            if os.path.exists(xml_path):
                os.unlink(xml_path)
