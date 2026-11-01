# Use official Microsoft Playwright image with Python & Chromium pre-installed
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=5000 \
    IS_CLOUD_DEPLOY=true

# Install Gujarati, Hindi and Indian regional fonts for rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-lohit-gujr \
    fonts-gujr \
    fonts-deva \
    fonts-indic \
    fonts-freefont-ttf \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy application files
COPY . .

# Ensure upload & data directories exist with write permissions
RUN mkdir -p uploads data static/screenshots && chmod -R 777 uploads data static

EXPOSE 5000

# Start Gunicorn server binding to PORT environment variable (Render/Railway compatible)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 wsgi:app"]
