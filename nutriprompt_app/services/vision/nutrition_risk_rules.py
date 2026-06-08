from __future__ import annotations

import re
import unicodedata
from typing import Any


HIGH_FODMAP_RULES = {
    "ajo": ["ajo", "ajo en polvo", "extracto de ajo"],
    "cebolla": ["cebolla", "cebolla en polvo", "cebolla deshidratada", "extracto de cebolla"],
    "trigo": ["trigo", "harina de trigo", "sémola de trigo", "semola de trigo"],
    "lactosa": ["lactosa", "leche", "leche en polvo", "suero de leche", "nata"],
    "miel": ["miel"],
    "fructosa": ["fructosa", "jarabe de fructosa", "jarabe de maíz alto en fructosa"],
    "inulina": ["inulina", "fibra de achicoria", "achicoria"],
    "polioles": ["sorbitol", "manitol", "xilitol", "maltitol", "isomalt"],
    "legumbres": ["garbanzos", "lentejas", "alubias", "judías", "frijoles"],
    "frutas altas en FODMAP": ["manzana", "pera", "sandía", "mango", "cerezas"],
    "verduras altas en FODMAP": ["coliflor", "champiñón", "champiñones", "setas"],
}

GLUTEN_RULES = {
    "gluten": ["gluten"],
    "trigo": ["trigo", "harina de trigo", "sémola", "semola"],
    "cebada": ["cebada", "malta", "extracto de malta"],
    "centeno": ["centeno"],
}

LACTOSE_RULES = {
    "lactosa": ["lactosa"],
    "leche": ["leche", "leche en polvo"],
    "derivados lácteos": ["suero de leche", "nata", "queso", "mantequilla"],
}

NUTRITIONAL_CAUTION_RULES = {
    "azúcares añadidos": ["azúcar", "glucosa", "dextrosa", "jarabe", "sirope"],
    "sodio / sal": ["sal", "sodio", "glutamato monosódico", "glutamato monosodico"],
    "ultraprocesado": ["potenciador del sabor", "aroma", "colorante", "conservador", "estabilizante"],
}

PROFESSIONAL_NOTICE = (
    "Este análisis es orientativo y no sustituye la valoración de un profesional "
    "sanitario o nutricional. Si existe una pauta de nutricionista, debe prevalecer "
    "sobre cualquier sugerencia automática."
)


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_term(text: str, term: str) -> bool:
    normalized_text = _normalize_text(text)
    normalized_term = _normalize_text(term)
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def _scan_rules(text: str, rules: dict[str, list[str]]) -> list[dict[str, Any]]:
    detected = []

    for category, variants in rules.items():
        matches = [
            variant
            for variant in variants
            if _contains_term(text, variant)
        ]

        if matches:
            detected.append(
                {
                    "category": category,
                    "matches": sorted(set(matches), key=_normalize_text),
                }
            )

    return detected


def _flatten_detected(detected: list[dict[str, Any]]) -> list[str]:
    ingredients = []

    for item in detected:
        ingredients.extend(item.get("matches", []))

    return sorted(set(ingredients), key=_normalize_text)


def _calculate_risk_score(
    *,
    fodmap_hits: list[dict[str, Any]],
    gluten_hits: list[dict[str, Any]],
    lactose_hits: list[dict[str, Any]],
    caution_hits: list[dict[str, Any]],
) -> int:
    score = 0
    score += len(fodmap_hits) * 3
    score += len(gluten_hits) * 2
    score += len(lactose_hits) * 2
    score += len(caution_hits)

    return score


def _risk_level(score: int) -> str:
    if score >= 7:
        return "high"

    if score >= 3:
        return "medium_high"

    if score >= 1:
        return "medium"

    return "low_unknown"


def _build_message(
    *,
    risk: str,
    fodmap_hits: list[dict[str, Any]],
    gluten_hits: list[dict[str, Any]],
    lactose_hits: list[dict[str, Any]],
    caution_hits: list[dict[str, Any]],
) -> str:
    if risk == "high":
        return (
            "Se han detectado varias señales relevantes. Este producto podría no encajar "
            "con una pauta baja en FODMAPs, sin gluten o sin lactosa. Conviene revisarlo "
            "con detalle antes de incluirlo en el plan."
        )

    if risk == "medium_high":
        return (
            "Se han detectado posibles ingredientes sensibles. Revisa la etiqueta completa "
            "y contrástala con tus restricciones antes de usar este producto."
        )

    if risk == "medium":
        return (
            "Se ha detectado alguna señal nutricional a revisar. Puede ser compatible o no "
            "según cantidades, tolerancia individual y pauta profesional."
        )

    return (
        "No se han detectado ingredientes problemáticos evidentes en el texto leído, "
        "pero la imagen puede no contener toda la lista de ingredientes o el OCR puede no haberla leído completa."
    )


def analyze_fodmap_risk(text: str) -> dict[str, Any]:
    clean_text = _safe_text(text)

    fodmap_hits = _scan_rules(clean_text, HIGH_FODMAP_RULES)
    gluten_hits = _scan_rules(clean_text, GLUTEN_RULES)
    lactose_hits = _scan_rules(clean_text, LACTOSE_RULES)
    caution_hits = _scan_rules(clean_text, NUTRITIONAL_CAUTION_RULES)

    score = _calculate_risk_score(
        fodmap_hits=fodmap_hits,
        gluten_hits=gluten_hits,
        lactose_hits=lactose_hits,
        caution_hits=caution_hits,
    )

    risk = _risk_level(score)

    detected_ingredients = _flatten_detected(
        fodmap_hits + gluten_hits + lactose_hits + caution_hits
    )

    return {
        "risk": risk,
        "risk_score": score,
        "detected_ingredients": detected_ingredients,
        "fodmap_hits": fodmap_hits,
        "gluten_hits": gluten_hits,
        "lactose_hits": lactose_hits,
        "caution_hits": caution_hits,
        "message": _build_message(
            risk=risk,
            fodmap_hits=fodmap_hits,
            gluten_hits=gluten_hits,
            lactose_hits=lactose_hits,
            caution_hits=caution_hits,
        ),
        "professional_notice": PROFESSIONAL_NOTICE,
        "analysis_scope": {
            "uses_ocr_text": True,
            "uses_kaggle_nutrition_dataset": False,
            "note": (
                "El dataset de Kaggle aporta valores nutricionales como calorías, proteínas, hidratos, grasas, fibra, sodio "
                "y densidad nutricional. La detección de FODMAPs, gluten o lactosa se basa en reglas de ingredientes, "
                "porque esos campos no vienen medidos directamente en el dataset."
            ),
        },
    }