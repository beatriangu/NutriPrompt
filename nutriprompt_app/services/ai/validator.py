from __future__ import annotations

import re
from typing import Any

from nutriprompt_app.services.ai.rules import _infer_rules, _normalize_text
from nutriprompt_app.services.ai.json_parser import parse_ai_json_response


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


def validate_plan_data(data: Any, user_input: str) -> list[dict[str, str]]:
    if not isinstance(data, list):
        raise ValueError("La salida del modelo no es una lista JSON válida.")

    if len(data) != 7:
        raise ValueError(f"Se esperaban 7 días, pero se recibieron {len(data)}.")

    validated: list[dict[str, str]] = []

    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El elemento {index} no es un objeto JSON válido.")

        missing = set(REQUIRED_KEYS) - item.keys()

        if missing:
            raise ValueError(f"Faltan claves en el día {index}: {', '.join(sorted(missing))}")

        normalized_item: dict[str, str] = {}

        for key in REQUIRED_KEYS:
            value = item.get(key)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"El campo '{key}' del día {index} debe ser texto no vacío.")

            normalized_item[key] = value.strip()

        expected_day = SPANISH_DAYS[index - 1]

        if _normalize_text(normalized_item["day"]) != _normalize_text(expected_day):
            normalized_item["day"] = expected_day

        validated.append(normalized_item)

    return validated


def parse_and_validate_plan(raw_output: str, user_input: str) -> list[dict[str, str]]:
    data = parse_ai_json_response(raw_output)
    return validate_plan_data(data, user_input)
