# LegalBERT API

## OCR Performance Baseline

Tesseract OCR 5.5.1 was evaluated straight out of the box at 200 DPI without any preprocessing.

| Metric                   | Score  |
| ------------------------ | ------ |
| Average CER              | 0.0466 |
| Average WER              | 0.0650 |
| Character-Level Accuracy | 95%    |
| Word-Level Accuracy      | 93%    |

Average CER: 0.04665670563890406
Average WER: 0.06504165719621838

> CER (Character Error Rate) and WER (Word Error Rate) are the standard metrics for OCR accuracy evaluation.
> Lower is better; 0.0 = perfect, 1.0 = completely wrong.

---

# Running with Docker

The LegalBERT API can be run using Docker, which removes the need to manually install Python dependencies or manage virtual environments.

## Prerequisites

Make sure the following are installed:

* Docker
* Docker Compose (optional but recommended)

Verify installation:

```bash
docker --version
docker compose version
```

---

## Build the Docker Image

From the project root directory, build the Docker container:

```bash
docker build -t legalbert-api .
```

---

## Run the Container

Start the API container:

```bash
docker run -p 8000:8000 legalbert-api
```

The API will now be available at:

```
http://localhost:8000
```

Interactive API documentation:

```
http://localhost:8000/docs
```

---

## Run with Docker Compose (Recommended)

If a docker-compose.yml file is included, you can start the entire stack with:

```bash
docker compose up --build
```

To stop the containers:

```bash
docker compose down
```

---

## Rebuilding After Code Changes

If you modify dependencies or Docker configuration, rebuild the container:

```bash
docker compose up --build
```

or

```bash
docker build -t legalbert-api .
```
