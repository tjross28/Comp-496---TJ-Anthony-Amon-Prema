# ClearPolicy language model card

## Model and task

The app calls GPT-6 Luna (`gpt-6-luna`) through the OpenAI Responses API. The
model reads the supplied policy text and generates a plain-language summary,
important details with source quotations, wording to review, and questions a
reader may want to ask.

## Intended use

This prototype is an educational reading aid for English-language privacy
policies. It helps readers navigate long, technical text. It is not intended to
provide legal advice, determine regulatory compliance, decide whether a policy
is fair, or assess whether an organization is trustworthy.

## How the app uses the model

The backend sends the full submitted text with instructions to explain it
carefully in everyday language. Structured Outputs keeps the response fields
consistent. The backend also checks each quotation against the submitted text
and drops evidence items whose quote is not present. The model's explanations
remain generated text and are not independently validated for completeness or
meaning.

The request sets `store=false`. The backend does not save raw policy text in a
database or write it to application logs. The API key is read from the backend
environment and must not be exposed in the browser.

## Training and evaluation

The project does not fine-tune the hosted model and does not train on user
submissions. Results are generated at request time. The project has not yet
measured summary quality on a held-out set of policies reviewed by people.

Before relying on the summary beyond a classroom prototype, create a
representative evaluation set and have reviewers check factual support,
important omissions, quote accuracy, readability, and unsupported statements.

## Limitations

- The model may omit a material detail, misunderstand context, or phrase a
  statement too strongly.
- A quote can be copied exactly while the explanation of that quote is still
  mistaken.
- The model describes what the supplied text says; it cannot establish what an
  organization actually does.
- The model may perform differently on incomplete text, OCR errors, unusual
  policy formats, or languages other than English.
- Readers should compare important explanations with the complete policy and
  seek qualified help for legal questions.
