# ASVH-HARDEN-010 — Restart / Recovery Attack Freeze

Status: FROZEN BEFORE REMEDIATION

This pass attacks the remediation candidate's recovery semantics. It does not change the original H10-001..H10-011 failure-first assertions or the earlier HC-H10 findings.

## Proposition

A runtime restart, recovery-state loss, or authority-state replay MUST NOT allow an older or conflicting positive authority observation to become ACTIVE merely because the in-memory high-watermark has disappeared.

## Frozen attacks

- HR06: process restart must not erase the effective revision floor.
- HR07: missing/untrusted recovery state must not fail open into ACTIVE.
- HR08: source alias/substitution after restart must not satisfy a declared authority requirement.
- HR09: replayed older positive standing must not override a newer recovered revocation.
- HR10: contradictory standing at the same authority revision must be INDETERMINATE rather than ACTIVE.

## Expected first-run finding

The current candidate uses in-memory `AuthorityConvergenceState`. HR06 and HR07 are therefore expected to expose a recovery weakness unless durable/recovered state is explicitly established. HR10 also probes whether same-revision contradictory observations are remembered across sequential reads rather than only within one basis.

## Evidence boundary

These tests are reference-model attacks. They do not demonstrate production storage durability, cryptographic source authentication, NHS deployment, external registry atomicity, or real EPR non-bypassability. Failures must be preserved before remediation.