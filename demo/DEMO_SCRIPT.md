# Privacy Policy Analyzer Demo Script

**Run time:** about 4 minutes  
**Demo input:** [`public/sample_privacy_policy.txt`](../public/sample_privacy_policy.txt)  
**Setup:** start the Flask API and the Vite UI in two terminals; open the local app.

## 1. Introduce the problem (30 seconds)

**Presenter:** “Privacy policies disclose important practices, but the details are spread across long documents. Our prototype helps a reader locate those details and see a plain-language set of review signals.”

## 2. Load the example (30 seconds)

**Action:** Choose **Try sample policy** or download and upload `sample_privacy_policy.txt`.

**Presenter:** “This is a fictional policy made for this demo. It mentions information collection, advertising and analytics sharing, retention, user requests, and security. No real company's policy is being represented.”

## 3. Analyze it (30 seconds)

**Action:** Select **Analyze policy** and wait for the results panel.

**Presenter:** “The browser sends the text to our local analysis API. The API processes it in memory, returns the result, and does not save the submitted policy.”

## 4. Explain the model and score (90 seconds)

**Action:** Point to the Trust Score and five category rows, then the rule findings and AI clause tags.

**Presenter:** “The Trust Score is calculated by the documented, weighted rules engine. Its categories are data sharing at 25 percent, readability at 20 percent, data collection at 20 percent, legal language at 20 percent, and user agency at 15 percent. The score describes signals in the supplied text; it is not a legal compliance rating.”

“The AI clause tagger is a separate model. It was trained on consolidated expert annotations from the OPP-115 research corpus and suggests topics such as collection, sharing, user choice, and retention for each clause. The tagger's score is a model estimate, not a calibrated probability. These tags do not change the Trust Score.”

## 5. Review examples and limitations (60 seconds)

**Action:** Point out the advertising-sharing statement, open-ended retention sentence, access/deletion language, and opt-out control in the sample. Match them to the rule findings and nearby clause tags.

**Presenter:** “The findings include a short explanation and the policy text that triggered a rule. A model tag or rule match can be wrong or incomplete, so users should check the original wording. The training corpus is small, from 2016, and limited to English website policies. We use this build for an academic demo, not commercial deployment.”

## 6. Close (20 seconds)

**Presenter:** “The prototype combines learned topic suggestions with transparent, versioned rules. It is an educational aid for finding relevant policy language, not legal advice and not proof of compliance.”

## Optional handoff

- **Model/data presenter:** describe OPP-115, the policy-level holdout, model artifact, and non-commercial restriction.
- **Backend presenter:** describe `/api/v1/analyses`, in-memory processing, and the versioned JSON response.
- **UI presenter:** show policy entry, score categories, rule findings, and clause tags.
