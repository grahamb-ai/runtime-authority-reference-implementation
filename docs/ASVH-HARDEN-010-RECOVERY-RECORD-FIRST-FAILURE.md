# ASVH-HARDEN-010 — Recovery Record First-Failure Matrix

Status: PRESERVED SEMANTIC FAILURE ANALYSIS — BEFORE RECOVERY-EVIDENCE REMEDIATION

This is derived from the frozen HR11–HR16 assertions and the candidate implementation. It is not represented as GitHub Actions evidence.

| Test | Candidate behaviour | Expected |
|---|---|---|
| HR11 | `recover(())` sets `recovery_trusted=True` | FAIL |
| HR12 | partial record set is trusted; later observations can fill missing dependency | FAIL |
| HR13 | contradictory same-revision records make state untrusted | PASS |
| HR14 | negative revision makes state untrusted | PASS |
| HR15 | arbitrary very-high positive revision is accepted as trusted | FAIL |
| HR16 | older positive-only record set is trusted without completeness evidence | FAIL |

Expected matrix: 4 FAIL / 2 PASS.

## Preserved findings

- HC-H10-FR-007: empty recovery is treated as trusted recovery.
- HC-H10-FR-008: partial recovery can be completed by post-restart observations without proving the missing dependency history.
- HC-H10-FR-009: monotonic-looking high revision is treated as self-authenticating.
- HC-H10-FR-010: recovery completeness is not demonstrated; omitted newer prohibitive history cannot be detected from the record list alone.

The candidate already rejects negative revisions and contradictory same-revision recovery records.
