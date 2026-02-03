from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

REPO_ID = "Meowmeow17/legalbert-custom" # Your repo
TOKEN = "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"

try:
    # Test downloading/loading the tokenizer
    tokenizer = AutoTokenizer.from_pretrained(REPO_ID, token=TOKEN)
    # Test downloading/loading the model
    model = AutoModelForSequenceClassification.from_pretrained(REPO_ID, token=TOKEN)
    print("✅ Model and Tokenizer loaded successfully!")
except OSError as e:
    print(f"❌ Loading failed. Check if files like 'model.safetensors' exist: {e}")