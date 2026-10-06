"""Train/evaluate a portable OPP-115 clause tagger using only Python stdlib."""

from __future__ import annotations

import argparse
import csv
import html
import json
import random
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from privacy_classifier import text_features

ROOT = Path(__file__).resolve().parent
DEFAULT_ARCHIVE = ROOT / ".training_work" / "OPP-115_v1_0.zip"
DEFAULT_OUTPUT = ROOT / "privacy_clause_model_v1.json"
DEFAULT_REPORT = ROOT / "training_report_v1.json"
MODEL_VERSION = "1.0.0"
CORPUS_PREFIX = "OPP-115/"
CONSOLIDATION_DIR = "consolidation/threshold-0.5-overlap-similarity/"
POLICY_DIR = "sanitized_policies/"
CATEGORY_TO_DASHBOARD = {
    "First Party Collection/Use": "data_collection",
    "Third Party Sharing/Collection": "data_sharing",
    "User Choice/Control": "user_agency",
    "User Access, Edit and Deletion": "user_agency",
    "Data Retention": "legal_language",
    "Data Security": "legal_language",
    "Policy Change": "legal_language",
    "Do Not Track": "user_agency",
    "International and Specific Audiences": "legal_language",
    "Other": None,
}
TAG_PATTERN = re.compile(r"<[^>]*>")
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


def policy_segments(raw_html: str) -> list[str]:
    segments = []
    for part in raw_html.split("|||"):
        text = html.unescape(TAG_PATTERN.sub(" ", part))
        text = re.sub(r"\s+", " ", text).strip()
        segments.append(text)
    return segments


def read_corpus(archive_path: Path) -> tuple[list[dict[str, Any]], dict[str, int]]:
    examples: dict[tuple[str, int], dict[str, Any]] = {}
    category_counts: Counter[str] = Counter()
    with zipfile.ZipFile(archive_path) as archive:
        policy_files = [
            name
            for name in archive.namelist()
            if name.startswith(CORPUS_PREFIX + CONSOLIDATION_DIR) and name.endswith(".csv")
        ]
        for consolidation_path in policy_files:
            filename = Path(consolidation_path).name
            policy_key = filename.removesuffix(".csv")
            sanitized_path = CORPUS_PREFIX + POLICY_DIR + policy_key + ".html"
            try:
                segments = policy_segments(archive.read(sanitized_path).decode("utf-8", "replace"))
            except KeyError:
                continue

            with archive.open(consolidation_path) as stream:
                reader = csv.reader((line.decode("utf-8-sig", "replace") for line in stream))
                for row in reader:
                    if len(row) < 6:
                        continue
                    try:
                        segment_id = int(row[4])
                    except ValueError:
                        continue
                    label = row[5].strip()
                    if label not in CATEGORY_TO_DASHBOARD or not (0 <= segment_id < len(segments)):
                        continue
                    text = segments[segment_id]
                    if len(text) < 8:
                        continue
                    key = (policy_key, segment_id)
                    example = examples.setdefault(key, {"policy": policy_key, "text": text, "labels": set()})
                    example["labels"].add(label)
                    category_counts[label] += 1

    cleaned = []
    for item in examples.values():
        if item["labels"]:
            cleaned.append({"policy": item["policy"], "text": item["text"], "labels": item["labels"]})
    return cleaned, dict(category_counts)


def split_by_policy(examples: list[dict[str, Any]], seed: int = 496) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    policies = sorted({example["policy"] for example in examples})
    random.Random(seed).shuffle(policies)
    holdout_count = max(1, round(len(policies) * 0.2))
    holdout = set(policies[:holdout_count])
    train = [example for example in examples if example["policy"] not in holdout]
    validation = [example for example in examples if example["policy"] in holdout]
    return train, validation


def train_counts(examples: list[dict[str, Any]]) -> tuple[dict[str, Any], set[str]]:
    labels = sorted(CATEGORY_TO_DASHBOARD)
    document_frequency: Counter[str] = Counter()
    example_features: list[tuple[dict[str, Any], set[str]]] = []
    for example in examples:
        features = {feature for feature in text_features(example["text"]) if len(feature) >= 2}
        example_features.append((example, features))
        document_frequency.update(features)

    vocabulary = {feature for feature, frequency in document_frequency.items() if frequency >= 2}
    classes: dict[str, Any] = {}
    for label in labels:
        positive_tokens: Counter[str] = Counter()
        negative_tokens: Counter[str] = Counter()
        positive_documents = 0
        negative_documents = 0
        for example, features in example_features:
            selected = features & vocabulary
            if label in example["labels"]:
                positive_documents += 1
                positive_tokens.update(selected)
            else:
                negative_documents += 1
                negative_tokens.update(selected)
        classes[label] = {
            "dashboard_category": CATEGORY_TO_DASHBOARD[label],
            "positive_documents": positive_documents,
            "negative_documents": negative_documents,
            "positive_token_total": sum(positive_tokens.values()),
            "negative_token_total": sum(negative_tokens.values()),
            "positive_token_counts": dict(positive_tokens),
            "negative_token_counts": dict(negative_tokens),
        }
    return classes, vocabulary


