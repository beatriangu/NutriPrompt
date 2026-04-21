from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from typing import Any


CATEGORY_MAP = {
    "pollo": "Proteínas",
    "pavo": "Proteínas",
    "ternera": "Proteínas",
    "carne picada": "Proteínas",
    "huevo": "Proteínas",
    "hamburguesa": "Proteínas",
    "atun": "Proteínas",
    "atún": "Proteínas",
    "salmon": "Proteínas",
    "salmón": "Proteínas",
    "merluza": "Proteínas",
    "bacalao": "Proteínas",
    "aguacate": "Verduras y hortalizas",
    "boniato": "Verduras y hortalizas",
    "espinacas": "Verduras y hortalizas",
    "patata": "Verduras y hortalizas",
    "tomate": "Verduras y hortalizas",
    "zanahoria": "Verduras y hortalizas",
    "calabacín": "Verduras y hortalizas",
    "verduras": "Verduras y hortalizas",
    "arroz": "Cereales y básicos",
    "avena": "Cereales y básicos",
    "pan sin gluten": "Cereales y básicos",
    "pasta sin gluten": "Cereales y básicos",
    "quinoa": "Cereales y básicos",
    "yogur sin lactosa": "Lácteos y alternativas",
    "bebida vegetal": "Lácteos y alternativas",
    "aceite de oliva": "Extras y semillas",
    "crema de cacahuete": "Extras y semillas",
    "fruta": "Frutas",
    "plátano": "Frutas",
    "frutos rojos": "Frutas",
    "nueces": "Extras y semillas",
}


CANONICAL_REPLACEMENTS = {
    "yogur": "yogur sin lactosa",
    "pan": "pan sin gluten",
    "pasta": "pasta sin gluten",
    "huevos": "huevo",
}


PRIORITY_PATTERNS = [
    "yogur sin lactosa",
    "pan sin gluten",
    "pasta sin gluten",
    "aceite de oliva",
    "crema de cacahuete",
    "carne picada",
    "frutos rojos",
]


BASIC_PATTERNS = [
    "pollo",
    "pavo",
    "ternera",
    "hamburguesa",
    "huevo",
    "huevos",
    "atun",
    "atún",
    "salmon",
    "salmón",
    "merluza",
    "bacalao",
    "aguacate",
    "boniato",
    "espinacas",
    "patata",
    "tomate",
    "zanahoria",
    "calabacín",
    "verduras",
    "arroz",
    "avena",
    "pan",
    "pasta",
    "quinoa",
    "yogur",
    "bebida vegetal",
    "aceite de oliva",
    "crema de cacahuete",
    "fruta",
    "plátano",
    "frutos rojos",
    "nueces",
]


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_term(text: str, term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text) is not None


def _canonicalize(item: str) -> str:
    normalized = _normalize_text(item)
    return CANONICAL_REPLACEMENTS.get(normalized, normalized)


def _preprocess_meal_text(text: str) -> str:
    normalized = _normalize_text(text)

    normalized = normalized.replace("yogur sin lactosa alto en proteina", "yogur sin lactosa")
    normalized = normalized.replace("yogur alto en proteina", "yogur sin lactosa")
    normalized = normalized.replace("tostadas sin gluten", "pan sin gluten")
    normalized = normalized.replace("tostada sin gluten", "pan sin gluten")
    normalized = normalized.replace("tostadas", "pan")
    normalized = normalized.replace("tostada", "pan")

    return normalized


def _extract_items_from_text(text: str) -> set[str]:
    normalized = _preprocess_meal_text(text)
    found: set[str] = set()

    for pattern in PRIORITY_PATTERNS:
        if _contains_term(normalized, pattern):
            found.add(_canonicalize(pattern))

    for pattern in BASIC_PATTERNS:
        if _contains_term(normalized, pattern):
            found.add(_canonicalize(pattern))

    return found


def generate_shopping_list(plan_rows: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, set[str]] = defaultdict(set)

    for row in plan_rows:
        for field in ("breakfast", "lunch", "dinner"):
            text = row.get(field, "")
            items = _extract_items_from_text(text)

            for item in items:
                category = CATEGORY_MAP.get(item)
                if category:
                    grouped[category].add(item)

    return {
        category: sorted(items, key=lambda x: (_normalize_text(x)))
        for category, items in grouped.items()
    }