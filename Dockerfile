# Lightweight Python base image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first to avoid unnecessary NVIDIA CUDA dependencies.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
       torch==2.15.0 \
       --index-url https://download.pytorch.org/whl/cpu

# Install orjson separately to isolate ChromaDB's JSON dependency.
RUN pip install --no-cache-dir "orjson>=3.9.12"

# Install remaining application dependencies.
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/documents/ ./data/documents/
RUN mkdir -p /app/data/chroma_db /app/logs

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
