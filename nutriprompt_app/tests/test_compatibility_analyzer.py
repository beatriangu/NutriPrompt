from django.test import SimpleTestCase

from nutriprompt_app.services.vision.compatibility_analyzer import (
    analyze_context_compatibility,
)


class CompatibilityAnalyzerTests(SimpleTestCase):

    def test_gluten_conflict_detected(self):
        plan_analysis = {
            "detected_restrictions": ["sin_gluten"]
        }

        product_analyses = [
            {
                "intake_type": "product_label",
                "ocr_text": "Ingredientes: harina de trigo, agua y sal"
            }
        ]

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            product_analyses=product_analyses,
        )

        self.assertEqual(result["global_status"], "not_compatible")

    def test_low_fodmap_conflict_detected(self):
        plan_analysis = {
            "detected_restrictions": ["low_fodmap"]
        }

        product_analyses = [
            {
                "ocr_text": "Ingredientes: sopa de cebolla y especias"
            }
        ]

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            product_analyses=product_analyses,
        )

        self.assertEqual(result["global_status"], "not_compatible")

    def test_compatible_detected_items_are_marked_compatible(self):
        plan_analysis = {
            "detected_restrictions": ["low_fodmap"]
        }

        product_analyses = [
            {
                "detected_items": ["arroz", "pollo"]
            }
        ]

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            product_analyses=product_analyses,
        )

        self.assertEqual(result["global_status"], "compatible")
        self.assertIn("arroz", result["compatible_items"])
        self.assertIn("pollo", result["compatible_items"])

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            product_analyses=product_analyses,
        )

        self.assertIn(
            result["global_status"],
            ["compatible", "review"]
        )

    def test_unknown_when_no_information_exists(self):
        result = analyze_context_compatibility()

        self.assertEqual(result["global_status"], "unknown")

    def test_plan_profile_is_generated(self):
        plan_analysis = {
            "detected_restrictions": [
                "sin_gluten",
                "low_fodmap"
            ],
            "detected_goals": [
                "organizar comidas"
            ]
        }

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis
        )

        self.assertIn(
            "detected_restrictions",
            result["plan_profile"]
        )

    def test_detected_items_are_collected(self):
        plan_analysis = {
            "detected_restrictions": ["low_fodmap"]
        }

        product_analyses = [
            {
                "detected_items": [
                    "arroz",
                    "pollo"
                ]
            }
        ]

        result = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            product_analyses=product_analyses,
        )

        self.assertIn("arroz", result["available_items"])
        self.assertIn("pollo", result["available_items"])

    def test_professional_notice_exists(self):
        result = analyze_context_compatibility()

        self.assertIn(
            "profesional",
            result["professional_notice"].lower()
        )