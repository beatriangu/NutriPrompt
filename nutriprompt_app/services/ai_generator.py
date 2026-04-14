import json
from typing import Any

from django.conf import settings
from google import genai


SYSTEM_PROMPT = """
Actúa como un asistente de generación de planes alimenticios inspirado en buenas prácticas nutricionales, con especial atención a la dieta baja en FODMAPs.

Tu objetivo es generar un plan semanal estructurado y orientativo adaptado a un cliente.

IMPORTANTE:
- Este plan es orientativo y no sustituye el asesoramiento de un profesional sanitario.
- No realices afirmaciones médicas ni diagnósticos.

REQUISITOS:
- Genera un plan de 7 días
- Incluye desayuno, comida y cena para cada día
- Evita alimentos altos en FODMAPs
- Evita ajo y cebolla
- Usa comidas sencillas y prácticas
- Mantén variedad durante la semana

FORMATO DE SALIDA:
Devuelve SOLO un JSON válido con esta estructura:

[
  {
    "day": "Lunes",
    "breakfast": "...",
    "lunch": "...",
    "dinner": "..."
  }
]

No añadas texto antes ni después del JSON.
"""


def _get_client() -> genai.Client:
    api_key = settings.GOOGLE_API_KEY
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")
    return genai.Client(api_key=api_key)


def _clean_json_output(raw_output: str) -> str:
    return raw_output.replace("```json", "").replace("```", "").strip()


def _validate_plan_data(data: Any) -> list[dict]:
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list of meal-plan days.")

    required_keys = {"day", "breakfast", "lunch", "dinner"}

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Item {index} is not a valid JSON object.")

        missing = required_keys - item.keys()
        if missing:
            raise ValueError(
                f"Missing keys in item {index}: {', '.join(sorted(missing))}"
            )

    return data


def generate_meal_plan(
    user_input: str,
    model: str = "gemini-2.5-flash",
) -> list[dict]:
    if not user_input or not user_input.strip():
        raise ValueError("Client input cannot be empty.")

    client = _get_client()
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_input.strip()}"

    try:
        response = client.models.generate_content(
            model=model,
            contents=full_prompt,
        )
    except Exception as exc:
        error_message = str(exc)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise ValueError(
                "Gemini quota has been reached for now. Please try again later."
            ) from exc

        if "503" in error_message or "UNAVAILABLE" in error_message:
            raise ValueError(
                "Gemini is temporarily overloaded. Please try again in a few minutes."
            ) from exc

        if "404" in error_message or "NOT_FOUND" in error_message:
            raise ValueError(
                f"The model '{model}' is not available in this configuration."
            ) from exc

        raise ValueError(f"Could not generate the plan: {error_message}") from exc

    raw_output = getattr(response, "text", "") or ""
    if not raw_output.strip():
        raise ValueError("The model returned an empty response.")

    clean_output = _clean_json_output(raw_output)

    try:
        data = json.loads(clean_output)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model output is not valid JSON: {exc}") from exc

    return _validate_plan_data(data)
def get_mock_meal_plan() -> list[dict]:
    return [
        {
            "day": "Lunes",
            "breakfast": "Avena sin gluten con leche de almendras y arándanos.",
            "lunch": "Ensalada de pollo con pepino y zanahoria.",
            "dinner": "Salmón al horno con patatas y judías verdes.",
        },
        {
            "day": "Martes",
            "breakfast": "Huevos revueltos con espinacas y pan sin gluten.",
            "lunch": "Sobras de salmón con patatas.",
            "dinner": "Pollo a la plancha con arroz y calabacín.",
        },
        {
            "day": "Miércoles",
            "breakfast": "Yogur sin lactosa con kiwi.",
            "lunch": "Quinoa con pollo y tomates cherry.",
            "dinner": "Bacalao con zanahorias al vapor.",
        },
        {
            "day": "Jueves",
            "breakfast": "Tortitas de arroz con crema de cacahuete y plátano firme.",
            "lunch": "Sobras de bacalao con zanahorias.",
            "dinner": "Salteado de pollo con pimiento rojo y fideos de arroz.",
        },
        {
            "day": "Viernes",
            "breakfast": "Copos de maíz sin gluten con leche de almendras.",
            "lunch": "Ensalada de atún con lechuga.",
            "dinner": "Muslos de pollo al horno con boniato y ensalada verde.",
        },
        {
            "day": "Sábado",
            "breakfast": "Batido de leche de almendras, espinacas y plátano firme.",
            "lunch": "Sobras de pollo y boniato.",
            "dinner": "Tacos de pescado en tortillas de maíz con lechuga.",
        },
        {
            "day": "Domingo",
            "breakfast": "Huevos revueltos con tomate y aguacate.",
            "lunch": "Ensalada grande con pollo a la parrilla.",
            "dinner": "Sopa de pollo con zanahoria, calabacín y patata.",
        },
    ]