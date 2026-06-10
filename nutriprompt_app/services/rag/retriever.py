from typing import Any

from nutriprompt_app.services.rag.embeddings import rule_to_text


def normalize_text(text: str) -> str:
    """
    Normalize text for simple keyword-based retrieval.
    """

    return text.lower().strip()


def score_rule(query: str, rule: dict[str, Any]) -> int:
    """
    Score a rule according to how many relevant words match the user query.
    This is a simple first version before using real embeddings.
    """

    normalized_query = normalize_text(query)
    searchable_text = normalize_text(rule_to_text(rule))

    score = 0

    for keyword in rule.get("keywords", []):
        if normalize_text(keyword) in normalized_query:
            score += 3

    for word in normalized_query.split():
        if word in searchable_text:
            score += 1

    return score


def retrieve_relevant_rules(
    query: str,
    rules: list[dict[str, Any]],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    Retrieve the most relevant nutrition rules for a user query.
    """

    scored_rules = []

    for rule in rules:
        score = score_rule(query, rule)

        if score > 0:
            scored_rules.append(
                {
                    "score": score,
                    "rule": rule,
                }
            )

    scored_rules.sort(key=lambda item: item["score"], reverse=True)

    return [item["rule"] for item in scored_rules[:top_k]]