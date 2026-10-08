# Privacy Policy Analyzer

A React interface and Flask analysis API for the COMP 496 Privacy Policy Analyzer.

## Run locally

```powershell
pnpm install
pnpm dev
```

The app supports pasting policy text or uploading `.txt` files. The Flask API returns evidence-backed rule findings, a weighted Trust Score, and experimental clause topic suggestions from a compact trained classifier. The classifier is distinct from the rule engine and does not determine the Trust Score. Text is processed in memory and is not persisted by the API. This is an academic prototype, not legal advice.

## Run the analyzer on Windows

Start the backend and UI in two separate PowerShell terminals. Run these commands from the project root.

**Terminal 1 - backend and model** (create the environment and install Flask once):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe backend\app.py
```

The API loads `backend/ml/privacy_clause_model_v1.json` automatically. Check `http://127.0.0.1:5000/healthz`; the response should include `"classifier_version":"1.0.0"`.

**Terminal 2 - React UI** (`pnpm install` is needed once per checkout):

```powershell
pnpm install
pnpm dev
```

Open the Vite URL printed by `pnpm dev` (usually `http://localhost:5173`). Keep both terminals running while you present. The demo policy can be loaded with **Try sample policy** or downloaded from `public/sample_privacy_policy.txt`.

## Model artifacts

- Downloadable package: [`backend/ml/privacy_policy_clause_model_v1.zip`](backend/ml/privacy_policy_clause_model_v1.zip)
- Plain model JSON: [`backend/ml/privacy_clause_model_v1.json`](backend/ml/privacy_clause_model_v1.json)
- Model card and training guide: [`backend/ml/MODEL_CARD.md`](backend/ml/MODEL_CARD.md) and [`backend/ml/README.md`](backend/ml/README.md)
- Demo script: [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md)

The model was trained from the consolidated OPP-115 annotations for academic demonstration. The research corpus terms restrict use to research, teaching, and scholarship and are non-commercial; do not use this artifact for commercial deployment without the required license. The source policies are not bundled.
