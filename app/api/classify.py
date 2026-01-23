from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="")

# ----------- Models -----------

class ClassifyDocumentRequest(BaseModel):
    case_id: str
    file_url: str
    extracted_text: str


class ClassifyDocumentResponse(BaseModel):
    case_id: str
    file_url: str
    ai_tag: str
    confidence_score: float
    extracted_text: str


# ----------- Endpoint -----------

@router.post("/classify-document", response_model=ClassifyDocumentResponse)
def classify_document(req: ClassifyDocumentRequest):
    # Temporary stub – LegalBERT later
    ai_label = "affidavit"
    confidence = 0.91

    return {
        "case_id": req.case_id,
        "file_url": req.file_url,
        "ai_tag": ai_label,
        "confidence_score": confidence,
        "extracted_text": req.extracted_text,
    }
