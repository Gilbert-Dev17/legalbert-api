import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Railway Environment Variables
REPO_ID = os.getenv("HF_REPO_ID") # e.g., "Gilbert-Dev17/legalbert-custom"
HF_TOKEN = os.getenv("HF_TOKEN") # Your 'Read' token
BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/models")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")

def ensure_model_present():
    print(f"Loading model from Hugging Face: {REPO_ID}")

    # cache_dir ensures files stay in your Railway Volume forever
    # local_files_only=False allows it to download if missing
    tokenizer = AutoTokenizer.from_pretrained(
        REPO_ID,
        cache_dir=MODEL_DIR,
        token=HF_TOKEN
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        REPO_ID,
        cache_dir=MODEL_DIR,
        token=HF_TOKEN
    )

    print(f"Model successfully loaded in {MODEL_DIR}")
    return MODEL_DIR