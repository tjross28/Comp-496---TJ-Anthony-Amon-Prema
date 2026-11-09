# Natural-language summary

The app uses GPT-6 Luna (`gpt-6-luna`) through the OpenAI Responses API to
summarize the full supplied privacy-policy text in plain language. The backend
requests structured output for the overview, useful policy details, wording to
review, and questions for the reader.

Set `OPENAI_API_KEY` before starting the Flask backend. `OPENAI_MODEL` can
override the default model ID. The key stays in the backend environment and
must not be put in React code. The API request sets `store=false`.

The model is not fine-tuned by this project and does not learn from individual
analysis requests. The backend checks generated quotations against the source
text, but the explanations may still omit or misinterpret details. Compare
important statements with the complete policy.

See `MODEL_CARD.md` for the intended use and limitations.
