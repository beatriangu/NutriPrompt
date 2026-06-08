from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    pytesseract = None
    Image = None
    ImageEnhance = None
    ImageFilter = None
    ImageOps = None


logger = logging.getLogger(__name__)

OCR_LANGUAGES = "spa+eng"

MIN_IMAGE_WIDTH = 1600

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".avif",
}

OCR_CONFIG_LABEL = "--oem 3 --psm 6"
OCR_CONFIG_DOCUMENT = "--oem 3 --psm 4"
OCR_CONFIG_PANTRY = "--oem 3 --psm 11"


HIGH_PRIORITY_TERMS = [
    "ajo",
    "cebolla",
    "gluten",
    "trigo",
    "lactosa",
    "leche",
    "inulina",
    "sorbitol",
    "fructosa",
    "jarabe",
    "sin gluten",
    "sin lactosa",
    "low fodmap",
    "proteina",
    "proteína",
]


def _is_ocr_available() -> bool:
    return pytesseract is not None and Image is not None


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _resize_for_ocr(image):
    width, height = image.size

    if width >= MIN_IMAGE_WIDTH:
        return image

    ratio = MIN_IMAGE_WIDTH / width
    new_size = (
        int(width * ratio),
        int(height * ratio),
    )

    return image.resize(new_size)


def _preprocess_image(image):
    image = ImageOps.exif_transpose(image)

    image = image.convert("L")
    image = _resize_for_ocr(image)

    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = ImageEnhance.Sharpness(image).enhance(1.8)

    image = image.filter(ImageFilter.MedianFilter())
    image = image.filter(ImageFilter.SHARPEN)

    return image


def _clean_ocr_text(text: str) -> str:
    text = text.replace("|", " ")
    text = text.replace("=", " ")
    text = text.replace("°", " ")

    lines = []

    for line in text.splitlines():
        clean_line = " ".join(line.strip().split())

        if clean_line:
            lines.append(clean_line)

    return "\n".join(lines).strip()


def _extract_priority_terms(text: str) -> list[str]:
    normalized = _normalize_text(text)

    found = []

    for term in HIGH_PRIORITY_TERMS:
        pattern = rf"(?<!\w){re.escape(_normalize_text(term))}(?!\w)"

        if re.search(pattern, normalized):
            found.append(term)

    return sorted(set(found))


def _build_ai_summary(text: str) -> str:
    terms = _extract_priority_terms(text)

    if not terms:
        return (
            "No se han detectado ingredientes o términos prioritarios claros. "
            "La imagen podría necesitar más resolución o mejor iluminación."
        )

    visible_terms = ", ".join(terms)

    return (
        "Se han identificado posibles ingredientes o conceptos relevantes: "
        f"{visible_terms}."
    )


def _infer_ocr_mode(path: Path) -> str:
    filename = path.name.casefold()

    if "pantry" in filename or "despensa" in filename:
        return "pantry"

    if "fridge" in filename or "nevera" in filename:
        return "pantry"

    if "pdf" in filename or "document" in filename:
        return "document"

    return "label"


def _get_ocr_config(mode: str) -> str:
    if mode == "document":
        return OCR_CONFIG_DOCUMENT

    if mode == "pantry":
        return OCR_CONFIG_PANTRY

    return OCR_CONFIG_LABEL


def extract_text_from_image(image_path: str) -> str:
    if not _is_ocr_available():
        return (
            "OCR no disponible. Instala pytesseract y pillow "
            "para activar el análisis visual inteligente."
        )

    try:
        path = Path(image_path)

        if not path.exists():
            return "No se ha encontrado la imagen para analizar."

        if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            return (
                "Formato no soportado. "
                "Usa JPG, PNG, WEBP o AVIF."
            )

        image = Image.open(path)

        processed_image = _preprocess_image(image)

        ocr_mode = _infer_ocr_mode(path)
        config = _get_ocr_config(ocr_mode)

        raw_text = pytesseract.image_to_string(
            processed_image,
            lang=OCR_LANGUAGES,
            config=config,
        )

        clean_text = _clean_ocr_text(raw_text)

        if not clean_text:
            return (
                "No se ha podido extraer texto legible. "
                "Prueba con una imagen más cercana, enfocada y con buena iluminación."
            )

        return clean_text

    except Exception as exc:
        logger.exception(
            "Error durante OCR de '%s': %s",
            image_path,
            exc,
        )

        return (
            "No se ha podido procesar la imagen correctamente. "
            "Prueba con una imagen más clara o con mejor iluminación."
        )


def extract_structured_vision_data(image_path: str) -> dict[str, Any]:
    extracted_text = extract_text_from_image(image_path)

    normalized_text = _normalize_text(extracted_text)

    priority_terms = _extract_priority_terms(extracted_text)

    return {
        "success": bool(extracted_text),
        "ocr_text": extracted_text,
        "normalized_text": normalized_text,
        "priority_terms": priority_terms,
        "ai_summary": _build_ai_summary(extracted_text),
        "has_priority_terms": bool(priority_terms),
        "ocr_engine": "pytesseract",
        "languages": OCR_LANGUAGES,
    }