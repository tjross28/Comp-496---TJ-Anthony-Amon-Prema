import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compliance_engine.scoring import CategoryAssessment, calculate_score


def assessment(score, rationale="Test assessment", finding_ids=()):
    return CategoryAssessment(score=score, rationale=rationale, finding_ids=finding_ids)


class ScoringTests(unittest.TestCase):
    def test_full_weighted_score_and_risk_are_deterministic(self):
        result = calculate_score({
            "data_sharing": assessment(40, finding_ids=("sharing-1",)),
            "readability": assessment(70),
            "data_collection": assessment(50),
            "legal_language": assessment(55),
            "user_agency": assessment(80),
        })

        self.assertEqual(57.0, result["trust_score"])
        self.assertEqual("moderate", result["risk_level"])
        self.assertEqual("complete", result["coverage"]["status"])
        self.assertEqual(["sharing-1"], result["categories"][0]["finding_ids"])

    def test_partial_assessment_is_normalized_and_disclosed(self):
        result = calculate_score({"data_sharing": assessment(20)})

        self.assertEqual(20.0, result["trust_score"])
        self.assertEqual("partial", result["coverage"]["status"])
        self.assertEqual("high", result["risk_level"])
        self.assertIsNone(result["categories"][1]["score"])

    def test_missing_all_categories_is_unknown_not_low_risk(self):
        result = calculate_score({})

        self.assertEqual(0.0, result["trust_score"])
        self.assertEqual("unknown", result["risk_level"])
        self.assertEqual("insufficient_evidence", result["coverage"]["status"])

    def test_rejects_invalid_category_and_score(self):
        with self.assertRaisesRegex(ValueError, "Unknown scoring"):
            calculate_score({"made_up": assessment(50)})
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            calculate_score({"data_sharing": assessment(101)})


if __name__ == "__main__":
    unittest.main()
