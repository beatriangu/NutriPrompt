from __future__ import annotations

import logging
import unicodedata
from typing import Any

logger = logging.getLogger(__name__)

PROFILE_LABELS = [
    "perder peso",
    "ganar energía",
    "ganar masa muscular",
    "organizar comidas",
    "comer más equilibrado",
    "alta proteína",
    "sin lactosa",
    "sin gluten",
    "bajo en FODMAPs",
    "vegetariano",
    "vegano",
    "pescetariano",
    "digestiones pesadas",
    "hinchazón frecuente",
    "poco tiempo para cocinar",
    "presupuesto ajustado",
]

ZERO_SHOT_MODEL = "joeddav/xlm-roberta-large-xnli"
DEFAULT_THRESHOLD = 0.60

_classifier = None

STRICT_RULE_ONLY_TAGS = {
    "sin lactosa",
    "sin gluten",
    "bajo en FODMAPs",
    "vegetariano",
    "vegano",
    "pescetariano",
}

SOFT_HF_TAGS = {
    "perder peso",
    "ganar energía",
    "ganar masa muscular",
    "organizar comidas",
    "comer más equilibrado",
    "alta proteína",
    "digestiones pesadas",
    "hinchazón frecuente",
    "poco tiempo para cocinar",
    "presupuesto ajustado",
}


def _load_classifier():
    global _classifier

    if _classifier is not None:
        return _classifier

    try:
        from transformers import pipeline

        _classifier = pipeline(
            "zero-shot-classification",
            model=ZERO_SHOT_MODEL,
        )
        logger.info("Clasificador de perfil cargado correctamente: %s", ZERO_SHOT_MODEL)
        return _classifier

    except Exception as exc:
        logger.exception("No se ha podido cargar el clasificador de Hugging Face: %s", exc)
        return None


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_any(text: str, keywords: list[str] | set[str]) -> bool:
    normalized_text = _normalize_text(text)
    return any(_normalize_text(keyword) in normalized_text for keyword in keywords)


def _build_classification_text(
    objetivo: str,
    restricciones: str,
    preferencias: str,
    presupuesto: str,
    meal_context: str,
    special_situation: str,
) -> str:
    parts = [
        f"Objetivo: {_safe_text(objetivo)}",
        f"Restricciones: {_safe_text(restricciones)}",
        f"Preferencias: {_safe_text(preferencias)}",
        f"Presupuesto: {_safe_text(presupuesto)}",
        f"Contexto: {_safe_text(meal_context)}",
        f"Situación especial: {_safe_text(special_situation)}",
    ]
    return "\n".join(parts)


