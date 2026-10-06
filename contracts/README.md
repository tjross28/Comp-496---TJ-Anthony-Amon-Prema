# Analysis contracts

`analysis-request.schema.json` is the handoff from the text extraction/NLP layer to the compliance engine. `analysis-response.schema.json` is the stable handoff from the engine to the API and dashboard.

The engine evaluates the supplied text; it must report unknown or insufficient evidence instead of treating an absent phrase as proof of legal compliance. The response also includes `classifier_version` and `clause_classifications`: experimental topic suggestions from the trained OPP-115 clause model, each tied to a clause ID and excerpt. Those suggestions do not alter the Trust Score.

A Trust Score measures the documented scoring model's transparency/user-protection signal. It is not a legal compliance finding. Classifier scores are not calibrated probabilities and are not legal conclusions.

The fixtures demonstrate the minimum fields that the producer and consumer must preserve. Any breaking change requires a new contract version and updated fixtures.
