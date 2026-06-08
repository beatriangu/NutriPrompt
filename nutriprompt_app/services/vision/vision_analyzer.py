from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Any

from .nutrition_risk_rules import analyze_fodmap_risk
from .label_reader import extract_text_from_image


logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


RESTRICTION_KEYWORDS = {
    "sin_gluten": [
        "sin gluten",
        "gluten free",
        "celiaquia",
        "celíaco",
        "celiaco",
    ],
    "sin_lactosa": [
        "sin lactosa",
        "lactose free",
        "intolerancia a la lactosa",
        "lactosa",
    ],
    "low_fodmap": [
        "low fodmap",
        "bajo en fodmap",
        "fodmaps",
        "fodmap",
        "evitar ajo",
        "evitar cebolla",
    ],
    "vegetariano": [
        "vegetariano",
        "vegetarian",
    ],
    "vegano": [
        "vegano",
        "vegan",
    ],
    "pescetariano": [
        "pescetariano",
        "pescatarian",
    ],
}


GOAL_KEYWORDS = {
    "energia": [
        "ganar energia",
        "ganar energía",
        "energia",
        "energía",
        "fatiga",
        "cansancio",
    ],
    "peso": [
        "perder peso",
        "adelgazar",
        "deficit calorico",
        "déficit calórico",
        "control de peso",
    ],
    "musculo": [
        "ganar masa muscular",
        "masa muscular",
        "proteina",
        "proteína",
        "hipertrofia",
    ],
    "equilibrado": [
        "comer equilibrado",
        "alimentacion equilibrada",
        "alimentación equilibrada",
        "habitos saludables",
        "hábitos saludables",
    ],
}


PANTRY_FOOD_KEYWORDS = [
    "arroz",
    "pasta",
    "quinoa",
    "avena",
    "pan",
    "lentejas",
    "garbanzos",
    "atun",
    "atún",
    "aceite",
    "tomate",
    "leche",
    "yogur",
    "huevos",
    "pollo",
    "pavo",
    "queso",
    "verduras",
    "fruta",
    "plátano",
    "platano",
    "patata",
    "boniato",
    "calabacín",
    "calabacin",
    "zanahoria",
]


