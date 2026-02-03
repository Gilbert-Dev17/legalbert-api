from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.classify import router as classify_router
from app.api.ocr import router as ocr_router
from app.model_loader import load_model

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
    print("🚀 Railway Container Started")
    print("🧠 Loading LegalBERT into memory...")
    load_model()
    print("✅ Model ready — API accepting requests")
