from fastapi import APIRouter, HTTPException
from app.services.ocr_service import perform_ocr
from app.services.legalbert_model import classify_text
from .schemas import ClassifyDocumentResponse # Import the schema you created
import requests

router = APIRouter()

from urllib.parse import urlparse
import os

@router.post("/process-document", response_model=ClassifyDocumentResponse)
async def process_document(file_url: str):
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        # --- NEW LOGIC: Extract the filename from a complex URL ---
        # This takes '.../motion_for_permanent_dismissal.pdf?token=...'
        # and turns it into 'motion_for_permanent_dismissal.pdf'
        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # PASS BOTH: file data and the filename
        extracted_text = perform_ocr(response.content, filename)

        if not extracted_text:
            raise HTTPException(status_code=400, detail="OCR could not extract any text")

        # ... (rest of your classification logic)
        classification = classify_text(extracted_text)

        return {
            "case_id": "extract-from-logic-here", # Ensure you pass the required schema fields
            "file_url": file_url,
            "ai_tag": str(classification["label"]),
            "confidence_score": classification["confidence"],
            "extracted_text": extracted_text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))