# Rule catalog

Rules are versioned configuration, not embedded regulatory conclusions in application code. A match produces a text-based `signal` or `requires_review` finding; it does not establish whether a business is subject to a law or legally noncompliant.

Each rule records its jurisdiction, source, review date, scoring impact, positive/concern patterns, and unsupported inference policy. Before release, a team-approved reviewer must update the `reviewed_on` date and confirm scope/effective-date applicability.

Initial primary sources:

- GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj
- CCPA/CPRA: https://oag.ca.gov/privacy/ccpa
