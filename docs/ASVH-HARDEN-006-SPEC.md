# ASVH-HARDEN-006 — Independence, Recovery & Authority-Service Failover

Status: FROZEN SPECIFICATION — implementation not yet demonstrated

## Purpose

HARDEN-006 tests whether a recovery or failover Runtime Authority component can become execution-authoritative without proving that it is at least as current as the accepted authority high-watermark and without preserving the declared independence boundary.

This stage addresses recovery authority, stale failover, authority-service identity, continuity across restart, and explicit failure semantics when independence or current standing cannot be established.

## Boundary

This is a reference-harness demonstration only. It does not establish production organisational independence, infrastructure tenancy separation, HSM/KMS isolation, network segmentation, NHS deployment resilience, or distributed consensus.

## Core invariants

H6-I01 A recovery authority instance MUST NOT become active until its accepted state is not behind the persistent authority high-watermark.

H6-I02 Authority high-watermark state MUST survive executor/recovery component recreation inside the harness boundary.

H6-I03 A lower epoch or sequence MUST NOT silently become current authority after restart/failover.

H6-I04 The same authority position with materially different state MUST be treated as equivocation, not as a legitimate recovery state.

H6-I05 Authority-service identity is part of the trust boundary. An unrecognised service identity MUST NOT become active merely because it presents a numerically current state.

H6-I06 Independence level is explicitly declared. The harness SHALL NOT infer a stronger level than demonstrated.

H6-I07 Requesting/action-proposing components MUST NOT be permitted to register themselves as authority-service identities inside the active trust profile.

H6-I08 Recovery without current standing is fail-closed for protected execution.

H6-I09 Failure to read the persistent high-watermark is explicit and MUST NOT default to zero/current.

H6-I10 A failover authority at exactly the accepted high-watermark is admissible only when its state fingerprint matches the accepted state fingerprint.

H6-I11 Authority-service replacement requires an authorised trust-profile transition; changing only runtime input is insufficient.

H6-I12 Trust-profile downgrade or independence-level reduction MUST be explicit and versioned; it cannot be accepted under the same profile identity/version.

H6-I13 The resulting evidence SHALL distinguish ACTIVE, PREVENTED and INDETERMINATE recovery states.

H6-I14 Recovery evidence preserves authority-service identity, trust-profile identity/version, observed epoch/sequence, accepted epoch/sequence, state fingerprint, and reason.

## Reference independence levels

- L0: no declared separation.
- L1: logical component separation only.
- L2: independently invoked authority component with separate state boundary inside the reference harness.

HARDEN-006 may demonstrate at most L2 inside the harness. It SHALL NOT claim L3+ production or organisational independence.

## Frozen conformance vectors

H6-001 primary authority current -> ACTIVE.
H6-002 failover exactly current with matching fingerprint -> ACTIVE.
H6-003 failover lower sequence -> PREVENTED.
H6-004 failover lower epoch -> PREVENTED.
H6-005 same position/different fingerprint -> PREVENTED equivocation.
H6-006 unknown authority-service identity -> PREVENTED.
H6-007 requester attempts to act as authority service -> PREVENTED.
H6-008 persistent high-watermark unavailable -> INDETERMINATE/PREVENTED; never ACTIVE.
H6-009 restart retains high-watermark and blocks stale recovery.
H6-010 new higher sequence accepted and raises high-watermark.
H6-011 later stale primary cannot roll back raised high-watermark.
H6-012 trust-profile version mismatch -> PREVENTED.
H6-013 same profile version but changed authorised service set -> PREVENTED.
H6-014 same profile version but reduced declared independence level -> PREVENTED.
H6-015 authorised profile transition can replace service identity when version advances.
H6-016 malformed authority position -> explicit failure, no exception escape.
H6-017 negative sequence/epoch -> PREVENTED.
H6-018 repeated same valid state deterministic.
H6-019 recovery evidence reconstructs service/profile/high-watermark basis.
H6-020 all earlier HARDEN regressions remain green.

## Hostile focus

After the frozen baseline, hostile review SHALL attempt:

- same-version trust-profile service expansion;
- same-version independence downgrade;
- failover with higher sequence but fabricated fingerprint history;
- high-watermark store reset/recreation;
- malformed and extremely large authority counters;
- requester service identity substitution;
- recovery when durable state read fails.

## Exit claim after PASS

Within the declared ASVH reference-harness boundary, a recovery Runtime Authority component cannot become execution-authoritative solely by presenting a locally favourable state. Activation is conditioned on an authorised authority-service identity, an exact active trust profile, and recovery state that is not behind or equivocal with the persistent authority high-watermark. Recovery uncertainty fails closed or remains INDETERMINATE rather than silently restoring stale authority.
