import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification

REPO_ID = os.getenv("HF_REPO_ID")  # e.g., "Gilbert-Dev17/legalbert-custom"
HF_TOKEN = os.getenv("HF_TOKEN")    # Your 'Read' token
BASE_DIR = os.getenv("MODEL_STORAGE_PATH", "/models")
MODEL_DIR = os.path.join(BASE_DIR, "legalbert")

def ensure_model_present():
    # Check for the weights and the config
    weights_path = os.path.join(MODEL_DIR, "model.safetensors")
    config_path = os.path.join(MODEL_DIR, "config.json")

    if os.path.exists(weights_path) and os.path.exists(config_path):
        print(f"✅ Found Safetensors weights and config in {MODEL_DIR}.")
    else:
        print(f"📥 Missing weights or config. Downloading from HF...")
        os.makedirs(MODEL_DIR, exist_ok=True)

        # This will download the .safetensors version automatically
        tokenizer = AutoTokenizer.from_pretrained(REPO_ID, token=HF_TOKEN)
        model = AutoModelForSequenceClassification.from_pretrained(REPO_ID, token=HF_TOKEN)

        tokenizer.save_pretrained(MODEL_DIR)
        model.save_pretrained(MODEL_DIR)
        print(f"🚀 Model and Tokenizer saved to {MODEL_DIR}")

    return MODEL_DIR
