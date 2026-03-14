from celery import Task
from app.celery_app import celery_app
from app.services.ocr_service import perform_ocr
from app.services.legalbert_model import classify_text
from app.services.supabase.database_service import get_supabase_client
from app.services.vector_service import index_full_document
import time


def generate_signed_url(file_path: str, expires_in: int = 300) -> str:
    """Generate a short-lived signed URL from a Supabase storage path."""
    supabase = get_supabase_client()
    response = supabase.storage.from_("Case-Documents").create_signed_url(
        file_path, expires_in
    )
    url = response.get("signedURL")
    if not url:
        raise ValueError(f"Failed to generate signed URL for path: {file_path}")
    return url


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def classify_document_task(self: Task, doc_id: str, file_path: str, case_id: str) -> None:
    """
    Celery task — runs fully independently of FastAPI.
    1. Generate signed URL from storage path
    2. OCR page 1
    3. LegalBERT classification
    4. Write result back to DB
    """
    supabase = get_supabase_client()

    try:
        # Mark as processing
        supabase.table("documents_table").update({
            "status": "processing"
        }).eq("doc_id", doc_id).execute()

        start_time = time.time()

        # Step 1: Generate signed URL — worker owns this, not the frontend
        signed_url = generate_signed_url(file_path)

        # Step 2: Download file content
        import requests as req
        response = req.get(signed_url)
        response.raise_for_status()

        import os
        from urllib.parse import urlparse
        filename = os.path.basename(urlparse(file_path).path)

        # Step 3: OCR page 1 only for classification
        extracted_text = perform_ocr(response.content, filename, pages=[1])

        if not extracted_text:
            raise ValueError("OCR could not extract text from document")

        # Step 4: LegalBERT classification
        classification = classify_text(extracted_text)

        processing_time = round(time.time() - start_time, 4)

        # Step 5: Write success back to DB
        supabase.table("documents_table").update({
            "status": "success",
            "ai_tag": str(classification["label"]),
            "confidence_score": float(classification["confidence"]),
            "extracted_text_p1": extracted_text,
            "processing_time_seconds": processing_time,
        }).eq("doc_id", doc_id).eq("case_id", case_id).execute()

        # Step 6: Background vector indexing (full document)
        index_full_document(signed_url, doc_id)

    except Exception as e:
        print(f"[classify_document_task] Failed for doc_id={doc_id}: {e}")

        # Retry if within retry limit, otherwise mark as failed
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            supabase.table("documents_table").update({
                "status": "failed",
                "error_message": str(e),
            }).eq("doc_id", doc_id).execute()