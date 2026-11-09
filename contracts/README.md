# Analysis contracts

The request contract contains the policy text to summarize. The response
contract describes the GPT-generated plain-language overview, details with
source quotations, wording to review, and reader questions.

The backend checks each returned quotation against the submitted text. This
helps keep the highlighted details tied to the source, but it does not verify
that every explanation is complete or correct. Readers should check important
claims against the full policy. The output is not legal advice or a legal
compliance determination.

Example request and response bodies are in `../fixtures/`. Update the schemas
and fixtures together when changing the API shape.
