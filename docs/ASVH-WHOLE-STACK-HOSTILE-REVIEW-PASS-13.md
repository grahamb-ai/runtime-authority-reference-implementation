# ASVH Whole-Stack Hostile Review — Pass 13

## Scope

Pass 13 attacked the structural identity semantics of integrity-valid break-glass authority. The question was whether a correctly signed emergency override could still be accepted with semantically empty identity fields.

The frozen hostile suite was committed before remediation in `tests/test_asvh_whole_stack_hostile_v13.py`.

## Frozen hostile scenarios

- WS13-001 — whitespace-only `authority_identity` must not form the consequence.
- WS13-002 — empty `override_id` must not form the consequence.
- WS13-003 — whitespace-only `override_id` must not form the consequence.
- WS13-004 — a well-formed integrity-bound, single-use break-glass authority remains a valid positive control.

## Preserved failure

Initial workflow run: `34621323664`.

HARDEN-001 through HARDEN-009 passed. Whole-stack hostile Passes 1 through 12 also passed. Pass 13 failed 3 of 4 hostile scenarios:

- whitespace-only authority identity was accepted and returned `FORMED`;
- empty override identifier was accepted and returned `FORMED`;
- whitespace-only override identifier was accepted and returned `FORMED`;
- the well-formed positive control passed.

Finding: `HC-WS13-FR-001 — integrity-valid but structurally empty break-glass identity fields were admissible`.

Root cause: integrity verification proved that the presented fields were signed, but the enforcer only checked truthiness of `authority_identity` and did not validate `override_id` at all. Whitespace-only strings therefore remained integrity-valid while being semantically empty identifiers.

## Remediation

Remediation commit: `1f7f8b5f57e51f70f384a496222982aeed1347a6`.

The deployment enforcer now requires both:

- `override_id` to be a string containing at least one non-whitespace character; and
- `authority_identity` to be a string containing at least one non-whitespace character.

These checks occur after integrity verification and before deployment, exact-consequence, temporal and replay processing.

The remediation does not attempt to prove that the named authority identity corresponds to a real NHS role-holder or that the override identifier originated from an external authoritative issuer. It only prevents structurally blank signed identifiers from becoming admissible authority inside the declared reference-harness boundary.

## Re-verification

Full re-verification workflow run: `34621431933`.

Result:

- HARDEN-001 through HARDEN-009: PASS;
- whole-stack hostile Passes 1 through 12: PASS;
- Pass 13: 4/4 PASS.

## Bounded conclusion

Within the declared ASVH reference-harness boundary, integrity-valid break-glass authority is not accepted solely because its signed payload verifies cryptographically. The emergency authority must also contain non-blank authority and override identifiers before the simulated consequence can form.

This remains a structural admissibility claim only. It does not establish external identity truth, production IAM, NHS role authority, production cryptographic trust, external monotonic storage or real EPR route closure.
