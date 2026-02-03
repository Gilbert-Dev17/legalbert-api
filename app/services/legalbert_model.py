from transformers import pipeline
import os

REPO_ID = os.getenv("HF_REPO_ID")
HF_TOKEN = os.getenv("HF_TOKEN")

classifier = pipeline(
    "text-classification",
    model=REPO_ID,
    tokenizer=REPO_ID,
    device=-1,
    torch_dtype="float16",
    use_auth_token=HF_TOKEN
)

def classify_text(text: str):
    results = classifier(text, truncation=True, max_length=128)
    # Check if results is a list and has at least one element
    if not results or not isinstance(results, list):
        return {"label": "UNKNOWN", "confidence": 0.0}
    first_result = results[0]
    return {
        "label": first_result["label"],
        "confidence": first_result["score"]
    }
