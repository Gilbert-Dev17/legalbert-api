FROM python:3.11-slim

WORKDIR /app

# Ensure the models directory exists and is writable
RUN mkdir -p /models && chmod 777 /models

# ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV HF_HOME=/tmp/hf_home

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Install CPU-only PyTorch FIRST ---
RUN pip install --no-cache-dir \
    torch==2.2.1+cpu \
    torchvision==0.17.1+cpu \
    torchaudio==2.2.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install accelerate
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
