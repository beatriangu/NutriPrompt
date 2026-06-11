from nutriprompt_app.services.rag.embeddings import build_text_corpus, rule_to_text
from nutriprompt_app.services.rag.knowledge_base import get_rules, load_knowledge_base
from nutriprompt_app.services.rag.rag_context_builder import build_rag_context
from nutriprompt_app.services.rag.retriever import retrieve_relevant_rules
from nutriprompt_app.services.ai.prompt_builder import build_full_prompt


def test_knowledge_base_loads_rules():
    knowledge_base = load_knowledge_base()

    assert "rules" in knowledge_base
    assert isinstance(knowledge_base["rules"], list)
    assert len(knowledge_base["rules"]) > 0


def test_rule_to_text_contains_relevant_fields():
    rules = get_rules()
    text = rule_to_text(rules[0])

    assert "Category:" in text
    assert "Title:" in text
    assert "Rule:" in text
    assert "Risk level:" in text
    assert "Keywords:" in text


def test_build_text_corpus_from_rules():
    rules = get_rules()
    corpus = build_text_corpus(rules)

    assert isinstance(corpus, list)
    assert len(corpus) == len(rules)
    assert all(isinstance(item, str) for item in corpus)


def test_retriever_finds_low_fodmap_rules():
    rules = get_rules()
    query = "Tengo dieta low FODMAP y quiero evitar sopa de cebolla"

    results = retrieve_relevant_rules(query=query, rules=rules, top_k=3)

    assert len(results) > 0
    assert any("cebolla" in rule["title"].lower() for rule in results)


def test_retriever_finds_gluten_rules():
    rules = get_rules()
    query = "No puedo tomar gluten y quiero saber si puedo comer trigo"

    results = retrieve_relevant_rules(query=query, rules=rules, top_k=3)

    assert len(results) > 0
    assert any(rule["category"] == "sin_gluten" for rule in results)


def test_rag_context_builder_returns_context_block():
    query = "Tengo dieta sin gluten y bajo en FODMAPs. ¿Puedo tomar sopa de cebolla?"

    context = build_rag_context(query)

    assert "CONTEXTO NUTRICIONAL RECUPERADO" in context
    assert "Cebolla" in context or "cebolla" in context
    assert "Nivel de riesgo" in context


def test_prompt_builder_includes_rag_context():
    user_input = """
    Nombre: Bea
    Objetivo: organizar comidas
    Restricciones: sin gluten, bajo en FODMAPs
    Preferencias: arroz, pollo, sopa de cebolla
    Presupuesto semanal: ajustado
    Contexto principal: trabajo
    ¿Necesita tupper?: sí
    Acceso a cocina: completo
    Etiquetas de perfil detectadas: sin gluten, bajo en FODMAPs, necesita tupper
    """

    prompt = build_full_prompt(user_input)

    assert "CONTEXTO NUTRICIONAL RECUPERADO MEDIANTE RAG" in prompt
    assert "Cebolla en dieta low FODMAP" in prompt
    assert "Trigo y gluten" in prompt or "sin_gluten" in prompt