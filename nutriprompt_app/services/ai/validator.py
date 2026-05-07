from __future__ import annotations

import json
import re
from typing import Any, Callable

SPANISH_DAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]

REQUIRED_KEYS = ("day", "breakfast", "lunch", "dinner")


FORBIDDEN_MEATS = {
    "chicken", "pollo", "turkey", "pavo", "beef", "ternera", "res", "vacuno",
    "pork", "cerdo", "lamb", "cordero", "duck", "pato", "ham", "jamon", "jamón",
    "bacon", "tocino", "sausage", "sausages", "salchicha", "salchichas",
    "meatball", "meatballs", "albondiga", "albondigas", "albóndiga", "albóndigas",
    "burger", "hamburguesa", "chorizo", "morcilla", "mortadela", "pepperoni",
    "prosciutto", "fiambre", "carne", "meat",
}

FORBIDDEN_FISH_AND_SEAFOOD = {
    "fish", "pescado", "atun", "atún", "salmon", "salmón", "merluza", "bacalao",
    "sardina", "sardinas", "caballa", "dorada", "lubina", "lenguado", "marisco",
    "mariscos", "gamba", "gambas", "langostino", "langostinos", "mejillon",
    "mejillón", "mejillones", "calamar", "calamares", "pulpo",
}

FORBIDDEN_ANIMAL_PRODUCTS_FOR_VEGAN = {
    "huevo", "huevos", "egg", "eggs", "leche", "milk", "queso", "cheese",
    "yogur", "yogurt", "yoghurt", "nata", "cream", "mantequilla", "butter",
    "kefir", "kéfir", "mozzarella", "parmesano", "parmesan", "brie",
    "camembert", "helado", "ice cream", "miel", "honey",
}

FORBIDDEN_LACTOSE_WORDS = {
    "milk", "leche", "cheese", "queso", "yogurt", "yoghurt", "yogur", "cream",
    "nata", "butter", "mantequilla", "ice cream", "helado", "mozzarella",
    "brie", "camembert", "parmesan", "parmesano",
}

SAFE_LACTOSE_PATTERNS = {
    "sin lactosa", "yogur sin lactosa", "yogurt sin lactosa", "leche sin lactosa",
    "queso sin lactosa", "bebida vegetal", "bebida de almendra", "bebida de arroz",
    "bebida de avena sin gluten", "yogur vegetal",
}

FORBIDDEN_GLUTEN_WORDS = {
    "wheat", "trigo", "barley", "cebada", "rye", "centeno", "bread", "pan",
    "pasta", "flour", "harina", "breadcrumb", "pan rallado", "beer", "cerveza",
    "couscous", "cuscus", "cuscús", "bulgur", "seitan", "galleta", "galletas",
    "bizcocho", "croissant", "wrap",
}

SAFE_GLUTEN_PATTERNS = {
    "sin gluten", "pan sin gluten", "pasta sin gluten", "wrap sin gluten",
    "avena sin gluten", "copos de avena sin gluten", "copos de maiz sin gluten",
    "copos de maíz sin gluten", "corn flakes sin gluten", "tortitas sin gluten",
    "tortillas de maiz", "tortillas de maíz", "arroz", "quinoa", "patata",
    "maiz", "maíz",
}

FORBIDDEN_HIGH_FODMAP_WORDS = {
    "ajo", "cebolla", "puerro", "coliflor", "manzana", "pera", "sandia", "sandía",
    "mango", "ciruela", "ciruelas", "garbanzos", "lentejas", "judias", "judías",
    "setas", "champiñones",
}

SAFE_FODMAP_PATTERNS = {
    "sin ajo", "sin cebolla", "bajo en fodmaps", "low fodmap",
    "aceite infusionado con ajo", "cebollino", "tomate en cantidad moderada",
    "aguacate en pequeña porción",
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


RetryPromptBuilder = Callable[[str, str, str], str]


def _normalize_text(value: str) -> str:
    value = (value or "").strip().casefold()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"\s+", " ", value)
    return value


def _get_gemini_client() -> genai.Client:
    api_key = getattr(settings, "GOOGLE_API_KEY", None)
    if not api_key:
        raise ValueError("GOOGLE_API_KEY no está configurada.")
    return genai.Client(api_key=api_key)


def _get_openai_client() -> OpenAI:
    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("OPENAI_API_KEY no está configurada.")
    return OpenAI(api_key=api_key)


def _clean_json_output(raw_output: str) -> str:
    if not raw_output or not raw_output.strip():
        return ""

    cleaned = raw_output.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    array_match = re.search(r"\[\s*{.*}\s*\]", cleaned, flags=re.DOTALL)
    if array_match:
        return array_match.group(0).strip()

    return cleaned


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


