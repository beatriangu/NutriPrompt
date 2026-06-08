from __future__ import annotations

import csv
import logging
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[3]
KAGGLE_DATASET_DIR = BASE_DIR / "data" / "raw" / "kaggle" / "FINAL FOOD DATASET"

KAGGLE_CSV_FILES = [
    "FOOD-DATA-GROUP1.csv",
    "FOOD-DATA-GROUP2.csv",
    "FOOD-DATA-GROUP3.csv",
    "FOOD-DATA-GROUP4.csv",
    "FOOD-DATA-GROUP5.csv",
]


CATEGORY_MAP = {
    "pollo": "Proteínas",
    "pavo": "Proteínas",
    "ternera": "Proteínas",
    "carne picada": "Proteínas",
    "huevo": "Proteínas",
    "hamburguesa": "Proteínas",
    "atún": "Proteínas",
    "salmon": "Proteínas",
    "salmón": "Proteínas",
    "merluza": "Proteínas",
    "bacalao": "Proteínas",
    "yogur sin lactosa": "Lácteos y alternativas",
    "bebida vegetal": "Lácteos y alternativas",
    "queso fresco": "Lácteos y alternativas",
    "arroz": "Cereales y básicos",
    "avena": "Cereales y básicos",
    "pan sin gluten": "Cereales y básicos",
    "pasta sin gluten": "Cereales y básicos",
    "quinoa": "Cereales y básicos",
    "boniato": "Verduras y hortalizas",
    "espinacas": "Verduras y hortalizas",
    "patata": "Verduras y hortalizas",
    "tomate": "Verduras y hortalizas",
    "zanahoria": "Verduras y hortalizas",
    "calabacín": "Verduras y hortalizas",
    "verduras": "Verduras y hortalizas",
    "ensalada": "Verduras y hortalizas",
    "aguacate": "Verduras y hortalizas",
    "fruta": "Frutas",
    "plátano": "Frutas",
    "frutos rojos": "Frutas",
    "manzana": "Frutas",
    "naranja": "Frutas",
    "aceite de oliva": "Extras y semillas",
    "crema de cacahuete": "Extras y semillas",
    "nueces": "Extras y semillas",
    "semillas": "Extras y semillas",
}


CANONICAL_REPLACEMENTS = {
    "atun": "atún",
    "huevos": "huevo",
    "salmon": "salmón",
    "yogur": "yogur sin lactosa",
    "yogurt": "yogur sin lactosa",
    "pan": "pan sin gluten",
    "pasta": "pasta sin gluten",
    "tostada": "pan sin gluten",
    "tostadas": "pan sin gluten",
}


PRIORITY_PATTERNS = [
    "yogur sin lactosa",
    "pan sin gluten",
    "pasta sin gluten",
    "aceite de oliva",
    "crema de cacahuete",
    "carne picada",
    "frutos rojos",
    "bebida vegetal",
    "queso fresco",
]


BASIC_PATTERNS = [
    "pollo",
    "pavo",
    "ternera",
    "carne picada",
    "hamburguesa",
    "huevo",
    "huevos",
    "atun",
    "atún",
    "salmon",
    "salmón",
    "merluza",
    "bacalao",
    "arroz",
    "avena",
    "pan",
    "pasta",
    "quinoa",
    "yogur",
    "yogurt",
    "bebida vegetal",
    "queso fresco",
    "boniato",
    "espinacas",
    "patata",
    "tomate",
    "zanahoria",
    "calabacín",
    "verduras",
    "ensalada",
    "aguacate",
    "fruta",
    "plátano",
    "frutos rojos",
    "manzana",
    "naranja",
    "aceite de oliva",
    "crema de cacahuete",
    "nueces",
    "semillas",
]


NUTRITION_KEYS = {
    "food": "food",
    "calories": "Caloric Value",
    "protein": "Protein",
    "carbs": "Carbohydrates",
    "fat": "Fat",
    "fiber": "Dietary Fiber",
    "sugars": "Sugars",
    "sodium": "Sodium",
    "density": "Nutrition Density",
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_term(text: str, term: str) -> bool:
    normalized_term = _normalize_text(term)
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, text) is not None


def _canonicalize(item: str) -> str:
    normalized = _normalize_text(item)
    return CANONICAL_REPLACEMENTS.get(normalized, normalized)