def make_runtime_model(classes: dict[str, Any], vocabulary: set[str], train_policy_count: int, train_segment_count: int) -> dict[str, Any]:
    return {
        "artifact_type": "privacy_policy_clause_classifier",
        "version": MODEL_VERSION,
        "algorithm": "multi-label multinomial Naive Bayes with binary unigram and adjacent-bigram features",
        "tokenizer": "lowercase alphanumeric words; unigrams and adjacent bigrams; binary feature presence",
        "smoothing_alpha": 1.0,
        "suggestion_threshold": 0.5,
        "training_corpus": "OPP-115 v1.0 (2016), consolidated at 0.5 overlap-similarity threshold",
        "training_policy_count": train_policy_count,
        "training_segment_count": train_segment_count,
        "vocabulary_size": len(vocabulary),
        "classes": classes,
        "vocabulary": sorted(vocabulary),
    }


def evaluate(model: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    from privacy_classifier import PrivacyClauseClassifier

    classifier = PrivacyClauseClassifier(model)
    labels = sorted(CATEGORY_TO_DASHBOARD)
    counts = {label: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for label in labels}
    exact_match = 0
    for example in examples:
        scores = {row["label"]: row["score"] for row in classifier.predict(example["text"], top_k=len(labels))}
        predicted = {label for label, score in scores.items() if score >= 0.5}
        actual = example["labels"]
        exact_match += predicted == actual
        for label in labels:
            positive = label in actual
            guess = label in predicted
            counts[label]["support"] += positive
            counts[label]["tp"] += positive and guess
            counts[label]["fp"] += (not positive) and guess
            counts[label]["fn"] += positive and (not guess)

    per_class = {}
    f1_values = []
    macro_f1 = 0.0
    micro_tp = micro_fp = micro_fn = 0
    for label, values in counts.items():
        tp, fp, fn = values["tp"], values["fp"], values["fn"]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"support": values["support"], "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
        if values["support"]:
            f1_values.append(f1)
        micro_tp += tp
        micro_fp += fp
        micro_fn += fn
    micro_precision = micro_tp / (micro_tp + micro_fp) if micro_tp + micro_fp else 0.0
    micro_recall = micro_tp / (micro_tp + micro_fn) if micro_tp + micro_fn else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if micro_precision + micro_recall else 0.0
    macro_f1 = sum(f1_values) / len(f1_values) if f1_values else 0.0
    return {
        "policy_level_split_seed": 496,
        "validation_segment_count": len(examples),
        "micro_precision_at_0_5": round(micro_precision, 4),
        "micro_recall_at_0_5": round(micro_recall, 4),
        "micro_f1_at_0_5": round(micro_f1, 4),
        "macro_f1_at_0_5": round(macro_f1, 4),
        "exact_match_at_0_5": round(exact_match / max(1, len(examples)), 4),
        "per_class": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-zip", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    if not args.dataset_zip.is_file():
        raise SystemExit(f"Dataset archive not found: {args.dataset_zip}")

    examples, annotation_counts = read_corpus(args.dataset_zip)
    if not examples:
        raise SystemExit("No annotated policy segments were loaded.")
    train, validation = split_by_policy(examples)
    classes, vocabulary = train_counts(train)
    validation_model = make_runtime_model(classes, vocabulary, len({item["policy"] for item in train}), len(train))
    report = evaluate(validation_model, validation)
    final_classes, final_vocabulary = train_counts(examples)
    model = make_runtime_model(final_classes, final_vocabulary, len({item["policy"] for item in examples}), len(examples))
    model["evaluation"] = {
        "split": "deterministic 80/20 policy-level holdout; metrics are on unseen policies",
        "validation_policy_count": len({item["policy"] for item in validation}),
        "validation_segment_count": len(validation),
        "micro_f1_at_0_5": report["micro_f1_at_0_5"],
        "macro_f1_at_0_5": report["macro_f1_at_0_5"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    report.update(
        {
            "training_policy_count": len({item["policy"] for item in train}),
            "training_segment_count": len(train),
            "validation_policy_count": len({item["policy"] for item in validation}),
            "validation_segment_count": len(validation),
            "full_corpus_policy_count": len({item["policy"] for item in examples}),
            "full_corpus_segment_count": len(examples),
            "full_corpus_category_counts": annotation_counts,
            "full_model_vocabulary_size": len(final_vocabulary),
            "model_artifact": str(args.output.name),
        }
    )
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "per_class"}, indent=2))
    print("per_class", json.dumps(report["per_class"], ensure_ascii=False))
    print("model_bytes", args.output.stat().st_size)


if __name__ == "__main__":
    main()
