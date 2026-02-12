import requests
import time
from app.services.ocr_service import perform_ocr
from urllib.parse import urlparse
import os

def index_full_document(file_url: str):
    """
    Background task to scan pages 2-N and prepare for Search Vector.
    """
    print(f"\n[QUEUE] Background indexing started for: {file_url}")

    start_time = time.time()

    try:
        # 1. Download the file again for the full scan
        response = requests.get(file_url)
        response.raise_for_status()

        parsed_url = urlparse(file_url)
        filename = os.path.basename(parsed_url.path)

        # 2. OCR pages 2 to the end (MAX_PDF_PAGES is 10)
        extracted_text_rest = perform_ocr(response.content, filename, pages=list(range(2, 101)))

        # Calculate duration immediately after OCR finishes
        end_time = time.time()
        duration = end_time - start_time

        if not extracted_text_rest:
            print(f"No additional text found in pages 2-10 for {filename}")
            return

        # 3. CHUNKING & EMBEDDINGS
        chunks = chunk_text(extracted_text_rest)

        # 4. SAVE TO VECTOR STORE
        save_to_vector_db(file_url, chunks)

        # for testing purposes, you can run this function directly to see the OCR results without waiting for the background task
        if extracted_text_rest:
            # Output the results and the time taken
            print(f"\n--- BACKGROUND SCAN REPORT ---")
            print(f"File: {filename}")
            print(f"Time Taken: {duration:.2f} seconds") # Prints something like '24.52 seconds'
            print(f"Content Sample: {extracted_text_rest[:500]}...")
            print(f"-------------------------------\n")
        else:
            print("\nERROR: No text found in the background scan.")

        print(f"Background indexing completed for: {filename}")

    except Exception as e:
        print(f"Background task failed for {file_url}: {e}")

def chunk_text(text, size=500):
    """Simple character-based chunking."""
    return [text[i:i+size] for i in range(0, len(text), size)]

def save_to_vector_db(file_url, chunks):
    """Placeholder for your Supabase/Vector DB logic."""
    # Logic to generate embeddings and upsert to your database
    pass