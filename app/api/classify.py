from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/classify")
# !! Temporary stub – real LegalBERT later
class ClassifyRequest(BaseModel):
    text: str

@router.post("/")
def classify(req: ClassifyRequest):
    # Temporary stub – real LegalBERT later
    return {
        "label": "contract",
        "confidence": 0.87,
        "note": "mock response"
    }
