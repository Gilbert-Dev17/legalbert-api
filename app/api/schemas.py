from pydantic import BaseModel

class ConfirmClassificationRequest(BaseModel):
    doc_id: str
    human_tag: str

class ClassifyDocumentResponse(BaseModel):
    doc_id: str
    case_id: str
    file_url: str
    ai_tag: str
    confidence_score: float
    extracted_text_p1: str