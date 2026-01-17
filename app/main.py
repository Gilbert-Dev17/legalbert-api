from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.classify import router as classify_router

app = FastAPI(title="LegalBERT API")

app.include_router(health_router)
app.include_router(classify_router)

@app.on_event("startup")
def startup():
    # Placeholder for future model loading
    print("App started – model placeholder loaded")