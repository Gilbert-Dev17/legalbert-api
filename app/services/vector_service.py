import requests
import time
import os
from urllib.parse import urlparse
from app.services.ocr_service import perform_ocr
from app.services.supabase.database_service import get_supabase_client

def index_full_document(file_url: str, doc_id: str):
    """
    Background task to scan pages 2-N and update the database record.
    """
    print(f"\n[QUEUE] Background indexing started for Doc ID: {doc_id}")
    start_time = time.time()

    try:
        # 1. Download for the deep scan
        response = requests.get(file_url)
        response.raise_for_status()

        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # 2. OCR pages 2 to 100 (Max limit for deep search)
        # This will take 1-3 minutes depending on length
        extracted_text_rest = perform_ocr(response.content, filename, pages=list(range(2, 101)))

        duration = time.time() - start_time

        if not extracted_text_rest:
            print(f"[WARN] No additional text found for {filename} after {duration:.2f}s")
            return

        # 3. PUSH TO SUPABASE
        # This updates the 'extracted_text_rest' column, which triggers the 'search_vector'
        db_update = get_supabase_client().table("documents_table").update({
            "extracted_text_rest": extracted_text_rest
        }).eq("doc_id", doc_id).execute()

        if db_update.data:
            print(f"\n--- BACKGROUND SCAN SUCCESS ---")
            print(f"Doc ID: {doc_id}")
            print(f"Time Taken: {duration:.2f} seconds")
            print(f"Status: Database record updated and search vector generated.")
            print(f"-------------------------------\n")
        else:
            print(f"[ERROR] Could not find Doc ID {doc_id} to update text.")

    except Exception as e:
        print(f"[CRITICAL] Background task failed for {doc_id}: {e}")

# Keep your chunking logic if you plan to add Semantic Vector Search later
def chunk_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]