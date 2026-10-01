import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compliance_engine.evaluator import evaluate_document


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        fixture = Path(__file__).resolve().parents[2] / "fixtures" / "analysis-request.sample.json"
        self.request = json.loads(fixture.read_text(encoding="utf-8"))

    def test_evaluates_matched_clauses_into_traceable_findings(self):
        result = evaluate_document(self.request, analyzed_at="2026-10-01T12:00:00Z")

        self.assertEqual("analysis-070f72d9ba3f", result["analysis_id"])
        self.assertEqual("0.1.0", result["rule_set_version"])
        self.assertEqual("complete", result["coverage"]["status"])
        self.assertEqual(3, len(result["findings"]))
        sharing = next(finding for finding in result["findings"] if finding["rule_id"] == "DSHARE-001")
        self.assertEqual("clause-2", sharing["evidence"][0]["clause_id"])
        self.assertEqual("signal-agency-001", result["positive_signals"][0]["signal_id"])
        self.assertEqual(66.5, result["trust_score"])
        self.assertEqual("low", result["risk_level"])

    def test_exclusion_prevents_a_false_positive(self):
        request = {
            "document_id": "no-ad-sharing",
            "text": "We do not share personal information with advertising partners. This statement provides enough words to evaluate readability as part of this test policy.",
            "clauses": [{"clause_id": "c-1", "text": "We do not share personal information with advertising partners.", "start_offset": 0, "end_offset": 60}],
        }
        result = evaluate_document(request)

        self.assertFalse(any(finding["rule_id"] == "DSHARE-001" for finding in result["findings"]))
        self.assertEqual("partial", result["coverage"]["status"])

    def test_missing_clause_evidence_is_reported_as_partial(self):
        request = {
            "document_id": "thin-policy",
            "text": "Short supplied policy text with enough words to make only readability assessable in this evaluator test.",
            "clauses": [{"clause_id": "c-1", "text": "Short supplied policy text with enough words to make only readability assessable in this evaluator test.", "start_offset": 0, "end_offset": 100}],
        }
        result = evaluate_document(request)

        self.assertEqual("partial", result["coverage"]["status"])
        self.assertTrue(any("insufficient evidence" in item.lower() for item in result["limitations"]))


if __name__ == "__main__":
    unittest.main()
