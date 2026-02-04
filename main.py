from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.classify import router as classify_router
from app.api.ocr import router as ocr_router
# from app.services.model_loader import load_model
import os

app = FastAPI(title="LegalBERT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(classify_router)
app.include_router(ocr_router)


@app.on_event("startup")
def startup():
    print("🚀 Railway container started")

    hf_token = os.getenv("HF_TOKEN")
    print("HF_TOKEN:", "SET" if hf_token else "MISSING")

    # Safe directory check
    models_dir = os.getenv("MODEL_STORAGE_PATH", "/models")
    legalbert_dir = os.path.join(models_dir, "legalbert")

    if os.path.exists(models_dir):
        print("📦 Model volume contents:", os.listdir(models_dir))
    else:
        print("📦 Model volume not initialized yet")

    if os.path.exists(legalbert_dir):
        print("📦 LegalBERT model files:", os.listdir(legalbert_dir))
    else:
        print("❌ LegalBERT directory missing!")

    print("⏳ Loading LegalBERT into memory...")
    # load_model()  # <-- Eagerly load the model here

    # print("✅ API ready — model loaded and accepting requests")
    print("✅ API ready — model will load lazily on first request")
