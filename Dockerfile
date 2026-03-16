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
    torch==2.2.1 \
    torchvision==0.17.1 \
    torchaudio==2.2.1 
    

COPY requirements.txt .
RUN pip install accelerate
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers"]
