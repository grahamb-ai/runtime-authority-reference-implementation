# ASVH-HARDEN-002-CTS — Authority Continuity / Present Standing

Status: FROZEN v1.0

## Test suite

H2-001 — valid standing at execution
- ALLOW + valid bind + current valid state
- expect EXECUTED and exactly one consequence

H2-002 — product authorisation revoked after ALLOW
- valid at determination, revoked before executor standing check
- expect PRESENT_STANDING_INVALID and zero consequences

H2-003 — monitoring state breached after ALLOW
- monitoring_clear changes true -> false before execution
- expect PRESENT_STANDING_INVALID and zero consequences

H2-004 — current standing unavailable
- provider returns unavailable
- expect PRESENT_STANDING_UNAVAILABLE and zero consequences

H2-005 — policy version changes after ALLOW
- provider policy_version differs from bound commit policy
- expect PRESENT_STANDING_INVALID and zero consequences

H2-006 — state changes after initial check but before consequence
- first standing read valid; second read reflects adverse state
- expect PRESENT_STANDING_CHANGED and zero consequences

H2-007 — bind expires during protected interval
- bind valid on first check; trusted clock passes expiry before final consequence check
- expect BIND_EXPIRED and zero consequences

H2-008 — stale state replay after higher version accepted
- accept sequence N, later provider presents N-1
- expect STATE_ROLLBACK_DETECTED and zero consequences

H2-009 — stale state resurrection after executor restart
- persisted high-watermark N must survive recreation of executor/provider-facing component
- snapshot N-1 must remain rejected

H2-010 — caller timestamp cannot extend bind lifetime
- attempted commit/request supplies arbitrary future transport time outside material object
- harness trusted clock controls expiry
- expect BIND_EXPIRED

H2-011 — forward state change that remains valid
- sequence increases, all standing predicates remain valid
- expect execution permitted

H2-012 — exact commit still enforced under continuity layer
- continuity state valid but document payload changes after ALLOW
- expect BINDING_MISMATCH and zero consequences

## Suite-level PASS

All twelve tests pass and no prevented case increments the simulator consequence count.

## Evidence expectations

Each run must record Git SHA, suite version, policy version, trusted clock profile, state source ID, high-watermark position, initial/final standing snapshot, bind state, executor result and consequence count.

## Claim permitted after PASS

Within the declared reference-harness boundary, outstanding execution authority is revalidated against versioned present-standing state immediately before simulated consequence formation; detected revocation, unavailability, expiry, policy mismatch or stale-state rollback prevents that consequence.

## Claims not permitted

Do not infer production EPR non-bypassability, live NHS state authority, distributed atomicity, production time security, or cross-system consistency guarantees.
