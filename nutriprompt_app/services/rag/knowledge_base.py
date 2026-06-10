import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[3]
DEFAULT_RULES_PATH = BASE_DIR / "data" / "processed" / "nutrition_rules.json"


def load_knowledge_base(rules_path: Path = DEFAULT_RULES_PATH) -> dict[str, Any]:
    """
    Load the NutriPrompt nutrition knowledge base from a JSON file.
    """

    if not rules_path.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {rules_path}")

    with rules_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "rules" not in data:
        raise ValueError("Invalid knowledge base format: missing 'rules' key.")

    if not isinstance(data["rules"], list):
        raise ValueError("Invalid knowledge base format: 'rules' must be a list.")

    return data


def get_rules(rules_path: Path = DEFAULT_RULES_PATH) -> list[dict[str, Any]]:
    """
    Return only the list of nutrition rules.
    """

    knowledge_base = load_knowledge_base(rules_path)
    return knowledge_base["rules"]