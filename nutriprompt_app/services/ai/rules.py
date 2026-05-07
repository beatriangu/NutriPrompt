from __future__ import annotations

import re
import unicodedata


PROFILE_TAG_GUIDANCE = {
    "perder peso": [
        "Evita prometer pérdida de peso.",
        "Propón comidas sencillas, saciantes y realistas sin lenguaje restrictivo.",
    ],
    "ganar energía": [
        "Propón comidas completas y sostenibles para la rutina semanal.",
        "Evita prometer efectos sobre energía o salud.",
    ],
    "ganar masa muscular": [
        "Incluye proteína de forma práctica y coherente con restricciones y preferencias.",
        "Evita prometer ganancia muscular.",
    ],
    "organizar comidas": [
        "Favorece recetas repetibles, simples y fáciles de planificar para varios días.",
        "Reutiliza ingredientes de forma inteligente durante la semana.",
    ],
    "comer más equilibrado": [
        "Mantén un patrón semanal variado, sencillo y fácil de seguir.",
        "Evita rigidez excesiva.",
    ],
    "alta proteína": [
        "Incluye fuentes de proteína compatibles con restricciones y preferencias.",
    ],
    "sin lactosa": [
        "Asegúrate de que todas las propuestas sean compatibles con una pauta sin lactosa.",
        "Puedes usar alternativas vegetales o productos claramente indicados como sin lactosa.",
    ],
    "sin gluten": [
        "Asegúrate de que todas las propuestas sean compatibles con una pauta sin gluten.",
        "Si usas pan, pasta, wraps o avena, deben indicarse como sin gluten.",
    ],
    "bajo en FODMAPs": [
        "Mantén el plan suave, sencillo y compatible con un enfoque bajo en FODMAPs.",
        "No hagas afirmaciones médicas ni prometas mejora de síntomas.",
    ],
    "vegetariano": [
        "No incluyas carne, pescado ni marisco.",
        "Usa opciones vegetarianas simples y realistas.",
    ],
    "vegano": [
        "No incluyas carne, pescado, marisco, huevos, lácteos, miel ni productos de origen animal.",
        "Usa opciones veganas simples, prácticas y realistas.",
    ],
    "pescetariano": [
        "No incluyas carne.",
        "Puedes usar pescado y marisco como proteína animal.",
    ],
    "digestiones pesadas": [
        "Propón preparaciones suaves y sencillas.",
        "No hagas afirmaciones médicas.",
    ],
    "hinchazón frecuente": [
        "Propón platos sencillos y suaves.",
        "Recomienda consultar con un profesional si los síntomas persisten.",
    ],
    "poco tiempo para cocinar": [
        "Prioriza recetas rápidas, muy simples y con pocos pasos.",
        "Favorece cocciones sencillas y preparaciones de baja elaboración.",
    ],
    "presupuesto ajustado": [
        "Usa ingredientes asequibles, fáciles de encontrar y reutilizables durante la semana.",
        "Evita ingredientes caros, exóticos o difíciles de conseguir.",
    ],
    "necesita tupper": [
        "Favorece comidas transportables y fáciles de conservar.",
    ],
    "sin cocina": [
        "No propongas recetas que requieran cocinar.",
        "Usa opciones de montaje, frías o muy fáciles de resolver fuera de casa.",
    ],
    "cocina limitada": [
        "Usa comidas de preparación mínima y técnicas muy simples.",
    ],
    "días fuera de casa": [
        "Haz el plan especialmente práctico para comer fuera o con logística limitada.",
    ],
}


FIELD_ALIASES = {
    "nombre": ["nombre", "cliente"],
    "objetivo": ["objetivo"],
    "restricciones": ["restricciones", "restriccion", "restricción"],
    "preferencias": ["preferencias", "preferencia"],
    "presupuesto": ["presupuesto semanal", "presupuesto"],
    "contexto_principal": ["contexto principal", "contexto"],
    "situacion_especial": ["situacion especial", "situación especial", "situacion", "situación"],
    "necesita_tupper": ["¿necesita tupper?", "necesita tupper", "tupper"],
    "acceso_cocina": ["acceso a cocina", "cocina"],
    "dias_fuera": ["dias fuera de casa", "días fuera de casa", "dias fuera", "días fuera"],
    "etiquetas_perfil": ["etiquetas de perfil detectadas", "etiquetas de perfil", "perfil detectado"],
}


