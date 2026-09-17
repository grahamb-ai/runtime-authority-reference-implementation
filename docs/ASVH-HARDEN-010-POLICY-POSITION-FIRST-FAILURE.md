# ASVH-HARDEN-010 — Policy Position / Final-Bind First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE POLICY-POSITION REMEDIATION

This matrix is derived from frozen HR37–HR48 and the current reference implementation. It is not GitHub Actions evidence.

| Test | Candidate behaviour | Expected |
|---|---|---|
| HR37 | policy position has no authoritative source identity | FAIL |
| HR38 | policy position carries no freshness evidence | FAIL |
| HR39 | impossible negative age cannot be represented/validated | FAIL |
| HR40 | same-revision/different-digest equivocation has no authority epoch/equivocation evidence | FAIL |
| HR41 | forged high revision has no attestation requirement | FAIL |
| HR42 | UNAVAILABLE can be represented directly, but cannot pass positive-standing check | PASS |
| HR43 | policy-position source substitution cannot be detected because source is absent | FAIL |
| HR44 | observation context is absent | FAIL |
| HR45 | naive check-then-commit permits revocation after the check | FAIL |
| HR46 | successful policy check creates an unbound commit opportunity | FAIL |
| HR47 | final policy-authority unavailability is not checked by naive commit | FAIL |
| HR48 | commit can occur without a policy-position binding token/receipt | FAIL |

Expected matrix: 11 FAIL / 1 PASS.

## Preserved findings

- HC-H10-FR-026 — policy-position provenance/source is not represented.
- HC-H10-FR-027 — policy-position freshness is not represented.
- HC-H10-FR-028 — same-position equivocation cannot be explicitly detected.
- HC-H10-FR-029 — policy-position revision is not independently authenticated.
- HC-H10-FR-030 — policy observation is not bound to an observation context.
- HC-H10-FR-031 — policy revalidation is vulnerable to check-to-consequence change.
- HC-H10-FR-032 — consequence formation is not bound to the verified policy position.
