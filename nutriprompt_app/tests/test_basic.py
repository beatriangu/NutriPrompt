from django.test import TestCase


class BasicProjectTests(TestCase):
    def test_project_loads_correctly(self):
        self.assertEqual(1 + 1, 2)
