import time
import os
from urllib.parse import urlparse

from celery import Task
from app.celery_app import celery_app
from app.services.ocr_service import perform_ocr
from app.services.legalbert_model import classify_text
from app.services.supabase.database_service import get_supabase_client
from app.services.vector_service import index_full_document


def generate_signed_url(file_path: str, expires_in: int = 300) -> str:
    supabase = get_supabase_client()
    response = supabase.storage.from_("Case-Documents").create_signed_url(
        file_path, expires_in
    )
    url = response.get("signedURL")
    if not url:
        raise ValueError(f"Failed to generate signed URL for path: {file_path}")
    return url


def extract_text(file_url: str, filename: str):
    import requests
    from io import BytesIO

    ext = filename.lower().split(".")[-1]

    if ext in ["pdf", "png", "jpg", "jpeg"]:
        return perform_ocr(file_url, filename, pages=[1])

    elif ext == "docx":
        from docx import Document

        response = requests.get(file_url, timeout=30)
        response.raise_for_status()

        doc = Document(BytesIO(response.content))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        return text[:2500]  # keep within ~512 tokens

    else:
        raise ValueError(f"Unsupported file type: {ext}")

@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def classify_document_task(self: Task, doc_id: str, file_path: str, case_id: str) -> None:
    """
    FAST task — page 1 OCR + LegalBERT classification + DB write.
    No manual file download — signed URL is streamed directly inside perform_ocr.
    Kicks off index_document_task as a fire-and-forget after writing results.
    """
    supabase = get_supabase_client()

    try:
        supabase.table("documents_table").update({
            "status": "processing"
        }).eq("doc_id", doc_id).execute()

        start_time = time.time()

        # Step 1: Generate signed URL — perform_ocr will stream from this directly
        signed_url = generate_signed_url(file_path)

        # Step 2: Derive filename for file type detection inside perform_ocr
        filename = os.path.basename(urlparse(file_path).path)

        # Step 3: OCR page 1 ONLY — no req.get() here, streaming happens inside perform_ocr
        # extracted_text = perform_ocr(signed_url, filename, pages=[1])
        extracted_text = extract_text(signed_url, filename)

        if not extracted_text:
            raise ValueError("OCR could not extract text from document")

        # Step 4: LegalBERT classification
        classification = classify_text(extracted_text)

        processing_time = round(time.time() - start_time, 4)

        # Step 5: Write success — Supabase Realtime notifies the frontend here
        supabase.table("documents_table").update({
            "status": "success",
            "ai_tag": str(classification["label"]),
            "confidence_score": float(classification["confidence"]),
            "extracted_text_p1": extracted_text,
            "processing_time_seconds": processing_time,
        }).eq("doc_id", doc_id).eq("case_id", case_id).execute()

        # Step 6: Fire and forget — full indexing runs on the index queue separately
        # Does NOT block this task or the next classify task from starting
        index_document_task.delay(doc_id=doc_id, file_path=file_path)  # type: ignore[attr-defined]

    except Exception as e:
        print(f"[classify_document_task] Failed for doc_id={doc_id}: {e}")
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            supabase.table("documents_table").update({
                "status": "failed",
                "error_message": str(e),
            }).eq("doc_id", doc_id).execute()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def index_document_task(self: Task, doc_id: str, file_path: str) -> None:
    """
    SLOW task — full document OCR + vector indexing for pages 2-N.
    Runs on the index queue after classify_document_task completes.
    User never waits for this — purely background.
    A fresh signed URL is generated here since the classify task's URL may have expired.
    """
    try:
        filename = os.path.basename(urlparse(file_path).path)

        # Fresh signed URL with longer expiry — indexing pages 2-100 takes time
        signed_url = generate_signed_url(file_path, expires_in=600)
        index_full_document(signed_url, doc_id, filename)
        print(f"[index_document_task] Indexed doc_id={doc_id}")

    except Exception as e:
        print(f"[index_document_task] Failed for doc_id={doc_id}: {e}")
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            print(f"[index_document_task] Max retries exceeded for doc_id={doc_id}")
            # Intentionally NOT marking as failed in DB —
            # classification already succeeded, indexing failure is non-critical