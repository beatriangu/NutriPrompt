from typing import Any

from nutriprompt_app.services.rag.knowledge_base import get_rules
from nutriprompt_app.services.rag.retriever import retrieve_relevant_rules


def build_rag_context(query: str, top_k: int = 3) -> str:
    """
    Build a readable RAG context block from the most relevant nutrition rules.
    """

    rules = get_rules()
    relevant_rules = retrieve_relevant_rules(query=query, rules=rules, top_k=top_k)

    if not relevant_rules:
        return (
            "No se han recuperado reglas nutricionales específicas para esta consulta. "
            "Responde con prudencia, indicando que la información es orientativa."
        )

    context_lines = [
        "CONTEXTO NUTRICIONAL RECUPERADO:",
        "",
    ]

    for rule in relevant_rules:
        context_lines.append(f"- Categoría: {rule.get('category', 'general')}")
        context_lines.append(f"  Título: {rule.get('title', 'Sin título')}")
        context_lines.append(f"  Regla: {rule.get('rule', '')}")
        context_lines.append(f"  Nivel de riesgo: {rule.get('risk_level', 'unknown')}")
        context_lines.append("")

    return "\n".join(context_lines)