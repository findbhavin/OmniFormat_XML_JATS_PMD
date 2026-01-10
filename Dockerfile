FROM python:3.10-slim

# Install system dependencies and manually download Pandoc 3.1.1
# This specific version is REQUIRED for the --table-captions=top flag
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    fonts-liberation \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    && wget https://github.com/jgm/pandoc/releases/download/3.1.1/pandoc-3.1.1-1-amd64.deb \
    && dpkg -i pandoc-3.1.1-1-amd64.deb \
    && rm pandoc-3.1.1-1-amd64.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Unlimited timeout (0) is CRITICAL for generating two PDFs in one request
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app