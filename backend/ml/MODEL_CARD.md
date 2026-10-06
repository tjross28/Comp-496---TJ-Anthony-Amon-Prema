# Privacy Policy Clause Classifier

## Summary

| Item | Value |
| --- | --- |
| Artifact | `privacy_clause_model_v1.json` |
| Model version | 1.0.0 |
| Task | Multi-label topic suggestions for policy clauses |
| Algorithm | Multinomial Naive Bayes with binary unigram and adjacent-bigram features |
| Runtime dependencies | Python standard library |
| Training data | OPP-115 Corpus v1.0, consolidated annotations at the 0.5 overlap-similarity threshold |
| Training examples | 3,790 policy segments from 115 policies |
| Held-out evaluation | 862 segments from 23 policies; split by policy, not by clause |
| Main metric | Micro F1 = 0.7119 at a 0.5 decision threshold |

## Intended use

This model suggests one to three OPP-115 topic labels for text clauses, such as first-party collection, third-party sharing, user choice, retention, and security. Each suggestion includes the source clause ID, a short excerpt, the mapped product category when available, and a model score.

Use it as an educational aid to find clauses that may deserve attention. Review the source text before drawing conclusions. The model does not determine whether a policy is fair, trustworthy, legally compliant, or subject to a law.

## How the app uses it

The Flask API runs the classifier alongside the existing deterministic rules engine. The classifier returns topic suggestions in `clause_classifications`; it does not modify rule findings, category scores, or the weighted Trust Score. The current readability score remains a separate heuristic because OPP-115 does not provide readability labels.

The logistic transform of Naive Bayes log odds is a ranking score, not a calibrated probability. The API returns only labels whose score reaches 0.5, up to three labels per clause. An empty prediction list means no label passed that display threshold; it does not mean the clause has no privacy significance.

## Data and preparation

OPP-115 contains 115 website privacy policies annotated by three graduate law students. This build uses its consolidated annotations and sanitized, paragraph-sized policy segments. Multiple labels may apply to the same segment. The train/validation split is deterministic (seed 496) and keeps complete policies in one split to reduce leakage between near-identical clauses.

The corpus is from 2016 and reflects the websites, terminology, and policy formats available at that time. It does not provide an up-to-date regulatory knowledge base. PrivaSeer is a larger, mostly unlabeled corpus discussed in the team's planning materials; it is not used for supervised labels in this model.

## Evaluation

The validation set contains policies the model did not see during training. At a fixed 0.5 threshold, micro precision is 0.7633, micro recall is 0.6669, micro F1 is 0.7119, macro F1 is 0.6150, and exact set match is 0.3805. These figures are a baseline on one small historical corpus, not a performance guarantee for current policies.

Label performance is uneven. For example, on the held-out data, First Party Collection/Use has F1 0.7671 (356 positive segments), Third Party Sharing/Collection has F1 0.7654 (255), Data Retention has F1 0.2439 (34), and User Access, Edit and Deletion has F1 0.5111 (63). Do Not Track had only 6 positive validation segments, so its apparent performance is especially uncertain. The detailed per-label figures are in `training_report_v1.json`.

## Limitations and risks

- The corpus is small and dated; language and disclosure practices have changed.
- Labels are imbalanced and some categories have few held-out examples.
- A policy segment can contain more than one topic; this baseline may miss secondary topics or over-tag ambiguous wording.
- The model was trained on website policies in English; do not assume it works on other languages, app-only notices, contracts, or law texts.
- The taxonomy is about what a segment discusses, not whether the practice is good or bad.
- A model score is not a calibrated confidence value and is not evidence of legal compliance.
- Training/evaluation quality depends on the corpus consolidation and preprocessing choices recorded by the training script.

## Fairness, privacy, and security

The API processes submitted policy text in memory and does not persist it. Completion logs exclude policy text and clause excerpts. Deployments still need to protect the API, use request limits, and disclose their data handling. Do not send sensitive material to a publicly hosted service without an approved privacy review.

## Dataset terms and attribution

The OPP-115 project states that the corpus is made available for research, teaching, and scholarship purposes only, with terms in the spirit of a Creative Commons Attribution-NonCommercial license. This model package is intended for the team's non-commercial academic demonstration. The source corpus is not included. Do not use or distribute this artifact commercially without obtaining the necessary permission from the dataset rights holders. Confirm the terms with the Usable Privacy Policy Project before broader redistribution.

Dataset source: [Usable Privacy Policy Project - Data and Tools](https://www.usableprivacy.org/data/).

Required research citation:

Shomir Wilson, Florian Schaub, Aswarth Abhilash Dara, Frederick Liu, Sushain Cherivirala, Pedro Giovanni Leon, Mads Schaarup Andersen, Sebastian Zimmeck, Kanthashree Mysore Sathyendra, N. Cameron Russell, Thomas B. Norton, Eduard Hovy, Joel Reidenberg, and Norman Sadeh. “The Creation and Analysis of a Website Privacy Policy Corpus.” *Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics*, 2016. [ACL Anthology](https://aclanthology.org/P16-1126/).
