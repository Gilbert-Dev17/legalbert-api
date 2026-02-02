import requests
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.ocr_service import perform_ocr

router = APIRouter()

@router.post("/extract-text")
def extract_text(file_url: str):
    try:
        response = requests.get(file_url, timeout=15)
        response.raise_for_status()

        # Extract the filename from the URL
        filename = file_url.split("/")[-1]

        # Pass BOTH arguments here
        text = perform_ocr(response.content, filename)

        return {"status": "success", "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))