import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

REPO_ID = os.getenv("HF_REPO_ID")
HF_TOKEN = os.getenv("HF_TOKEN")

BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/models")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")

def ensure_model_present():
    weights = os.path.join(MODEL_DIR, "model.safetensors")
    config = os.path.join(MODEL_DIR, "config.json")

    if os.path.exists(weights) and os.path.exists(config):
        print("✅ LegalBERT already cached")
        return

    print("⬇️ Downloading LegalBERT from Hugging Face...")
    os.makedirs(MODEL_DIR, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(
        REPO_ID,
        token=HF_TOKEN
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        REPO_ID,
        token=HF_TOKEN
    )

    tokenizer.save_pretrained(MODEL_DIR)
    model.save_pretrained(MODEL_DIR)

    print("✅ LegalBERT downloaded and saved")
