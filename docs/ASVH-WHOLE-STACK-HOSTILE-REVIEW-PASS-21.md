# ASVH Whole-Stack Hostile Review — Pass 21

## Scope
Pass 21 tested whether the separate break-glass execution path remained bound to the exact clinical commit's normal runtime policy and rule-catalogue basis.

The hostile construction deliberately made the upstream whole-stack authority context internally coherent and integrity-bound to an older/different policy or rule catalogue while leaving the exact clinical commit on its current basis. The question was whether break-glass could turn that coherent-but-different authority context into a consequence.

## Frozen hostile scenarios
- WS21-001: break-glass cannot form when the authority context and signed layer evidence use a different runtime policy version from the exact commit.
- WS21-002: break-glass cannot form when the authority context and signed layer evidence use a different rule-catalogue version from the exact commit.
- WS21-003: matching current commit policy/rules basis remains the valid control.

## Preserved failure
Frozen failure run: `34623942071`.

HARDEN-001 through HARDEN-009 and whole-stack hostile passes 1 through 20 remained green. Pass 21 failed 2 of 3 scenarios:
- coherent alternate runtime-policy basis still produced `FORMED`;
- coherent alternate rule-catalogue basis still produced `FORMED`.

Finding: `HC-WS21-FR-001 — break-glass path bypassed exact-commit policy/rules coherence`.

Root cause: exact-commit policy and rule-catalogue comparisons were performed only inside the ordinary `ALLOW` / Protected Clinical Bind branch. The separate break-glass path therefore inherited upstream policy evidence without independently proving that the exact consequence had been formed under that same policy/rules basis.

## Remediation
Remediation commit: `792c35b9fa768a2e2874d56ad8b3fcf9de331080`.

Exact-commit runtime-policy and rule-catalogue coherence is now checked before execution-path branching, so the requirement applies to both ordinary ALLOW execution and separate break-glass authority. Protected-bind-specific policy/rules checks remain on the ordinary ALLOW path.

## Re-verification
Full verification run: `34624108722`.

Result:
- HARDEN-001 through HARDEN-009: PASS.
- Whole-stack hostile passes 1 through 20: PASS.
- Pass 21: PASS, 3/3.

## Bounded conclusion
Within the declared ASVH reference-harness boundary, separate break-glass authority cannot silently execute an exact clinical consequence under a runtime policy or rule-catalogue basis different from the basis bound to that consequence and the composed authority context.

## Non-claims
This does not establish production emergency-access governance, clinical appropriateness of break-glass, external truth of policy provenance, production key management, real NHS/EPR non-bypassability, or distributed atomicity.
