# ASVH-HARDEN-010 — Candidate Hostile Findings

Status: PRESERVED PRE-VERIFICATION FINDINGS

The first remediation candidate addresses fresh aggregate override and consequence-time re-read, but the next hostile pass identifies three residual seams.

## HC-H10-FR-001 — Revision rollback / replay
The candidate evaluates a dependency revision for structural validity but does not persist or compare a source/subject high-watermark. A replayed older positive revision can therefore appear ACTIVE in isolation. Required remediation: monotonic per-authority revision floor across observations/restarts, with rollback prevented or indeterminate according to evidence semantics.

## HC-H10-FR-002 — Same-revision contradictory evidence
The candidate rejects duplicate identical source/subject identities, but contradictory observations at the same logical revision from distinct source identities expose an unresolved authority-source model. Required remediation: explicit authority-source set and conflict semantics; do not treat source diversity as independent permission votes.

## HC-H10-FR-003 — Source substitution
The candidate binds a source_id string but does not authenticate or constrain which source is authoritative for a dependency. A lookalike/substituted source can provide a positive assertion. Required remediation: declared authoritative source identity/binding and fail closed for unexpected source substitution.

These findings must not be hidden by changing hostile expectations. They remain part of the HARDEN-010 evidence trail.