def _contains_forbidden_with_exceptions(
    text: str,
    forbidden_terms: set[str],
    safe_patterns: set[str] | None = None,
) -> bool:
    normalized = _normalize_text(text)
    safe_patterns = safe_patterns or set()

    for safe in safe_patterns:
        normalized = normalized.replace(_normalize_text(safe), " ")

    normalized = re.sub(r"\s+", " ", normalized).strip()

    for term in forbidden_terms:
        pattern = rf"\b{re.escape(_normalize_text(term))}\b"
        if re.search(pattern, normalized):
            return True

    return False


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


def _build_context_guidance(user_input: str) -> str:
    meal_context = _extract_field(user_input, "contexto_principal")
    special_situation = _extract_field(user_input, "situacion_especial")
    needs_tupper = _extract_field(user_input, "necesita_tupper")
    has_kitchen = _extract_field(user_input, "acceso_cocina")
    profile_tags = _extract_profile_tags(user_input)

    guidance: list[str] = []

    meal_context_normalized = _normalize_text(meal_context)
    special_situation_normalized = _normalize_text(special_situation)
    needs_tupper_normalized = _normalize_text(needs_tupper)
    has_kitchen_normalized = _normalize_text(has_kitchen)

    if meal_context_normalized == "viaje":
        guidance.extend(CONTEXT_KNOWLEDGE["travel"])
    elif meal_context_normalized in {"restaurante / comer fuera", "restaurante", "comer fuera"}:
        guidance.extend(CONTEXT_KNOWLEDGE["restaurant"])
    elif meal_context_normalized == "trabajo":
        guidance.extend(CONTEXT_KNOWLEDGE["work"])

    if special_situation_normalized == "fin de semana":
        guidance.extend(CONTEXT_KNOWLEDGE["weekend"])
    elif special_situation_normalized in {"evento / celebracion", "evento", "celebracion"}:
        guidance.extend(CONTEXT_KNOWLEDGE["event"])
    elif special_situation_normalized == "viaje":
        guidance.extend(CONTEXT_KNOWLEDGE["travel"])

    if needs_tupper_normalized in {"si", "sí", "yes"}:
        guidance.extend(CONTEXT_KNOWLEDGE["tupper"])

    if has_kitchen_normalized in {"acceso limitado", "limited", "cocina limitada"} or _has_profile_tag(user_input, "cocina limitada"):
        guidance.extend(CONTEXT_KNOWLEDGE["limited_kitchen"])
    elif has_kitchen_normalized in {"no", "sin cocina"} or _has_profile_tag(user_input, "sin cocina"):
        guidance.extend(CONTEXT_KNOWLEDGE["no_kitchen"])

    for tag in profile_tags:
        guidance.extend(PROFILE_TAG_GUIDANCE.get(tag, []))

    if not guidance:
        return ""

    unique_guidance = list(dict.fromkeys(guidance))
    return "\n".join(f"- {item}" for item in unique_guidance)


def _build_rule_guidance(user_input: str) -> str:
    rules = _infer_rules(user_input)
    extra_rules: list[str] = []

    if rules["fish_only"]:
        extra_rules.extend([
            "- La preferencia 'solo pescado' es una regla estricta.",
            "- Solo puedes usar pescado y marisco como proteína animal.",
            "- No incluyas pollo, pavo, ternera, cerdo, cordero ni carnes procesadas.",
        ])

    if rules["vegetarian"]:
        extra_rules.extend([
            "- La preferencia vegetariana es una regla estricta.",
            "- No incluyas carne, pescado ni marisco.",
        ])

    if rules["vegan"]:
        extra_rules.extend([
            "- La preferencia vegana es una regla estricta.",
            "- No incluyas carne, pescado, marisco, huevos, lácteos, miel ni productos de origen animal.",
        ])

    if rules["pescetarian"]:
        extra_rules.extend([
            "- La preferencia pescetariana es una regla estricta.",
            "- No incluyas carne.",
            "- Puedes usar pescado y marisco como proteína animal.",
        ])

    if rules["lactose_free"]:
        extra_rules.append("- Todas las propuestas deben ser sin lactosa.")

    if rules["gluten_free"]:
        extra_rules.append("- Todas las propuestas deben ser sin gluten.")

    if rules["low_fodmap"]:
        extra_rules.extend([
            "- Todas las propuestas deben ser compatibles con un enfoque bajo en FODMAPs.",
            "- No hagas afirmaciones médicas ni prometas mejora de síntomas.",
        ])

    return "\n".join(extra_rules)


