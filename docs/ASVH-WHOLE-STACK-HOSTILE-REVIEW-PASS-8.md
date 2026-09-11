# ASVH Whole-Stack Hostile Review — Pass 8

## Scope

Pass 8 attacked rollback and replacement of the shared durable bind-claim database introduced by Pass 7.

## Preserved hostile failure

Workflow run `34616469994` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 and whole-stack passes 1–7 remained green. Pass 8 failed 2 of 4 attacks. The claim-store-unavailable and normal durable-claim controls behaved correctly.

Observed failures showed that a previously claimed Protected Clinical Bind could become execution-usable again if:

- the operational bind database was restored to a coherent pre-claim snapshot; or
- the operational bind database was deleted, recreated, and the same bind re-issued.

## Finding

**WS-FR-008 — Durable single-use state could be rolled back or replaced with the operational bind database.**

Pass 7 made replay state persistent and shared, but that state remained in the same operational database whose rollback could restore an earlier `ISSUED` state.

## Remediation

Commit `9b70a884a5f6e448617248e49f975ecea914373a` added a separate reference claim-anchor database to `BindStore`.

For each claim, the anchor is written first using an atomic insert keyed by `bind_id`. Only a first anchor claim may proceed to the operational `ISSUED -> CLAIMED` transition. This makes interrupted updates conservative: a failure after the anchor write may burn the bind, but rollback or replacement of the operational database alone cannot silently resurrect it.

The anchor is a reference model of a stronger failure domain. It is not an external cryptographic or production durability claim.

## Final re-verification

Workflow run `34616574399` completed successfully.

Result:

- HARDEN-001 through HARDEN-009: PASS
- Whole-stack Passes 1–7: PASS
- WS8-001 through WS8-004: PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, rollback or replacement of the operational bind database alone cannot resurrect a previously claimed Protected Clinical Bind because claim standing is retained in a separate reference anchor and checked before the operational claim transition.

## Explicit non-claims

The anchor remains a local reference model. This does not demonstrate protection against coherent rollback or replacement of both the operational database and its claim anchor, production external failure-domain isolation, cryptographic anchoring, replicated consensus, multi-region linearizability, or real EPR non-bypassability. Coherent rollback of every trust anchor remains outside the demonstrated boundary and requires an external monotonic authority source.
