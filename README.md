# ClearPolicy

ClearPolicy turns privacy-policy text into a plain-language summary for readers.
It uses GPT through the OpenAI Responses API to describe the policy, highlight
useful passages, point out wording a reader may want to review, and suggest
questions to ask. ClearPolicy is an educational reading aid and does not make
legal compliance decisions.

## Run locally

Start the backend and interface in two PowerShell terminals from the project
root.

**Terminal 1 — backend and OpenAI API**

Create the environment and install dependencies once:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Set the API key in this terminal before starting Flask:

```powershell
$env:OPENAI_API_KEY = "your-api-key"
.\.venv\Scripts\python.exe backend\app.py
```

The backend uses model ID `gpt-6-luna` by default. Set `OPENAI_MODEL` to choose
another compatible model. Keep the API key in the backend environment; never
put it in frontend code. If you set the key after Flask is running, restart the
backend.

**Terminal 2 — React interface**

```powershell
pnpm install
pnpm dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`. Keep both
terminals running. Select **Try sample policy** to load the fictional example.
The backend health endpoint is `http://127.0.0.1:5000/healthz`.

## API

`POST /api/v1/analyses` accepts a JSON body with one `text` field. The response
contains the plain-language summary, important details with exact source
passages, wording to review, and questions for the reader. The request and
response shapes are documented in `contracts/`.

The API sends the full policy text to OpenAI with response storage disabled
(`store=false`). The project backend does not save policy text to a database or
write it to application logs. Use the prototype with text approved for this
purpose. Generated explanations can miss context or make mistakes; compare
important details with the complete policy. This is an educational reading aid,
not legal advice.
