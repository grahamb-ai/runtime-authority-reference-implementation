# ASVH-HARDEN-003 — Hostile Review & Remediation Record

Status: RE-VERIFIED IN REFERENCE HARNESS

## Baseline
HARDEN-001 regression: PASS
HARDEN-002 regression: PASS
HARDEN-003 frozen CTS: PASS

## Hostile review findings
The first hostile HARDEN-003 run exposed three weaknesses:

1. HC-H3-FR-001 — Unrelated Authority Receipt accepted for consequence formation — CRITICAL.
   Observed: consequence_status FORMED.
   Expected: PREVENTED / invalid authority chain.

2. HC-H3-FR-002 — Protected Clinical Bind issued for a different Exact Clinical Commit accepted for consequence formation — CRITICAL.
   Observed: consequence_status FORMED.
   Expected: PREVENTED / invalid authority chain.

3. HC-H3-FR-003 — Reconciliation target unavailable propagated an exception instead of preserving uncertainty — HIGH.
   Observed: TimeoutError escaped reconciliation.
   Expected: INDETERMINATE.

Historical failing workflow: 34606839488, hostile-review job 103287300762.

## Remediation
- Added explicit authority-chain validation before target consequence formation.
- Bind integrity must verify.
- Receipt decision must be ALLOW.
- bind.authority_receipt_id must equal receipt.receipt_id.
- bind and receipt commit IDs/hashes must match the attempted Exact Clinical Commit.
- policy and rule-catalogue versions must remain consistent across bind, receipt and commit.
- Reconciliation read-back unavailability now returns INDETERMINATE with explicit provenance instead of raising through the evidence boundary.

## Re-verification
Remediation commit: 3695eccdaa9c4f1814fa90dbacffe8e317ac8d17
Workflow run: 34606946792

Results:
- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 frozen CTS: PASS
- HARDEN-003 hostile review: PASS

## Claim boundary
This demonstrates consequence-evidence separation, stable consequence identity, simulator idempotency, authority-chain binding and reconciliation semantics within the declared ASVH reference-harness boundary only.

It does not demonstrate production EPR idempotency, production transaction atomicity, independent target audit integrity, real NHS reconciliation, or production-grade consequence provenance.
