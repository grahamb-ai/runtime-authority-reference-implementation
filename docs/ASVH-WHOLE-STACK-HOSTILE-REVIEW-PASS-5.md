# ASVH Whole-Stack Hostile Review — Pass 5

## Scope

Pass 5 attacked replay and substitution across fencing/version dimensions that were still absent from the signed whole-stack composition evidence after Pass 4.

## Preserved hostile failure

Workflow run `34615233716` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 and whole-stack passes 1–4 remained green. Pass 5 failed 8 of 9 attacks; only the fully bound positive control passed.

The final execution boundary accepted current, integrity-valid layer evidence even when that signed evidence carried:

- an old distributed authority epoch;
- a superseded lease identity;
- a different runtime policy version;
- a different rule catalogue version;
- a different control-contract version;
- a different deployment-profile version;
- none of those fencing/version dimensions at all; or
- a stale lease basis on the break-glass path.

## Finding

**WS-FR-005 — Integrity-valid composition evidence was not bound to the full authority/version basis.**

A signed `ACTIVE` or `ALLOW` status for the correct deployment and consequence was still too weak if it could be replayed under a different authority epoch, lease, policy/ruleset, contract or deployment-profile basis.

## Remediation

Commit `299a80b32aad16bd8430d9a527447294d76f59e0` made those dimensions execution-significant at the whole-stack boundary. `LayerAuthorityEvidence` now carries and integrity-binds:

- authority epoch;
- authority lease identity;
- runtime policy version;
- rule catalogue version;
- control-contract version; and
- deployment-profile version.

The coordinator requires each dimension to be present and to match the current composed execution basis before a layer result can contribute to simulated consequence formation.

Commit `f5314d8b9b1406e2f01fb293ecc37826b888f165` updated the shared positive fixtures to issue current, fully bound layer evidence. That re-run exposed one test-fixture issue: WS5-007 was intended to preserve the legacy unbound-evidence case but had begun using the now-hardened shared fixture. Commit `73a38ee00b6e8314c77d8dc885f27b93ccb26603` restored an explicit legacy evidence fixture for that attack without weakening the coordinator.

## Final re-verification

Workflow run `34615516657` completed successfully.

Result:

- HARDEN-001 through HARDEN-009: PASS
- WS-001 through WS-016: PASS
- WS2-001 through WS2-008: PASS
- WS3-001 through WS3-011: PASS
- WS4-001 through WS4-011: PASS
- WS5-001 through WS5-009: PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, integrity-valid whole-stack layer evidence is not execution-usable merely because it is fresh and bound to the correct deployment and consequence. It must also be bound to the current authority epoch, current lease, runtime policy, rule catalogue, control contract and deployment-profile version.

## Explicit non-claims

This remains a reference-harness model. It does not establish production lease issuance, consensus, PKI/HSM signing, external attestation, globally atomic policy transition, NHS deployment identity or real EPR route closure.
