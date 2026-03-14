from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import multiprocessing as mp

from app.api.health import router as health_router
from app.api.classify import router as classify_router
from app.api.ocr import router as ocr_router

from app.services.legalbert_model import (
    get_memory_usage,
    get_current_mem,
    preload_model,  # we'll add this safely
)

# # Prevent semaphore resource leak warnings
# if mp.get_start_method(allow_none=True) is None:
#     mp.set_start_method('fork', force=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("Container starting...")
    print("Initial memory usage:")
    get_memory_usage()
    get_current_mem()

    # OPTIONAL: preload model ONLY if you want
    # Comment this out if Azure cold-starts are failing
    preload_model()

    print(" App startup complete")
    yield

    # --- SHUTDOWN ---
    print(" Container shutting down")
    # Clean up multiprocessing resources
    mp.active_children()

app = FastAPI(
    title="LegalBERT API",
    lifespan=lifespan,
)

# --- CORS (Vercel-safe) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ""],  # replace with Vercel domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router)
app.include_router(classify_router)
app.include_router(ocr_router)
