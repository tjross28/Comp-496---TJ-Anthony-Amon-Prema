# ClearPolicy presentation script

**Estimated run time:** about 5 minutes 30 seconds, including a 2 minute 30 second live demo.

## Before presenting

1. Start the backend in one terminal: `.\.venv\Scripts\python.exe backend\app.py`. If dependencies are not installed, follow the one-time Windows setup in the project README.
2. Start the interface in a second terminal: `pnpm dev`.
3. Open the local URL printed by Vite and leave the policy field blank. Keep the browser with TJ for the demo.
4. Use the fictional sample policy included in the project.

## Slide-by-slide script

### Slide 1: Opening — Anthony (0:20)

**Cue:** Introduce the three presenters and the purpose of the project.

**Anthony:** “Hi, we’re TJ, Anthony, and Amon. We built ClearPolicy, a class prototype that helps readers find privacy policy language worth reviewing. Amon will show how the app handles a policy, I’ll explain the rule engine, and TJ will cover the clause tagger and run the live demo.”

### Slide 2: Analysis flow — Amon (0:40)

**Cue:** Point to the interface, API, and the two analysis paths.

**Amon:** “A reader can paste policy text or load the sample. The React interface splits the text into clauses and sends them to our Flask API. The API runs two separate analyses: the versioned rules engine returns findings and the weighted Trust Score, while the learned classifier suggests topics for clauses. The interface brings those results together so a reader can compare them with the policy wording. Submitted text is processed in memory and is not saved by the service.”

### Slide 3: Rules and Trust Score — Anthony (0:45)

**Cue:** Walk through the category weights and explain what one rule finding contains.

**Anthony:** “Our rule engine uses versioned phrase rules and returns evidence with each finding: the matched wording, a plain-language explanation, and a suggested next step. The Trust Score weights data sharing at 25 percent, readability at 20, data collection at 20, legal language at 20, and user agency at 15. If the policy text does not provide enough evidence for a category, the app marks it as needing evidence and excludes it from the normalized score rather than treating it as favorable. The score summarizes transparency signals in the supplied text; it is not a legal compliance result.”

### Slide 4: OPP-115 clause tagger — TJ (0:45)

**Cue:** Explain the training set, policy-level holdout, and baseline results.

**TJ:** “The clause tagger is a multi-label Naive Bayes model trained on consolidated OPP-115 annotations: 3,790 segments from 115 policies. We held out whole policies, using 92 for training and 23 for evaluation, which gave us 862 held-out segments. On that baseline, micro F1 was 0.7119, macro F1 was 0.6150, and exact label-set match was 0.3805. The final model artifact was then fit on all 115 policies. These topic tags are experimental, their scores are not calibrated probabilities, and they do not affect the Trust Score. The corpus is historical and limited to English website policies; this artifact is for non-commercial academic use under the OPP-115 terms.”

### Slide 5: Live demo — TJ (2:30)

**Cue:** Take browser control. Load the fictional sample, analyze it, then trace rule findings and any displayed clause tag back to the source text.

**TJ:** “I’ll run the sample policy through the app. It is fictional and was written for this classroom demonstration, not taken from a real company.”

**Browser actions:**

- **Load:** Select Try sample policy. Briefly show the input text.
- **Analyze:** Select Analyze policy and wait for the results.
- **Trace:** Show the score and category coverage. Point to the advertising-sharing and open-ended-retention findings, then compare each with its source sentence. Note the access and deletion language. If a clause tag appears, read its topic and check the original clause.

**TJ:** “The rules help me find language to review. A topic tag is only a model suggestion, and a missing tag does not mean a clause is unimportant. I’ll use the original policy text to interpret every signal. The app does not tell us whether the policy complies with a law.”

### Slide 6: Project workstreams and close — Anthony (0:20)

**Cue:** Recap the three project workstreams and thank the audience.

**Anthony:** “Today, we’ve shown three connected areas: TJ’s clause model and demo, Amon’s API and interface integration, and my rule engine and scoring. Together, they make policy language easier to inspect while keeping evidence visible. This is an educational aid, not legal advice or proof of compliance. Thank you.”

## Timing

Opening and project explanation: about 2 minutes 50 seconds. Live demo: about 2 minutes 30 seconds. Closing and transitions bring the total to roughly 5 minutes 30 seconds.
