FROM python:3.11-slim

WORKDIR /app

RUN mkdir -p /model_assets && chmod 777 /model_assets

ENV TRANSFORMERS_CACHE=/model_assets
ENV HF_HOME=/model_assets

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch==2.2.1+cpu \
    torchvision==0.17.1+cpu \
    torchaudio==2.2.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start both FastAPI and Celery worker in the same container
# Azure free tier has no storage so we can't run separate containers
CMD ["sh", "-c", "\
    celery -A app.celery_app worker --loglevel=info --pool=solo --concurrency=1 & \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers \
"]