from __future__ import annotations

import json
import re
import time
import unicodedata
from typing import Any, Callable

from django.conf import settings
from google import genai
from openai import OpenAI

from nutriprompt_app.services.ai.prompt_builder import (
    build_full_prompt,
    build_retry_prompt,
)
from nutriprompt_app.services.ai.validator import parse_and_validate_plan


MODEL_NAME_GEMINI = "gemini-2.5-flash"
MODEL_NAME_OPENAI = "gpt-5-mini"

MAX_PROVIDER_RETRIES = 2
DEFAULT_ATTEMPTS_PER_PROVIDER = 2


SYSTEM_PROMPT = """
Actúa como un asistente de organización semanal de comidas.

IMPORTANTE:
- NO actúes como nutricionista, médico, dietista ni profesional sanitario.
- NO hagas diagnósticos.
- NO prometas beneficios de salud.
- NO uses lenguaje clínico ni prescriptivo.
- El plan debe presentarse como una propuesta orientativa de organización de comidas.
- Recomienda siempre consultar con un profesional sanitario o nutricional si la persona tiene patologías, síntomas persistentes, dudas médicas o restricciones complejas.
- TODO el contenido debe estar en ESPAÑOL.
- NO mezcles idiomas.
- Devuelve SOLO JSON válido, sin texto adicional.

OBJETIVO:
Generar una propuesta semanal sencilla, práctica y realista de comidas, adaptada a los datos proporcionados por la persona usuaria.

REGLAS OBLIGATORIAS:
- Genera un plan de 7 días completos.
- Incluye desayuno, comida y cena para cada día.
- Respeta SIEMPRE las restricciones alimentarias indicadas.
- Evita ajo y cebolla.
- Usa comidas simples, prácticas, realistas y fáciles de entender.
- Mantén variedad durante la semana.
- Adapta el plan al objetivo, preferencias, presupuesto y contexto real de la persona.
- Si la persona comerá fuera de casa, adapta las propuestas a esa situación.
- Si necesita tupper, prioriza comidas transportables y prácticas.
- Si tiene acceso limitado o nulo a cocina, evita recetas complejas.
- Si el perfil es bajo en FODMAPs, mantén propuestas suaves y sencillas, sin afirmar efectos médicos.
- Si el objetivo es ganar masa muscular o energía, sugiere comidas completas y saciantes sin prometer resultados.
- Si el perfil indica presupuesto ajustado, prioriza ingredientes asequibles y reutilizables.
- Si el perfil indica poco tiempo para cocinar, prioriza recetas rápidas y de baja elaboración.
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
- Todo está en español.
- El JSON es válido.
- Hay exactamente 7 días.
- Los días están en este orden: Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo.
- No aparecen ingredientes prohibidos según restricciones, preferencias y etiquetas detectadas.
""".strip()


CONTEXT_KNOWLEDGE = {
    "travel": [
        "Prioriza comidas fáciles de encontrar, adaptar o transportar durante un viaje.",
        "Sugiere platos simples con ingredientes claramente identificables.",
        "Evita recomendaciones que dependan de acceso completo a cocina.",
        "Incluye opciones prácticas para comer fuera de casa.",
    ],
    "restaurant": [
        "Prefiere platos sencillos a la plancha, al horno o al vapor.",
        "Sugiere opciones fáciles de pedir y adaptar.",
        "Evita platos con alta probabilidad de llevar ajo, cebolla o ingredientes ocultos.",
        "Haz recomendaciones realistas para pedir en restaurante.",
    ],
    "work": [
        "Prioriza comidas prácticas para los días laborables.",
        "Sugiere preparaciones sencillas que puedan dejarse hechas con antelación.",
        "Haz que las comidas del mediodía sean eficientes y realistas para una rutina laboral.",
    ],
    "weekend": [
        "Permite comidas algo más flexibles, manteniendo una estructura sencilla.",
        "Mantén opciones agradables y realistas.",
    ],
    "event": [
        "Haz el plan práctico y flexible alrededor de comidas sociales o celebraciones.",
        "Evita lenguaje restrictivo o compensatorio.",
    ],
    "tupper": [
        "Prioriza comidas que se conserven bien y sean cómodas de transportar.",
        "Prefiere comidas fáciles de recalentar o consumir.",
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
    retry_prompt_builder: RetryPromptBuilder,
    user_input: str,
    model: str,
    max_attempts: int,
) -> tuple[list[dict[str, str]], str]:
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
            data = parse_and_validate_plan(raw_output, user_input)
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
    max_attempts_per_provider: int = DEFAULT_ATTEMPTS_PER_PROVIDER,
) -> tuple[list[dict[str, str]], str]:
    if not user_input or not user_input.strip():
        raise ValueError("Los datos de la persona no pueden estar vacíos.")

    if max_attempts_per_provider < 1:
        raise ValueError("max_attempts_per_provider debe ser al menos 1.")

    full_prompt = build_full_prompt(user_input)
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
        "No se ha podido generar una propuesta válida con ninguno de los proveedores disponibles. "
        + " | ".join(provider_errors)
    )


def get_mock_meal_plan() -> list[dict[str, str]]:
    return [
        {
            "day": "Lunes",
            "breakfast": "Avena sin gluten con bebida vegetal y arándanos.",
            "lunch": "Ensalada de arroz con huevo, pepino y zanahoria.",
            "dinner": "Tortilla francesa con verduras suaves.",
        },
        {
            "day": "Martes",
            "breakfast": "Huevos revueltos con espinacas y pan sin gluten.",
            "lunch": "Quinoa con calabacín y huevo cocido.",
            "dinner": "Crema de verduras con patata.",
        },
        {
            "day": "Miércoles",
            "breakfast": "Yogur sin lactosa con kiwi y semillas de chía.",
            "lunch": "Arroz con zanahoria, espinacas y tortilla francesa.",
            "dinner": "Patata cocida con ensalada sencilla.",
        },
        {
            "day": "Jueves",
            "breakfast": "Tortitas de avena sin gluten con fresas.",
            "lunch": "Ensalada templada de quinoa con huevo y pepino.",
            "dinner": "Revuelto de huevo con calabacín.",
        },
        {
            "day": "Viernes",
            "breakfast": "Copos de maíz sin gluten con bebida vegetal y plátano firme.",
            "lunch": "Arroz blanco con verduras suaves y huevo.",
            "dinner": "Tortillas de maíz con lechuga y tomate.",
        },
        {
            "day": "Sábado",
            "breakfast": "Batido con bebida de almendra, espinacas y frutos rojos.",
            "lunch": "Ensalada de patata con pepino y huevo cocido.",
            "dinner": "Crema de calabaza con arroz.",
        },
        {
            "day": "Domingo",
            "breakfast": "Huevos revueltos con tomate y aguacate en pequeña porción.",
            "lunch": "Arroz sencillo con verduras sin ajo ni cebolla.",
            "dinner": "Crema de calabacín y zanahoria.",
        },
    ]