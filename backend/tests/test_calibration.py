import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compliance_engine.evaluator import evaluate_document


class CalibrationTests(unittest.TestCase):
    def test_versioned_fixture_corpus_stays_within_expected_bounds(self):
        directory = Path(__file__).resolve().parents[2] / "fixtures" / "calibration"
        for fixture_path in sorted(directory.glob("*.json")):
            with self.subTest(fixture=fixture_path.name):
                fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
                result = evaluate_document(fixture["request"], analyzed_at="2026-10-01T00:00:00Z")
                expected = fixture["expected"]
                finding_rules = {finding["rule_id"] for finding in result["findings"]}
                signal_rules = {signal["signal_id"].replace("signal-", "").upper() for signal in result["positive_signals"]}

                self.assertEqual(expected["coverage"], result["coverage"]["status"])
                self.assertGreaterEqual(result["trust_score"], expected["min_trust_score"])
                self.assertLessEqual(result["trust_score"], expected["max_trust_score"])
                self.assertTrue(set(expected.get("rule_ids", [])).issubset(finding_rules))
                self.assertTrue(set(expected.get("excluded_rule_ids", [])).isdisjoint(finding_rules))
                expected_positive = {rule.lower() for rule in expected.get("positive_rule_ids", [])}
                self.assertTrue(expected_positive.issubset({rule.lower() for rule in signal_rules}))
