from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from .model_loader import ensure_model_present

# Ensure the model exists before trying to load it
MODEL_PATH = ensure_model_present()

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

def classify_text(text: str):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        label_index = torch.argmax(probs, dim=1).item()
        label_name = model.config.id2label.get(label_index, f"LABEL_{label_index}")

    return {
        "label": label_name,
        "confidence": probs[0][label_index].item()
    }