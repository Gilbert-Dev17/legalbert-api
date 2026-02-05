from fastapi import APIRouter
import os


router = APIRouter()
# !! Health check endpoint
@router.get("/health/model")
def model_health():
    return {
        "model": "legalbert",
        "version": os.getenv("LEGALBERT_VERSION", "v1"),
        "loaded": "maybe loaded"
    }
