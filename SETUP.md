# OmniFormat XML JATS PMD - Environment Setup Guide

This guide provides step-by-step instructions for setting up the development environment for the OmniFormat XML JATS PMD pipeline.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Tool Setup](#tool-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows with WSL2
- **Python**: 3.9 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: 2GB free space

### Required External Tools

#### 1. Pandoc
Pandoc is required for DOCX to JATS XML conversion.

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install pandoc

# macOS
brew install pandoc

# Or download from: https://pandoc.org/installing.html
```

**Verify:**
```bash
pandoc --version
# Should show version 2.11+ or higher
```

#### 2. LibreOffice (Optional, for enhanced DOCX to PDF)
Used for direct DOCX to PDF conversion with font preservation.

**Installation:**
```bash
# Ubuntu/Debian
sudo apt-get install libreoffice

# macOS
brew install --cask libreoffice
```

**Verify:**
```bash
libreoffice --version
```

#### 3. System Libraries for WeasyPrint
WeasyPrint requires several system libraries for PDF generation.

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev python3-pip python3-setuptools \
    python3-wheel python3-cffi libcairo2 libpango-1.0-0 \
    libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

**macOS:**
```bash
brew install cairo pango gdk-pixbuf libffi
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/findbhavin/OmniFormat_XML_JATS_PMD.git
cd OmniFormat_XML_JATS_PMD
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (WSL):
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 4. Install Development Dependencies
```bash
# Install testing and development tools
pip install pytest pytest-cov pytest-mock black flake8 mypy
```

## Tool Setup

### 1. PMC Style Checker
Download and setup the PMC Style Checker for PMC compliance validation.

```bash
# Download PMC Style Checker (if not already present)
cd pmc-stylechecker
bash fetch_pmc_style.sh
cd ..
```

### 2. JATS XSD Schemas
The JATS 1.3 XSD schemas should already be present in the repository:
- `JATS-journalpublishing-oasis-article1-3-mathml2.xsd`
- `JATS-journalpublishing-oasis-article1-3-elements.xsd`
- `standard-modules/` directory

If missing, download from: https://jats.nlm.nih.gov/publishing/

### 3. Google Cloud (Optional, for AI Repair)
If you want to use AI-powered content repair features:

```bash
# Install Google Cloud SDK
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set project
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

## Verification

### 1. Run the Test Suite
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### 2. Run Verification Script
```bash
python tools/verify_functionality.py
```

### 3. Test the Web Interface
```bash
# Start the Flask app
python app.py

# Access in browser: http://localhost:8080
```

### 4. Test the Pipeline Directly
```bash
# Run a conversion
python -c "
from MasterPipeline import HighFidelityConverter
converter = HighFidelityConverter('sample.docx')
converter.run()
"
```

## Environment Variables

Create a `.env` file (optional) for configuration:

```bash
# Google Cloud Configuration (optional)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
PORT=8080

# Logging
LOG_LEVEL=INFO
```

## Docker Setup (Optional)

### Build Docker Image
```bash
docker build -t omnijax-converter .
```

### Run with Docker
```bash
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  omnijax-converter
```

## Troubleshooting

### Issue: Pandoc not found
**Solution:** Ensure Pandoc is installed and in your PATH:
```bash
which pandoc
export PATH=$PATH:/usr/local/bin
```

### Issue: WeasyPrint import errors
**Solution:** Install system dependencies:
```bash
# Ubuntu
sudo apt-get install libcairo2-dev libpango1.0-dev

# Then reinstall
pip install --force-reinstall weasyprint
```

### Issue: PMC Style Checker not working
**Solution:** Ensure xsltproc is installed:
```bash
sudo apt-get install xsltproc
```

### Issue: Font errors in PDF
**Solution:** Install required fonts:
```bash
sudo apt-get install fonts-liberation fonts-dejavu
fc-cache -fv
```

### Issue: Permission denied errors
**Solution:** Check write permissions for output directories:
```bash
chmod -R 755 /tmp/output_files/
```

### Issue: Memory errors during conversion
**Solution:** Increase available memory or reduce batch size.

## Development Workflow

### 1. Make Changes
```bash
# Create a feature branch
git checkout -b feature/my-feature

# Make your changes
# ...
```

### 2. Run Tests
```bash
# Run specific test file
pytest tests/test_jats_generation.py -v

# Run with debugging
pytest tests/test_jats_generation.py -v -s
```

### 3. Format Code
```bash
# Format with black
black MasterPipeline.py app.py tools/

# Lint with flake8
flake8 MasterPipeline.py app.py tools/
```

### 4. Commit Changes
```bash
git add .
git commit -m "Description of changes"
git push origin feature/my-feature
```

## Additional Resources

- **JATS Specification**: https://jats.nlm.nih.gov/
- **PMC Tagging Guidelines**: https://www.ncbi.nlm.nih.gov/pmc/pub/tagging-guidelines/
- **WeasyPrint Documentation**: https://weasyprint.readthedocs.io/
- **Pandoc Manual**: https://pandoc.org/MANUAL.html

## Support

For issues and questions:
- Open an issue on GitHub: https://github.com/findbhavin/OmniFormat_XML_JATS_PMD/issues
- Check existing documentation in the repository

## License

See LICENSE file in the repository root.
