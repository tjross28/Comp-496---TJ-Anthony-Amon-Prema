# Compliance engine backend

The backend package contains the policy-rule and scoring implementation. It deliberately has no persistence layer: submitted policy text is evaluated in memory and is not logged by the engine.

Run unit tests with:

```powershell
& 'C:\Users\antho\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s backend/tests -v
```

Run the API locally with:

```powershell
& 'C:\Users\antho\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' backend/app.py
```

`POST /api/v1/analyses` accepts the request contract in `../contracts/analysis-request.schema.json` and returns the matching response contract. The service evaluates requests in memory; it does not persist policy text or log it.
