# Chrome Extension Downloader Dockerfile

FROM python:3.11-slim

# Set metadata
LABEL maintainer="Chrome Extension Downloader Team"
LABEL description="Enhanced tool for downloading Chrome extensions from the Chrome Web Store"
LABEL version="2.0.0"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY chrome_extension_downloader.py .
COPY crx_utils.py .
COPY setup.py .
COPY README.md .
COPY API_DOCUMENTATION.md .

# Create directories for downloads and cache
RUN mkdir -p /app/downloads /app/cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd -m -u 1000 downloader && \
    chown -R downloader:downloader /app
USER downloader

# Expose volume for downloads
VOLUME ["/app/downloads", "/app/cache"]

# Set default command
CMD ["python", "chrome_extension_downloader.py", "--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import chrome_extension_downloader; print('OK')" || exit 1
