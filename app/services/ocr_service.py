import io
from typing import Optional

from PIL import Image
from pdf2image import convert_from_bytes
from google.cloud import vision


vision_client = vision.ImageAnnotatorClient()


def _google_ocr_image(pil_image: Image.Image) -> str:
    """
    Runs Google Vision OCR on a single image.
    """

    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format="PNG")
    content = img_byte_arr.getvalue()

    image = vision.Image(content=content)

    response = vision_client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(response.error.message)

    return response.full_text_annotation.text or ""


def _google_ocr_pdf(pdf_bytes: bytes) -> str:
    """
    Converts PDF bytes to images and runs OCR on 1 page.
    """

    images = images = convert_from_bytes(
                        pdf_bytes,
                        dpi=300,
                        first_page=1,
                        last_page=1
                    )


    full_text = ""

    for i, image in enumerate(images):
        text = _google_ocr_image(image)
        full_text += f"\n--- Page {i+1} ---\n"
        full_text += text

    return full_text


def perform_ocr(file_bytes: bytes, filename: str, engine: Optional[str] = "google") -> str:
    """
    Main OCR entry point.
    You can later extend this to support multiple engines.
    """

    filename = filename.lower()

    if engine == "google":

        if filename.endswith(".pdf"):
            return _google_ocr_pdf(file_bytes)

        else:
            image = Image.open(io.BytesIO(file_bytes))
            return _google_ocr_image(image)

    else:
        raise ValueError("Unsupported OCR engine")
