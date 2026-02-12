from pydantic import BaseModel

# class ClassifyDocumentRequest(BaseModel):
#     case_id: str
#     file_url: str
#     extracted_text: str

class ClassifyDocumentResponse(BaseModel):
    # case_id: str
    file_url: str
    ai_tag: str
    confidence_score: float
    extracted_text: str