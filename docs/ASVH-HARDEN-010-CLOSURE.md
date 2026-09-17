# ASVH-HARDEN-010 — Authority Dependency Convergence Closure

Status: REFERENCE-MODEL HARDENING COMPLETE; EXECUTABLE WHOLE-SUITE / CI VERIFICATION STILL REQUIRED

## Hardened proposition

A fresh aggregate standing snapshot is not sufficient where a required authoritative dependency has advanced to conflicting, withdrawn, superseded or indeterminate standing. Recovery, trust policy, policy-position evidence and the final consequence bind are themselves treated as authority dependencies that must remain current at the relevant boundary.

## Preserved hostile findings

HARDEN-010 preserves failure-first findings across aggregate convergence, multi-source conflict, check-to-consequence races, rollback/restart, recovery completeness/provenance, attestation binding, trust-root circularity, trust-policy lifecycle, policy-position provenance/freshness and final-bind continuity. Historical hostile tests and first-failure matrices are evidence records and are not to be rewritten merely to obtain a green suite.

## Current reference controls

The candidate now includes required authoritative-source matching; prohibitive/indeterminate fail-closed semantics; revision high-watermarks; same-revision equivocation detection; explicit trusted recovery; exact record-set digest binding; recovery evidence coverage; configured trust policy; trust-policy revision/standing/digest; policy-position source/freshness/context/attempt evidence; fail-closed verifier/read exceptions; and a consequence bind over policy revision, policy digest, authority epoch, source, attestation digest, context and attempt identity. The policy position is re-read at the reference final-bind boundary.

## Deliberate residual boundary

The reference `final_bind_and_execute` calls an injected consequence callback. It does NOT demonstrate that a real EPR commit route cannot bypass the bind, that the callback enforces the bind, or that the policy read and EPR write are atomic. It also does not demonstrate production PKI/KMS/HSM trust, trusted time, durable high-watermark storage, crash consistency, consensus, real network partitions, NHS deployment or production source authentication.

The correct bounded conclusion is therefore not "non-bypassability proven". It is: the reference model now exposes the final enforcement boundary explicitly and fails closed across the modeled authority-continuity conditions; production route closure remains a separate integration property to demonstrate.

## Verification state

No GitHub Actions green run is claimed here. Earlier H10 workflow registration was not evidenced on this branch. Before promotion, run an executable candidate verification suite that separates preserved historical RED tests from current remediation verification, plus HARDEN-001 through HARDEN-009 regression. Preserve any new failure before remediation.
