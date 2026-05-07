from __future__ import annotations

import json
from typing import Any

from nutriprompt_app.services.ai.response_cleaner import clean_markdown_json_response


def parse_ai_json_response(text: str) -> Any:
    """
    Limpia y convierte una respuesta de IA en JSON Python.

    Devuelve:
    - dict si el JSON es un objeto
    - list si el JSON es una lista

    Lanza ValueError si la respuesta no es JSON válido.
    """
    cleaned_text = clean_markdown_json_response(text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La respuesta de IA no contiene JSON válido: {exc}") from exc
