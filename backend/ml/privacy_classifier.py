"""Inference for the compact OPP-115-trained multi-label clause classifier."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

MODEL_PATH = Path(__file__).resolve().parent / "privacy_clause_model_v1.json"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


def text_features(text: str) -> set[str]:
    """Return binary unigram and adjacent-bigram features."""

    words = TOKEN_PATTERN.findall(text.casefold())
    features = set(words)
    features.update(f"{left}_{right}" for left, right in zip(words, words[1:]))
    return features


class PrivacyClauseClassifier:
    """Portable multi-label multinomial Naive Bayes model loaded from JSON."""

    def __init__(self, model: Mapping[str, Any]):
        if model.get("artifact_type") != "privacy_policy_clause_classifier":
            raise ValueError("Unsupported classifier artifact.")
        self.model = model
        self.version = str(model["version"])
        self.vocabulary = set(model["vocabulary"])
        self.classes = model["classes"]
        self.alpha = float(model.get("smoothing_alpha", 1.0))
        self.threshold = float(model.get("suggestion_threshold", 0.5))

    @classmethod
    def from_path(cls, path: str | Path = MODEL_PATH) -> "PrivacyClauseClassifier":
        with Path(path).open(encoding="utf-8") as source:
            return cls(json.load(source))

    def predict(self, text: str, *, top_k: int = 3) -> list[dict[str, Any]]:
        features = text_features(text) & self.vocabulary
        vocabulary_size = max(1, len(self.vocabulary))
        ranked: list[tuple[float, str, Mapping[str, Any]]] = []

        for label, statistics in self.classes.items():
            positives = int(statistics["positive_documents"])
            negatives = int(statistics["negative_documents"])
            prior_log_odds = math.log((positives + self.alpha) / (negatives + self.alpha))
            positive_denominator = int(statistics["positive_token_total"]) + self.alpha * vocabulary_size
            negative_denominator = int(statistics["negative_token_total"]) + self.alpha * vocabulary_size
            log_odds = prior_log_odds
            for feature in features:
                positive_count = int(statistics["positive_token_counts"].get(feature, 0))
                negative_count = int(statistics["negative_token_counts"].get(feature, 0))
                log_odds += math.log((positive_count + self.alpha) / positive_denominator)
                log_odds -= math.log((negative_count + self.alpha) / negative_denominator)
            if log_odds >= 0:
                score = 1.0 / (1.0 + math.exp(-min(log_odds, 700)))
            else:
                exponential = math.exp(max(log_odds, -700))
                score = exponential / (1.0 + exponential)
            ranked.append((score, label, statistics))

        ranked.sort(key=lambda item: (-item[0], item[1]))
        suggestions = []
        for score, label, statistics in ranked[: max(0, top_k)]:
            suggestions.append(
                {
                    "label": label,
                    "dashboard_category": statistics["dashboard_category"],
                    "score": round(score, 4),
                }
            )
        return suggestions

    def classify_clauses(self, clauses: Iterable[Mapping[str, Any]], *, top_k: int = 3) -> list[dict[str, Any]]:
        results = []
        for clause in clauses:
            text = str(clause.get("text", ""))
            predictions = self.predict(text, top_k=top_k)
            results.append(
                {
                    "clause_id": str(clause.get("clause_id", "")),
                    "excerpt": re.sub(r"\s+", " ", text).strip()[:240],
                    "predictions": [item for item in predictions if item["score"] >= self.threshold],
                }
            )
        return results
