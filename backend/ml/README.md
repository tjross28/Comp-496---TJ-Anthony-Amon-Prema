# Model package and integration

The OPP-115-trained model is a small JSON artifact that the Flask API loads at startup. It adds experimental clause-topic suggestions to the existing analysis response without changing the weighted Trust Score or rule findings.

## Use it in this project

Start the backend from the project root:

```powershell
python backend/app.py
```

Start the UI in another terminal:

```powershell
pnpm dev
```

`POST /api/v1/analyses` now includes `classifier_version` and `clause_classifications`. Each clause entry has its ID, text excerpt, and up to three OPP-115 topic predictions above the 0.5 model-score threshold. `dashboard_category` maps the topic to the existing dashboard when possible; `Other` has a null mapping.

To load another compatible model JSON, set `ANALYSIS_CLASSIFIER_PATH` before starting Flask. The current default is `backend/ml/privacy_clause_model_v1.json`.

## Downloadable files

- `privacy_policy_clause_model_v1.zip` includes the model, inference code, CLI, training code, model card, and validation report. It does not contain the OPP-115 policies or annotations.
- `privacy_clause_model_v1.json` is the model weights/statistics file loaded by the backend.
- `privacy_classifier.py` is the dependency-free predictor.
- `train_privacy_classifier.py` rebuilds the model from the official research archive.
- `training_report_v1.json` records held-out metrics and data counts.

## Run the standalone predictor

From the extracted model-package directory, pipe a JSON object with `clauses` into `predict.py`:

```powershell
'{"clauses":[{"clause_id":"c1","text":"We may share personal information with advertising partners."}]}' | python predict.py
```

The output is JSON with the model version and clause classifications.

## Rebuild from OPP-115

1. Download `OPP-115_v1_0.zip` from the [official dataset page](https://www.usableprivacy.org/data/).
2. Place it at `backend/ml/.training_work/OPP-115_v1_0.zip`.
3. Run `python backend/ml/train_privacy_classifier.py` from the repository root.

The script uses standard-library modules only. It makes a reproducible 80/20 split by policy using seed 496, reports per-label and aggregate scores at a 0.5 threshold, then trains the distributable weights on all 115 policies. It does not copy policy text into the output artifact.

## License and attribution

OPP-115 is offered for research, teaching, and scholarship purposes, with terms in the spirit of CC BY-NC. This model is for the team's non-commercial academic demo. Do not use it commercially or redistribute it more broadly without permission from the dataset rights holders. See `MODEL_CARD.md` for attribution and performance details.
