from __future__ import annotations

import re
import unicodedata
from typing import Any


LABEL_FIXES = {
    "sin glutén": "sin gluten",
    "fácil. de preparar": "fácil de preparar",
    "sin lactosa y baja en fodmaps": "sin lactosa y bajo en FODMAPs",
}

PHRASES_TO_REMOVE = {
    "(rápido de preparar)",
}


def safe_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_text(value: Any) -> str:
    text = safe_text(value).casefold()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.split())


def clean_label(text: str) -> str:
    value = safe_text(text)
    lower = normalize_text(value)

    for wrong, correct in LABEL_FIXES.items():
        if normalize_text(wrong) == lower:
            return correct
    return value


def clean_meal_text(text: str) -> str:
    value = safe_text(text)

    for phrase in PHRASES_TO_REMOVE:
        value = re.sub(r"\s+", " ", value).strip()
        value = remove_duplicate_phrases(value)

    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ,", ",")
    value = value.replace(" .", ".")
    return value


def clean_list(values: list[str]) -> list[str]:
    seen = set()
    result = []

    for item in values:
        cleaned = clean_label(clean_meal_text(item))
        key = normalize_text(cleaned)
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)

    return result

def remove_duplicate_phrases(text: str) -> str:
    words = text.split()
    seen = []
    for word in words:
        if not seen or word.lower() != seen[-1].lower():
            seen.append(word)
    return " ".join(seen)