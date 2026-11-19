
# Use a lightweight Python base image
FROM python:3.12-slim

# Prevent Python from writing bytecode files
ENV PYTHONDONTWRITEBYTECODE=1

# Display Python logs immediately
ENV PYTHONUNBUFFERED=1

# Set application working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./app/

# Copy enterprise sample documents
COPY data/documents/ ./data/documents/

# Create directories for persistent data and logs
RUN mkdir -p /app/data/chroma_db /app/logs

# Expose API and frontend ports
EXPOSE 8000 8501

# Default command: start FastAPI
# Docker Compose will override this for the frontend container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
