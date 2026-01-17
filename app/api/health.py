from fastapi import APIRouter

router = APIRouter()
# !! Health check endpoint
@router.get("/health")
def health():
    return {"status": "ok"}
