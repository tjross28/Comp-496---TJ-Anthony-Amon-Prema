"""Deterministic weighted Trust Score calculation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

CATEGORY_ORDER = (
    "data_sharing",
    "readability",
    "data_collection",
    "legal_language",
    "user_agency",
)

CATEGORY_LABELS = {
    "data_sharing": "Data sharing",
    "readability": "Readability and transparency",
    "data_collection": "Data collection",
    "legal_language": "Legal language",
    "user_agency": "User agency",
}

WEIGHTS = {
    "data_sharing": Decimal("0.25"),
    "readability": Decimal("0.20"),
    "data_collection": Decimal("0.20"),
    "legal_language": Decimal("0.20"),
    "user_agency": Decimal("0.15"),
}


@dataclass(frozen=True)
class CategoryAssessment:
    """Evidence-derived assessment for one score category."""

    score: float | None
    rationale: str
    finding_ids: tuple[str, ...] = ()


def _round(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _risk_level(trust_score: Decimal, coverage_status: str) -> str:
    if coverage_status == "insufficient_evidence":
        return "unknown"
    if trust_score < Decimal("40"):
        return "high"
    if trust_score < Decimal("65"):
        return "moderate"
    return "low"


def calculate_score(assessments: Mapping[str, CategoryAssessment]) -> dict:
    """Return category math, score, and coverage from explicit assessments.

    A category without enough evidence has ``score=None``. Its weight is not
    silently counted as a favorable score; the result carries partial coverage.
    The reported Trust Score is normalized across assessed category weights.
    """

    unexpected = set(assessments).difference(CATEGORY_ORDER)
    if unexpected:
        raise ValueError(f"Unknown scoring categories: {sorted(unexpected)}")

    categories = []
    weighted_total = Decimal("0")
    assessed_weight = Decimal("0")
    assessed_count = 0

    for category_id in CATEGORY_ORDER:
        assessment = assessments.get(category_id)
        weight = WEIGHTS[category_id]
        if assessment is None or assessment.score is None:
            categories.append(
                {
                    "id": category_id,
                    "label": CATEGORY_LABELS[category_id],
                    "weight": float(weight),
                    "score": None,
                    "weighted_score": None,
                    "status": "insufficient_evidence",
                    "rationale": assessment.rationale if assessment else "No assessment was provided.",
                    "finding_ids": list(assessment.finding_ids) if assessment else [],
                }
            )
            continue

        if not 0 <= assessment.score <= 100:
            raise ValueError(f"{category_id} score must be between 0 and 100")

        score = Decimal(str(assessment.score))
        weighted_score = score * weight
        weighted_total += weighted_score
        assessed_weight += weight
        assessed_count += 1
        categories.append(
            {
                "id": category_id,
                "label": CATEGORY_LABELS[category_id],
                "weight": float(weight),
                "score": _round(score),
                "weighted_score": _round(weighted_score),
                "status": "assessed",
                "rationale": assessment.rationale,
                "finding_ids": list(assessment.finding_ids),
            }
        )

    if assessed_count == 0:
        coverage_status = "insufficient_evidence"
        trust_score = Decimal("0")
    else:
        coverage_status = "complete" if assessed_count == len(CATEGORY_ORDER) else "partial"
        trust_score = weighted_total / assessed_weight

    return {
        "trust_score": _round(trust_score),
        "risk_level": _risk_level(trust_score, coverage_status),
        "categories": categories,
        "coverage": {
            "assessed_categories": assessed_count,
            "total_categories": len(CATEGORY_ORDER),
            "status": coverage_status,
        },
    }
