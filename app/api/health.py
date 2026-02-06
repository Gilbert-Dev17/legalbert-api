from fastapi import APIRouter
import os
import psutil  # You'll need this for hardware stats
from app.services.legalbert_model import _model, get_current_mem

router = APIRouter()

@router.get("/health/model")
def model_health():
    # 1. Check if the model is currently residing in RAM
    is_loaded = _model is not None

    # 2. Get the current memory footprint of the app
    current_mem = get_current_mem()

    # 3. Get overall System RAM usage (important for Azure VM stability)
    system_ram = psutil.virtual_memory().percent

    return {
        "status": "healthy" if system_ram < 90 else "degraded",
        "model": "legalbert-base-uncased",
        "version": os.getenv("LEGALBERT_VERSION", "1.0.0"),
        "is_loaded": is_loaded,
        "memory_usage_mb": round(current_mem, 2),
        "system_ram_percent": system_ram,
        "device": str(getattr(_model, 'device', 'not_loaded'))
    }