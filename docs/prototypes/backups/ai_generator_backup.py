import json
import re
import time
import unicodedata
from typing import Any

from django.conf import settings
from google import genai
from openai import OpenAI


MODEL_NAME_GEMINI = "gemini-2.5-flash"
MODEL_NAME_OPENAI = "gpt-5-mini"

MAX_PROVIDER_RETRIES = 2


SYSTEM_PROMPT = """
Actúa como un asistente experto en planificación semanal de comidas, inspirado en buenas prácticas nutricionales y con especial atención al enfoque low-FODMAP cuando sea relevante.

Tu tarea es generar un plan semanal estructurado, práctico, realista y coherente con los datos del cliente.

IMPORTANTE:
- Este plan es únicamente informativo y no sustituye el consejo de un profesional sanitario cualificado.
- No hagas diagnósticos ni afirmaciones médicas.
- TODO el contenido debe estar en ESPAÑOL.
- NO mezcles idiomas.
- Devuelve SOLO JSON válido, sin texto adicional.

REGLAS OBLIGATORIAS:
- Genera un plan de 7 días completos.
- Incluye desayuno, comida y cena para cada día.
- Respeta SIEMPRE las restricciones alimentarias indicadas.
- Evita ajo y cebolla.
- Usa comidas simples, prácticas y realistas.
- Mantén variedad durante la semana.
- Adapta el plan al objetivo, preferencias, presupuesto y contexto real del cliente.
- Si la persona comerá fuera de casa, adapta las propuestas a esa situación.
- Si necesita tupper, prioriza comidas transportables y prácticas.
- Si tiene acceso limitado o nulo a cocina, evita recetas complejas.
- Si el perfil es bajo en FODMAPs, evita ingredientes problemáticos y mantén las propuestas suaves y sencillas.
- Si el objetivo es ganar masa muscular, aumenta la presencia de proteína de forma equilibrada y realista.
- Si el perfil indica presupuesto ajustado, prioriza ingredientes asequibles y reutilizables.
- Si el perfil indica poco tiempo para cocinar, prioriza recetas rápidas y de baja elaboración.
- Si el perfil indica digestiones pesadas o hinchazón frecuente, usa opciones suaves y fáciles de tolerar.
- Si no puedes cumplir una condición exactamente, adáptate sin incumplir ninguna restricción principal.

FORMATO DE SALIDA:
Devuelve SOLO un JSON válido con esta estructura exacta:

[
  {
    "day": "Lunes",
    "breakfast": "....",
    "lunch": "....",
    "dinner": "...."
  }
]

No añadas markdown, ni ```json, ni explicaciones antes o después.

Antes de responder, verifica internamente que:
- Todo está en español
- El JSON es válido
- Hay 7 días
- No aparecen ingredientes prohibidos según las restricciones, preferencias y etiquetas detectadas
""".strip()


CONTEXT_KNOWLEDGE = {
    "travel": [
        "Prioriza comidas fáciles de encontrar, adaptar o transportar durante un viaje.",
        "Sugiere platos simples con ingredientes claramente identificables.",
        "Evita recomendaciones que dependan de acceso completo a cocina.",
        "Incluye opciones prácticas para comer fuera de casa.",
    ],
    "restaurant": [
        "Prefiere platos a la plancha, al horno o al vapor.",
        "Sugiere pedir salsas y aliños aparte.",
        "Evita platos con alta probabilidad de llevar ajo, cebolla o ingredientes ocultos.",
        "Haz recomendaciones realistas para pedir en restaurante.",
    ],
    "work": [
        "Prioriza comidas prácticas para los días laborables.",
        "Sugiere preparaciones sencillas que puedan dejarse hechas con antelación.",
        "Haz que las comidas del mediodía sean eficientes y realistas para una rutina laboral.",
    ],
    "weekend": [
        "Permite comidas algo más flexibles, manteniendo el equilibrio general.",
        "Mantén la estructura semanal pero con opciones agradables y realistas.",
    ],
    "event": [
        "Haz el plan práctico y flexible alrededor de comidas sociales o celebraciones.",
        "Sugiere compensaciones sencillas sin caer en restricciones excesivas.",
    ],
    "tupper": [
        "Prioriza comidas que se conserven bien y sean cómodas de transportar.",
        "Prefiere comidas aptas para batch cooking y fáciles de recalentar o consumir.",
        "Evita platos que pierdan calidad rápidamente tras guardarse.",
    ],
    "limited_kitchen": [
        "Usa comidas que requieran muy poca preparación.",
        "Evita recetas dependientes del horno o elaboradas.",
        "Prefiere platos de montaje simple o cocciones muy básicas.",
    ],
    "no_kitchen": [
        "Evita recetas que requieran cocinar.",
        "Prefiere comidas frías seguras, opciones de montaje fácil y elecciones externas sencillas.",
    ],
}


