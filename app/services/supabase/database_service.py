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

def create_initial_document(
    case_id: str,
    file_url: str,
    ai_tag: str,
    confidence: float,
    text_p1: str
) -> str:
    """Inserts the initial record and returns the doc_id."""

    data = {
        "case_id": case_id,
        "file_url": file_url.split("?")[0],
        "ai_tag": ai_tag,
        "status": "pending_review",
        "confidence_score": confidence,
        "extracted_text_p1": text_p1,
    }

    try:
        response = get_supabase_client().table("documents_table").insert(data).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Supabase insert returned no data.")

        # Correctly handles Pylance type checking
        rows = cast(List[Dict[str, Any]], response.data)

        if len(rows) == 0:
            raise HTTPException(status_code=500, detail="Insert successful but no rows returned.")

        doc_id = rows[0].get("doc_id")

        if not doc_id:
            raise HTTPException(status_code=500, detail="doc_id missing from Supabase response.")

        return str(doc_id)

    except Exception as e:
        # Log the error for your thesis performance records
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(e)}")
