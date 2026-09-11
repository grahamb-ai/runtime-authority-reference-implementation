# ASVH-HARDEN-002 — Hostile Review & Remediation Record

Status: RE-VERIFIED IN REFERENCE HARNESS

## Baseline

The frozen HARDEN-002 CTS passed on the first implementation, while the HARDEN-001 regression suite also remained green.

## Hostile review findings

A separate hostile review was then executed against the continuity model. Three material weaknesses were observed and preserved:

### HC-H2-FR-001 — Same-position state equivocation

Observed: an adverse snapshot at `(epoch=1, sequence=5)` could be followed by a different favourable snapshot at the same state position. The watermark compared position only, so the favourable representation restored executable standing.

Observed outcome: EXECUTED
Expected outcome: STATE_EQUIVOCATION_DETECTED or equivalent prevention.

Severity: CRITICAL

### HC-H2-FR-002 — State-source substitution

Observed: after accepting a high-watermark from `HC-STATE-01`, a caller/provider could switch to a new source identifier and thereby establish an independent low watermark.

Observed outcome: EXECUTED
Expected outcome: STATE_SOURCE_MISMATCH.

Severity: CRITICAL

### HC-H2-FR-003 — Stale high-sequence snapshot

Observed: a two-hour-old snapshot with a very high sequence number was accepted as current standing because monotonic version position was checked without temporal freshness.

Observed outcome: EXECUTED
Expected outcome: PRESENT_STANDING_STALE.

Severity: HIGH

## Remediation

The continuity layer was strengthened as follows:

1. **State fingerprinting** — every accepted standing snapshot is fingerprinted over its full material state. Reuse of the same `(epoch, sequence)` with different state is rejected as `STATE_EQUIVOCATION_DETECTED`.
2. **Authoritative source binding** — the executor requires the configured standing source (`HC-STATE-01` in the reference harness). Source substitution is rejected as `STATE_SOURCE_MISMATCH`.
3. **Freshness enforcement** — present standing must fall within the configured reference freshness window (30 seconds in the harness). Stale or future-dated snapshots are rejected as `PRESENT_STANDING_STALE`.
4. **High-watermark persistence retained** — rollback detection remains durable across executor recreation.
5. **HARDEN-001 regression retained** — exact-consequence binding, bind integrity and replay protections remain unchanged.

## Re-verification

Remediated commit:

`bbab4bcecbd86c790a16ff274b54bef73db8bed0`

GitHub Actions run:

`34606242444`

Results:

- HARDEN-001 regression: PASS
- Frozen HARDEN-002 CTS: PASS
- HARDEN-002 hostile review: PASS
- Same-position equivocation attack: PREVENTED
- Source-ID substitution attack: PREVENTED
- Stale high-sequence snapshot attack: PREVENTED

## Permitted claim

Within the declared ASVH reference-harness boundary, execution authority is revalidated against an explicitly bound, fresh, monotonic present-standing source immediately before simulated consequence formation. Detected revocation, unavailability, expiry, source substitution, stale-state rollback, same-version state equivocation, policy mismatch or bind expiry prevents the simulated clinical consequence.

## Non-claims

This does not demonstrate production distributed consensus, live NHS authoritative-source integrity, EPR transaction atomicity, production trusted-time infrastructure, protection against compromise of the configured authoritative source, or real-world non-bypassability outside the reference harness.
