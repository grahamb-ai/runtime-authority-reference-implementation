# ASVH-AIRP-009 — Standing Dependency First Result

**Result:** FAIL / RED  
**Run:** 35498716152  
**Frozen test:** 9837c64874f1dfd5e2cac299ab0264af02ada71f  
**Frozen specification:** 8a518deed8a63bb4f6af4e7eca62b47f1ea8e2fe

## Result

`2 failed, 5 passed in 0.11s`

The configured gateway correctly blocked PREVENTED, INDETERMINATE, null standing and reader exceptions, and the ACTIVE positive control committed.

Two gaps were exposed:

1. A plain string `"ACTIVE"` was accepted as equal to `ConvergenceResult.ACTIVE`, so an untyped/unverified representation could satisfy the check.
2. A gateway configured with no consequence-time standing reader retained legacy behavior and COMMITTED.

## Classification

**RED — standing enforcement is not yet structurally mandatory and the accepted standing type is too permissive.**

AIRP-008 remains PASS AFTER REMEDIATION for the configured, typed scenario. AIRP-009 narrows the claim by showing configuration/type conditions under which that protection is not guaranteed.

No remediation was made before this result was preserved.
