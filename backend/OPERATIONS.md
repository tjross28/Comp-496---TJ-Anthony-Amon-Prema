# Compliance engine operations

The service processes policy text in memory and should not log raw text, clause text, uploads, or user identifiers. Its completion log contains only a one-way document-ID fingerprint, analysis ID, rule-set version, finding count, and duration.

## Runtime safeguards

- Set `ANALYSIS_API_TOKEN` in non-local environments; callers send it in `X-Analysis-Token`.
- Set `ANALYSIS_CLASSIFIER_PATH` to load a compatible classifier JSON artifact; the default is `backend/ml/privacy_clause_model_v1.json`.
- Set `MAX_ANALYSIS_REQUEST_BYTES` to bound request size (default: 1,000,000 bytes).
- Set `ANALYSIS_RATE_LIMIT` and `ANALYSIS_RATE_WINDOW_SECONDS` to control the in-memory per-client rate limit (default: 60 requests per 60 seconds).
- Keep Flask debug mode disabled in deployed environments.

## Rule-set rollback

The default catalog is `backend/rules/rules-v0.1.json`. To roll back a faulty catalog, set `ANALYSIS_RULESET_PATH` to a previously approved, versioned catalog and restart the service. Every response identifies the rule-set version used.

## Release checks

1. Run the full backend test suite and frontend build.
2. Review catalog source URLs and `reviewed_on` dates.
3. Verify the deployed API requires a token, request limits, and safe logging.
4. Verify the dashboard shows the disclaimer, category coverage, evidence, and limitations.

The AI clause topic suggestions are returned separately from the score and must remain labeled as experimental. Do not use the academic OPP-115-derived artifact for commercial deployment without obtaining the needed rights.
