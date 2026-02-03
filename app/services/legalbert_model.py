from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

MODEL_DIR = os.path.join(
    os.getenv("MODEL_STORAGE_PATH", "/models"),
    "legalbert"
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)

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