def _rule_based_tags(
    objetivo: str,
    restricciones: str,
    preferencias: str,
    presupuesto: str,
    meal_context: str,
    special_situation: str,
    needs_tupper: str,
    has_kitchen: str,
    days_away: str,
) -> list[str]:
    tags: set[str] = set()

    objetivo_text = _normalize_text(objetivo)
    restricciones_text = _normalize_text(restricciones)
    preferencias_text = _normalize_text(preferencias)
    presupuesto_text = _normalize_text(presupuesto)
    meal_context_text = _normalize_text(meal_context)
    special_situation_text = _normalize_text(special_situation)
    needs_tupper_text = _normalize_text(needs_tupper)
    has_kitchen_text = _normalize_text(has_kitchen)
    days_away_text = _safe_text(days_away)

    combined = " ".join(
        [
            objetivo_text,
            restricciones_text,
            preferencias_text,
            presupuesto_text,
            meal_context_text,
            special_situation_text,
        ]
    )

    if _contains_any(combined, {"perder peso", "adelgazar", "perder grasa", "deficit", "déficit"}):
        tags.add("perder peso")

    if _contains_any(combined, {"energia", "energía", "cansancio", "fatiga", "agotamiento"}):
        tags.add("ganar energía")

    if _contains_any(combined, {"musculo", "músculo", "masa muscular", "ganar masa", "hipertrofia"}):
        tags.add("ganar masa muscular")

    if _contains_any(combined, {"organizar", "planificar", "rutina"}):
        tags.add("organizar comidas")

    if _contains_any(combined, {"equilibrado", "equilibrada", "saludable", "mejorar alimentacion", "mejorar alimentación"}):
        tags.add("comer más equilibrado")

    if _contains_any(combined, {"proteina", "proteína", "proteico", "proteica"}):
        tags.add("alta proteína")

    if _contains_any(combined, {"sin lactosa", "lactosa", "lacteos", "lácteos", "leche"}):
        tags.add("sin lactosa")

    if _contains_any(combined, {"sin gluten", "gluten", "celiaquia", "celiaquía", "celiac"}):
        tags.add("sin gluten")

    if _contains_any(combined, {"fodmap", "fodmaps", "low fodmap", "bajo en fodmaps", "baja en fodmaps", "sibo"}):
        tags.add("bajo en FODMAPs")

    if _contains_any(combined, {"digestiones pesadas", "digestivo", "pesadez", "reflujo"}):
        tags.add("digestiones pesadas")

    if _contains_any(combined, {"hinchazon", "hinchazón", "inflamacion", "inflamación", "gases", "distension", "distensión"}):
        tags.add("hinchazón frecuente")

    if _contains_any(combined, {"vegano", "vegana", "vegan"}):
        tags.add("vegano")

    if _contains_any(combined, {"vegetariano", "vegetariana", "vegetarian"}):
        tags.add("vegetariano")

    if _contains_any(combined, {"pescetariano", "pescetariana", "pescetarian"}):
        tags.add("pescetariano")

    if _contains_any(combined, {"rapido", "rápido", "poco tiempo", "sin tiempo", "trabajo", "laboral"}):
        tags.add("poco tiempo para cocinar")

    if _contains_any(combined, {"economico", "económico", "economica", "económica", "barato", "barata", "ajustado", "ajustada", "ahorro"}):
        tags.add("presupuesto ajustado")

    if needs_tupper_text in {"yes", "si", "sí"}:
        tags.add("necesita tupper")

    if has_kitchen_text == "no":
        tags.add("sin cocina")
    elif has_kitchen_text in {"acceso limitado", "limited"}:
        tags.add("cocina limitada")

    try:
        if int(days_away_text) > 0:
            tags.add("días fuera de casa")
    except (TypeError, ValueError):
        pass

    if meal_context_text == "travel" or special_situation_text == "travel":
        tags.add("días fuera de casa")

    return sorted(tags)


def _hf_tags(
    objetivo: str,
    restricciones: str,
    preferencias: str,
    presupuesto: str,
    meal_context: str,
    special_situation: str,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[str]:
    classifier = _load_classifier()
    if classifier is None:
        return []

    sequence = _build_classification_text(
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
        meal_context=meal_context,
        special_situation=special_situation,
    )

    try:
        result = classifier(
            sequence,
            candidate_labels=PROFILE_LABELS,
            multi_label=True,
        )

        labels = result.get("labels", [])
        scores = result.get("scores", [])

        selected = [
            label
            for label, score in zip(labels, scores)
            if float(score) >= threshold and label in SOFT_HF_TAGS
        ]

        logger.info("Etiquetas detectadas por Hugging Face: %s", selected)
        return selected

    except Exception as exc:
        logger.exception("Ha fallado la clasificación zero-shot: %s", exc)
        return []


def _post_process_tags(tags: list[str]) -> list[str]:
    tag_set = {tag for tag in tags if tag}

    if "vegano" in tag_set:
        tag_set.discard("vegetariano")
        tag_set.discard("pescetariano")

    if "pescetariano" in tag_set:
        tag_set.discard("vegetariano")

    if "sin cocina" in tag_set:
        tag_set.discard("cocina limitada")

    return sorted(tag_set)


def classify_user_profile(
    objetivo: str,
    restricciones: str,
    preferencias: str,
    presupuesto: str,
    meal_context: str,
    special_situation: str,
    needs_tupper: str,
    has_kitchen: str,
    days_away: str,
) -> list[str]:
    rule_tags = _rule_based_tags(
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
        meal_context=meal_context,
        special_situation=special_situation,
        needs_tupper=needs_tupper,
        has_kitchen=has_kitchen,
        days_away=days_away,
    )

    hf_tags = _hf_tags(
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
        meal_context=meal_context,
        special_situation=special_situation,
    )

    final_tags = _post_process_tags(rule_tags + hf_tags)
    logger.info("Etiquetas finales de perfil: %s", final_tags)
    return final_tags