from __future__ import annotations

import re
import unicodedata
from typing import Any


PROFESSIONAL_NOTICE = (
    "Este análisis es orientativo y no sustituye la valoración de un profesional "
    "sanitario o nutricional. Si existe una pauta profesional, debe prevalecer "
    "sobre cualquier sugerencia automática."
)


SAFE_PATTERNS = {
    "sin gluten",
    "gluten free",
    "sin lactosa",
    "lactose free",
    "sin azucar anadido",
    "sin azucar añadido",
    "no contiene gluten",
    "no contiene lactosa",
}


HIGH_FODMAP_RULES = {
    "ajo": ["ajo", "ajo en polvo", "extracto de ajo"],
    "cebolla": ["cebolla", "cebolla en polvo", "cebolla deshidratada", "extracto de cebolla"],
    "trigo": ["trigo", "harina de trigo", "semola de trigo", "sémola de trigo"],
    "lactosa": ["lactosa", "leche", "leche en polvo", "suero de leche", "nata"],
    "miel": ["miel"],
    "fructosa": ["fructosa", "jarabe de fructosa", "jarabe de maiz alto en fructosa"],
    "inulina": ["inulina", "fibra de achicoria", "achicoria"],
    "polioles": ["sorbitol", "manitol", "xilitol", "maltitol", "isomalt"],
    "legumbres": ["garbanzos", "lentejas", "alubias", "judias", "judías", "frijoles"],
    "frutas altas en FODMAP": ["manzana", "pera", "sandia", "sandía", "mango", "cerezas"],
    "verduras altas en FODMAP": ["coliflor", "champinon", "champiñon", "champiñones", "setas"],
}


GLUTEN_RULES = {
    "gluten": ["gluten"],
    "trigo": ["trigo", "harina de trigo", "semola", "sémola"],
    "cebada": ["cebada", "malta", "extracto de malta"],
    "centeno": ["centeno"],
}


LACTOSE_RULES = {
    "lactosa": ["lactosa"],
    "leche": ["leche", "leche en polvo"],
    "derivados lacteos": ["suero de leche", "nata", "queso", "mantequilla"],
}


NUTRITIONAL_CAUTION_RULES = {
    "azucares añadidos": ["azucar", "azúcar", "glucosa", "dextrosa", "jarabe", "sirope"],
    "sodio / sal": ["sal", "sodio", "glutamato monosodico", "glutamato monosódico"],
    "ultraprocesado": ["potenciador del sabor", "aroma", "colorante", "conservador", "estabilizante"],
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9ñáéíóúü\s/-]", " ", text)
    return " ".join(text.split())


def _remove_safe_patterns(text: str) -> str:
    normalized = _normalize_text(text)

    for pattern in SAFE_PATTERNS:
        normalized = normalized.replace(_normalize_text(pattern), " ")

    return " ".join(normalized.split())


def _contains_term(text: str, term: str) -> bool:
    normalized_text = _remove_safe_patterns(text)
    normalized_term = _normalize_text(term)

    if not normalized_term:
        return False

    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def _scan_rules(text: str, rules: dict[str, list[str]]) -> list[dict[str, Any]]:
    detected: list[dict[str, Any]] = []

    for category, variants in rules.items():
        matches = [variant for variant in variants if _contains_term(text, variant)]

        if matches:
            detected.append(
                {
                    "category": category,
                    "matches": sorted(set(matches), key=_normalize_text),
                }
            )

    return detected


def _flatten_detected(detected: list[dict[str, Any]]) -> list[str]:
    ingredients: list[str] = []

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
    score += len(gluten_hits) * 3
    score += len(lactose_hits) * 2
    score += len(caution_hits)

    return score


def _risk_level(score: int) -> str:
    if score >= 8:
        return "high"

    if score >= 4:
        return "medium_high"

    if score >= 1:
        return "medium"

    return "low_unknown"


def _build_summary(
    *,
    fodmap_hits: list[dict[str, Any]],
    gluten_hits: list[dict[str, Any]],
    lactose_hits: list[dict[str, Any]],
    caution_hits: list[dict[str, Any]],
) -> list[str]:
    summary: list[str] = []

    if fodmap_hits:
        summary.append("Se han detectado ingredientes que pueden ser sensibles en un enfoque bajo en FODMAPs.")

    if gluten_hits:
        summary.append("Se han detectado posibles ingredientes con gluten o relacionados con cereales con gluten.")

    if lactose_hits:
        summary.append("Se han detectado posibles ingredientes con lactosa o derivados lácteos.")

    if caution_hits:
        summary.append("Se han detectado elementos nutricionales a revisar, como azúcares añadidos, sal o aditivos.")

    if not summary:
        summary.append("No se han detectado ingredientes problemáticos evidentes en el texto analizado.")

    return summary


def _build_message(risk: str) -> str:
    messages = {
        "high": (
            "Se han detectado varias señales relevantes. Este producto podría no encajar "
            "con determinadas restricciones indicadas, especialmente si la persona sigue una pauta "
            "baja en FODMAPs, sin gluten o sin lactosa."
        ),
        "medium_high": (
            "Se han detectado posibles ingredientes sensibles. Conviene revisar la etiqueta completa "
            "y contrastarla con las restricciones antes de incluir el producto en el plan."
        ),
        "medium": (
            "Se ha detectado alguna señal a revisar. La compatibilidad puede depender del contexto, "
            "la cantidad, la tolerancia individual y la pauta profesional."
        ),
        "low_unknown": (
            "No se han detectado ingredientes problemáticos evidentes en el texto leído. Aun así, "
            "el OCR puede no haber capturado toda la etiqueta."
        ),
    }

    return messages.get(risk, messages["low_unknown"])


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
    all_hits = fodmap_hits + gluten_hits + lactose_hits + caution_hits

    return {
        "risk": risk,
        "risk_score": score,
        "detected_ingredients": _flatten_detected(all_hits),
        "fodmap_hits": fodmap_hits,
        "gluten_hits": gluten_hits,
        "lactose_hits": lactose_hits,
        "caution_hits": caution_hits,
        "summary": _build_summary(
            fodmap_hits=fodmap_hits,
            gluten_hits=gluten_hits,
            lactose_hits=lactose_hits,
            caution_hits=caution_hits,
        ),
        "message": _build_message(risk),
        "professional_notice": PROFESSIONAL_NOTICE,
        "analysis_scope": {
            "uses_ocr_text": True,
            "uses_rule_based_detection": True,
            "uses_kaggle_nutrition_dataset": False,
            "note": (
                "La detección se basa en reglas de ingredientes extraídos mediante OCR. "
                "El dataset nutricional puede enriquecer valores como calorías, proteínas, hidratos, grasas, fibra o sodio, "
                "pero no sustituye la lectura de ingredientes ni una validación profesional."
            ),
        },
    }