from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

try:
    from nutriprompt_app.services.rag.rag_context_builder import build_rag_context
except Exception:
    build_rag_context = None

from .nutrition_risk_rules import analyze_fodmap_risk


logger = logging.getLogger(__name__)


PLAN_RESTRICTION_LABELS = {
    "sin_gluten": "Sin gluten",
    "sin_lactosa": "Sin lactosa",
    "low_fodmap": "Bajo en FODMAPs",
    "vegetariano": "Vegetariano",
    "vegano": "Vegano",
    "pescetariano": "Pescetariano",
}

COMPATIBILITY_LEVELS = {
    "compatible": "Compatible",
    "review": "Revisar",
    "not_compatible": "No compatible",
    "unknown": "Información insuficiente",
}

PROFESSIONAL_NOTICE = (
    "Este análisis es orientativo y no sustituye la valoración de un profesional "
    "sanitario o nutricional. Si existe una pauta profesional, debe prevalecer."
)


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value

    if value in (None, "", [], {}, ()):
        return []

    return [value]


def _normalize_restriction_name(value: Any) -> str:
    text = _normalize_text(value)

    aliases = {
        "sin gluten": "sin_gluten",
        "gluten free": "sin_gluten",
        "gluten-free": "sin_gluten",
        "celiaco": "sin_gluten",
        "celiaca": "sin_gluten",
        "celíaco": "sin_gluten",
        "celíaca": "sin_gluten",
        "sin lactosa": "sin_lactosa",
        "lactose free": "sin_lactosa",
        "lactose-free": "sin_lactosa",
        "bajo en fodmaps": "low_fodmap",
        "bajo en fodmap": "low_fodmap",
        "low fodmap": "low_fodmap",
        "fodmap": "low_fodmap",
        "fodmaps": "low_fodmap",
        "vegetariano": "vegetariano",
        "vegetariana": "vegetariano",
        "vegano": "vegano",
        "vegana": "vegano",
        "pescetariano": "pescetariano",
        "pescetariana": "pescetariano",
    }

    return aliases.get(text, text)


def _normalize_restrictions(restrictions: list[str] | None) -> list[str]:
    normalized: list[str] = []

    for restriction in _safe_list(restrictions):
        restriction_key = _normalize_restriction_name(restriction)

        if restriction_key:
            normalized.append(restriction_key)

    return sorted(set(normalized))


def _build_plan_summary(restrictions: list[str], goals: list[str]) -> str:
    if not restrictions and not goals:
        return "La pauta aportada no contiene restricciones u objetivos detectados de forma clara."

    parts: list[str] = []

    if restrictions:
        visible_restrictions = [
            PLAN_RESTRICTION_LABELS.get(item, item)
            for item in restrictions
        ]
        parts.append("Restricciones detectadas: " + ", ".join(visible_restrictions))

    if goals:
        parts.append("Objetivos detectados: " + ", ".join(str(goal) for goal in goals))

    return ". ".join(parts) + "."


def _build_plan_profile(plan_analysis: dict[str, Any] | None) -> dict[str, Any]:
    if not plan_analysis:
        return {
            "detected_restrictions": [],
            "detected_goals": [],
            "summary": "No se ha aportado una pauta nutricional para comparar.",
        }

    restrictions = _normalize_restrictions(plan_analysis.get("detected_restrictions"))
    goals = [str(goal).strip() for goal in _safe_list(plan_analysis.get("detected_goals")) if str(goal).strip()]

    return {
        "detected_restrictions": restrictions,
        "detected_goals": goals,
        "summary": _build_plan_summary(restrictions, goals),
    }


def _extract_text_from_analysis(analysis: dict[str, Any]) -> str:
    candidates = [
        analysis.get("ocr_text"),
        analysis.get("extracted_text"),
        analysis.get("text"),
        analysis.get("raw_text"),
        analysis.get("label_text"),
        analysis.get("ingredients_text"),
    ]

    return "\n".join(_safe_text(item) for item in candidates if _safe_text(item))


