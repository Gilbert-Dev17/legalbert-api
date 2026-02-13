from typing import Any, Dict, List, cast
from supabase import create_client, Client
import os
from fastapi import HTTPException
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env.local
env_path = Path(__file__).parent.parent.parent.parent / ".env.local"
load_dotenv(env_path)

_supabase_client: Client | None = None

def get_supabase_client() -> Client:
    """Get or create the Supabase client (lazy initialization)."""
    global _supabase_client
    if _supabase_client is None:
        url: str = os.environ.get("SUPABASE_URL", "")
        key: str = os.environ.get("SUPABASE_ROLE_KEY", "")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ROLE_KEY environment variables are required")
        _supabase_client = create_client(url, key)
    return _supabase_client

def update_document_classification(
    doc_id: str,
    ai_tag: str,
    confidence: float,
    text_p1: str
) -> str:
    """Updates the existing record with AI classification results."""

    data = {
        "ai_tag": ai_tag,
        "confidence_score": confidence,
        "extracted_text_p1": text_p1,
    }

    try:
        # We use .update() instead of .insert() because the frontend already created the row
        response = get_supabase_client().table("documents_table").update(data).eq("doc_id", doc_id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found.")

        return doc_id

    except Exception as e:
        print(f"Database Update Error: {e}")
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")