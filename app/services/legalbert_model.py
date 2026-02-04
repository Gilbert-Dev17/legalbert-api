import torch
from app.services.model_loader import load_model


def classify_text(text: str):
    tokenizer, model = load_model()

    # 👇 Tell Pylance these are guaranteed
    assert tokenizer is not None
    assert model is not None

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        label_index = int(torch.argmax(probs, dim=1).item())
        label_name = model.config.id2label.get(label_index, "UNKNOWN")

    return {
        "label": label_name,
        "confidence": float(probs[0][label_index].item())
    }
