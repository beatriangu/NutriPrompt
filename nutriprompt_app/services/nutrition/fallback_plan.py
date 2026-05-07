from __future__ import annotations

import re
import unicodedata
from typing import Any

from nutriprompt_app.services.presentation.presentation_cleaner import clean_list, clean_meal_text


DAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

YES_VALUES = {"si", "sí", "yes", "true", "1"}
NO_VALUES = {"no", "false", "0"}
LIMITED_KITCHEN_VALUES = {"acceso limitado", "limited", "cocina limitada"}

STRICT_DIET_TAGS = {
    "sin lactosa",
    "sin gluten",
    "bajo en fodmaps",
    "vegano",
    "vegetariano",
    "pescetariano",
    "sin cocina",
    "cocina limitada",
    "necesita tupper",
}

SOFT_TAGS = {
    "alta proteína",
    "ganar masa muscular",
    "perder peso",
    "poco tiempo para cocinar",
}

MEAT_KEYWORDS = {
    "pollo",
    "pavo",
    "ternera",
    "carne",
    "jamon",
    "jamón",
    "hamburguesa",
    "pechuga",
    "carne picada",
}

FISH_KEYWORDS = {
    "pescado",
    "atun",
    "atún",
    "salmon",
    "salmón",
    "merluza",
    "bacalao",
    "caballa",
    "sardinas",
}


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_text(value: Any) -> str:
    text = _safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def _contains_any(text: str, keywords: set[str] | list[str] | tuple[str, ...]) -> bool:
    normalized_text = _normalize_text(text)
    return any(_normalize_text(keyword) in normalized_text for keyword in keywords)