def _ensure_fodmap_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    existing = analysis.get("fodmap_analysis")

    if isinstance(existing, dict) and existing:
        return existing

    text = _extract_text_from_analysis(analysis)

    if not text:
        return {}

    try:
        return analyze_fodmap_risk(text)
    except Exception as exc:
        logger.warning("Could not analyze nutrition risk from OCR text: %s", exc)
        return {}


def _extract_detected_items(analysis: dict[str, Any]) -> list[str]:
    detected_items = _safe_list(analysis.get("detected_items"))
    detected_foods = _safe_list(analysis.get("detected_foods"))
    detected_ingredients = _safe_list(analysis.get("detected_ingredients"))

    fodmap_analysis = _ensure_fodmap_analysis(analysis)
    risk_detected_ingredients = _safe_list(fodmap_analysis.get("detected_ingredients"))

    items = [
        *detected_items,
        *detected_foods,
        *detected_ingredients,
        *risk_detected_ingredients,
    ]

    return sorted(
        {str(item).strip() for item in items if str(item).strip()},
        key=_normalize_text,
    )


def _extract_alert_categories(analysis: dict[str, Any]) -> set[str]:
    fodmap_analysis = _ensure_fodmap_analysis(analysis)
    categories: set[str] = set()

    if fodmap_analysis.get("fodmap_hits"):
        categories.add("low_fodmap")

    if fodmap_analysis.get("gluten_hits"):
        categories.add("sin_gluten")

    if fodmap_analysis.get("lactose_hits"):
        categories.add("sin_lactosa")

    for warning in _safe_list(analysis.get("detected_warnings")):
        if not isinstance(warning, dict):
            continue

        category = _normalize_text(warning.get("category"))

        if category in {"gluten", "sin_gluten"}:
            categories.add("sin_gluten")

        if category in {"lactosa", "lactose", "sin_lactosa"}:
            categories.add("sin_lactosa")

        if category in {"fodmap", "fodmaps", "low_fodmap"}:
            categories.add("low_fodmap")

    return categories


def _build_rag_support_context(
    *,
    items: list[str],
    plan_restrictions: list[str],
) -> str:
    if build_rag_context is None:
        return ""

    query = " ".join([*items, *plan_restrictions]).strip()

    if not query:
        return ""

    try:
        return build_rag_context(query=query, top_k=3)
    except Exception as exc:
        logger.warning("Could not build RAG support context: %s", exc)
        return ""


def _build_evaluation_message(
    *,
    compatibility: str,
    matched_restrictions: list[str],
    alert_categories: set[str],
) -> str:
    if compatibility == "not_compatible":
        visible = ", ".join(
            PLAN_RESTRICTION_LABELS.get(item, item)
            for item in matched_restrictions
        )
        return (
            "Se han detectado señales que podrían entrar en conflicto con la pauta indicada: "
            f"{visible}. Conviene revisar este producto antes de incluirlo en el plan."
        )

    if compatibility == "review":
        visible = ", ".join(
            PLAN_RESTRICTION_LABELS.get(item, item)
            for item in sorted(alert_categories)
        )
        return (
            "Se han detectado señales nutricionales a revisar"
            + (f" relacionadas con: {visible}." if visible else ".")
        )

    if compatibility == "compatible":
        return (
            "No se han detectado conflictos evidentes con la pauta analizada. "
            "Aun así, conviene revisar cantidades, tolerancia individual e indicaciones profesionales."
        )

    return (
        "No hay suficiente información detectada para confirmar compatibilidad. "
        "Prueba con una imagen más clara o una etiqueta más legible."
    )


