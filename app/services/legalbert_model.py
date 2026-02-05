from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import psutil
import os

MODEL_PATH = "model_assets"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
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
        label = int(torch.argmax(probs, dim=1).item())
        confidence = probs[0][label].item()

# testing
        label_index = torch.argmax(probs, dim=1).item()
        label_name = model.config.id2label.get(label_index, f"LABEL_{label_index}")

    return {
        "label": label_name,
        "confidence": confidence
    }

def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)  # Convert bytes to MB

# In your startup function:
print(f"Memory usage before loading model: {get_memory_usage():.2f} MB")
# ... load model ...
print(f"Memory usage after loading model: {get_memory_usage():.2f} MB")

def get_current_mem():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # MB

print(f"Current memory usage: {get_current_mem():.2f} MB")