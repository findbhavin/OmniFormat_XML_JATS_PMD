FROM python:3.11-slim

# Install system dependencies including pandoc AND wgets
RUN apt-get update && apt-get install -y \
    pandoc \
    wget \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pandoc to latest version for better JATS support
RUN wget https://github.com/jgm/pandoc/releases/download/3.1.12.1/pandoc-3.1.12.1-1-amd64.deb \
    && dpkg -i pandoc-3.1.12.1-1-amd64.deb \
    && rm pandoc-3.1.12.1-1-amd64.deb

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p templates

# Verify pandoc is installed and check version
RUN pandoc --version

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
