import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io

TESSERACT_CONFIG = "--oem 3 --psm 6"

def perform_ocr(file_bytes: bytes, filename: str) -> str:
    """Takes bytes and filename to determine if it's a PDF or Image"""
     # Check if the file is a PDF based on extension
    if filename.lower().endswith(".pdf"):
        # Convert PDF pages to a list of PIL images
        images = convert_from_bytes(file_bytes)

        full_text = []
        for i, image in enumerate(images):
            # Process each page
            image = image.convert("L")  # grayscale
            # page_text = pytesseract.image_to_string(image)
            page_text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
            full_text.append(f"--- Page {i+1} ---\n{page_text}")

        return "\n".join(full_text)
    else:
        # Image logic here...
       # Process as a standard image
        image = Image.open(io.BytesIO(file_bytes))
        return pytesseract.image_to_string(
            image,
            config=TESSERACT_CONFIG
            ).strip()