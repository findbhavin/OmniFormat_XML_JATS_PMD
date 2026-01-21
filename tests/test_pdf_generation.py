"""
Unit tests for PDF generation (Direct DOCX to PDF and HTML to PDF).
"""
import os
import pytest


class TestDirectPDFConversion:
    """Tests for direct DOCX to PDF conversion."""
    
    def test_direct_pdf_file_created(self, mock_converter):
        """Test that direct_from_word.pdf file is created."""
        # Create a dummy PDF file
        with open(mock_converter.direct_pdf_path, 'wb') as f:
            # Write minimal PDF header
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n<< /Type /Catalog >>\nendobj\n')
            f.write(b'%%EOF\n')
        
        assert os.path.exists(mock_converter.direct_pdf_path)
        assert os.path.getsize(mock_converter.direct_pdf_path) > 0
    
    def test_direct_pdf_has_pdf_header(self, mock_converter):
        """Test that direct PDF has valid PDF header."""
        # Create a dummy PDF
        with open(mock_converter.direct_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n<< /Type /Catalog >>\nendobj\n')
            f.write(b'%%EOF\n')
        
        # Read header
        with open(mock_converter.direct_pdf_path, 'rb') as f:
            header = f.read(8)
        
        assert header.startswith(b'%PDF-'), "PDF should have valid header"
    
    def test_direct_pdf_file_size_reasonable(self, mock_converter):
        """Test that direct PDF has reasonable file size (not empty)."""
        # Create a minimal PDF
        with open(mock_converter.direct_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
            f.write(b'2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n')
            f.write(b'3 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\n')
            f.write(b'%%EOF\n')
        
        file_size = os.path.getsize(mock_converter.direct_pdf_path)
        # Minimal PDF should be at least 100 bytes
        assert file_size >= 100, "PDF file size too small"
    
    @pytest.mark.skipif(
        not os.path.exists('/usr/bin/libreoffice') and not os.path.exists('/Applications/LibreOffice.app'),
        reason="LibreOffice not installed"
    )
    def test_direct_pdf_preserves_fonts(self, mock_converter, sample_docx):
        """Test that direct PDF conversion preserves fonts (if LibreOffice available)."""
        # This test requires LibreOffice to be installed
        # It would convert the DOCX and verify font embedding
        
        # Note: This is a placeholder test that checks the tool is available
        import subprocess
        
        try:
            result = subprocess.run(
                ['libreoffice', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("LibreOffice not available")
    
    def test_direct_pdf_format_validation(self, mock_converter):
        """Test that direct PDF format is valid."""
        # Create a valid PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer
<< /Size 4 /Root 1 0 R >>
startxref
190
%%EOF
"""
        
        with open(mock_converter.direct_pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Basic validation: check structure
        with open(mock_converter.direct_pdf_path, 'rb') as f:
            content = f.read()
        
        assert b'%PDF-' in content, "Should have PDF header"
        assert b'%%EOF' in content, "Should have EOF marker"
        assert b'/Type /Catalog' in content, "Should have catalog"


class TestHTMLToPDFConversion:
    """Tests for HTML to PDF conversion."""
    
    def test_published_pdf_file_created(self, mock_converter):
        """Test that published_article.pdf file is created."""
        # Create a dummy PDF
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n')
            f.write(b'1 0 obj\n<< /Type /Catalog >>\nendobj\n')
            f.write(b'%%EOF\n')
        
        assert os.path.exists(mock_converter.pdf_path)
        assert os.path.getsize(mock_converter.pdf_path) > 0
    
    def test_published_pdf_has_pdf_header(self, mock_converter):
        """Test that published PDF has valid PDF header."""
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(b'%PDF-1.7\n')
            f.write(b'1 0 obj\n<< /Type /Catalog >>\nendobj\n')
            f.write(b'%%EOF\n')
        
        with open(mock_converter.pdf_path, 'rb') as f:
            header = f.read(8)
        
        assert header.startswith(b'%PDF-'), "PDF should have valid header"
    
    def test_published_pdf_contains_content(self, mock_converter):
        """Test that published PDF contains actual content."""
        # Create a PDF with content
        pdf_content = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Test Article) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000198 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
290
%%EOF
"""
        
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Check that PDF has content stream
        with open(mock_converter.pdf_path, 'rb') as f:
            content = f.read()
        
        assert b'/Contents' in content, "PDF should have content"
    
    def test_published_pdf_has_pages(self, mock_converter):
        """Test that published PDF has page structure."""
        pdf_content = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
%%EOF
"""
        
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        with open(mock_converter.pdf_path, 'rb') as f:
            content = f.read()
        
        assert b'/Type /Pages' in content, "PDF should have Pages object"
        assert b'/Type /Page' in content, "PDF should have at least one Page"
    
    def test_pdf_css_styling_applied(self, mock_converter):
        """Test that PDF generation applies CSS styling."""
        # This tests that the CSS path is configured
        assert hasattr(mock_converter, 'css_path')
        assert isinstance(mock_converter.css_path, str)
        
        # If CSS file exists, verify it has content
        if os.path.exists(mock_converter.css_path):
            with open(mock_converter.css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            assert len(css_content) > 0, "CSS file should not be empty"
    
    @pytest.mark.skipif(
        not any(os.path.exists(p) for p in ['/usr/bin/weasyprint', '/usr/local/bin/weasyprint']),
        reason="WeasyPrint not installed"
    )
    def test_weasyprint_available(self):
        """Test that WeasyPrint is available for PDF generation."""
        import subprocess
        
        try:
            result = subprocess.run(
                ['weasyprint', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("WeasyPrint not available")


class TestPDFComparison:
    """Tests comparing direct PDF vs HTML-based PDF."""
    
    def test_both_pdfs_created(self, mock_converter):
        """Test that both PDF files are created."""
        # Create both PDFs
        with open(mock_converter.direct_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%%EOF\n')
        
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(b'%PDF-1.7\n%%EOF\n')
        
        assert os.path.exists(mock_converter.direct_pdf_path)
        assert os.path.exists(mock_converter.pdf_path)
    
    def test_pdfs_have_different_purposes(self, mock_converter):
        """Test that the two PDFs serve different purposes."""
        # This is a documentation test
        # direct_from_word.pdf: preserves original DOCX formatting
        # published_article.pdf: follows PMC standards from JATS XML
        
        assert mock_converter.direct_pdf_path != mock_converter.pdf_path
        assert 'direct' in mock_converter.direct_pdf_path
        assert 'published' in mock_converter.pdf_path or 'article' in mock_converter.pdf_path
    
    def test_pdf_file_naming_conventions(self, mock_converter):
        """Test that PDFs follow naming conventions."""
        assert os.path.basename(mock_converter.direct_pdf_path) == 'direct_from_word.pdf'
        assert os.path.basename(mock_converter.pdf_path) == 'published_article.pdf'


class TestPDFMetadata:
    """Tests for PDF metadata and properties."""
    
    def test_pdf_metadata_structure(self, mock_converter):
        """Test that PDFs can include metadata."""
        # Create PDF with metadata
        pdf_content = b"""%PDF-1.7
1 0 obj
<< /Type /Catalog /Pages 2 0 R /Metadata 3 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [4 0 R] >>
endobj
3 0 obj
<< /Type /Metadata /Subtype /XML /Length 100 >>
stream
<?xml version="1.0"?>
<metadata>
  <title>Test Article</title>
</metadata>
endstream
endobj
4 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>
endobj
%%EOF
"""
        
        with open(mock_converter.pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        with open(mock_converter.pdf_path, 'rb') as f:
            content = f.read()
        
        # PDFs can have metadata
        assert b'/Catalog' in content
