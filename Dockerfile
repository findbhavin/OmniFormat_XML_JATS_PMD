FROM python:3.10-slim

# Install system dependencies for High-Fidelity Rendering
# Note: corrected libgdk-pixbuf name for newer Debian versions
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    fonts-liberation \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libgdk-pixbuf-xlib-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2-dev \
    libxslt-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files including XSDs
COPY . .

# Port binding for Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app