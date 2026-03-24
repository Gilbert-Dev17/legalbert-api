import time
import os
from urllib.parse import urlparse
from app.services.ocr_service import perform_ocr
from app.services.supabase.database_service import get_supabase_client


def index_full_document(file_url: str, doc_id: str) -> None:
    """
    Background task to OCR pages 2-N and update the database record.
    Passes the signed URL directly to perform_ocr — no manual download needed.
    perform_ocr streams the file into a temp path so poppler can seek by page range.
    """
    print(f"\n[QUEUE] Background indexing started for Doc ID: {doc_id}")
    start_time = time.time()

    try:
        # Derive filename from URL for file type detection in perform_ocr
        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # OCR pages 2–100 — URL is streamed directly, no full download into RAM
        extracted_text_rest = perform_ocr(file_url, filename, pages=list(range(2, 101)))

        duration = time.time() - start_time

        if not extracted_text_rest:
            print(f"[WARN] No additional text found for {filename} after {duration:.2f}s")
            return

        # Push to Supabase — triggers search_vector column update via DB trigger
        db_update = get_supabase_client().table("documents_table").update({
            "extracted_text_rest": extracted_text_rest
        }).eq("doc_id", doc_id).execute()

        if db_update.data:
            print(f"\n--- BACKGROUND SCAN SUCCESS ---")
            print(f"Doc ID:     {doc_id}")
            print(f"Time Taken: {duration:.2f} seconds")
            print(f"Status:     Database record updated and search vector generated.")
            print(f"-------------------------------\n")
        else:
            print(f"[ERROR] Could not find Doc ID {doc_id} to update extracted text.")

    except Exception as e:
        print(f"[CRITICAL] Background indexing failed for doc_id={doc_id}: {e}")


def chunk_text(text: str, size: int = 500) -> list[str]:
    """Split text into chunks for semantic vector search (future use)."""
    return [text[i:i + size] for i in range(0, len(text), size)]