import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class RuleCatalogTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "rules" / "rules-v0.1.json"
        self.catalog = json.loads(path.read_text(encoding="utf-8"))

    def test_rule_ids_are_unique_and_have_required_metadata(self):
        rules = self.catalog["rules"]
        self.assertEqual(len(rules), len({rule["id"] for rule in rules}))
        for rule in rules:
            self.assertIn(rule["status"], {"signal", "requires_review"})
            self.assertIn(rule["category"], {"data_sharing", "readability", "data_collection", "legal_language", "user_agency"})
            self.assertIsInstance(rule["score_impact"], int)
            self.assertTrue(rule["explanation"])

    def test_regulation_references_have_traceable_sources(self):
        for rule in self.catalog["rules"]:
            for reference in rule["regulations"]:
                self.assertTrue(reference["source_url"].startswith("https://"))
                self.assertTrue(reference["reviewed_on"])


if __name__ == "__main__":
    unittest.main()
