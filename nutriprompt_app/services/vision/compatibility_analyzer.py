from __future__ import annotations

import logging
from typing import Any

from .nutrition_risk_rules import analyze_nutrition_risk


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


def _safe_list(value: Any) -> list:
    if isinstance(value, list):
        return value

    if not value:
        return []

    return [value]


def _normalize_restrictions(restrictions: list[str] | None) -> list[str]:
    normalized = []

    for restriction in _safe_list(restrictions):
        text = str(restriction or "").strip()

        if text:
            normalized.append(text)

    return sorted(set(normalized))


def _extract_detected_items(analysis: dict[str, Any]) -> list[str]:
    detected_items = analysis.get("detected_items") or []
    fodmap_analysis = analysis.get("fodmap_analysis") or {}
    detected_ingredients = fodmap_analysis.get("detected_ingredients") or []

    items = [*detected_items, *detected_ingredients]

    return sorted(set(str(item).strip() for item in items if str(item).strip()))


def _extract_alert_categories(analysis: dict[str, Any]) -> set[str]:
    fodmap_analysis = analysis.get("fodmap_analysis") or {}

    categories = set()

    if fodmap_analysis.get("fodmap_hits"):
        categories.add("low_fodmap")

    if fodmap_analysis.get("gluten_hits"):
        categories.add("sin_gluten")

    if fodmap_analysis.get("lactose_hits"):
        categories.add("sin_lactosa")

    for warning in analysis.get("detected_warnings") or []:
        category = warning.get("category")

        if category == "gluten":
            categories.add("sin_gluten")

        if category == "lactosa":
            categories.add("sin_lactosa")

        if category == "fodmap":
            categories.add("low_fodmap")

    return categories


def _build_plan_profile(plan_analysis: dict[str, Any] | None) -> dict[str, Any]:
    if not plan_analysis:
        return {
            "detected_restrictions": [],
            "detected_goals": [],
            "summary": "No se ha aportado una pauta nutricional para comparar.",
        }

    restrictions = _normalize_restrictions(plan_analysis.get("detected_restrictions"))
    goals = _safe_list(plan_analysis.get("detected_goals"))

    return {
        "detected_restrictions": restrictions,
        "detected_goals": goals,
        "summary": _build_plan_summary(restrictions, goals),
    }


def _build_plan_summary(restrictions: list[str], goals: list[str]) -> str:
    if not restrictions and not goals:
        return "La pauta aportada no contiene restricciones u objetivos detectados de forma clara."

    parts = []

    if restrictions:
        visible_restrictions = [
            PLAN_RESTRICTION_LABELS.get(item, item)
            for item in restrictions
        ]
        parts.append("Restricciones detectadas: " + ", ".join(visible_restrictions))

    if goals:
        parts.append("Objetivos detectados: " + ", ".join(goals))

    return ". ".join(parts) + "."


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
        message = (
            "Se han detectado señales que podrían entrar en conflicto con la pauta indicada: "
            + ", ".join(PLAN_RESTRICTION_LABELS.get(item, item) for item in matched_restrictions)
            + "."
        )
    elif alert_categories:
        compatibility = "review"
        message = (
            "Se han detectado señales nutricionales a revisar, aunque no coinciden claramente "
            "con las restricciones extraídas de la pauta."
        )
    elif items:
        compatibility = "compatible"
        message = (
            "No se han detectado conflictos evidentes con la pauta analizada. "
            "Aun así, conviene revisar cantidades, tolerancia individual e indicaciones profesionales."
        )
    else:
        compatibility = "unknown"
        message = (
            "No hay suficiente información detectada para confirmar compatibilidad. "
            "Prueba con una imagen más clara o una pauta más legible."
        )

    return {
        "intake_type": intake_type,
        "compatibility": compatibility,
        "compatibility_label": COMPATIBILITY_LEVELS[compatibility],
        "message": message,
        "matched_restrictions": matched_restrictions,
        "detected_items": items,
        "alert_categories": sorted(alert_categories),
        "source_analysis": analysis,
    }


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

    evaluations = []

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
        "professional_notice": (
            "Este análisis es orientativo. No sustituye la valoración de un profesional "
            "sanitario o nutricional. Si existe una pauta profesional, debe prevalecer."
        ),
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
    items = []

    for evaluation in evaluations:
        items.extend(evaluation.get("detected_items", []))

    return sorted(set(items))


def _collect_items_by_status(
    evaluations: list[dict[str, Any]],
    statuses: set[str],
) -> list[str]:
    items = []

    for evaluation in evaluations:
        if evaluation.get("compatibility") in statuses:
            items.extend(evaluation.get("detected_items", []))

    return sorted(set(items))