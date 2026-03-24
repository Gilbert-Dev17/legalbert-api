import pytesseract
import requests
from PIL import Image
from pdf2image import convert_from_path
import io
import sys
import os
import tempfile
from typing import Optional

TESSERACT_CONFIG = "--oem 3 --psm 6"
MAX_PDF_PAGES = 100
PDF_DPI = 200


def perform_ocr(source: str | bytes, filename: str, pages: Optional[list] = None) -> str:
    """
    Perform OCR on a PDF or image.
    - source: either a URL (str) or raw bytes
    - filename: used to determine file type (.pdf vs image)
    - pages: list of page numbers to OCR (1-indexed). Defaults to all pages up to MAX_PDF_PAGES.
    """
    try:
        if filename.lower().endswith(".pdf"):
            if isinstance(source, str):
                # URL path — stream into temp file, never loads full file into RAM at once
                return _ocr_pdf_from_url(source, pages=pages)
            else:
                # Bytes path — write to temp file so convert_from_path can seek by page
                return _ocr_pdf_from_bytes(source, pages=pages)
        else:
            # Image — bytes or URL
            if isinstance(source, str):
                response = requests.get(source)
                response.raise_for_status()
                return _ocr_image(response.content)
            return _ocr_image(source)
    except Exception as e:
        print(f"OCR failed: {e}", file=sys.stderr)
        return ""


def _ocr_pdf_from_url(url: str, pages: list | None = None) -> str:
    """
    Stream the PDF from a URL into a temp file, then OCR only the requested page range.
    This avoids loading the entire file into memory before processing.
    """
    first = pages[0] if pages else 1
    last = pages[-1] if pages else MAX_PDF_PAGES

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                tmp.write(chunk)

    try:
        return _run_ocr_on_path(tmp_path, first, last)
    finally:
        os.unlink(tmp_path)


def _ocr_pdf_from_bytes(file_bytes: bytes, pages: list | None = None) -> str:
    """
    Write bytes to a temp file, then OCR only the requested page range.
    Using convert_from_path (vs convert_from_bytes) allows poppler to seek
    directly to the page range without holding everything in RAM.
    """
    first = pages[0] if pages else 1
    last = pages[-1] if pages else MAX_PDF_PAGES

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        return _run_ocr_on_path(tmp_path, first, last)
    finally:
        os.unlink(tmp_path)


def _run_ocr_on_path(pdf_path: str, first: int, last: int) -> str:
    """
    Core OCR logic — convert a page range from a PDF file path to text.
    Poppler uses first_page/last_page to seek directly, skipping unneeded pages.
    """
    images = convert_from_path(
        pdf_path,
        dpi=PDF_DPI,
        fmt="jpeg",
        thread_count=1,
        first_page=first,
        last_page=last,
    )

    full_text = []
    for i, image in enumerate(images):
        try:
            image = _prepare_image(image)
            page_text = pytesseract.image_to_string(image, config=TESSERACT_CONFIG)
            actual_page_num = first + i
            full_text.append(f"--- Page {actual_page_num} ---\n{page_text}")
        except Exception as e:
            print(f"OCR failed on page {first + i}: {e}", file=sys.stderr)

    return "\n".join(full_text)


def _ocr_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    image = _prepare_image(image)
    return pytesseract.image_to_string(image, config=TESSERACT_CONFIG).strip()


def _prepare_image(image: Image.Image) -> Image.Image:
    """Normalize image for Tesseract — grayscale gives better accuracy."""
    if image.mode != "L":
        image = image.convert("L")
    return image