WARNING_KEYWORDS = {
    "gluten": [
        "trigo",
        "cebada",
        "centeno",
        "gluten",
        "harina de trigo",
        "sémola",
        "semola",
    ],
    "lactosa": [
        "leche",
        "lactosa",
        "suero de leche",
        "nata",
        "queso",
        "leche en polvo",
    ],
    "fodmap": [
        "ajo",
        "cebolla",
        "inulina",
        "fructosa",
        "jarabe de fructosa",
        "polioles",
        "sorbitol",
        "manitol",
    ],
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_keyword(text: str, keyword: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_keyword = _normalize_text(keyword)
    pattern = rf"(?<!\w){re.escape(normalized_keyword)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def _detect_matches(text: str, keyword_map: dict[str, list[str]]) -> dict[str, list[str]]:
    matches: dict[str, list[str]] = {}

    for category, keywords in keyword_map.items():
        detected = [
            keyword
            for keyword in keywords
            if _contains_keyword(text, keyword)
        ]

        if detected:
            matches[category] = detected

    return matches


def _detect_pantry_items(text: str) -> list[str]:
    detected = [
        item
        for item in PANTRY_FOOD_KEYWORDS
        if _contains_keyword(text, item)
    ]

    return sorted(set(detected), key=_normalize_text)


def _detect_restrictions(text: str) -> list[str]:
    matches = _detect_matches(text, RESTRICTION_KEYWORDS)
    return sorted(matches.keys())


def _detect_goals(text: str) -> list[str]:
    matches = _detect_matches(text, GOAL_KEYWORDS)
    return sorted(matches.keys())


def _detect_warnings(text: str) -> list[dict[str, Any]]:
    warning_matches = _detect_matches(text, WARNING_KEYWORDS)

    warnings = []

    for category, keywords in warning_matches.items():
        warnings.append(
            {
                "category": category,
                "keywords": sorted(set(keywords), key=_normalize_text),
                "message": _build_warning_message(category, keywords),
            }
        )

    return warnings


def _build_warning_message(category: str, keywords: list[str]) -> str:
    visible_keywords = ", ".join(sorted(set(keywords), key=_normalize_text))

    if category == "gluten":
        return f"Posible presencia de gluten detectada: {visible_keywords}."

    if category == "lactosa":
        return f"Posible presencia de lactosa o lácteos detectada: {visible_keywords}."

    if category == "fodmap":
        return f"Posibles ingredientes altos en FODMAP detectados: {visible_keywords}."

    return f"Se han detectado posibles alertas nutricionales: {visible_keywords}."


def _infer_analysis_title(intake_type: str) -> str:
    titles = {
        "nutrition_pdf": "Pauta nutricional analizada",
        "product_label": "Producto o etiqueta analizada",
        "pantry_image": "Despensa analizada",
        "fridge_image": "Nevera analizada",
        "ingredient_image": "Ingrediente analizado",
    }

    return titles.get(intake_type, "Análisis nutricional")


def _infer_analysis_description(intake_type: str) -> str:
    descriptions = {
        "nutrition_pdf": (
            "Se ha intentado extraer información útil de la pauta nutricional: "
            "objetivos, restricciones, alimentos recomendados y posibles alertas."
        ),
        "product_label": (
            "Se ha analizado el texto visible del producto para detectar ingredientes "
            "compatibles o sensibles."
        ),
        "pantry_image": (
            "Se ha intentado identificar alimentos disponibles en la despensa para "
            "orientar mejor el plan semanal."
        ),
        "fridge_image": (
            "Se ha intentado identificar alimentos disponibles en la nevera para "
            "adaptar mejor la planificación."
        ),
        "ingredient_image": (
            "Se ha analizado el ingrediente o producto concreto para detectar posibles "
            "restricciones relevantes."
        ),
    }

    return descriptions.get(
        intake_type,
        "Se ha realizado una primera interpretación orientativa del archivo subido.",
    )


def _build_structured_summary(
    *,
    intake_type: str,
    extracted_text: str,
    restrictions: list[str],
    goals: list[str],
    items: list[str],
    warnings: list[dict[str, Any]],
    fodmap_analysis: dict[str, Any],
) -> dict[str, Any]:
    return {
        "title": _infer_analysis_title(intake_type),
        "description": _infer_analysis_description(intake_type),
        "intake_type": intake_type,
        "detected_restrictions": restrictions,
        "detected_goals": goals,
        "detected_items": items,
        "detected_warnings": warnings,
        "fodmap_analysis": fodmap_analysis,
        "has_extracted_text": bool(extracted_text.strip()),
        "professional_notice": (
            "Este análisis es orientativo y no sustituye la valoración de un profesional "
            "sanitario o nutricional. Si existe una pauta de nutricionista, debe prevalecer "
            "sobre cualquier sugerencia automática."
        ),
    }


def _extract_text_from_pdf_placeholder(file_path: str) -> str:
    return (
        "Lectura de PDF pendiente de implementación avanzada. "
        "El archivo se ha recibido correctamente, pero esta versión todavía no extrae "
        "texto completo desde PDF. Próximo paso: integrar PyMuPDF o pdfplumber."
    )


def extract_text_from_uploaded_file(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return extract_text_from_image(file_path)

    if extension in SUPPORTED_PDF_EXTENSIONS:
        return _extract_text_from_pdf_placeholder(file_path)

    return (
        "Formato no soportado para análisis automático. "
        "Sube una imagen JPG, PNG, WEBP, AVIF o un PDF."
    )


def analyze_smart_intake(file_path: str, intake_type: str = "product_label") -> dict[str, Any]:
    extracted_text = extract_text_from_uploaded_file(file_path)

    fodmap_analysis = analyze_fodmap_risk(extracted_text)
    restrictions = _detect_restrictions(extracted_text)
    goals = _detect_goals(extracted_text)
    items = _detect_pantry_items(extracted_text)
    warnings = _detect_warnings(extracted_text)

    structured_summary = _build_structured_summary(
        intake_type=intake_type,
        extracted_text=extracted_text,
        restrictions=restrictions,
        goals=goals,
        items=items,
        warnings=warnings,
        fodmap_analysis=fodmap_analysis,
    )

    return {
        "intake_type": intake_type,
        "extracted_text": extracted_text,
        "fodmap_analysis": fodmap_analysis,
        "detected_restrictions": restrictions,
        "detected_goals": goals,
        "detected_items": items,
        "detected_warnings": warnings,
        "structured_summary": structured_summary,
    }


def analyze_food_label(image_path: str) -> dict[str, Any]:
    return analyze_smart_intake(image_path, intake_type="product_label")