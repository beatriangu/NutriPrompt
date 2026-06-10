from typing import Any


def rule_to_text(rule: dict[str, Any]) -> str:
    """
    Convert a structured nutrition rule into searchable text.
    """

    title = rule.get("title", "")
    category = rule.get("category", "")
    rule_text = rule.get("rule", "")
    risk_level = rule.get("risk_level", "")
    keywords = ", ".join(rule.get("keywords", []))

    return f"""
    Category: {category}
    Title: {title}
    Rule: {rule_text}
    Risk level: {risk_level}
    Keywords: {keywords}
    """.strip()


def build_text_corpus(rules: list[dict[str, Any]]) -> list[str]:
    """
    Build a text corpus from nutrition rules.
    """

    return [rule_to_text(rule) for rule in rules]