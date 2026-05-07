from __future__ import annotations

import time

from django.conf import settings
from openai import OpenAI


MODEL_NAME_OPENAI = "gpt-5-mini"
MAX_PROVIDER_RETRIES = 2


def get_openai_client() -> OpenAI:
    api_key = getattr(settings, "OPENAI_API_KEY", None)

    if not api_key:
        raise ValueError("OPENAI_API_KEY no está configurada.")

    return OpenAI(api_key=api_key)


def should_retry_provider_error(error_message: str) -> bool:
    upper = error_message.upper()
    return any(
        marker in upper
        for marker in ["503", "UNAVAILABLE", "OVERLOADED", "TIMEOUT", "TIMED OUT"]
    )


def is_quota_error(error_message: str) -> bool:
    upper = error_message.upper()
    return "429" in upper or "RESOURCE_EXHAUSTED" in upper or "RATE LIMIT" in upper


def call_openai(
    prompt: str,
    model: str = MODEL_NAME_OPENAI,
    max_retries: int = MAX_PROVIDER_RETRIES,
) -> str:
    client = get_openai_client()
    last_error = ""

    for attempt in range(1, max_retries + 1):
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

            if should_retry_provider_error(last_error) and attempt < max_retries:
                time.sleep(2)
                continue

            if is_quota_error(last_error):
                raise ValueError("OpenAI ha alcanzado temporalmente su límite de uso.") from exc

            if should_retry_provider_error(last_error):
                raise ValueError(
                    "OpenAI está temporalmente saturado. Inténtalo de nuevo en unos minutos."
                ) from exc

            if "404" in last_error or "NOT_FOUND" in last_error.upper():
                raise ValueError(f"El modelo de OpenAI '{model}' no está disponible.") from exc

            raise ValueError(f"No se ha podido generar el plan con OpenAI: {last_error}") from exc

    raise ValueError(f"No se ha podido generar el plan con OpenAI: {last_error}")
