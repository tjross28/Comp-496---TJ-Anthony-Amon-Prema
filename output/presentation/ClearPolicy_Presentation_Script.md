# ClearPolicy presentation script

**Estimated run time:** about 5 minutes, including a 2-minute live demo.

## Before presenting

1. Start Flask in one terminal with `OPENAI_API_KEY` set in that terminal.
2. Start the interface in a second terminal with `pnpm dev`.
3. Open the local Vite URL and choose the fictional sample policy.

## Slide 1: The problem — Anthony

**Cue:** Introduce the project and its purpose.

**Anthony:** “Hi, we’re TJ, Anthony, and Amon. We built ClearPolicy to help people understand privacy policies without having to work through every sentence of dense legal language. The app turns the policy text into a readable overview and points readers back to passages they may want to inspect.”

## Slide 2: How the app works — Amon

**Cue:** Show the text field, backend, and results screen.

**Amon:** “A reader pastes policy text or loads our fictional sample. The React interface sends the text to our Flask API. The backend sends the complete policy to GPT-6 Luna through the OpenAI Responses API, then returns a plain-language summary, useful details, passages to review, and questions for the reader.”

## Slide 3: Reading the summary — Anthony

**Cue:** Show the overview and one quoted detail.

**Anthony:** “The overview is meant to make the main points easier to follow. Each highlighted detail includes a short quotation, and the backend checks that the quotation is present in the policy text. That makes it easier to trace the explanation to its source, though the explanation can still miss context or get something wrong.”

## Slide 4: Natural-language model — TJ

**Cue:** Explain the model’s role and the API call.

**TJ:** “The app uses GPT-6 Luna through the OpenAI Responses API to read the submitted policy and explain it in everyday language. Structured Outputs keeps the response organized into sections; it doesn’t limit the model to fixed labels. The project does not fine-tune the hosted model or learn from individual submissions. We have not yet measured summary quality against a held-out set of policies reviewed by people.”

## Slide 5: Live demo — TJ

**Cue:** Load the fictional sample, create the summary, and compare a quote with its original sentence.

**TJ:** “This sample was written for the classroom demonstration, not taken from a real company. I’ll show how the overview and quoted details make a long policy quicker to scan. We should still check important statements against the full text.”

## Slide 6: Close — Anthony

**Cue:** Summarize the project and its limits.

**Anthony:** “ClearPolicy helps a reader get oriented and decide what to look at more closely. It describes the submitted text; it does not establish what an organization does in practice or decide whether a policy complies with a law. It is an educational reading aid, not legal advice. Thank you.”
