from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import PreTrainedTokenizer, PreTrainedModel
import torch
import psutil
import os
import sys
from threading import Lock
from typing import Optional, cast, Dict, Any
from pathlib import Path

torch.set_num_threads(1)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "model_assets"))

_lock = Lock()
_tokenizer: Optional[PreTrainedTokenizer] = None
_model: Optional[PreTrainedModel] = None

# Friendly label mapping: human-readable <-> numeric ids
LABEL_MAP = {"civil": 0, "criminal": 1, "legal fees": 2}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}


def label_to_id(label: str) -> int:
    """Convert a human label to its numeric id.

    Example: label_to_id('civil') -> 0
    """
    return LABEL_MAP[label.strip().lower()]


def id_to_label_fn(idx: int) -> str:
    """Convert a numeric id to its human label.

    Example: id_to_label_fn(1) -> 'criminal'
    """
    return ID_TO_LABEL.get(int(idx), f"LABEL_{idx}")


def preload_model():
    """Explicitly preload the model."""
    _load_model_if_needed()


def _load_model_if_needed():
    global _tokenizer, _model

    if _model is not None and _tokenizer is not None:
        return

    with _lock:
        if _model is None or _tokenizer is None:
            print("Loading LegalBERT model...", file=sys.stderr)

            _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
            _model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

            if _model is not None:
                _model.eval()

            # Ensure model config uses friendly labels
            try:
                if _model is not None and hasattr(_model, "config"):
                    _model.config.id2label = {0: "civil", 1: "criminal", 2: "legal_fees"}
                    _model.config.label2id = {"civil": 0, "criminal": 1, "legal_fees": 2}
            except Exception:
                # Non-fatal: continue even if config cannot be modified
                pass

            print(
                f"Model loaded. Memory usage: {get_current_mem():.2f} MB",
                file=sys.stderr,
            )


def classify_text(text: str) -> Dict[str, Any]:
    _load_model_if_needed()

    tokenizer = cast(PreTrainedTokenizer, _tokenizer)
    model = cast(Any, _model)

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)

        label_index: int = int(torch.argmax(probs, dim=1).item())
        confidence: float = float(probs[0][label_index].item())

        label_name = "Unknown"
        if hasattr(model, "config") and model.config.id2label:
            label_name = model.config.id2label.get(label_index, f"LABEL_{label_index}")

    return {
        "label": label_name,
        "confidence": confidence
    }


def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def get_current_mem():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)
