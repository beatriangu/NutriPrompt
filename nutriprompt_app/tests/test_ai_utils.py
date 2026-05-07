from django.test import SimpleTestCase

from nutriprompt_app.services.ai.response_cleaner import clean_markdown_json_response
from nutriprompt_app.services.ai.json_parser import parse_ai_json_response


class AIUtilsTests(SimpleTestCase):
    def test_clean_markdown_json_response(self):
        raw = """```json
{"dia": 1}
```"""
        self.assertEqual(clean_markdown_json_response(raw), '{"dia": 1}')

    def test_parse_ai_json_response(self):
        raw = """```json
[{"dia": 1, "desayuno": "Avena"}]
```"""
        result = parse_ai_json_response(raw)

        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["dia"], 1)
        self.assertEqual(result[0]["desayuno"], "Avena")