def _evaluate_single_analysis(
    *,
    analysis: dict[str, Any],
    plan_restrictions: list[str],
) -> dict[str, Any]:
    intake_type = analysis.get("intake_type", "product_label")
    items = _extract_detected_items(analysis)
    alert_categories = _extract_alert_categories(analysis)
    matched_restrictions = sorted(set(plan_restrictions) & alert_categories)

    if matched_restrictions:
        compatibility = "not_compatible"
    elif alert_categories:
        compatibility = "review"
    elif items:
        compatibility = "compatible"
    else:
        compatibility = "unknown"

    rag_context = _build_rag_support_context(
        items=items,
        plan_restrictions=plan_restrictions,
    )

    return {
        "intake_type": intake_type,
        "compatibility": compatibility,
        "compatibility_label": COMPATIBILITY_LEVELS[compatibility],
        "message": _build_evaluation_message(
            compatibility=compatibility,
            matched_restrictions=matched_restrictions,
            alert_categories=alert_categories,
        ),
        "matched_restrictions": matched_restrictions,
        "detected_items": items,
        "alert_categories": sorted(alert_categories),
        "rag_context": rag_context,
        "risk_analysis": _ensure_fodmap_analysis(analysis),
        "source_analysis": analysis,
    }


def _calculate_global_status(evaluations: list[dict[str, Any]]) -> str:
    if not evaluations:
        return "unknown"

    statuses = {evaluation["compatibility"] for evaluation in evaluations}

    if "not_compatible" in statuses:
        return "not_compatible"

    if "review" in statuses:
        return "review"

    if "compatible" in statuses:
        return "compatible"

    return "unknown"


def _build_global_message(
    status: str,
    evaluations: list[dict[str, Any]],
    plan_profile: dict[str, Any],
) -> str:
    if status == "not_compatible":
        return (
            "Hay alimentos o productos que podrían no ser compatibles con la pauta detectada. "
            "Revisa las alertas antes de usarlos en el plan."
        )

    if status == "review":
        return (
            "No se ha detectado una incompatibilidad directa, pero hay elementos que conviene revisar "
            "antes de incorporarlos al plan."
        )

    if status == "compatible":
        return (
            "Los alimentos detectados parecen compatibles con la información analizada, "
            "siempre que las cantidades y la pauta profesional lo permitan."
        )

    return (
        "No hay suficiente información para valorar compatibilidad. "
        + plan_profile.get("summary", "")
    )


def _collect_available_items(evaluations: list[dict[str, Any]]) -> list[str]:
    items: list[str] = []

    for evaluation in evaluations:
        items.extend(evaluation.get("detected_items", []))

    return sorted(set(items), key=_normalize_text)


def _collect_items_by_status(
    evaluations: list[dict[str, Any]],
    statuses: set[str],
) -> list[str]:
    items: list[str] = []

    for evaluation in evaluations:
        if evaluation.get("compatibility") in statuses:
            items.extend(evaluation.get("detected_items", []))

    return sorted(set(items), key=_normalize_text)


def analyze_context_compatibility(
    *,
    plan_analysis: dict[str, Any] | None = None,
    pantry_analyses: list[dict[str, Any]] | None = None,
    fridge_analyses: list[dict[str, Any]] | None = None,
    product_analyses: list[dict[str, Any]] | None = None,
    ingredient_analyses: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    plan_profile = _build_plan_profile(plan_analysis)
    plan_restrictions = plan_profile["detected_restrictions"]

    grouped_inputs = {
        "pantry": pantry_analyses or [],
        "fridge": fridge_analyses or [],
        "products": product_analyses or [],
        "ingredients": ingredient_analyses or [],
    }

    evaluations: list[dict[str, Any]] = []

    for group_name, analyses in grouped_inputs.items():
        for analysis in analyses:
            evaluations.append(
                {
                    "group": group_name,
                    **_evaluate_single_analysis(
                        analysis=analysis,
                        plan_restrictions=plan_restrictions,
                    ),
                }
            )

    global_status = _calculate_global_status(evaluations)

    return {
        "global_status": global_status,
        "global_label": COMPATIBILITY_LEVELS[global_status],
        "global_message": _build_global_message(global_status, evaluations, plan_profile),
        "plan_profile": plan_profile,
        "evaluations": evaluations,
        "available_items": _collect_available_items(evaluations),
        "items_to_review": _collect_items_by_status(evaluations, {"review", "not_compatible"}),
        "compatible_items": _collect_items_by_status(evaluations, {"compatible"}),
        "professional_notice": PROFESSIONAL_NOTICE,
    }