# Anthony Charleston Implementation Workflow

## Purpose and ownership

This workflow turns Anthony's assigned responsibilities into an implementation plan for the current Privacy Policy Analyzer prototype.

Anthony owns the **policy rule engine and compliance evaluation layer**:

- evaluate extracted policy clauses against privacy requirements;
- calculate the weighted Trust Score;
- map findings to GDPR and CCPA/CPRA obligations; and
- return structured, evidence-backed assessment results.

This is a technical risk signal, not legal advice or a legal compliance determination. Regulatory content must have a documented source, effective date, jurisdiction, and review owner before it is treated as production-ready.

## Current-state gap

The existing React prototype has browser-only keyword matching in `src/main.jsx`. It can display broad signals and a rough score, but it does not yet provide a backend service, extracted-clause input, configurable rules, regulatory citations, per-category score explanations, confidence/coverage, or automated tests. The tasks below close those gaps.

## Workflow

### 1. Define the analysis contract (first)

1. Agree on the input produced by the document/NLP component.
   - Required fields: `document_id`, `source_type`, normalized full text, and an ordered `clauses[]` array.
   - Each clause needs a stable `clause_id`, text, section heading (when known), character offsets, and NLP tags/confidence (when available).
2. Define the rule-engine output schema before implementation.
   - Include `analysis_id`, engine/rule-set version, timestamp, overall Trust Score, category scores, findings, positive signals, limitations, and coverage/confidence.
   - Each finding must include `finding_id`, severity, category, rule ID, plain-language explanation, regulation references, affected clause IDs, evidence excerpts, and remediation/next-step text.
3. Define score semantics clearly: 100 means more transparent/user-protective (higher trust), while a separate `risk_level` communicates concern. Do not label a high risk score as a high Trust Score.
4. Publish the schemas as versioned JSON/OpenAPI artifacts and add example input/output fixtures.

**Done when:** Taylor can hand the engine a clause payload without implementation questions, and Amon can render every result field from a stable example response.

### 2. Establish the scoring model

1. Preserve the agreed weights in versioned configuration:
   - Data sharing: 25%
   - Readability/transparency: 20%
   - Data collection: 20%
   - Legal language: 20%
   - User agency: 15%
2. For every category, define:
   - starting score and allowed range (0-100);
   - positive evidence that raises the score;
   - concern evidence that lowers it;
   - a cap or penalty for critical findings;
   - a missing-information rule; and
   - the minimum evidence needed to consider the category covered.
3. Implement the calculation as a pure, deterministic function: category assessments in, score breakdown out.
4. Return both the weighted calculation and human-readable rationale so the number is auditable.
5. Add a score calibration set with expected scores for representative policies; tune weights/penalties only through recorded version changes.

**Done when:** the same fixture always produces the same category and overall scores, the weighted math totals correctly, and every score movement points to finding IDs/evidence.

### 3. Create the rule and regulatory knowledge base

1. Store rules outside application code (for example, YAML/JSON under a versioned `rules/` directory).
2. Define a rule format with ID, title, category, severity, rationale, match logic, exclusions, score impact, plain-language copy, applicable jurisdictions, sources, effective date, and status.
3. Implement the first GDPR rule set around the project’s intended scope:
   - transparency/information duties;
   - lawful basis and consent signals;
   - purpose limitation and data minimization;
   - retention information;
   - controller contact and data-subject rights;
   - third-party/international transfer disclosures where in scope.
4. Implement the first CCPA/CPRA rule set around:
   - notice at collection and categories of personal information;
   - sale/share disclosures and opt-out rights;
   - access, deletion, correction, and non-discrimination rights;
   - retention disclosure; and
   - sensitive personal-information controls where applicable.
5. Mark every rule as `signal`, `requires_review`, or `not_assessable_from_policy_text`; avoid asserting legal noncompliance from text absence alone.
6. Add source links and review dates. Schedule rule-set review so "current regulatory framework" is operational, not an undocumented claim.

**Done when:** each supported requirement is traceable to a source and a rule version, and a user-visible finding distinguishes text evidence from an absence or uncertainty.

### 4. Implement clause evaluation

1. Build a rule evaluator that accepts the contract from Step 1 and runs rules against individual clauses plus document-level context.
2. Begin with explainable matchers: normalized phrases, patterns, tag combinations, negation handling, and section context. Do not rely only on simple substring checks.
3. Add rule exclusions to reduce false positives (for example, distinguish a statement that data is *not* shared from a sharing disclosure).
4. Aggregate clause matches into one finding per issue while retaining all supporting evidence.
5. Identify missing or vague language only when the input has sufficient coverage; return an `unknown`/`insufficient_evidence` state otherwise.
6. Produce category assessments from findings, including positive signals and unresolved limitations.

