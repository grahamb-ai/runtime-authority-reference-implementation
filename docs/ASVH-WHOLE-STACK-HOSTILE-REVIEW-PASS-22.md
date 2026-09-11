# ASVH Whole-Stack Hostile Review — Pass 22

## Scope
Pass 22 attacked numeric fence semantics at the whole-stack composition boundary. The target was whether values that compare equal in Python, or are internally consistent but semantically invalid, could be accepted as authority epochs or deployment-profile versions.

## Frozen hostile scenarios
- WS22-001: boolean `True` used coherently as the distributed authority epoch must not form.
- WS22-002: authority epoch `0` must not form.
- WS22-003: negative authority epoch must not form.
- WS22-004: boolean `True` used as layer-evidence deployment-profile version must not form even though `True == 1` in Python.
- WS22-005: positive exact integer epoch/profile versions remain the valid control.

## Preserved failure
Frozen failure run: `34624305279`.

HARDEN-001 through HARDEN-009 and whole-stack hostile passes 1 through 21 remained green. Pass 22 failed 4 of 5 hostile scenarios: boolean, zero and negative authority epochs, and boolean deployment-profile versions all still produced `FORMED`.

Finding: `HC-WS22-FR-001 — equality-only numeric fencing accepted semantically invalid values`.

Root cause: the composition boundary compared epoch and profile-version values for equality but did not enforce their value domain. Python booleans are subclasses of integers, and zero/negative integers can remain internally self-consistent while still being invalid monotonic fence positions.

## Remediation
Remediation commit: `5f83bc58cf6e3f03400502745bc5758db8830b77`.

The whole-stack coordinator now requires:
- distributed and current authority epochs to be exact `int` values, excluding `bool`, and greater than zero;
- every layer-evidence authority epoch to be an exact positive `int`;
- every layer-evidence deployment-profile version to be an exact positive `int`.

These validations occur before equality comparisons are allowed to establish coherence.

## Re-verification
Full verification run: `34624447433`.

Result:
- HARDEN-001 through HARDEN-009: PASS.
- Whole-stack hostile passes 1 through 21: PASS.
- Pass 22: PASS, 5/5.

## Bounded conclusion
Within the declared ASVH reference-harness boundary, numeric fencing at the whole-stack composition point requires exact positive integer semantics; boolean, zero and negative values cannot silently satisfy authority-epoch or deployment-profile version equality checks.

## Non-claims
This does not establish production consensus, externally anchored monotonic counters, Byzantine resistance, distributed storage guarantees, or real NHS/EPR enforcement.