def _preprocess_meal_text(text: str) -> str:
    normalized = _normalize_text(text)

    replacements = {
        "yogur sin lactosa alto en proteina": "yogur sin lactosa",
        "yogur alto en proteina": "yogur sin lactosa",
        "yogurt sin lactosa alto en proteina": "yogur sin lactosa",
        "tostadas sin gluten": "pan sin gluten",
        "tostada sin gluten": "pan sin gluten",
        "tostadas": "pan",
        "tostada": "pan",
        "pechuga de pollo": "pollo",
        "pechuga de pavo": "pavo",
        "pollo a la plancha": "pollo",
        "pavo al horno": "pavo",
        "ternera salteada": "ternera",
        "tortilla francesa": "huevo",
        "huevos revueltos": "huevo",
        "batido de yogur": "yogur",
        "crema de verduras": "verduras",
        "ensalada completa": "ensalada",
    }

    for old, new in replacements.items():
        normalized = normalized.replace(old, new)

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


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _load_kaggle_food_index() -> dict[str, dict[str, Any]]:
    food_index: dict[str, dict[str, Any]] = {}

    if not KAGGLE_DATASET_DIR.exists():
        logger.info("Dataset Kaggle no encontrado en %s", KAGGLE_DATASET_DIR)
        return food_index

    for filename in KAGGLE_CSV_FILES:
        csv_path = KAGGLE_DATASET_DIR / filename

        if not csv_path.exists():
            logger.warning("Archivo Kaggle no encontrado: %s", csv_path)
            continue

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    food_name = _safe_text(row.get(NUTRITION_KEYS["food"]))

                    if not food_name:
                        continue

                    normalized_name = _normalize_text(food_name)

                    food_index[normalized_name] = {
                        "name": food_name,
                        "calories": _to_float(row.get(NUTRITION_KEYS["calories"])),
                        "protein": _to_float(row.get(NUTRITION_KEYS["protein"])),
                        "carbs": _to_float(row.get(NUTRITION_KEYS["carbs"])),
                        "fat": _to_float(row.get(NUTRITION_KEYS["fat"])),
                        "fiber": _to_float(row.get(NUTRITION_KEYS["fiber"])),
                        "sugars": _to_float(row.get(NUTRITION_KEYS["sugars"])),
                        "sodium": _to_float(row.get(NUTRITION_KEYS["sodium"])),
                        "nutrition_density": _to_float(row.get(NUTRITION_KEYS["density"])),
                        "source": filename,
                    }

        except Exception as exc:
            logger.exception("No se pudo cargar el archivo Kaggle %s: %s", csv_path, exc)

    logger.info("Índice nutricional Kaggle cargado con %s alimentos.", len(food_index))
    return food_index


def _find_nutrition_match(item: str) -> dict[str, Any] | None:
    food_index = _load_kaggle_food_index()

    if not food_index:
        return None

    normalized_item = _normalize_text(item)

    if normalized_item in food_index:
        return food_index[normalized_item]

    for food_name, data in food_index.items():
        if normalized_item in food_name or food_name in normalized_item:
            return data

    return None


def _format_item_label(item: str) -> str:
    return item.strip().capitalize()


def _build_enriched_item(item: str) -> dict[str, Any]:
    nutrition = _find_nutrition_match(item)

    enriched = {
        "name": _format_item_label(item),
        "slug": _normalize_text(item),
        "nutrition": nutrition,
        "has_nutrition_data": nutrition is not None,
    }

    if nutrition:
        enriched["summary"] = _build_nutrition_summary(nutrition)
    else:
        enriched["summary"] = "Sin datos nutricionales enlazados todavía."

    return enriched


def _build_nutrition_summary(nutrition: dict[str, Any]) -> str:
    calories = nutrition.get("calories")
    protein = nutrition.get("protein")
    carbs = nutrition.get("carbs")
    fat = nutrition.get("fat")

    parts = []

    if calories is not None:
        parts.append(f"{calories:g} kcal")

    if protein is not None:
        parts.append(f"{protein:g} g proteína")

    if carbs is not None:
        parts.append(f"{carbs:g} g hidratos")

    if fat is not None:
        parts.append(f"{fat:g} g grasa")

    return " · ".join(parts) if parts else "Datos nutricionales disponibles."


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
        category: sorted(items, key=_normalize_text)
        for category, items in grouped.items()
    }


def generate_enriched_shopping_list(plan_rows: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
    basic_list = generate_shopping_list(plan_rows)

    return {
        category: [_build_enriched_item(item) for item in items]
        for category, items in basic_list.items()
    }


def get_dataset_status() -> dict[str, Any]:
    food_index = _load_kaggle_food_index()

    return {
        "dataset_available": bool(food_index),
        "total_foods": len(food_index),
        "dataset_path": str(KAGGLE_DATASET_DIR),
    }