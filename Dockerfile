# Market News Radar - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for lxml/beautifulsoup)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Volume for persistent data
VOLUME /data

# Environment variables (can be overridden by docker-compose or docker run)
# ADMIN_TOKEN - Optional admin authentication token
# DB_PATH - Database path (default: /data/news.db)

# Run the application
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