PROFILE_TAG_GUIDANCE = {
    "perder peso": [
        "Prioriza platos equilibrados, saciantes y realistas, evitando propuestas extremas o muy restrictivas.",
        "Favorece combinaciones sencillas con buena presencia de proteína y vegetales tolerables.",
    ],
    "ganar energía": [
        "Incluye comidas completas y estables, fáciles de sostener durante la semana.",
        "Evita propuestas demasiado escasas o poco saciantes.",
    ],
    "ganar masa muscular": [
        "Aumenta la presencia de proteína de forma práctica y coherente con restricciones y preferencias.",
        "Incluye comidas completas, saciantes y realistas.",
        "Evita propuestas demasiado ligeras o insuficientes.",
    ],
    "organizar comidas": [
        "Favorece recetas repetibles, simples y fáciles de planificar para varios días.",
        "Reutiliza ingredientes de forma inteligente durante la semana.",
    ],
    "comer más equilibrado": [
        "Mantén un patrón semanal variado, sencillo y bien compensado.",
        "Incluye opciones prácticas y fáciles de seguir sin rigidez excesiva.",
    ],
    "alta proteína": [
        "Aumenta la presencia de proteína de forma práctica y coherente con restricciones y preferencias.",
    ],
    "sin lactosa": [
        "Asegúrate de que todas las propuestas sean compatibles con una pauta sin lactosa.",
    ],
    "sin gluten": [
        "Asegúrate de que todas las propuestas sean compatibles con una pauta sin gluten.",
    ],
    "bajo en FODMAPs": [
        "Mantén el plan suave, práctico y compatible con un enfoque bajo en FODMAPs.",
        "Evita combinaciones especialmente pesadas o potencialmente irritantes.",
    ],
    "vegetariano": [
        "No incluyas carne, pescado ni marisco.",
        "Usa opciones vegetarianas simples y realistas.",
    ],
    "vegano": [
        "No incluyas carne, pescado, marisco, huevos, lácteos, miel ni otros productos de origen animal.",
        "Usa opciones veganas simples, prácticas y realistas.",
    ],
    "pescetariano": [
        "No incluyas carne.",
        "Puedes usar pescado y marisco como proteína animal.",
    ],
    "digestiones pesadas": [
        "Prioriza preparaciones suaves, simples y poco pesadas.",
        "Evita mezclas muy copiosas o demasiado grasas.",
    ],
    "hinchazón frecuente": [
        "Favorece platos sencillos, suaves y fáciles de tolerar.",
        "Evita combinaciones muy pesadas o difíciles de digerir.",
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
    "chicken",
    "pollo",
    "turkey",
    "pavo",
    "beef",
    "ternera",
    "res",
    "vacuno",
    "pork",
    "cerdo",
    "lamb",
    "cordero",
    "duck",
    "pato",
    "ham",
    "jamon",
    "bacon",
    "tocino",
    "sausage",
    "sausages",
    "salchicha",
    "salchichas",
    "meatball",
    "meatballs",
    "albondiga",
    "albondigas",
    "burger",
    "hamburguesa",
    "chorizo",
    "morcilla",
    "mortadela",
    "pepperoni",
    "prosciutto",
    "fiambre",
    "carne",
    "meat",
}

FORBIDDEN_FISH_AND_SEAFOOD = {
    "fish",
    "pescado",
    "atun",
    "atún",
    "salmon",
    "salmón",
    "merluza",
    "bacalao",
    "sardina",
    "sardinas",
    "caballa",
    "dorada",
    "lubina",
    "lenguado",
    "marisco",
    "mariscos",
    "gamba",
    "gambas",
    "langostino",
    "langostinos",
    "mejillon",
    "mejillón",
    "mejillones",
    "calamar",
    "calamares",
    "pulpo",
}

FORBIDDEN_ANIMAL_PRODUCTS_FOR_VEGAN = {
    "huevo",
    "huevos",
    "egg",
    "eggs",
    "leche",
    "milk",
    "queso",
    "cheese",
    "yogur",
    "yogurt",
    "yoghurt",
    "nata",
    "cream",
    "mantequilla",
    "butter",
    "kefir",
    "kéfir",
    "mozzarella",
    "parmesano",
    "parmesan",
    "brie",
    "camembert",
    "helado",
    "ice cream",
    "miel",
    "honey",
}

FORBIDDEN_LACTOSE_WORDS = {
    "milk",
    "leche",
    "cheese",
    "queso",
    "yogurt",
    "yoghurt",
    "yogur",
    "cream",
    "nata",
    "butter",
    "mantequilla",
    "ice cream",
    "helado",
    "mozzarella",
    "brie",
    "camembert",
    "parmesan",
    "parmesano",
}

SAFE_LACTOSE_PATTERNS = {
    "sin lactosa",
    "yogur sin lactosa",
    "yogurt sin lactosa",
    "leche sin lactosa",
    "queso sin lactosa",
    "bebida vegetal",
    "bebida de almendra",
    "bebida de arroz",
    "bebida de avena sin gluten",
}

FORBIDDEN_GLUTEN_WORDS = {
    "wheat",
    "trigo",
    "barley",
    "cebada",
    "rye",
    "centeno",
    "bread",
    "pan",
    "pasta",
    "flour",
    "harina",
    "breadcrumb",
    "pan rallado",
    "beer",
    "cerveza",
    "couscous",
    "cuscus",
    "bulgur",
    "seitan",
    "galleta",
    "galletas",
    "bizcocho",
    "croissant",
}

SAFE_GLUTEN_PATTERNS = {
    "sin gluten",
    "pan sin gluten",
    "avena sin gluten",
    "copos de avena sin gluten",
    "copos de maiz sin gluten",
    "copos de maíz sin gluten",
    "corn flakes sin gluten",
    "tortitas sin gluten",
    "tortillas de maiz",
    "tortillas de maíz",
    "arroz",
    "quinoa",
    "patata",
    "maiz",
    "maíz",
}

FORBIDDEN_HIGH_FODMAP_WORDS = {
    "ajo",
    "cebolla",
    "puerro",
    "coliflor",
    "manzana",
    "pera",
    "sandia",
    "sandía",
    "mango",
    "ciruela",
    "ciruelas",
    "garbanzos",
    "lentejas",
    "judias",
    "judías",
    "setas",
    "champiñones",
}

SAFE_FODMAP_PATTERNS = {
    "sin ajo",
    "sin cebolla",
    "bajo en fodmaps",
    "low fodmap",
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

    for line in user_input.splitlines():
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
    normalized_no_detectadas = _normalize_text("No detectadas")

    unique_tags: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        normalized_tag = _normalize_text(tag)
        if normalized_tag == normalized_no_detectadas:
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
        restrictions,
        {
            "sin lactosa",
            "lactose free",
            "lactose-free",
            "no lactosa",
        },
    ) or _has_profile_tag(user_input, "sin lactosa")

    gluten_free = _contains_phrase(
        restrictions,
        {
            "sin gluten",
            "gluten free",
            "gluten-free",
            "no gluten",
        },
    ) or _has_profile_tag(user_input, "sin gluten")

    vegetarian = _contains_phrase(
        preferences,
        {
            "vegetariano",
            "vegetariana",
            "vegetarian",
        },
    ) or _has_profile_tag(user_input, "vegetariano")

    vegan = _contains_phrase(
        preferences,
        {
            "vegano",
            "vegana",
            "vegan",
        },
    ) or _has_profile_tag(user_input, "vegano")

    pescetarian = _contains_phrase(
        preferences,
        {
            "pescetariano",
            "pescetariana",
            "pescetarian",
        },
    ) or _has_profile_tag(user_input, "pescetariano")

    low_fodmap = _contains_phrase(
        restrictions,
        {
            "low fodmap",
            "bajo en fodmaps",
            "baja en fodmaps",
            "fodmap",
            "fodmaps",
        },
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

    if has_kitchen_normalized == "acceso limitado" or _has_profile_tag(user_input, "cocina limitada"):
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
            "- Evita ingredientes altos en FODMAPs y mantén el plan suave y práctico.",
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


def _build_full_prompt(user_input: str) -> str:
    context_guidance = _build_context_guidance(user_input)
    rule_guidance = _build_rule_guidance(user_input)
    profile_guidance = _build_profile_guidance(user_input)

    parts = [
        SYSTEM_PROMPT,
        "",
        "DATOS DEL CLIENTE:",
        user_input.strip(),
    ]

    if rule_guidance:
        parts.extend([
            "",
            "REGLAS ADICIONALES DERIVADAS DE LOS DATOS DEL CLIENTE:",
            rule_guidance,
        ])

    if profile_guidance:
        parts.extend([
            "",
            "GUÍA DE PERSONALIZACIÓN BASADA EN ETIQUETAS DE PERFIL:",
            profile_guidance,
        ])

    if context_guidance:
        parts.extend([
            "",
            "GUÍA DE CONTEXTO RELEVANTE:",
            context_guidance,
        ])

    parts.extend([
        "",
        "Genera ahora el plan semanal solicitado.",
    ])

    return "\n".join(parts).strip()


def _build_retry_prompt(user_input: str, previous_output: str, validation_error: str) -> str:
    return f"""
El intento anterior fue inválido y debes corregirlo.

ERROR DETECTADO:
{validation_error}

SALIDA ANTERIOR INVÁLIDA:
{previous_output}

INSTRUCCIONES:
- Corrige el plan completo.
- Cumple estrictamente todas las restricciones, preferencias y etiquetas del cliente.
- Devuelve SOLO JSON válido.
- TODO debe estar en español.
- No añadas explicaciones.
- Genera de nuevo los 7 días completos.

DATOS DEL CLIENTE:
{user_input.strip()}

Vuelve a generar el plan desde cero.
""".strip()


def _validate_plan_item(
    item: dict[str, Any],
    index: int,
    rules: dict[str, bool],
    valid_days: set[str],
) -> None:
    missing = set(REQUIRED_KEYS) - item.keys()
    if missing:
        raise ValueError(f"Faltan claves en el día {index}: {', '.join(sorted(missing))}")

    for key in REQUIRED_KEYS:
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"El campo '{key}' del día {index} debe ser un texto no vacío.")

    day_normalized = _normalize_text(item["day"])
    if day_normalized not in valid_days:
        raise ValueError(f"El valor de 'day' en el día {index} no está en español o no es válido.")

    full_day_text = " ".join([
        item["day"],
        item["breakfast"],
        item["lunch"],
        item["dinner"],
    ])

    if rules["fish_only"] and _contains_forbidden_with_exceptions(
        full_day_text,
        FORBIDDEN_MEATS,
    ):
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

    if rules["pescetarian"] and _contains_forbidden_with_exceptions(
        full_day_text,
        FORBIDDEN_MEATS,
    ):
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


def _validate_plan_data(data: Any, user_input: str) -> list[dict]:
    if not isinstance(data, list):
        raise ValueError("La salida del modelo no es una lista JSON válida.")

    if len(data) != 7:
        raise ValueError(f"Se esperaban 7 días en el plan, pero se recibieron {len(data)}.")

    rules = _infer_rules(user_input)
    valid_days = {_normalize_text(day) for day in SPANISH_DAYS}

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El elemento {index} del plan no es un objeto JSON válido.")
        _validate_plan_item(item, index, rules, valid_days)

    return data


def _parse_and_validate(raw_output: str, user_input: str) -> list[dict]:
    clean_output = _clean_json_output(raw_output)

    try:
        data = json.loads(clean_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La salida del modelo no es JSON válido: {exc}") from exc

    return _validate_plan_data(data, user_input)


def _should_retry_provider_error(error_message: str) -> bool:
    upper = error_message.upper()
    return any(marker in upper for marker in ["503", "UNAVAILABLE", "OVERLOADED", "TIMEOUT", "TIMED OUT"])


def _is_quota_error(error_message: str) -> bool:
    upper = error_message.upper()
    return "429" in upper or "RESOURCE_EXHAUSTED" in upper or "RATE LIMIT" in upper


def _call_gemini(prompt: str, model: str) -> str:
    client = _get_gemini_client()
    last_error = ""

    for attempt in range(1, MAX_PROVIDER_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            raw_output = getattr(response, "text", "") or ""
            if not raw_output.strip():
                raise ValueError("Gemini ha devuelto una respuesta vacía.")
            return raw_output

        except Exception as exc:
            last_error = str(exc)

            if _should_retry_provider_error(last_error) and attempt < MAX_PROVIDER_RETRIES:
                time.sleep(2)
                continue

            if _is_quota_error(last_error):
                raise ValueError("Gemini ha alcanzado temporalmente su límite de uso.") from exc

            if _should_retry_provider_error(last_error):
                raise ValueError("Gemini está temporalmente saturado. Inténtalo de nuevo en unos minutos.") from exc

            if "404" in last_error or "NOT_FOUND" in last_error.upper():
                raise ValueError(f"El modelo de Gemini '{model}' no está disponible.") from exc

            raise ValueError(f"No se ha podido generar el plan con Gemini: {last_error}") from exc

    raise ValueError(f"No se ha podido generar el plan con Gemini: {last_error}")


def _call_openai(prompt: str, model: str) -> str:
    client = _get_openai_client()
    last_error = ""

    for attempt in range(1, MAX_PROVIDER_RETRIES + 1):
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )
            raw_output = getattr(response, "output_text", "") or ""
            if not raw_output.strip():
                raise ValueError("OpenAI ha devuelto una respuesta vacía.")
            return raw_output

        except Exception as exc:
            last_error = str(exc)

            if _should_retry_provider_error(last_error) and attempt < MAX_PROVIDER_RETRIES:
                time.sleep(2)
                continue

            if _is_quota_error(last_error):
                raise ValueError("OpenAI ha alcanzado temporalmente su límite de uso.") from exc

            if _should_retry_provider_error(last_error):
                raise ValueError("OpenAI está temporalmente saturado. Inténtalo de nuevo en unos minutos.") from exc

            if "404" in last_error or "NOT_FOUND" in last_error.upper():
                raise ValueError(f"El modelo de OpenAI '{model}' no está disponible.") from exc

            raise ValueError(f"No se ha podido generar el plan con OpenAI: {last_error}") from exc

    raise ValueError(f"No se ha podido generar el plan con OpenAI: {last_error}")


def _generate_with_provider(
    provider: str,
    prompt: str,
    retry_prompt_builder,
    user_input: str,
    model: str,
    max_attempts: int,
) -> tuple[list[dict], str]:
    last_error = ""
    previous_output = ""
    current_prompt = prompt

    for attempt in range(1, max_attempts + 1):
        if provider == "gemini":
            raw_output = _call_gemini(current_prompt, model)
        elif provider == "openai":
            raw_output = _call_openai(current_prompt, model)
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")

        previous_output = raw_output

        try:
            data = _parse_and_validate(raw_output, user_input)
            return data, provider
        except ValueError as exc:
            last_error = str(exc)
            if attempt == max_attempts:
                break

            current_prompt = retry_prompt_builder(
                user_input=user_input,
                previous_output=_clean_json_output(previous_output),
                validation_error=last_error,
            )

    raise ValueError(f"{provider}: {last_error}")


def generate_meal_plan(
    user_input: str,
    gemini_model: str = MODEL_NAME_GEMINI,
    openai_model: str = MODEL_NAME_OPENAI,
    max_attempts_per_provider: int = 2,
) -> tuple[list[dict], str]:
    if not user_input or not user_input.strip():
        raise ValueError("Los datos del cliente no pueden estar vacíos.")

    if max_attempts_per_provider < 1:
        raise ValueError("max_attempts_per_provider debe ser al menos 1.")

    full_prompt = _build_full_prompt(user_input)
    provider_errors: list[str] = []

    try:
        return _generate_with_provider(
            provider="gemini",
            prompt=full_prompt,
            retry_prompt_builder=_build_retry_prompt,
            user_input=user_input,
            model=gemini_model,
            max_attempts=max_attempts_per_provider,
        )
    except Exception as exc:
        provider_errors.append(f"Gemini: {exc}")

    try:
        return _generate_with_provider(
            provider="openai",
            prompt=full_prompt,
            retry_prompt_builder=_build_retry_prompt,
            user_input=user_input,
            model=openai_model,
            max_attempts=max_attempts_per_provider,
        )
    except Exception as exc:
        provider_errors.append(f"OpenAI: {exc}")

    raise ValueError(
        "No se ha podido generar un plan válido con ninguno de los proveedores disponibles. "
        + " | ".join(provider_errors)
    )


def get_mock_meal_plan() -> list[dict]:
    return [
        {
            "day": "Lunes",
            "breakfast": "Avena sin gluten con bebida de almendra y arándanos.",
            "lunch": "Ensalada de atún con pepino, zanahoria y patata cocida.",
            "dinner": "Salmón al horno con judías verdes y arroz.",
        },
        {
            "day": "Martes",
            "breakfast": "Huevos revueltos con espinacas y pan sin gluten.",
            "lunch": "Merluza con quinoa y calabacín a la plancha.",
            "dinner": "Tortilla francesa con ensalada de tomate y aceitunas.",
        },
        {
            "day": "Miércoles",
            "breakfast": "Yogur sin lactosa con kiwi y semillas de chía.",
            "lunch": "Arroz con gambas, zanahoria y espinacas.",
            "dinner": "Bacalao al vapor con patata cocida y calabaza.",
        },
        {
            "day": "Jueves",
            "breakfast": "Tortitas de avena sin gluten con fresas.",
            "lunch": "Ensalada templada de quinoa con atún y pepino.",
            "dinner": "Dorada al horno con boniato y judías verdes.",
        },
        {
            "day": "Viernes",
            "breakfast": "Copos de maíz sin gluten con bebida vegetal y plátano firme.",
            "lunch": "Sardinas con arroz blanco y zanahoria cocida.",
            "dinner": "Tacos de pescado en tortillas de maíz con lechuga y tomate.",
        },
        {
            "day": "Sábado",
            "breakfast": "Batido con bebida de almendra, espinacas y frutos rojos.",
            "lunch": "Ensalada de patata con caballa, pepino y huevo cocido.",
            "dinner": "Lenguado a la plancha con puré de calabaza.",
        },
        {
            "day": "Domingo",
            "breakfast": "Huevos revueltos con tomate y aguacate.",
            "lunch": "Paella sencilla de pescado y marisco sin ajo ni cebolla.",
            "dinner": "Crema de calabacín y zanahoria con filete de merluza.",
        },
    ]