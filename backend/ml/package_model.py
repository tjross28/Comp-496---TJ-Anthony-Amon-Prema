"""Bundle the model weights and lightweight runtime without the source corpus."""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "privacy_policy_clause_model_v1.zip"
PACKAGE_FILES = (
    "privacy_clause_model_v1.json",
    "privacy_classifier.py",
    "predict.py",
    "train_privacy_classifier.py",
    "README.md",
    "MODEL_CARD.md",
    "training_report_v1.json",
)


def main() -> None:
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for filename in PACKAGE_FILES:
            path = ROOT / filename
            if not path.is_file():
                raise FileNotFoundError(path)
            package.write(path, arcname=f"privacy_policy_clause_model_v1/{filename}")
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
