import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
import sys

TESSERACT_CONFIG = "--oem 3 --psm 6"

# Azure-safe limits
MAX_PDF_PAGES = 10
PDF_DPI = 200


def perform_ocr(file_bytes: bytes, filename: str) -> str:
    """Perform OCR on image or PDF bytes safely for Azure."""

    try:
        if filename.lower().endswith(".pdf"):
            return _ocr_pdf(file_bytes)
        else:
            return _ocr_image(file_bytes)
    except Exception as e:
        print(f"OCR failed: {e}", file=sys.stderr)
        return ""


def _ocr_pdf(file_bytes: bytes) -> str:
    full_text = []

    images = convert_from_bytes(
        file_bytes,
        dpi=PDF_DPI,
        fmt="jpeg",
        thread_count=1,
        last_page=MAX_PDF_PAGES
    )

    for i, image in enumerate(images):
        try:
            image = _prepare_image(image)
            page_text = pytesseract.image_to_string(
                image,
                config=TESSERACT_CONFIG
            )
            full_text.append(f"--- Page {i + 1} ---\n{page_text}")
        except Exception as e:
            print(f"OCR failed on page {i + 1}: {e}", file=sys.stderr)

    return "\n".join(full_text)


def _ocr_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    image = _prepare_image(image)
    return pytesseract.image_to_string(
        image,
        config=TESSERACT_CONFIG
    ).strip()


def _prepare_image(image: Image.Image) -> Image.Image:
    """Normalize image for Tesseract."""
    if image.mode != "L":
        image = image.convert("L")
    return image
