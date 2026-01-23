from fastapi import APIRouter

router = APIRouter(prefix="/ocr")

# ----------- Endpoints -----------
@router.post("/extract-text")
def extract_text(file_url: str):
    # Tesseract / PaddleOCR / cloud OCR later
    return {
        "extracted_text": "..."
    }