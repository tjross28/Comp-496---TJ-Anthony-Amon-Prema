# ClearPolicy demo script

**Run time:** about 4 minutes  
**Demo input:** [Fictional sample policy](../public/sample_privacy_policy.txt)  
**Setup:** start the Flask API and Vite interface in two terminals; open the local app.

## 1. Introduce the project

**Presenter:** “ClearPolicy helps people read privacy policies by turning long, technical text into a plain-language overview. It highlights useful passages and suggests questions readers may want to ask.”

## 2. Load the example

**Action:** Choose **Try sample policy**.

**Presenter:** “This sample is fictional and written for the demo. It includes examples of information collection, sharing, retention, user requests, and security.”

## 3. Generate the summary

**Action:** Select **Create summary** and wait for the results panel.

**Presenter:** “The interface sends the policy text to our Flask API. The backend sends it to GPT-6 Luna through the OpenAI Responses API. The model returns a plain-language overview, important details with short quotes, wording a reader may want to review, and questions to consider.”

## 4. Read the result

**Action:** Read the summary, then compare a highlighted quote with its original sentence in the sample.

**Presenter:** “The overview explains the policy in everyday language. The highlighted details include quotes from the source text, and the backend checks that each quote appears in the submitted policy. That check helps keep the evidence traceable, but it does not guarantee the explanation is complete or correct.”

## 5. Explain the model and its limits

**Presenter:** “The hosted model reads the submitted text and generates an explanation each time. The project does not fine-tune GPT or learn from individual submissions. The model can miss context or misunderstand a sentence, so readers should check important details against the complete policy. The app is an educational reading aid, not legal advice or a compliance decision.”

## 6. Close

**Presenter:** “ClearPolicy gives readers a quicker way into a long policy and a starting point for further questions. It does not replace reading the complete document or getting qualified legal advice.”
