from django.test import SimpleTestCase

from nutriprompt_app.services.ai.prompt_builder import build_full_prompt
from nutriprompt_app.services.rag.embeddings import build_text_corpus, rule_to_text
from nutriprompt_app.services.rag.knowledge_base import get_rules, load_knowledge_base
from nutriprompt_app.services.rag.rag_context_builder import build_rag_context
from nutriprompt_app.services.rag.retriever import retrieve_relevant_rules


class RAGServiceTests(SimpleTestCase):
    def test_knowledge_base_loads_rules(self):
        knowledge_base = load_knowledge_base()

        self.assertIn("rules", knowledge_base)
        self.assertIsInstance(knowledge_base["rules"], list)
        self.assertGreater(len(knowledge_base["rules"]), 0)

    def test_rule_to_text_contains_relevant_fields(self):
        rules = get_rules()
        text = rule_to_text(rules[0])

        self.assertIn("Category:", text)
        self.assertIn("Title:", text)
        self.assertIn("Rule:", text)
        self.assertIn("Risk level:", text)
        self.assertIn("Keywords:", text)

    def test_build_text_corpus_from_rules(self):
        rules = get_rules()
        corpus = build_text_corpus(rules)

        self.assertIsInstance(corpus, list)
        self.assertEqual(len(corpus), len(rules))
        self.assertTrue(all(isinstance(item, str) for item in corpus))

    def test_retriever_finds_low_fodmap_rules(self):
        rules = get_rules()
        query = "Tengo dieta low FODMAP y quiero evitar sopa de cebolla"

        results = retrieve_relevant_rules(query=query, rules=rules, top_k=3)

        self.assertGreater(len(results), 0)
        self.assertTrue(any("cebolla" in rule["title"].lower() for rule in results))

    def test_retriever_finds_gluten_rules(self):
        rules = get_rules()
        query = "No puedo tomar gluten y quiero saber si puedo comer trigo"

        results = retrieve_relevant_rules(query=query, rules=rules, top_k=3)

        self.assertGreater(len(results), 0)
        self.assertTrue(any(rule["category"] == "sin_gluten" for rule in results))

    def test_rag_context_builder_returns_context_block(self):
        query = "Tengo dieta sin gluten y bajo en FODMAPs. ¿Puedo tomar sopa de cebolla?"

        context = build_rag_context(query)

        self.assertIn("CONTEXTO NUTRICIONAL RECUPERADO", context)
        self.assertTrue("Cebolla" in context or "cebolla" in context)
        self.assertIn("Nivel de riesgo", context)

    def test_prompt_builder_includes_rag_context(self):
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

        self.assertIn("CONTEXTO NUTRICIONAL RECUPERADO MEDIANTE RAG", prompt)
        self.assertIn("Cebolla en dieta low FODMAP", prompt)
        self.assertTrue("Trigo y gluten" in prompt or "sin_gluten" in prompt)