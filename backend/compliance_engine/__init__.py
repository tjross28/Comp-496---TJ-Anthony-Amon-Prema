"""Explainable, rule-based privacy-policy assessment components."""

from .scoring import CATEGORY_ORDER, calculate_score

__all__ = ["CATEGORY_ORDER", "calculate_score"]