def _extract_field(user_text: str, field_name: str) -> str:
    pattern = rf"^{re.escape(field_name)}:\s*(.*)$"

    for line in _safe_text(user_text).splitlines():
        match = re.match(pattern, line.strip(), re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return ""


def _extract_profile_tags_from_text(user_text: str) -> list[str]:
    raw = _extract_field(user_text, "Etiquetas de perfil detectadas")

    if not raw or _normalize_text(raw) == "no detectadas":
        return []

    return [tag.strip() for tag in raw.split(",") if tag.strip()]


def _coerce_int(value: Any, default: int = 0) -> int:
    try:
        number = int(_safe_text(value))
        return max(number, 0)
    except (TypeError, ValueError):
        return default


def _filter_profile_tags(profile_tags: list[str]) -> set[str]:
    normalized = {_normalize_text(tag) for tag in profile_tags}
    valid_tags = {_normalize_text(tag) for tag in STRICT_DIET_TAGS | SOFT_TAGS}
    return {tag for tag in normalized if tag in valid_tags}


def _build_user_text_from_kwargs(**kwargs: Any) -> str:
    profile_tags = kwargs.get("profile_tags") or []
    tags_text = ", ".join(profile_tags) if profile_tags else "No detectadas"

    return f"""
Nombre: {_safe_text(kwargs.get("nombre"))}
Objetivo: {_safe_text(kwargs.get("objetivo"))}
Restricciones: {_safe_text(kwargs.get("restricciones"))}
Preferencias: {_safe_text(kwargs.get("preferencias"))}
Presupuesto semanal: {_safe_text(kwargs.get("presupuesto"))}
Contexto principal: {_safe_text(kwargs.get("meal_context"))}
Situación especial: {_safe_text(kwargs.get("special_situation"))}
Necesita tupper: {_safe_text(kwargs.get("needs_tupper"))}
Acceso a cocina: {_safe_text(kwargs.get("has_kitchen"))}
Días fuera de casa: {_safe_text(kwargs.get("days_away"))}
Etiquetas de perfil detectadas: {tags_text}
""".strip()


def _build_context(user_text: str) -> dict[str, Any]:
    objetivo = _extract_field(user_text, "Objetivo")
    restricciones = _extract_field(user_text, "Restricciones")
    preferencias = _extract_field(user_text, "Preferencias")
    presupuesto = _extract_field(user_text, "Presupuesto semanal")
    meal_context = _extract_field(user_text, "Contexto principal")
    special_situation = _extract_field(user_text, "Situación especial")
    needs_tupper = _extract_field(user_text, "Necesita tupper")
    has_kitchen = _extract_field(user_text, "Acceso a cocina")
    days_away = _extract_field(user_text, "Días fuera de casa")
    profile_tags = _extract_profile_tags_from_text(user_text)

    filtered_profile_tags = _filter_profile_tags(profile_tags)

    objective_text = _normalize_text(objetivo)
    restrictions_text = _normalize_text(restricciones)
    preferences_text = _normalize_text(preferencias)
    meal_context_text = _normalize_text(meal_context)
    special_situation_text = _normalize_text(special_situation)
    needs_tupper_text = _normalize_text(needs_tupper)
    has_kitchen_text = _normalize_text(has_kitchen)

    explicit_combined = " ".join(
        [
            objective_text,
            restrictions_text,
            preferences_text,
            meal_context_text,
            special_situation_text,
        ]
    )

    is_lactose_free = _contains_any(
        restrictions_text,
        {"sin lactosa", "lactosa", "lacteos", "lácteos", "leche"},
    ) or "sin lactosa" in filtered_profile_tags

    is_gluten_free = _contains_any(
        restrictions_text,
        {"sin gluten", "gluten", "celiaquia", "celiac", "celíaca", "celiaca"},
    ) or "sin gluten" in filtered_profile_tags

    is_low_fodmap = _contains_any(
        explicit_combined,
        {"fodmap", "fodmaps", "low fodmap", "bajo en fodmaps", "sibo"},
    ) or "bajo en fodmaps" in filtered_profile_tags

    is_vegan = (
        _contains_any(explicit_combined, {"vegano", "vegana", "vegan"})
        or "vegano" in filtered_profile_tags
    )

    is_vegetarian = (
        _contains_any(explicit_combined, {"vegetariano", "vegetariana", "vegetarian"})
        or "vegetariano" in filtered_profile_tags
    )

    is_pescetarian = (
        _contains_any(explicit_combined, {"pescetariano", "pescetariana", "pescetarian"})
        or "pescetariano" in filtered_profile_tags
    )

    if is_vegan:
        is_vegetarian = False
        is_pescetarian = False
    elif is_vegetarian:
        is_pescetarian = False

    wants_meat = (
        _contains_any(preferences_text, MEAT_KEYWORDS)
        and not is_vegetarian
        and not is_vegan
        and not is_pescetarian
    )

    wants_fish = (
        _contains_any(preferences_text, FISH_KEYWORDS)
        and not is_vegetarian
        and not is_vegan
    )

    wants_high_protein = (
        _contains_any(
            explicit_combined,
            {
                "masa muscular",
                "alta proteina",
                "alta proteína",
                "hipertrofia",
                "ganar masa",
                "ganar musculo",
                "ganar músculo",
                "ganar energia",
                "ganar energía",
            },
        )
        or "alta proteína" in filtered_profile_tags
        or "ganar masa muscular" in filtered_profile_tags
    )

    wants_weight_loss = _contains_any(
        objective_text,
        {"adelgazar", "perder peso", "perder grasa", "deficit", "déficit"},
    ) or "perder peso" in filtered_profile_tags

    needs_quick_meals = _contains_any(
        explicit_combined,
        {"poco tiempo", "rapido", "rápido", "sin tiempo", "trabajo", "laboral"},
    ) or "poco tiempo para cocinar" in filtered_profile_tags

    needs_tupper_flag = (
        needs_tupper_text in YES_VALUES
        or "necesita tupper" in filtered_profile_tags
    )

    no_kitchen = (
        has_kitchen_text in NO_VALUES
        or "sin cocina" in filtered_profile_tags
    )

    limited_kitchen = (
        has_kitchen_text in LIMITED_KITCHEN_VALUES
        or "cocina limitada" in filtered_profile_tags
    )

    days_away_int = _coerce_int(days_away, default=0)

    return {
        "objetivo": objetivo,
        "restricciones": restricciones,
        "preferencias": preferencias,
        "presupuesto": presupuesto,
        "meal_context": meal_context,
        "special_situation": special_situation,
        "needs_tupper": needs_tupper_flag,
        "has_no_kitchen": no_kitchen,
        "has_limited_kitchen": limited_kitchen,
        "days_away": days_away_int,
        "profile_tags": profile_tags,
        "filtered_profile_tags": filtered_profile_tags,
        "is_lactose_free": is_lactose_free,
        "is_gluten_free": is_gluten_free,
        "is_low_fodmap": is_low_fodmap,
        "is_vegan": is_vegan,
        "is_vegetarian": is_vegetarian,
        "is_pescetarian": is_pescetarian,
        "wants_meat": wants_meat,
        "wants_fish": wants_fish,
        "wants_high_protein": wants_high_protein,
        "wants_weight_loss": wants_weight_loss,
        "needs_quick_meals": needs_quick_meals,
    }


def _replace_word_boundary(text: str, old: str, new: str) -> str:
    pattern = rf"(?<!\w){re.escape(old)}(?!\w)"
    return re.sub(pattern, new, text)


def _apply_lactose_free_adjustments(options: list[str]) -> list[str]:
    cleaned: list[str] = []

    for item in options:
        text = _safe_text(item)

        text = text.replace(
            "Skyr o yogur alto en proteína",
            "Yogur sin lactosa alto en proteína",
        )
        text = text.replace("Skyr", "Yogur sin lactosa alto en proteína")

        if "Yogur sin lactosa" not in text:
            text = _replace_word_boundary(text, "Yogur", "Yogur sin lactosa")

        if "yogur sin lactosa" not in _normalize_text(text):
            text = _replace_word_boundary(text, "yogur", "yogur sin lactosa")

        text = _replace_word_boundary(text, "leche", "bebida vegetal")
        text = _replace_word_boundary(text, "Leche", "Bebida vegetal")
        text = text.replace("queso fresco", "aguacate")
        text = text.replace("Queso fresco", "Aguacate")
        text = _replace_word_boundary(text, "queso", "aguacate")
        text = _replace_word_boundary(text, "Queso", "Aguacate")

        cleaned.append(clean_meal_text(text))

    return cleaned


def _apply_gluten_free_adjustments(options: list[str]) -> list[str]:
    cleaned: list[str] = []

    for item in options:
        text = _safe_text(item)

        if "Tostadas sin gluten" not in text:
            text = text.replace("Tostadas", "Tostadas sin gluten")

        if "tostadas sin gluten" not in _normalize_text(text):
            text = text.replace("tostadas", "tostadas sin gluten")

        if "Wrap sin gluten" not in text:
            text = text.replace("Wrap", "Wrap sin gluten")

        if "wrap sin gluten" not in _normalize_text(text):
            text = text.replace("wrap", "wrap sin gluten")

        if "Pasta sin gluten" not in text:
            text = text.replace("Pasta", "Pasta sin gluten")

        if "pasta sin gluten" not in _normalize_text(text):
            text = text.replace("pasta", "pasta sin gluten")

        if "Pan sin gluten" not in text:
            text = _replace_word_boundary(text, "Pan", "Pan sin gluten")

        if "pan sin gluten" not in _normalize_text(text):
            text = _replace_word_boundary(text, "pan", "pan sin gluten")

        cleaned.append(clean_meal_text(text))

    return cleaned


def _apply_low_fodmap_option_adjustments(options: list[str]) -> list[str]:
    adjusted: list[str] = []

    for item in options:
        text = _safe_text(item)

        text = text.replace("garbanzos", "tofu firme")
        text = text.replace("Garbanzos", "Tofu firme")
        text = text.replace("lentejas", "arroz")
        text = text.replace("Lentejas", "Arroz")

        if "crema suave de tofu" not in _normalize_text(text):
            text = text.replace("hummus", "crema suave de tofu")
            text = text.replace("Hummus", "Crema suave de tofu")

        if "cebollino" not in _normalize_text(text):
            text = text.replace("cebolla", "cebollino")
            text = text.replace("Cebolla", "Cebollino")

        if "aceite infusionado con ajo" not in _normalize_text(text):
            text = text.replace("ajo", "aceite infusionado con ajo")
            text = text.replace("Ajo", "Aceite infusionado con ajo")

        if "aguacate en pequena porcion" not in _normalize_text(text):
            text = text.replace("aguacate", "aguacate en pequeña porción")
            text = text.replace("Aguacate", "Aguacate en pequeña porción")

        if "tomate en cantidad moderada" not in _normalize_text(text):
            text = text.replace("tomate", "tomate en cantidad moderada")
            text = text.replace("Tomate", "Tomate en cantidad moderada")

        adjusted.append(clean_meal_text(text))

    return adjusted


def _remove_meat_and_fish_for_vegetarian(
    options: list[str],
    *,
    vegan: bool = False,
) -> list[str]:
    replacements = {
        "pollo": "tofu firme" if vegan else "huevo cocido",
        "Pollo": "Tofu firme" if vegan else "Huevo cocido",
        "pavo": "tofu firme" if vegan else "huevo cocido",
        "Pavo": "Tofu firme" if vegan else "Huevo cocido",
        "ternera": "tofu firme" if vegan else "tortilla francesa",
        "Ternera": "Tofu firme" if vegan else "Tortilla francesa",
        "carne picada magra": "tofu firme" if vegan else "huevo cocido",
        "Carne picada magra": "Tofu firme" if vegan else "Huevo cocido",
        "carne picada": "tofu firme" if vegan else "huevo cocido",
        "Carne picada": "Tofu firme" if vegan else "Huevo cocido",
        "hamburguesa casera": "hamburguesa vegetal",
        "Hamburguesa casera": "Hamburguesa vegetal",
        "atún": "tofu firme" if vegan else "huevo cocido",
        "Atún": "Tofu firme" if vegan else "Huevo cocido",
        "salmon": "tofu firme" if vegan else "huevo cocido",
        "salmón": "tofu firme" if vegan else "huevo cocido",
        "Salmón": "Tofu firme" if vegan else "Huevo cocido",
        "merluza": "tofu firme" if vegan else "tortilla francesa",
        "Merluza": "Tofu firme" if vegan else "Tortilla francesa",
        "bacalao": "tofu firme" if vegan else "huevo cocido",
        "Bacalao": "Tofu firme" if vegan else "Huevo cocido",
        "caballa": "tofu firme" if vegan else "huevo cocido",
        "Caballa": "Tofu firme" if vegan else "Huevo cocido",
        "sardinas": "tofu firme" if vegan else "huevo cocido",
        "Sardinas": "Tofu firme" if vegan else "Huevo cocido",
        "pescado": "tofu firme" if vegan else "huevo cocido",
        "Pescado": "Tofu firme" if vegan else "Huevo cocido",
    }

    cleaned: list[str] = []

    for item in options:
        text = _safe_text(item)

        for old, new in replacements.items():
            text = text.replace(old, new)

        cleaned.append(clean_meal_text(text))

    return cleaned


def _apply_vegan_adjustments(options: list[str]) -> list[str]:
    options = _remove_meat_and_fish_for_vegetarian(options, vegan=True)
    cleaned: list[str] = []

    replacements = {
        "huevo cocido": "tofu firme",
        "Huevo cocido": "Tofu firme",
        "huevo": "tofu firme",
        "Huevo": "Tofu firme",
        "huevos": "tofu firme",
        "Huevos": "Tofu firme",
        "tortilla francesa": "revuelto de tofu",
        "Tortilla francesa": "Revuelto de tofu",
        "tortilla": "revuelto de tofu",
        "Tortilla": "Revuelto de tofu",
        "queso fresco": "aguacate",
        "Queso fresco": "Aguacate",
        "queso": "aguacate",
        "Queso": "Aguacate",
        "yogur sin lactosa": "yogur vegetal",
        "Yogur sin lactosa": "Yogur vegetal",
        "yogur": "yogur vegetal",
        "Yogur": "Yogur vegetal",
        "leche": "bebida vegetal",
        "Leche": "Bebida vegetal",
    }

    for item in options:
        text = _safe_text(item)

        for old, new in replacements.items():
            text = text.replace(old, new)

        cleaned.append(clean_meal_text(text))

    return cleaned


def _final_safety_filter(options: list[str], ctx: dict[str, Any]) -> list[str]:
    cleaned = [_safe_text(option) for option in options if _safe_text(option)]

    if ctx["is_vegan"]:
        cleaned = _apply_vegan_adjustments(cleaned)
    elif ctx["is_vegetarian"]:
        cleaned = _remove_meat_and_fish_for_vegetarian(cleaned, vegan=False)

    if ctx["is_lactose_free"]:
        cleaned = _apply_lactose_free_adjustments(cleaned)

    if ctx["is_gluten_free"]:
        cleaned = _apply_gluten_free_adjustments(cleaned)

    if ctx["is_low_fodmap"]:
        cleaned = _apply_low_fodmap_option_adjustments(cleaned)

    return clean_list(cleaned)


def _breakfast_options(ctx: dict[str, Any]) -> list[str]:
    if ctx["is_vegan"]:
        options = [
            "Porridge con bebida vegetal, plátano y crema de cacahuete",
            "Tostadas con crema suave de tofu y tomate",
            "Avena con bebida vegetal, frutos rojos y semillas",
            "Batido de bebida vegetal, avena y fruta",
            "Tortitas de avena con fruta",
            "Pan con aguacate y tomate",
            "Yogur vegetal con avena y nueces",
        ]
    elif ctx["is_vegetarian"]:
        options = [
            "Huevos revueltos con tostadas y fruta",
            "Yogur alto en proteína con avena y frutos rojos",
            "Tortilla francesa con pan y tomate",
            "Avena con bebida vegetal, crema de cacahuete y proteína",
            "Yogur alto en proteína con plátano y nueces",
            "Tostadas con aguacate en pequeña porción y tomate",
            "Batido de yogur, avena y fruta",
        ]
    elif ctx["wants_high_protein"]:
        options = [
            "Huevos revueltos con tostadas y fruta",
            "Yogur alto en proteína con avena y frutos rojos",
            "Tortilla francesa con pan y tomate",
            "Avena con bebida vegetal, crema de cacahuete y proteína",
            "Yogur alto en proteína con plátano y nueces",
            "Tostadas con pavo y aguacate en pequeña porción",
            "Batido de yogur, avena y fruta",
        ]
    else:
        options = [
            "Tostadas con tomate y aceite de oliva",
            "Yogur con avena y fruta",
            "Avena cocida con canela y plátano",
            "Tortilla francesa con fruta",
            "Batido de fruta y yogur",
            "Pan con queso fresco y tomate",
            "Yogur con nueces y fruta",
        ]

    return _final_safety_filter(options, ctx)


def _lunch_options(ctx: dict[str, Any]) -> list[str]:
    portable_mode = (
        ctx["has_no_kitchen"]
        or ctx["has_limited_kitchen"]
        or ctx["days_away"] > 0
    )

    if portable_mode:
        if ctx["is_vegan"]:
            options = [
                "Ensalada completa con tofu, arroz y verduras",
                "Bowl frío de arroz con crema suave de tofu y verduras",
                "Wrap frío con tofu, hojas verdes y tomate",
                "Pasta fría con tofu y verduras suaves",
                "Patata cocida con crema suave de tofu y ensalada",
                "Arroz cocido con tofu y verduras",
                "Boniato cocido con tofu marinado",
            ]
        elif ctx["is_vegetarian"]:
            options = [
                "Ensalada completa con huevo cocido y arroz",
                "Bowl frío de arroz con tortilla francesa y verduras",
                "Wrap frío con huevo, hojas verdes y tomate",
                "Pasta fría con queso fresco o aguacate y verduras",
                "Patata cocida con huevo y ensalada",
                "Arroz cocido con queso fresco o aguacate y verduras",
                "Boniato cocido con tortilla francesa",
            ]
        elif ctx["is_pescetarian"] or ctx["wants_fish"]:
            options = [
                "Ensalada completa con atún y arroz",
                "Bowl frío de arroz con salmón o atún y verduras",
                "Wrap frío con atún, hojas verdes y tomate",
                "Pasta fría con pescado y verduras suaves",
                "Patata cocida con caballa y ensalada",
                "Arroz cocido con conserva de pescado y verduras",
                "Boniato cocido con atún al natural",
            ]
        elif ctx["wants_meat"] or ctx["wants_high_protein"]:
            options = [
                "Ensalada completa con pollo y arroz",
                "Bowl frío de arroz con pollo y verduras",
                "Wrap frío con pavo, hojas verdes y tomate",
                "Pasta fría con pollo y verduras suaves",
                "Patata cocida con pavo y ensalada",
                "Arroz cocido con pollo frío y verduras",
                "Boniato cocido con pollo desmenuzado",
            ]
        else:
            options = [
                "Ensalada completa con arroz y verduras",
                "Bowl frío de arroz con huevo cocido y verduras",
                "Wrap frío con hojas verdes, tomate y tortilla francesa",
                "Pasta fría con verduras suaves y huevo",
                "Patata cocida con ensalada y huevo",
                "Arroz cocido con huevo y verduras",
                "Boniato cocido con tortilla francesa",
            ]
    else:
        if ctx["is_vegan"]:
            options = [
                "Quinoa con tofu firme, zanahoria y calabacín",
                "Arroz con tofu y verduras salteadas",
                "Arroz suave con verduras y tofu",
                "Ensalada templada de quinoa con crema suave de tofu y pepino",
                "Pasta con tomate natural y tofu",
                "Boniato asado con tofu y ensalada",
                "Arroz con tempeh y verduras",
            ]
        elif ctx["is_vegetarian"]:
            options = [
                "Tortilla de patata con ensalada",
                "Quinoa con huevo cocido y verduras",
                "Arroz con verduras y huevo",
                "Arroz con tortilla francesa y ensalada",
                "Pasta con verduras y queso fresco",
                "Boniato asado con huevo y espinacas",
                "Ensalada templada con huevo y quinoa",
            ]
        elif ctx["is_pescetarian"] or ctx["wants_fish"]:
            options = [
                "Arroz con atún y verduras",
                "Merluza con patata cocida y calabacín",
                "Quinoa con salmón y zanahoria",
                "Ensalada templada de patata con caballa",
                "Arroz basmati con pescado al horno",
                "Pasta con atún y tomate natural",
                "Sardinas con boniato y ensalada",
            ]
        elif ctx["wants_meat"] or ctx["wants_high_protein"]:
            options = [
                "Arroz con pollo a la plancha y verduras",
                "Pechuga de pavo con patata y ensalada",
                "Ternera salteada con arroz y calabacín",
                "Pasta con pollo y tomate natural",
                "Boniato asado con carne picada magra",
                "Quinoa con pollo y zanahoria",
                "Bowl de pollo con arroz y verduras",
            ]
        else:
            options = [
                "Arroz con huevo y verduras",
                "Patata cocida con tortilla francesa y calabacín",
                "Quinoa con huevo cocido y zanahoria",
                "Tortilla de patata con ensalada",
                "Arroz con verduras y tofu firme",
                "Boniato con huevo cocido y ensalada",
                "Quinoa con huevo cocido y espinacas",
            ]

    options = _final_safety_filter(options, ctx)

    if ctx["needs_tupper"]:
        options = [
            option if "apto para tupper" in option.lower() else f"{option} (apto para tupper)"
            for option in options
        ]
    elif ctx["needs_quick_meals"] and not portable_mode:
        options = [
            option if "rápido de preparar" in option.lower() else f"{option} (rápido de preparar)"
            for option in options
        ]

    return clean_list(options)


def _dinner_options(ctx: dict[str, Any]) -> list[str]:
    if ctx["is_vegan"]:
        options = [
            "Crema de verduras con tofu a la plancha",
            "Arroz con verduras y crema suave de tofu",
            "Sopa suave de verduras con quinoa",
            "Boniato asado con ensalada",
            "Salteado de tofu con calabacín y zanahoria",
            "Puré de calabaza con tofu firme",
            "Ensalada templada de arroz con tofu",
        ]
    elif ctx["is_vegetarian"]:
        options = [
            "Tortilla francesa con ensalada",
            "Crema de calabacín y huevo cocido",
            "Revuelto de huevo con espinacas",
            "Puré de verduras con tortilla",
            "Ensalada templada con queso fresco y tomate",
            "Sopa suave con huevo",
            "Patata asada con tortilla francesa",
        ]
    elif ctx["is_pescetarian"] or ctx["wants_fish"]:
        options = [
            "Pescado al horno con verduras",
            "Tortilla francesa con ensalada",
            "Merluza con puré de patata",
            "Sopa suave con atún al natural",
            "Salmón con calabacín a la plancha",
            "Ensalada templada de arroz con pescado",
            "Bacalao con calabaza asada",
        ]
    elif ctx["wants_meat"] or ctx["wants_high_protein"]:
        options = [
            "Tortilla francesa con ensalada",
            "Pollo a la plancha con verduras",
            "Pavo al horno con puré de patata",
            "Revuelto de huevo con espinacas",
            "Hamburguesa casera con ensalada",
            "Ternera salteada con calabacín",
            "Crema de verduras con pollo desmenuzado",
        ]
    else:
        options = [
            "Crema de calabacín y tortilla francesa",
            "Tortilla francesa con puré de patata",
            "Sopa suave de verduras con huevo",
            "Revuelto de huevo con espinacas",
            "Crema de zanahoria con huevo cocido",
            "Ensalada templada de arroz y tofu",
            "Tortilla de calabacín con tomate",
        ]

    if ctx["wants_weight_loss"]:
        options = [
            item.replace("con puré de patata", "con verduras").replace(
                "Hamburguesa casera con ensalada",
                "Hamburguesa casera con ensalada completa",
            )
            for item in options
        ]

    return _final_safety_filter(options, ctx)


def _apply_low_fodmap_adjustments(
    plan: list[dict[str, str]],
) -> list[dict[str, str]]:
    adjusted_plan: list[dict[str, str]] = []

    for item in plan:
        new_item = item.copy()

        for key in ("breakfast", "lunch", "dinner"):
            text = _safe_text(new_item.get(key))

            if "tomate en cantidad moderada" not in _normalize_text(text):
                text = text.replace("tomate", "tomate en cantidad moderada")
                text = text.replace("Tomate", "Tomate en cantidad moderada")

            replacements = {
                "hummus": "crema suave de tofu",
                "cebolla": "cebollino verde",
                "ajo": "aceite infusionado con ajo",
            }

            for old, new in replacements.items():
                if _normalize_text(new) not in _normalize_text(text):
                    text = text.replace(old, new)
                    text = text.replace(old.capitalize(), new.capitalize())

            new_item[key] = clean_meal_text(text)

        adjusted_plan.append(new_item)

    return adjusted_plan


def _validate_plan_against_context(
    plan: list[dict[str, str]],
    ctx: dict[str, Any],
) -> list[dict[str, str]]:
    validated: list[dict[str, str]] = []

    for item in plan:
        new_item = {
            "day": _safe_text(item.get("day")),
            "breakfast": _safe_text(item.get("breakfast")),
            "lunch": _safe_text(item.get("lunch")),
            "dinner": _safe_text(item.get("dinner")),
        }

        for key in ("breakfast", "lunch", "dinner"):
            text = new_item[key]

            if ctx["is_vegan"]:
                text = _final_safety_filter([text], {**ctx, "is_vegan": True})[0]
            elif ctx["is_vegetarian"]:
                text = _final_safety_filter([text], {**ctx, "is_vegetarian": True})[0]

            new_item[key] = clean_meal_text(text)

        validated.append(new_item)

    return validated


def generate_fallback_meal_plan(
    user_text: str = "",
    **kwargs: Any,
) -> list[dict[str, str]]:
    """
    Generates a personalized fallback weekly meal plan when AI providers are unavailable.

    It accepts either:
    - user_text: structured text assembled in views.py
    - keyword arguments from views.py, such as objetivo, restricciones, preferencias, etc.

    Returns:
        list[dict[str, str]] with day, breakfast, lunch and dinner keys.
    """
    if not _safe_text(user_text) and kwargs:
        user_text = _build_user_text_from_kwargs(**kwargs)

    ctx = _build_context(user_text)

    breakfasts = _breakfast_options(ctx)
    lunches = _lunch_options(ctx)
    dinners = _dinner_options(ctx)

    if not breakfasts or not lunches or not dinners:
        raise ValueError("No se han podido generar opciones suficientes para el plan semanal.")

    plan: list[dict[str, str]] = []

    for i, day in enumerate(DAYS):
        plan.append(
            {
                "day": day,
                "breakfast": breakfasts[(i + 1) % len(breakfasts)],
                "lunch": lunches[(i + 2) % len(lunches)],
                "dinner": dinners[(i + 3) % len(dinners)],
            }
        )

    if ctx["is_low_fodmap"]:
        plan = _apply_low_fodmap_adjustments(plan)

    plan = _validate_plan_against_context(plan, ctx)

    cleaned_plan: list[dict[str, str]] = []

    for item in plan:
        cleaned_item = {
            "day": _safe_text(item.get("day")),
            "breakfast": clean_meal_text(item.get("breakfast")),
            "lunch": clean_meal_text(item.get("lunch")),
            "dinner": clean_meal_text(item.get("dinner")),
        }

        if not all(cleaned_item.values()):
            raise ValueError("El plan fallback contiene campos vacíos.")

        cleaned_plan.append(cleaned_item)

    return cleaned_plan