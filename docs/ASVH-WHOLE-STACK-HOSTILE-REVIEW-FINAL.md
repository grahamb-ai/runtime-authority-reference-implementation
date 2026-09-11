# ASVH Whole-Stack Hostile Review — Final Reference-Harness Record

## Status

The bounded ASVH whole-stack hostile review has reached a defensible stopping point for the current reference-harness claim surface.

Final code verification run: **34632308295**

That run completed successfully across:

- HARDEN-001 through HARDEN-009; and
- the original whole-stack hostile suite plus frozen hostile review Passes 2 through 32.

The review method was deliberately failure-first: a new hostile condition was frozen as a test before remediation, the observed failure was retained in GitHub Actions history, remediation was then applied, and the complete hardening plus accumulated whole-stack suite was rerun.

## Late hostile-review findings

### Pass 27 — Deployment-profile semantic structure

Frozen failure run: `34630323556`.

Six of seven attacks demonstrated that internally coherent but structurally meaningless deployment metadata could still reach `FORMED`, including blank deployment/profile/contract/consequence/route/capability identities.

Remediation commit: `165b3e7d0ba224bb747240ef6b3cf97e8e83db29`.

Verification run: `34630460532`.

The deployment profile now requires meaningful nonblank identifiers, a positive exact-integer profile version, nonempty and structurally valid protected routes, nonblank target capabilities, and unique route identifiers.

### Pass 28 — Malformed integrity-reference types

Frozen failure run: `34630566455`.

Malformed non-string integrity references exposed fail-open/unhandled-type behaviour across composition evidence, protected binds and break-glass authority.

Remediation commits:

- `aee7ed8bb20961ac2d946411f1f6f9fdceb9922d` — protected-bind integrity type guard;
- `682777fee7126e37c39825d0f2d5da101a40af6e` — break-glass integrity type guard;
- `48d31c3bd9950e72dcd3688c4076c932d2db9644` — composition-evidence integrity type guard.

Verification run: `34630935001`.

Malformed integrity-reference types now fail closed rather than being interpreted or raising an unhandled comparison/path error.

### Pass 29 — Integrity-flag type confusion

Frozen failure run: `34631047405`.

`integrity_valid=1` and `integrity_valid="true"` were truthy and could reach `FORMED` even though neither was the declared boolean state.

Remediation commit: `07c7c62f6a23f67a69c89cbde98bd707cf8c48fb`.

The profile now requires exact boolean `True` semantics.

### Pass 30 — Protected-bind semantic identity

Frozen failure run: `34631300867`.

Six of seven attacks showed that a correctly re-signed bind could retain cryptographic integrity while carrying semantically invalid identity or profile data: blank bind identity, blank authority-receipt identity, blank runtime-authority version, altered materiality profile, altered canonicalisation profile, or blank bind schema.

Remediation commit: `916b9b1adb9785b39eecc44f3a8d975064af723e`.

Protected binds now require nonblank semantic identity and exact materiality/canonicalisation correspondence with the consequence being formed.

### Pass 31 — Unsupported consequence/bind profiles

Frozen failure run: `34631699085`.

Four of five attacks demonstrated that coherent but unsupported schema/profile identifiers could reach `FORMED`: `ECC-999`, an undeclared materiality profile, an undeclared canonicalisation profile, and `PCB-999`.

Remediation commit: `93f2b452e75a42a7ed739a87ff1fb8b58d64f941`.

Verification run: `34631869998`.

The reference harness now pins its declared exact-consequence schema, materiality profile, canonicalisation profile and protected-bind schema instead of treating arbitrary coherent labels as supported semantics.

### Pass 32 — Runtime-authority-version substitution

Frozen failure run: `34632006702`.

A re-signed protected bind carrying unsupported runtime-authority version `ASVH-RA-999` reached `FORMED` while all preceding hostile suites remained green.

Initial remediation correctly rejected the hostile version but also exposed a regression against the earlier HARDEN-005 fixture, which legitimately uses the separately declared reference-harness version `RA-1.0`. That regression was preserved in run `34632203699` rather than hidden by weakening the test.

Final remediation commit: `55fd9ada13674fb56eaa4e4fbc3d33c9427381c9`.

The boundary now uses an explicit closed allow-list of the runtime-authority versions actually declared by this reference harness: `RA-1.0` and `ASVH-RA-1.0`. Arbitrary or future-looking labels remain rejected.

Final code verification run: **34632308295** — all HARDEN-001 through HARDEN-009 and all accumulated whole-stack hostile passes through Pass 32 succeeded.

## What the accumulated review now demonstrates

Within the inputs and trust assumptions implemented by this reference harness, consequence formation is defended against the tested classes of stale, incoherent, replayed, substituted, malformed, structurally meaningless and semantically unsupported authority evidence.

The accumulated suite now exercises and constrains at least the following boundaries:

- deployment-profile identity, structure, integrity truth semantics, route closure and control-contract authority;
- closed runtime decision vocabulary;
- cross-layer producer, deployment, consequence, status, version, epoch, lease and observation-time coherence;
- positive-integer fencing/version semantics and nonblank lease identity;
- exact-consequence identity plus declared schema, materiality and canonicalisation profiles;
- protected-bind temporal validity, exact-consequence linkage, integrity, single-use semantics, semantic identity, declared schema/profile basis and declared runtime-authority versions;
- break-glass integrity, admitted authority identity, override identity, deployment/policy/consequence binding, exact single-use semantics, bounded temporal validity and replay protection; and
- failure-closed handling for absent, indeterminate, malformed and incorrectly typed evidence exercised by the frozen suites.

## Residual and explicitly excluded boundaries

This record is **not** a production security certification and must not be represented as one.

The harness does not establish production IAM correctness, production key custody or rotation, external KMS/HSM security, distributed consensus, formal verification, platform-level non-bypassability, production network isolation, or the availability/atomicity guarantees of a real external durable or monotonic replay/fencing service.

The protected bind carries `authority_receipt_id`, but the whole-stack coordinator is not supplied the originating Authority Receipt or an authoritative receipt registry. It therefore cannot independently prove receipt provenance at this boundary. Treating the identifier alone as proof would overclaim; receipt-registry/provenance verification remains outside the current composition input contract.

Similarly, the reference harness demonstrates declared version admission, not a production compatibility-negotiation or upgrade protocol.

## Stopping determination

After Pass 32, no further obvious high-value attack remains that can be tested honestly using the current reference-harness inputs without either repeating an already-covered invariant or pretending to validate an external trust service that the harness does not possess.

Accordingly, this hostile-review sequence is closed at **Pass 32** for the present claim surface. New passes should be opened only when the composition contract, external trust anchors, durable stores, production integration topology, or declared claim surface materially changes.
