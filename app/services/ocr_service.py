import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
import sys
from typing import Optional

TESSERACT_CONFIG = "--oem 3 --psm 6"
MAX_PDF_PAGES = 100
PDF_DPI = 200


def perform_ocr(file_bytes: bytes, filename: str, pages: Optional[list] = None) -> str:
    """Perform OCR on image or PDF bytes safely for Azure."""

    try:
        if filename.lower().endswith(".pdf"):
            return _ocr_pdf(file_bytes, pages=pages)
        else:
            return _ocr_image(file_bytes)
    except Exception as e:
        print(f"OCR failed: {e}", file=sys.stderr)
        return ""


def _ocr_pdf(file_bytes: bytes, pages: list | None = None) -> str:
    full_text = []

    first = pages[0] if pages else 1
    last = pages[-1] if pages else MAX_PDF_PAGES

    images = convert_from_bytes(
        file_bytes,
        dpi=PDF_DPI,
        fmt="jpeg",
        thread_count=1,
        first_page=first,  # NEW: respect the start page
        last_page=last    # NEW: respect the end page
    )

    for i, image in enumerate(images):
        try:
            image = _prepare_image(image)
            page_text = pytesseract.image_to_string(
                image,
                config=TESSERACT_CONFIG
            )
            actual_page_num = first + i
            full_text.append(f"--- Page {actual_page_num} ---\n{page_text}")
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
