# ASVH-AIRP-009 — Frozen Standing-Dependency Robustness Challenge

**Status:** FROZEN BEFORE EXECUTION  
**Date:** 2026-09-20  
**Origin:** residual dependency introduced by AIRP-008 remediation.

## Question

Does the protected execution boundary fail closed when consequence-time standing cannot be established, and can the standing dependency itself be omitted?

## Frozen cases

Expected BLOCKED with empty sink:
1. PREVENTED;
2. INDETERMINATE;
3. null/unavailable result;
4. wrong/unrecognised representation of ACTIVE;
5. reader exception;
6. gateway instantiated without a standing reader.

Positive control:
7. exact `ConvergenceResult.ACTIVE` permits the represented commit.

## Failure significance

Cases 1–5 test fail-closed behavior of the configured dependency. Case 6 tests whether the dependency is structurally mandatory or merely optional configuration.

If case 6 commits, preserve RED before changing constructor/configuration behavior.

## Boundary

Python reference-model evidence only. This does not prove production source authenticity, freshness, rollback resistance, availability, external atomicity or EPR route closure.
