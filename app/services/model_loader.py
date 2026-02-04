# app/services/model_loader.py
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

REPO_ID = os.getenv(
    "HF_REPO_ID",
    "nlpaueb/legal-bert-base-uncased"
)

HF_TOKEN = os.getenv("HF_TOKEN")

# if not REPO_ID:
#     raise RuntimeError("HF_REPO_ID environment variable is not set")

BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/data")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")

tokenizer = None
model = None
_loaded = False

def load_model():
    global tokenizer, model, _loaded

    if _loaded:
        return tokenizer, model

    print("🔍 Checking LegalBERT cache...")

    weights = os.path.join(MODEL_DIR, "model.safetensors")
    config = os.path.join(MODEL_DIR, "config.json")

    os.makedirs(MODEL_DIR, exist_ok=True)

    if not (os.path.exists(weights) and os.path.exists(config)):
        print("📥 Downloading LegalBERT from Hugging Face...")

        tokenizer = AutoTokenizer.from_pretrained(
            REPO_ID,
            token=HF_TOKEN,
            cache_dir=MODEL_DIR

        )
        model = AutoModelForSequenceClassification.from_pretrained(
            REPO_ID,
            token=HF_TOKEN,
            cache_dir=MODEL_DIR
        )

        tokenizer.save_pretrained(MODEL_DIR)
        model.save_pretrained(MODEL_DIR)

        print("✅ LegalBERT downloaded and cached")
    else:
        print("✅ LegalBERT found in volume cache")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)

        print("📁 MODEL_DIR contents:", os.listdir(MODEL_DIR))

    model.eval()
    _loaded = True
    return tokenizer, model

def is_loaded():
    return model is not None
