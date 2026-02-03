import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

REPO_ID = os.getenv("HF_REPO_ID")  # e.g., "Gilbert-Dev17/legalbert-custom"
HF_TOKEN = os.getenv("HF_TOKEN")    # Your 'Read' token
BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/models")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")

def ensure_model_present():
    print(f"Loading model from Hugging Face: {REPO_ID}")

    os.makedirs(MODEL_DIR, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(REPO_ID, token=HF_TOKEN)
    model = AutoModelForSequenceClassification.from_pretrained(REPO_ID, token=HF_TOKEN)

    tokenizer.save_pretrained(MODEL_DIR)
    model.save_pretrained(MODEL_DIR)

    if os.path.exists(os.path.join(MODEL_DIR, "config.json")):
        print(f"Model already present in {MODEL_DIR}")
    else:
        print(f"Downloading model from HF repo {REPO_ID} ...")
        os.makedirs(MODEL_DIR, exist_ok=True)
        tokenizer = AutoTokenizer.from_pretrained(REPO_ID, token=HF_TOKEN)
        model = AutoModelForSequenceClassification.from_pretrained(REPO_ID, token=HF_TOKEN)
        tokenizer.save_pretrained(MODEL_DIR)
        model.save_pretrained(MODEL_DIR)
        print(f"Model saved in {MODEL_DIR}")
    return MODEL_DIR
