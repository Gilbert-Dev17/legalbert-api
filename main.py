from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS
from app.api.health import router as health_router
from app.api.classify import router as classify_router
from app.api.ocr import router as ocr_router
from app.services.model_loader import ensure_model_present

app = FastAPI(title="LegalBERT API")

# --- CRITICAL FOR RAILWAY/VERCEL CONNECTIVITY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect your routers
app.include_router(health_router)
app.include_router(classify_router)
app.include_router(ocr_router)  # <--- ADD THIS LINE

# --- YOUR WARMUP STRATEGY ---
# This runs ONCE when Railway starts the container.
@app.on_event("startup")
def startup():
    print(" Railway Container Started")
    print(" Loading LegalBERT Model into Memory...")
    ensure_model_present()
    print("✅ LegalBERT ready")
    print(" Model Loaded! API is ready to accept requests.")