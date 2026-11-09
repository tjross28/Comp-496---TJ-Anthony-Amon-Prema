# ClearPolicy implementation workflow

## Project goal

ClearPolicy helps readers understand privacy-policy language by sending the
submitted text to GPT through the OpenAI Responses API and presenting a
plain-language summary. The generated explanation is the app's analysis
output; it does not make legal determinations or train a custom model.

## Request and response

The browser sends the full policy text to the Flask endpoint. The response
contains:

- a short, reader-focused overview;
- important details, each tied to a quotation from the source;
- specific wording a reader may want to review; and
- practical questions the reader may want to ask.

The backend checks that returned quotations occur in the submitted text. This
supports traceability, but does not validate the meaning or completeness of the
model's explanations.

## Local setup

Run Flask and the Vite interface in separate terminals from the project root.
Set `OPENAI_API_KEY` in the backend terminal before starting Flask. The
configured model defaults to `gpt-6-luna` and can be changed with
`OPENAI_MODEL`. Keep the API key on the server.

## Data handling

The backend sends policy text to OpenAI with response storage disabled using
`store=false`. The project does not save the submitted text in a database or
application logs. Deployments must protect the API, set an API access token,
limit request size, and review their applicable data controls.

## Review before presenting

Use the fictional sample policy for demos. Read the full generated summary,
check the quoted text against the sample, and explain that model-generated
content may miss context or make mistakes. Describe ClearPolicy as an
educational reading aid, not legal advice or a compliance tool.

## Future quality work

Before relying on the summary beyond a classroom prototype, create a diverse
set of policies with expert-reviewed reference summaries. Evaluate quote
accuracy, factual support, important omissions, readability, and unsupported
claims on policies not used to refine the prompt. Do not describe the model as
trained or fine-tuned by this project.
