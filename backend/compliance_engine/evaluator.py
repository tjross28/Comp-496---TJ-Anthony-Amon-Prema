"""Clause-level, explainable evaluation of the versioned rule catalog."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .scoring import CATEGORY_LABELS, CATEGORY_ORDER, CategoryAssessment, calculate_score

ENGINE_VERSION = "0.1.0"
DISCLAIMER = "Automated educational analysis only; this is not legal advice or a legal compliance determination."
BASE_SCORES = {
    "data_sharing": 75,
    "data_collection": 70,
    "legal_language": 75,
    "user_agency": 60,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def _excerpt(text: str, limit: int = 260) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else f"{text[:limit - 1].rstrip()}…"


def load_catalog(path: str | Path | None = None) -> dict[str, Any]:
    """Load the rule-set configuration supplied with this engine."""

    catalog_path = Path(path) if path else Path(__file__).resolve().parents[1] / "rules" / "rules-v0.1.json"
    with catalog_path.open(encoding="utf-8") as source:
        return json.load(source)


def _matching_clauses(rule: Mapping[str, Any], clauses: list[Mapping[str, Any]], field: str) -> list[dict[str, str]]:
    patterns = [_normalize(pattern) for pattern in rule[field]]
    exclusions = [_normalize(pattern) for pattern in rule.get("exclusions", [])]
    matches = []
    for clause in clauses:
        normalized = _normalize(str(clause["text"]))
        if any(exclusion in normalized for exclusion in exclusions):
            continue
        if any(pattern in normalized for pattern in patterns):
            matches.append({"clause_id": str(clause["clause_id"]), "excerpt": _excerpt(str(clause["text"]))})
    return matches


def _readability_assessment(text: str) -> CategoryAssessment | None:
    words = re.findall(r"\b[\w'-]+\b", text)
    sentences = re.findall(r"[.!?]+", text)
    if len(words) < 12:
        return None
    average = len(words) / max(1, len(sentences))
    score = max(0, min(100, round(100 - max(0, average - 12) * 3)))
    rationale = f"Average sentence length is {average:.1f} words across the supplied text."
    return CategoryAssessment(score=score, rationale=rationale)


def evaluate_document(request: Mapping[str, Any], *, catalog_path: str | Path | None = None, analyzed_at: str | None = None) -> dict[str, Any]:
    """Evaluate a normalized policy request and return the response contract shape.

    Only a matched phrase produces a regulatory-related finding. An unmatched
    rule does not mean the policy complies or that the framework applies.
    """

    clauses = list(request.get("clauses", []))
    if not clauses:
        raise ValueError("At least one clause is required for evaluation")
    for clause in clauses:
        if not clause.get("clause_id") or not str(clause.get("text", "")).strip():
            raise ValueError("Every clause requires clause_id and text")

    catalog = load_catalog(catalog_path)
    findings: list[dict[str, Any]] = []
    positive_signals: list[dict[str, Any]] = []
    impacts: dict[str, int] = {category: 0 for category in CATEGORY_ORDER}
    evidence_seen: dict[str, bool] = {category: False for category in CATEGORY_ORDER}
    finding_ids: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}

    for rule in catalog["rules"]:
        concern_evidence = _matching_clauses(rule, clauses, "concern_patterns")
        positive_evidence = _matching_clauses(rule, clauses, "positive_patterns")
        category = rule["category"]
        if concern_evidence:
            finding_id = f"finding-{rule['id'].casefold()}"
            findings.append(
                {
                    "finding_id": finding_id,
                    "rule_id": rule["id"],
                    "category": category,
                    "severity": rule["severity"],
                    "status": rule["status"],
                    "title": rule["title"],
                    "explanation": rule["explanation"],
                    "evidence": concern_evidence,
                    "regulations": rule["regulations"],
                    "next_step": rule["next_step"],
                }
            )
            impacts[category] += int(rule["score_impact"])
            evidence_seen[category] = True
            finding_ids[category].append(finding_id)
        if positive_evidence:
            positive_signals.append(
                {
                    "signal_id": f"signal-{rule['id'].casefold()}",
                    "category": category,
                    "title": rule["title"],
                    "evidence": positive_evidence,
                }
            )
            impacts[category] += int(rule["score_impact"])
            evidence_seen[category] = True

    assessments: dict[str, CategoryAssessment] = {}
    readability = _readability_assessment(str(request.get("text", "")))
    if readability:
        assessments["readability"] = readability
    for category, base_score in BASE_SCORES.items():
        if evidence_seen[category]:
            score = max(0, min(100, base_score + impacts[category]))
            assessments[category] = CategoryAssessment(
                score=score,
                rationale=f"Score starts at {base_score} and changes by {impacts[category]:+d} from documented text signals.",
                finding_ids=tuple(finding_ids[category]),
            )

    score_result = calculate_score(assessments)
    limitations = [catalog["disclaimer"], "An absent match is not evidence of legal compliance or regulatory applicability."]
    if score_result["coverage"]["status"] != "complete":
        limitations.append("One or more score categories had insufficient evidence in the supplied clauses.")

    document_id = str(request.get("document_id", "document"))
    digest = hashlib.sha256(document_id.encode("utf-8")).hexdigest()[:12]
    return {
        "analysis_id": f"analysis-{digest}",
        "engine_version": ENGINE_VERSION,
        "rule_set_version": catalog["version"],
        "analyzed_at": analyzed_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        **score_result,
        "findings": findings,
        "positive_signals": positive_signals,
        "limitations": limitations,
        "disclaimer": DISCLAIMER,
    }