**Done when:** a result contains clause-level evidence for each detected rule, avoids duplicate findings, and records unassessable categories instead of silently treating them as safe.

### 5. Deliver the backend service and integration boundary

1. Create a backend application module (the documented target stack is Python/Flask) with environment-based configuration and no frontend-only scoring logic.
2. Expose a protected internal analysis endpoint, such as `POST /api/v1/analyses`, that receives normalized clauses and returns the versioned result schema.
3. Add health/readiness endpoints and structured error responses for invalid input, unsupported document state, rule-engine failure, and over-size requests.
4. Make the analysis request idempotent with a document hash or caller-supplied request key; do not persist raw policy text by default unless the product decision explicitly requires it.
5. Coordinate with Amon on public API routing and dashboard fields. Anthony supplies the engine response contract and reference fixtures; Amon owns the UI/API client integration under the team allocation.
6. Remove or gate the current browser-side `analyze()` demo once the real service is connected, so users cannot confuse prototype output with rule-engine output.

**Done when:** a sample clause payload can be submitted through the service and the React app displays the identical structured score, category explanations, evidence, and limitations.

### 6. Add safeguards and observability

1. Enforce request size, supported type, timeout, and rate-limit boundaries before analysis.
2. Avoid logging raw policy text, uploaded files, or personally identifying content. Log request IDs, rule-set versions, durations, result counts, and safe error codes instead.
3. Add a prominent educational/not-legal-advice notice to API and UI result metadata.
4. Record the engine version, rule-set version, and analysis timestamp in every result for reproducibility.
5. Define a rollback process for a faulty rule set and keep previous configurations available for comparison.

**Done when:** the service can be debugged without retaining submitted policy content, and any result can be reproduced using its recorded engine/rule-set versions.

### 7. Test, calibrate, and validate

1. Create unit tests for each rule, including positive, negative, negated, ambiguous, and missing-disclosure cases.
2. Test score math, caps, rounding, category weight totals, and the separation between Trust Score and risk level.
3. Build a small, versioned fixture suite from diverse policies (short/long, plain/legalistic, sharing-heavy, rights-rich, and incomplete text). Use only material the team may lawfully retain.
4. Add contract tests against Taylor's clause output and Amon's expected API/UI payload.
5. Run end-to-end tests: document submission -> extraction -> clause evaluation -> score -> dashboard result.
6. Track false positives, false negatives, unknowns, and coverage by rule/category. Record every rule or threshold change with its reason and before/after test results.
7. Manually review a sample of results with the team/advisor; treat this as product validation, not legal certification.

**Done when:** automated tests cover all implemented rules and score paths, contract tests pass, and the team has reviewed representative end-to-end results with documented known limitations.

### 8. Release and maintain

1. Document local setup, configuration, API schema, rule authoring, test commands, and operational limits.
2. Add a changelog for rule-set and scoring-model versions.
3. Deploy first to a non-production environment with test fixtures and monitoring.
4. Run a release checklist: security/privacy review, response-schema check, regression tests, UI evidence display, disclaimer, and rollback validation.
5. Set a recurring review cadence for framework sources, rules, dependencies, and evaluation metrics.

**Done when:** another team member can run, test, and update the engine from documentation, and releases can identify exactly which scoring/rule version produced user results.

## Suggested implementation order

1. Analysis contract and fixtures
2. Deterministic scoring function
3. Rule configuration and initial GDPR/CCPA mappings
4. Clause evaluator with evidence aggregation
5. Flask service and API contract tests
6. React dashboard integration
7. Safety controls, full test suite, calibration, and release documentation

## Explicit handoffs

| Dependency | Provider | Anthony's needed input/output |
| --- | --- | --- |
| Normalized, segmented clauses | Taylor / NLP workstream | Versioned clause payload with tags, offsets, and confidence |
| Results API and dashboard presentation | Amon / UI-API workstream | Stable analysis response, fixtures, field documentation, and error behavior |
| Trust-score policy | Team/advisor review | Approval for scoring semantics, weights, severity thresholds, and scope |
| Regulatory source review | Team/advisor or qualified reviewer | Confirmed sources, applicability, effective dates, and revision dates |

## Definition of complete

Anthony's responsibilities are fully implemented when the deployed workflow can receive normalized policy clauses, apply a documented/versioned GDPR and CCPA/CPRA rule set, produce evidence-backed category assessments and the agreed weighted 0-100 Trust Score, expose those results through the agreed service contract, render them in the application, and pass repeatable unit, contract, and end-to-end tests with documented limitations.
