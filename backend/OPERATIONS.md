# ClearPolicy operations

The service processes policy text in memory and sends it to OpenAI for a
plain-language summary. The Responses API request uses `store=false`. The
backend does not log or persist raw policy text. Completion logs contain an
analysis ID, model name, and duration only.

## Runtime configuration

- Set `OPENAI_API_KEY` in the backend environment before starting Flask.
- `OPENAI_MODEL` defaults to `gpt-6-luna`.
- Set `ANALYSIS_API_TOKEN` outside local development; callers provide it in
  the `X-Analysis-Token` header.
- Set `MAX_ANALYSIS_REQUEST_BYTES` to change the request-size limit (default:
  1,000,000 bytes).
- Set `ANALYSIS_RATE_LIMIT` and `ANALYSIS_RATE_WINDOW_SECONDS` to adjust the
  in-memory per-client rate limit (default: 60 requests per 60 seconds).
- Keep Flask debug mode disabled in deployed environments.

## API behavior

- `GET /healthz` reports service status and the configured model ID.
- `POST /api/v1/analyses` accepts a JSON object with a non-empty `text`
  string.
- Missing API configuration returns `503`; provider failures return `502`.
- The backend checks generated evidence quotations against the submitted text
  before returning them.

Review privacy and data controls before using this prototype with policy text
that should not be sent to an external API.
