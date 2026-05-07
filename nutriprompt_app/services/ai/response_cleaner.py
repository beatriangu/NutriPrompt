from __future__ import annotations


def clean_markdown_json_response(text: str) -> str:
    """
    Limpia respuestas de IA que vienen envueltas en bloques Markdown.

    Ejemplo:
    ```json
    {...}
    ```

    Devuelve solo el contenido JSON/texto limpio.
    """
    if not text:
        return ""

    return (
        text.replace("```json", "")
        .replace("```JSON", "")
        .replace("```", "")
        .strip()
    )
