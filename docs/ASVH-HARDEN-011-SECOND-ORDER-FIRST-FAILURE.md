# ASVH HARDEN-011 — Second-Order First-Failure Record

Status: OPEN / RED
Run: 35494149267

Preconditions reproduced in the same run:
- HARDEN-010 frozen positive baseline: 225 passed.
- HARDEN-011 first remediation suite: 10 passed.
- HARDEN-011 second-order suite: 3 passed / 3 failed.

Preserved failures:
- SO03: possession of an exact valid capability was sufficient to form the represented consequence.
- SO04: recreated executor-local state could accept a previously consumed capability.
- SO06: two executor instances could independently accept the same capability.

The common architectural finding is executor-local issuance/consumption truth. The initial remediation establishes exact-attempt/payload binding and local single-use behavior, but not durable shared single-use authority across restart/instances, nor executor-authenticated use.

This is reference-model evidence only; it is not a claim about a deployed NHS EPR.

Remediation target: shared durable execution-authority state with atomic consumption and explicit executor identity binding. The original second-order probes are retained unchanged for rerun.
