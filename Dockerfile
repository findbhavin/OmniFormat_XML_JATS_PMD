FROM python:3.10-slim

<<<<<<< HEAD
# Install system dependencies for High-Fidelity Rendering
=======
>>>>>>> ca1087cb9726ede4dad044a4f5247266ea7ca8f1
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    fonts-liberation \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
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

<<<<<<< HEAD
# Port binding for Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
=======
# Use Gunicorn for production-grade stability on Google Cloud
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app
>>>>>>> ca1087cb9726ede4dad044a4f5247266ea7ca8f1