def _normalize_text(value: str) -> str:
    value = (value or "").strip().casefold()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"\s+", " ", value)
    return value


def _extract_field(user_input: str, canonical_field: str) -> str:
    aliases = FIELD_ALIASES.get(canonical_field, [canonical_field])
    normalized_aliases = {_normalize_text(alias) for alias in aliases}

    for line in (user_input or "").splitlines():
        if ":" not in line:
            continue

        left, right = line.split(":", 1)

        if _normalize_text(left) in normalized_aliases:
            return right.strip()

    return ""


def _extract_profile_tags(user_input: str) -> list[str]:
    raw_tags = _extract_field(user_input, "etiquetas_perfil")

    if not raw_tags:
        return []

    tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    unique_tags: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        normalized_tag = _normalize_text(tag)

        if normalized_tag == _normalize_text("No detectadas"):
            continue

        if normalized_tag not in seen:
            seen.add(normalized_tag)
            unique_tags.append(tag)

    return unique_tags


def _contains_phrase(text: str, phrases: set[str] | list[str]) -> bool:
    normalized = _normalize_text(text)
    return any(_normalize_text(phrase) in normalized for phrase in phrases)


def _has_profile_tag(user_input: str, target_tag: str) -> bool:
    target_normalized = _normalize_text(target_tag)
    return any(_normalize_text(tag) == target_normalized for tag in _extract_profile_tags(user_input))


def _infer_rules(user_input: str) -> dict[str, bool]:
    restrictions = _extract_field(user_input, "restricciones")
    preferences = _extract_field(user_input, "preferencias")
    combined = " ".join([restrictions, preferences, ", ".join(_extract_profile_tags(user_input))])

    fish_only = _contains_phrase(
        preferences,
        {
            "solo pescado",
            "unicamente pescado",
            "únicamente pescado",
            "pescado solo",
            "only fish",
            "fish only",
            "solo pescado y marisco",
            "solo pescado y mariscos",
        },
    )

    lactose_free = _contains_phrase(
        combined,
        {"sin lactosa", "lactose free", "lactose-free", "no lactosa"},
    ) or _has_profile_tag(user_input, "sin lactosa")

    gluten_free = _contains_phrase(
        combined,
        {"sin gluten", "gluten free", "gluten-free", "no gluten"},
    ) or _has_profile_tag(user_input, "sin gluten")

    vegan = _contains_phrase(
        combined,
        {"vegano", "vegana", "vegan"},
    ) or _has_profile_tag(user_input, "vegano")

    vegetarian = _contains_phrase(
        combined,
        {"vegetariano", "vegetariana", "vegetarian"},
    ) or _has_profile_tag(user_input, "vegetariano")

    pescetarian = _contains_phrase(
        combined,
        {"pescetariano", "pescetariana", "pescetarian"},
    ) or _has_profile_tag(user_input, "pescetariano")

    if vegan:
        vegetarian = False
        pescetarian = False
        fish_only = False
    elif vegetarian:
        pescetarian = False
        fish_only = False

    low_fodmap = _contains_phrase(
        combined,
        {"low fodmap", "bajo en fodmaps", "baja en fodmaps", "fodmap", "fodmaps"},
    ) or _has_profile_tag(user_input, "bajo en FODMAPs")

    return {
        "fish_only": fish_only,
        "lactose_free": lactose_free,
        "gluten_free": gluten_free,
        "vegetarian": vegetarian,
        "vegan": vegan,
        "pescetarian": pescetarian,
        "low_fodmap": low_fodmap,
    }
