from fastapi import APIRouter
import os
from app.services.model_loader import is_loaded

router = APIRouter()
# !! Health check endpoint
@router.get("/health/model")
def model_health():
    return {
        "model": "legalbert",
        "version": os.getenv("LEGALBERT_VERSION", "v1"),
        "loaded": is_loaded()
    }
