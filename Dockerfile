FROM python:3.10-slim

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
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use Gunicorn for production-grade stability on Google Cloud
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app
