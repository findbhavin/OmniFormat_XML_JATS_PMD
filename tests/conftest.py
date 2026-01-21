"""
Pytest configuration and shared fixtures for pipeline tests.
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def sample_docx():
    """
    Returns path to a sample DOCX file for testing.
    If no real DOCX exists, creates a minimal test file.
    """
    # Check if there's a sample DOCX in the repo
    repo_root = Path(__file__).parent.parent
    sample_files = list(repo_root.glob("*.docx"))
    
    if sample_files:
        # Real DOCX found, no cleanup needed
        yield str(sample_files[0])
        return
    
    # Create a minimal DOCX-like file for testing
    temp_dir = tempfile.mkdtemp()
    temp_docx = os.path.join(temp_dir, "test_sample.docx")
    
    # Create a minimal ZIP structure (DOCX is a ZIP)
    import zipfile
    with zipfile.ZipFile(temp_docx, 'w') as docx:
        # Add minimal required files
        docx.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        docx.writestr('word/document.xml', '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Test Document</w:t></w:r></w:p></w:body></w:document>')
    
    yield temp_docx
    
    # Cleanup
    try:
        shutil.rmtree(temp_dir)
    except:
        pass


@pytest.fixture
def sample_jats_xml():
    """
    Returns a sample JATS XML content string for testing.
    """
    return """<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink" 
         xmlns:mml="http://www.w3.org/1998/Math/MathML"
         dtd-version="1.3" 
         article-type="research-article">
  <front>
    <journal-meta>
      <journal-id journal-id-type="publisher-id">test-journal</journal-id>
      <journal-title-group>
        <journal-title>Test Journal</journal-title>
      </journal-title-group>
    </journal-meta>
    <article-meta>
      <title-group>
        <article-title>Test Article Title</article-title>
      </title-group>
      <contrib-group>
        <contrib contrib-type="author">
          <name>
            <surname>Doe</surname>
            <given-names>John</given-names>
          </name>
        </contrib>
      </contrib-group>
      <abstract>
        <p>This is a test abstract.</p>
      </abstract>
    </article-meta>
  </front>
  <body>
    <sec id="sec1">
      <title>Introduction</title>
      <p>This is the introduction section.</p>
    </sec>
  </body>
  <back>
    <ref-list>
      <ref id="ref1">
        <element-citation publication-type="journal">
          <person-group person-group-type="author">
            <name>
              <surname>Smith</surname>
              <given-names>J</given-names>
            </name>
          </person-group>
          <article-title>Sample Article</article-title>
          <source>Journal Name</source>
          <year>2020</year>
        </element-citation>
      </ref>
    </ref-list>
  </back>
</article>
"""


@pytest.fixture
def temp_output_dir():
    """
    Creates a temporary directory for test outputs.
    """
    temp_dir = tempfile.mkdtemp(prefix="test_output_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_converter(sample_docx, temp_output_dir):
    """
    Creates a HighFidelityConverter instance with mocked output directory.
    """
    # Import here to avoid issues if MasterPipeline has initialization side effects
    from MasterPipeline import HighFidelityConverter
    
    # Create converter - don't mock class attributes, just create instance
    converter = HighFidelityConverter(sample_docx)
    
    # Override instance attributes to use temp directory
    converter.output_dir = temp_output_dir
    converter.media_dir = os.path.join(temp_output_dir, "media")
    converter.xml_path = os.path.join(temp_output_dir, "article.xml")
    converter.xml_dtd_path = os.path.join(temp_output_dir, "articledtd.xml")
    converter.html_path = os.path.join(temp_output_dir, "article.html")
    converter.pdf_path = os.path.join(temp_output_dir, "published_article.pdf")
    converter.direct_pdf_path = os.path.join(temp_output_dir, "direct_from_word.pdf")
    
    # Create directories
    os.makedirs(temp_output_dir, exist_ok=True)
    os.makedirs(converter.media_dir, exist_ok=True)
    
    return converter


@pytest.fixture
def xsd_schema_path():
    """
    Returns path to the JATS XSD schema file.
    """
    repo_root = Path(__file__).parent.parent
    xsd_path = repo_root / "JATS-journalpublishing-oasis-article1-3-mathml2.xsd"
    
    if xsd_path.exists():
        return str(xsd_path)
    
    # If schema doesn't exist, skip tests that require it
    pytest.skip("JATS XSD schema not found")


@pytest.fixture
def pmc_stylechecker_path():
    """
    Returns path to the PMC Style Checker directory.
    """
    repo_root = Path(__file__).parent.parent
    pmc_path = repo_root / "pmc-stylechecker"
    
    if pmc_path.exists():
        return str(pmc_path)
    
    # If PMC Style Checker doesn't exist, skip tests that require it
    pytest.skip("PMC Style Checker not found")
