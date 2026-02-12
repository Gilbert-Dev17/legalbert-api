# app/api/classify.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.services.ocr_service import perform_ocr
from app.services.legalbert_model import classify_text
from app.services.supabase.database_service import create_initial_document # Import new service
from .schemas import ClassifyDocumentResponse
from app.services.vector_service import index_full_document
import requests
import os
from urllib.parse import urlparse

router = APIRouter()

@router.post("/process-document", response_model=ClassifyDocumentResponse)
async def process_document(case_id: str, file_url: str, background_tasks: BackgroundTasks):
    try:
        response = requests.get(file_url)
        response.raise_for_status()

        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # 1. Page 1 Scan for Classification
        extracted_text = perform_ocr(response.content, filename, pages=[1])

        if not extracted_text:
            raise HTTPException(status_code=400, detail="OCR could not extract text")

        # 2. LegalBERT Logic
        classification = classify_text(extracted_text)

        # 3. INITIAL SAVE: Create the row in Supabase to get the doc_id
        doc_id = create_initial_document(
            case_id=case_id,
            file_url=file_url,
            ai_tag=str(classification["label"]),
            confidence=float(classification["confidence"]),
            text_p1=extracted_text
        )

        # 4. BACKGROUND TASK: Use the real doc_id, not the filename
        background_tasks.add_task(index_full_document, file_url, doc_id)

        return {
            "doc_id": doc_id, # Frontend now has the UUID for confirmation
            "case_id": case_id,
            "file_url": file_url.split("?")[0],
            "ai_tag": str(classification["label"]),
            "confidence_score": classification["confidence"],
            "extracted_text_p1": extracted_text
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
