import torch
from app.services.model_loader import load_model

tokenizer, model = load_model()

def classify_text(text: str):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

    label_index = torch.argmax(probs, dim=1).item()
    label_name = model.config.id2label.get(label_index, f"LABEL_{label_index}")

    return {
        "label": label_name,
        "confidence": probs[0][label_index].item()
    }
