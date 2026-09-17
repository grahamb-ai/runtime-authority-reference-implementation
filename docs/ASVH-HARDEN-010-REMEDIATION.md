# ASVH-HARDEN-010 — Remediation Candidate

Status: REMEDIATION CANDIDATE — NOT YET VERIFICATION-EVIDENCED

Failure-first attack set remains frozen separately. This candidate does not alter H10-001 through H10-011.

## Remediation invariant

A required authoritative dependency participates directly in consequence-time standing. Aggregate freshness or majority positivity cannot override a prohibitive or indeterminate required dependency.

## Candidate mechanism

`AuthorityDependency` binds source identity, subject identity, monotonic revision, status and freshness. `DependencyBasis` is evaluated fail-closed. Required prohibitive standing returns `PREVENTED`; required unknown/unavailable/malformed/stale standing returns `INDETERMINATE`; only a complete positive required basis returns `ACTIVE`.

`consequence_time_converge` deliberately re-reads the authoritative basis at the consequence boundary. An earlier ACTIVE result is not itself authority to commit.

## Current candidate tests

R01 complete current positive basis -> ACTIVE.
R02 revocation cannot be outvoted -> PREVENTED.
R03 suspension cannot be outvoted -> PREVENTED.
R04 unknown required dependency -> INDETERMINATE.
R05 stale required dependency -> INDETERMINATE.
R06 impossible negative freshness -> INDETERMINATE.
R07 duplicate source/subject authority identity -> INDETERMINATE.
R08 absent required basis -> INDETERMINATE.
R09 consequence-time revocation is re-read -> PREVENTED.
R10 consequence-time UNKNOWN is re-read -> INDETERMINATE.

## Not yet demonstrated

This commit is not a green verification result. It does not yet prove rollback resistance/high-watermark persistence, same-revision contradictory evidence handling, source authentication, atomic external-registry read-to-EPR commit, production non-bypassability, NHS deployment, or completeness of a real authority-source hierarchy. Those remain attack targets.