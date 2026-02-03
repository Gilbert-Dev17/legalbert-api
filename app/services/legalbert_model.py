import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

REPO_ID = os.getenv("HF_REPO_ID")
HF_TOKEN = os.getenv("HF_TOKEN")

tokenizer = AutoTokenizer.from_pretrained(
    REPO_ID,
    token=HF_TOKEN
)

model = AutoModelForSequenceClassification.from_pretrained(
    REPO_ID,
    token=HF_TOKEN
)

model.eval()

def classify_text(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        label_index = torch.argmax(probs, dim=1).item()
        label_name = model.config.id2label.get(label_index, str(label_index))

    return {
        "label": label_name,
        "confidence": float(probs[0][label_index])
    }
