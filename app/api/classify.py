from fastapi import APIRouter
from fastapi.responses import JSONResponse
from .schemas import ProcessDocumentRequest
from app.tasks.classify_task import classify_document_task

router = APIRouter()

@router.post("/process-document", status_code=202)
async def process_document(request: ProcessDocumentRequest):
    try:
        classify_document_task.delay(  # type: ignore[attr-defined]
            doc_id=request.doc_id,
            file_path=request.file_url,
            case_id=request.case_id,
        )
        return JSONResponse(
            status_code=202,
            content={"message": "Classification queued", "doc_id": request.doc_id}
        )
    except Exception as e:
        print(f"[process_document] Failed to enqueue task: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )