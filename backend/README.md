# Compliance engine backend

The backend package contains the policy-rule and scoring implementation. It deliberately has no persistence layer: submitted policy text is evaluated in memory and is not logged by the engine.

Run unit tests with:

```powershell
python -m unittest discover -s backend/tests -v
```

Run the API locally with:

```powershell
python backend/app.py
```

`POST /api/v1/analyses` accepts the request contract in `../contracts/analysis-request.schema.json` and returns the matching response contract. Responses include topic tags for each clause from the trained model in `ml/privacy_clause_model_v1.json`, alongside the separate rule-based findings and weighted Trust Score. The service evaluates requests in memory; it does not persist policy text or log it.

The model can be replaced with another compatible JSON artifact using `ANALYSIS_CLASSIFIER_PATH`. See `ml/README.md` and `ml/MODEL_CARD.md` for training, licensing, validation, and model limitations.
