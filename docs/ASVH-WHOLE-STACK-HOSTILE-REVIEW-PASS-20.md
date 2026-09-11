# ASVH Whole-Stack Hostile Review — Pass 20

## Scope
Pass 20 tested trusted execution-time semantics on the ordinary ALLOW path. The target was whether an offset-naive caller-supplied `datetime` could be silently interpreted as UTC and still permit the simulated governed consequence.

## Frozen hostile scenarios
- WS20-001: offset-naive execution time must not form the ordinary ALLOW consequence.
- WS20-002: timezone-aware execution time remains the valid control.

## Preserved failure
Initial hostile run: `34623579650`.

HARDEN-001 through HARDEN-009 and whole-stack hostile passes 1 through 19 remained green. Pass 20 failed WS20-001: an offset-naive execution time was silently coerced to UTC and the result was `FORMED`.

Finding: `HC-WS20-FR-001 — caller-supplied naive execution time accepted as trusted time`.

Root cause: `WholeStackExecutionCoordinator.execute()` used `now.replace(tzinfo=timezone.utc)` when `now` had no timezone. That converted ambiguous time into trusted UTC instead of treating the temporal basis as indeterminate.

## Remediation
Remediation commit: `bf9b8324ba9b50fc4d22a21c49cc0ade79ec2e61`.

The coordinator now rejects an execution time whose `tzinfo` or UTC offset is absent, returning an explicit trusted-time failure rather than silently assigning UTC. Valid offset-aware time is normalized to UTC before composition and deployment enforcement.

## Re-verification
Full verification run: `34623776658`.

Result:
- HARDEN-001 through HARDEN-009: PASS.
- Whole-stack hostile passes 1 through 19: PASS.
- Pass 20: PASS, 2/2.

## Bounded conclusion
Within the declared ASVH reference-harness boundary, the whole-stack execution path does not silently convert an offset-naive caller time into trusted execution time. A governed consequence requires an explicit timezone-aware execution instant.

## Non-claims
This does not demonstrate an external trusted-time service, secure clock hardware, resistance to host-clock compromise, real NHS/EPR temporal integrity, or production distributed-time guarantees.
