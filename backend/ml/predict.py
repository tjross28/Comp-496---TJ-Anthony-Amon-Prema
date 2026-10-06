"""Read a clauses JSON object on stdin and print model suggestions as JSON."""

from __future__ import annotations

import argparse
import json
import sys

from privacy_classifier import MODEL_PATH, PrivacyClauseClassifier


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=str(MODEL_PATH), help="Path to a compatible model JSON artifact")
    args = parser.parse_args()
    payload = json.load(sys.stdin)
    clauses = payload.get("clauses") if isinstance(payload, dict) else None
    if not isinstance(clauses, list):
        raise SystemExit('Input must be an object with a "clauses" array.')
    classifier = PrivacyClauseClassifier.from_path(args.model)
    result = {
        "classifier_version": classifier.version,
        "clause_classifications": classifier.classify_clauses(clauses),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
