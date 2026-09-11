# ASVH-HARDEN-008 — Failure & Remediation Record

## Baseline

Initial workflow run: `34611366813`

Frozen conformance result:
- HARDEN-001 through HARDEN-007 regressions: PASS
- HARDEN-008 H8-001 through H8-020: PASS

Hostile review result: FAIL

## Preserved finding

### HC-H8-FR-001 — Lexical policy-version comparison could permit rollback

The hostile test established an accepted policy high-watermark of `10.0` and then presented `2.0` as the active policy state. The initial implementation compared version strings lexically. Under lexical comparison, `"2.0"` is greater than `"10.0"`, so the rollback was not detected and an unchanged-basis authority artefact was returned as `ALLOW`.

Observed hostile result:

- expected: `PREVENTED`
- observed: `ALLOW`

This is a material authority-continuity defect because a lower semantic policy version could be mistaken for a later version and could allow outstanding authority to reappear under an older policy basis.

## Remediation

Commit: `65daa3776d0239c475a2d85971bc68420664f783`

Changes:

1. Policy versions are parsed as dotted numeric version tuples before ordering comparison.
2. Policy high-watermark acceptance and rollback detection use semantic numeric ordering rather than string ordering.
3. Non-comparable policy versions produce an explicit `INDETERMINATE` result rather than a permissive fallback.
4. No frozen H8 test was weakened or removed.

## Re-verification

Workflow run: `34611473968`

Result:

- HARDEN-001 regression: PASS
- HARDEN-002 regression: PASS
- HARDEN-003 regression: PASS
- HARDEN-004 regression: PASS
- HARDEN-005 regression: PASS
- HARDEN-006 regression: PASS
- HARDEN-007 regression: PASS
- HARDEN-008 H8-001 through H8-020: PASS
- HARDEN-008 hostile review: PASS

## Bounded claim

Within the declared ASVH reference-harness boundary, outstanding authority does not silently survive a material policy/ruleset transition. Compatibility, revalidation or invalidation semantics are explicit, time-bound and deployment-bound; accepted higher policy state prevents rollback to a lower dotted-numeric policy version from resurrecting previously invalidated or superseded authority.

## Non-claims

This evidence does not demonstrate production policy distribution, external policy-signing authority, distributed consensus across policy stores, NHS/EPR deployment enforcement, production cryptographic trust, or universal semantic-version support beyond the dotted-numeric version format implemented and tested here.
