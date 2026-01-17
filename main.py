from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS
from app.api.health import router as health_router
from app.api.classify import router as classify_router

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

# --- YOUR WARMUP STRATEGY ---
# This runs ONCE when Railway starts the container.
@app.on_event("startup")
def startup():
    print(" Railway Container Started")
    print(" Loading LegalBERT Model into Memory...")
    # global model
    # model = load_model_function() <--- This is where the 15s delay happens
    print(" Model Loaded! API is ready to accept requests.")