FROM python:3.11-slim

WORKDIR /app

# Combine update, install, and cleanup to keep the image small
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This only works safely if you have the .dockerignore file above!
COPY . .

# Meow! Added --proxy-headers if you're behind Railway's internal networking
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]