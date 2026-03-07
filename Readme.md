# LegalBERT API

## OCR Performance Baseline

Tesseract OCR 5.5.1 was evaluated straight out of the box at 200 DPI without any preprocessing.

| Metric | Score |
|--------|-------|
| Average CER | 0.1079 |
| Average WER | 0.1405 |

> CER (Character Error Rate) and WER (Word Error Rate) are the standard metrics for OCR accuracy evaluation.
> Lower is better; 0.0 = perfect, 1.0 = completely wrong.

---

## Local Setup

For local instances, you need to create and activate a virtual environment before installing dependencies.

### Create Virtual Environment

```bash
python -m venv venv
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Install Dependencies

Once the virtual environment is activated, install the required packages:

```bash
# install all requirements:
pip install -r requirements.txt
```

### Run Locally

To start the API server with auto-reload enabled:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

You can access the interactive API documentation at `http://localhost:8000/docs`