def _build_profile_guidance(user_input: str) -> str:
    profile_tags = _extract_profile_tags(user_input)
    if not profile_tags:
        return ""

    guidance_lines = [f"- Etiquetas detectadas: {', '.join(profile_tags)}"]

    for tag in profile_tags:
        for instruction in PROFILE_TAG_GUIDANCE.get(tag, []):
            guidance_lines.append(f"- {instruction}")

    unique_guidance = list(dict.fromkeys(guidance_lines))
    return "\n".join(unique_guidance)


def validate_plan_item(
    item: dict[str, Any],
    index: int,
    rules: dict[str, bool],
    valid_days: set[str],
    expected_day: str,
) -> dict[str, str]:
    missing = set(REQUIRED_KEYS) - item.keys()

    if missing:
        raise ValueError(f"Faltan claves en el día {index}: {', '.join(sorted(missing))}")

    normalized_item: dict[str, str] = {}

    for key in REQUIRED_KEYS:
        value = item.get(key)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"El campo '{key}' del día {index} debe ser un texto no vacío.")

        normalized_item[key] = value.strip()

    day_normalized = _normalize_text(normalized_item["day"])
    expected_day_normalized = _normalize_text(expected_day)

    if day_normalized not in valid_days:
        raise ValueError(f"El valor de 'day' en el día {index} no está en español o no es válido.")

    if day_normalized != expected_day_normalized:
        normalized_item["day"] = expected_day

    full_day_text = " ".join([
        normalized_item["day"],
        normalized_item["breakfast"],
        normalized_item["lunch"],
        normalized_item["dinner"],
    ])

    if rules["fish_only"] and _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_MEATS):
        raise ValueError(f"El plan incumple la preferencia 'solo pescado' en el día {index}.")

    if rules["vegetarian"] and (
        _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_MEATS)
        or _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_FISH_AND_SEAFOOD)
    ):
        raise ValueError(f"El plan incumple la preferencia vegetariana en el día {index}.")

    if rules["vegan"] and (
        _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_MEATS)
        or _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_FISH_AND_SEAFOOD)
        or _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_ANIMAL_PRODUCTS_FOR_VEGAN)
    ):
        raise ValueError(f"El plan incumple la preferencia vegana en el día {index}.")

    if rules["pescetarian"] and _contains_forbidden_with_exceptions(full_day_text, FORBIDDEN_MEATS):
        raise ValueError(f"El plan incumple la preferencia pescetariana en el día {index}.")

    if rules["lactose_free"] and _contains_forbidden_with_exceptions(
        full_day_text,
        FORBIDDEN_LACTOSE_WORDS,
        SAFE_LACTOSE_PATTERNS,
    ):
        raise ValueError(f"El plan parece incumplir la restricción 'sin lactosa' en el día {index}.")

    if rules["gluten_free"] and _contains_forbidden_with_exceptions(
        full_day_text,
        FORBIDDEN_GLUTEN_WORDS,
        SAFE_GLUTEN_PATTERNS,
    ):
        raise ValueError(f"El plan parece incumplir la restricción 'sin gluten' en el día {index}.")

    if rules["low_fodmap"] and _contains_forbidden_with_exceptions(
        full_day_text,
        FORBIDDEN_HIGH_FODMAP_WORDS,
        SAFE_FODMAP_PATTERNS,
    ):
        raise ValueError(f"El plan parece incumplir el enfoque 'bajo en FODMAPs' en el día {index}.")

    return normalized_item


def validate_plan_data(data: Any, user_input: str) -> list[dict[str, str]]:
    if not isinstance(data, list):
        raise ValueError("La salida del modelo no es una lista JSON válida.")

    if len(data) != 7:
        raise ValueError(f"Se esperaban 7 días en el plan, pero se recibieron {len(data)}.")

    rules = _infer_rules(user_input)
    valid_days = {_normalize_text(day) for day in SPANISH_DAYS}
    validated: list[dict[str, str]] = []

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El elemento {index} del plan no es un objeto JSON válido.")

        validated.append(
            validate_plan_item(
                item=item,
                index=index,
                rules=rules,
                valid_days=valid_days,
                expected_day=SPANISH_DAYS[index - 1],
            )
        )

    return validated


def parse_and_validate_plan(raw_output: str, user_input: str) -> list[dict[str, str]]:
    clean_output = _clean_json_output(raw_output)

    try:
        data = json.loads(clean_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La salida del modelo no es JSON válido: {exc}") from exc

    return validate_plan_data(data, user_input)
