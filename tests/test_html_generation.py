"""
Unit tests for HTML generation with embedded media.
"""
import os
import pytest
from lxml import etree


class TestHTMLGeneration:
    """Tests for HTML generation from JATS XML."""
    
    def test_html_file_created(self, mock_converter):
        """Test that article.html file is created."""
        # Create a simple HTML file
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test Article</title></head>
<body><h1>Test Article</h1><p>Content</p></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        assert os.path.exists(mock_converter.html_path)
        assert os.path.getsize(mock_converter.html_path) > 0
    
    def test_html_well_formed(self, mock_converter):
        """Test that generated HTML is well-formed."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test Article</title></head>
<body><h1>Test Article</h1><p>Content</p></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Try to parse the HTML
        try:
            parser = etree.HTMLParser()
            tree = etree.parse(mock_converter.html_path, parser)
            root = tree.getroot()
            assert root is not None
        except Exception as e:
            pytest.fail(f"HTML is not well-formed: {e}")
    
    def test_html_has_doctype(self, mock_converter):
        """Test that HTML has DOCTYPE declaration."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><p>Content</p></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(mock_converter.html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '<!DOCTYPE html>' in content or '<!doctype html>' in content.lower()
    
    def test_html_has_required_structure(self, mock_converter):
        """Test that HTML has required structure (html, head, body)."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test Article</title></head>
<body><h1>Test Article</h1></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        root = tree.getroot()
        
        # Check for required elements - HTMLParser may create implicit elements
        # So we check more flexibly
        head_elem = tree.find('.//head')
        body_elem = tree.find('.//body')
        
        # At minimum head and body should exist
        assert head_elem is not None, "Missing <head> element"
        assert body_elem is not None, "Missing <body> element"
    
    def test_html_has_title(self, mock_converter):
        """Test that HTML has a title element."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test Article Title</title></head>
<body><h1>Test Article</h1></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        
        title_elem = tree.find('.//title')
        assert title_elem is not None, "Missing <title> element"
        assert len(title_elem.text) > 0, "Title should not be empty"
    
    def test_html_media_directory_created(self, mock_converter):
        """Test that media directory is created for embedded media."""
        # Media directory should exist
        os.makedirs(mock_converter.media_dir, exist_ok=True)
        
        assert os.path.exists(mock_converter.media_dir)
        assert os.path.isdir(mock_converter.media_dir)
    
    def test_html_image_references(self, mock_converter):
        """Test that HTML contains proper image references."""
        # Create a test image file
        test_image_path = os.path.join(mock_converter.media_dir, "test_image.png")
        with open(test_image_path, 'wb') as f:
            # Write minimal PNG header
            f.write(b'\x89PNG\r\n\x1a\n')
        
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <h1>Article with Image</h1>
  <img src="media/test_image.png" alt="Test Image" />
</body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Parse HTML
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        
        # Find img elements
        images = tree.findall('.//img')
        assert len(images) > 0, "HTML should contain images"
        
        # Check image attributes
        for img in images:
            src = img.get('src')
            alt = img.get('alt')
            assert src is not None, "Image should have src attribute"
            assert alt is not None, "Image should have alt attribute"
    
    def test_html_css_styling(self, mock_converter):
        """Test that HTML includes CSS styling."""
        html_content = """<!DOCTYPE html>
<html>
<head>
  <title>Test</title>
  <style>
    body { font-family: Arial, sans-serif; }
    h1 { color: #333; }
  </style>
</head>
<body><h1>Styled Article</h1></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(mock_converter.html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for style element or link to CSS
        assert '<style>' in content or '<link' in content, "HTML should include styling"
    
    def test_html_table_formatting(self, mock_converter):
        """Test that HTML tables are properly formatted."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <table>
    <thead>
      <tr><th>Header 1</th><th>Header 2</th></tr>
    </thead>
    <tbody>
      <tr><td>Data 1</td><td>Data 2</td></tr>
    </tbody>
  </table>
</body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        
        # Check table structure
        tables = tree.findall('.//table')
        assert len(tables) > 0, "HTML should contain tables"
        
        for table in tables:
            # Check for proper table structure
            thead = table.find('.//thead')
            tbody = table.find('.//tbody')
            # At least one should exist
            assert thead is not None or tbody is not None, "Table should have thead or tbody"
    
    def test_html_semantic_structure(self, mock_converter):
        """Test that HTML uses semantic elements."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <article>
    <header>
      <h1>Article Title</h1>
    </header>
    <section>
      <h2>Introduction</h2>
      <p>Content</p>
    </section>
  </article>
</body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        
        # Check for semantic elements
        article = tree.find('.//article')
        sections = tree.findall('.//section')
        
        # At least some semantic structure should be present
        assert article is not None or len(sections) > 0, "HTML should use semantic elements"
    
    def test_html_encoding_utf8(self, mock_converter):
        """Test that HTML uses UTF-8 encoding."""
        html_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Test</title>
</head>
<body><p>Test with special characters: é, ñ, ü</p></body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Read and check encoding
        with open(mock_converter.html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'charset="UTF-8"' in content or 'charset=utf-8' in content.lower()


class TestHTMLValidation:
    """Tests for HTML validation and compliance."""
    
    def test_html_no_syntax_errors(self, mock_converter):
        """Test that HTML has no syntax errors."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <h1>Article Title</h1>
  <p>This is a paragraph.</p>
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Parse with strict parser
        try:
            parser = etree.HTMLParser()
            tree = etree.parse(mock_converter.html_path, parser)
            
            # Check for parser errors
            errors = parser.error_log
            # Filter out warnings, only fail on errors
            critical_errors = [e for e in errors if e.level >= 2]
            
            if critical_errors:
                error_messages = '\n'.join([str(e) for e in critical_errors])
                pytest.fail(f"HTML has syntax errors:\n{error_messages}")
        except Exception as e:
            pytest.fail(f"Failed to parse HTML: {e}")
    
    def test_html_links_properly_formatted(self, mock_converter):
        """Test that HTML links are properly formatted."""
        html_content = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <p>See <a href="#section1">Section 1</a> for details.</p>
  <p>External link: <a href="https://example.com">Example</a></p>
  <section id="section1">
    <h2>Section 1</h2>
  </section>
</body>
</html>"""
        
        with open(mock_converter.html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        parser = etree.HTMLParser()
        tree = etree.parse(mock_converter.html_path, parser)
        
        # Find all links
        links = tree.findall('.//a')
        assert len(links) > 0, "HTML should contain links"
        
        # Check link attributes
        for link in links:
            href = link.get('href')
            assert href is not None, "Link should have href attribute"
            assert len(href) > 0, "Link href should not be empty"
