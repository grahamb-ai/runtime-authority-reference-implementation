# ASVH HARDEN-011 — Execution Route Closure First-Failure Record

Status: OPEN / RED
Run: 35493651334
Baseline: HARDEN-010 bounded positive suite reproduced GREEN before H11 execution.
H11 result: 8 failed / 0 passed.

## Frozen proposition

A represented clinical-record consequence must not be formable through a route that is independent of the final authority-controlled execution boundary. A complete bind is evidence input, not by itself an enforcement mechanism.

## Observed failures

The frozen H11 suite demonstrated that the pre-remediation reference sink remained independently callable. The represented consequence could therefore be formed by direct sink invocation, a downstream writer ignoring the bind, missing/incomplete bind routes, attempt substitution, replay, a direct route after gateway failure, and an alternate writer.

These findings are preserved as first-failure evidence. HARDEN-010 remains closed within its declared bounded reference-model scope; H11 tests the deliberately open executor/EPR enforcement residual.

## Claim boundary

This failure is a Python reference-model route-closure finding. It is not evidence that a real NHS EPR is bypassable, nor evidence of any deployed NHS integration.

## Remediation invariant

No public/protected represented commit operation may exist independently of the execution gateway. The gateway must own consequence formation, require an exact complete bind, bind the sink to the exact attempt, consume successful authority once, and fail closed on gateway/read/verification failure. Alternate writers must use the same boundary.
