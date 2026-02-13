import requests
from fastapi import APIRouter, HTTPException
from app.services.ocr_service import perform_ocr

router = APIRouter()


@router.post("/extract-text")
def extract_text(file_url: str):
    try:
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()

        filename = file_url.split("/")[-1]

        text = perform_ocr(response.content, filename, engine="google")

        return {
            "status": "success",
            "engine": "google_vision",
            "extracted_text": text
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
