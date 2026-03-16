FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch==2.2.1 \
    torchvision==0.17.1 \
    torchaudio==2.2.1 
    

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "\
    celery -A app.celery_app worker --loglevel=info --pool=solo --concurrency=1 -Q classify --hostname=classify@%h & \
    celery -A app.celery_app worker --loglevel=info --pool=solo --concurrency=1 -Q index --hostname=index@%h & \
    uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers \
"]