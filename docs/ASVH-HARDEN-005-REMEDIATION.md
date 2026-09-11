# ASVH-HARDEN-005 — Hostile Review & Remediation Record

## Status
REMEDIATED IN REFERENCE HARNESS / RE-VERIFIED

## Baseline
Frozen H5-001..H5-020 conformance suite passed with HARDEN-001..004 regressions green.

## Hostile review source
Workflow run: 34609304143
Head SHA: 36631ba3038d58e1024be5f8447cfe44d3dc8dc7

The hostile review intentionally failed 5/5 tests. These failures are preserved and must not be rewritten as if they never occurred.

### HC-H5-FR-001 — Same-version route-set substitution accepted
Severity: CRITICAL

Observed: a caller supplied a profile with the correct deployment/version but an additional `RAW_EPR_API` route. The enforcer accepted the altered profile and returned `FORMED`.

Root cause: profile authority was inferred from deployment_id + profile_version rather than exact authoritative profile identity/content.

### HC-H5-FR-002 — Deployment profile identity substitution accepted
Severity: HIGH

Observed: a profile with a substituted `profile_id` but the same version/deployment was accepted and returned `FORMED`.

Root cause: active profile identity was not bound to enforcement.

### HC-H5-FR-003 — ControlContract authority expansion accepted
Severity: CRITICAL

Observed: a same-version profile changed `active_control_contract_version` to `CC-PERMISSIVE`; supplying the same permissive version to the enforcer returned `FORMED`.

Root cause: contract authority was checked against caller-supplied profile content rather than the constructor-bound active profile.

### HC-H5-FR-004 — Break-glass single-use was declarative only
Severity: CRITICAL

Observed: the same `single_use=True` break-glass authority returned `FORMED` twice.

Root cause: no atomic consumed-override state existed.

### HC-H5-FR-005 — Future-issued break-glass accepted
Severity: HIGH

Observed: break-glass authority whose `issued_at` was five minutes in the future was accepted and returned `FORMED`.

Root cause: expiry was checked but not not-before/issuance time.

## Remediation
Commit: `7b5c5a1c841e132f60898e3ec4969124cd34e581`

Changes:
- supplied deployment profile must exactly equal the constructor-bound active immutable profile;
- route lookup and active ControlContract version are taken from the active profile, not caller-modified profile fields;
- active and supplied profile integrity states must be valid;
- break-glass issuance time and expiry are parsed and enforced;
- malformed temporal state fails closed;
- break-glass authority identity is required;
- single-use break-glass replay is prevented with an atomic in-process consumed-ID set guarded by a lock.

## Re-verification
Workflow run: 34609408168
Head SHA: `7b5c5a1c841e132f60898e3ec4969124cd34e581`

Results:
- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 frozen CTS: PASS
- HARDEN-005 hostile review: PASS

## Claim boundary
The remediation demonstrates bounded route/profile/contract binding and break-glass replay resistance inside the ASVH reference-harness process. It does not demonstrate real NHS/EPR route closure, distributed break-glass replay prevention, production IAM, production cryptographic profile authenticity, supplier alternate-route closure, network isolation, or external consequence non-formation.

## Permitted bounded statement
Within the declared ASVH reference-harness boundary, execution is bound to an exact active deployment profile, its declared protected routes and active ControlContract version. Same-version profile substitution, route-set expansion and contract-authority expansion are rejected. Break-glass remains a separate authority domain, preserves the original decision, is exact-consequence and deployment bound, time bounded, and single-use within the reference enforcer instance.
