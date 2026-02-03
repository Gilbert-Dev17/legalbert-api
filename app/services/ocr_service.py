import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io

TESSERACT_CONFIG = "--oem 3 --psm 6"

def perform_ocr(file_bytes: bytes, filename: str) -> str:
    """Perform OCR on PDF or Image bytes."""

    if filename.lower().endswith(".pdf"):
        images = convert_from_bytes(file_bytes)
        full_text = []
        for i, image in enumerate(images):
            image = image.convert("L")  # grayscale
            page_text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
            full_text.append(f"--- Page {i+1} ---\n{page_text}")
        return "\n".join(full_text)
    else:
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(image, config=TESSERACT_CONFIG).strip()
