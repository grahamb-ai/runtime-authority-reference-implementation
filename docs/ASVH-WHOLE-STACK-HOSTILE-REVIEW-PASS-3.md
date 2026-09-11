# ASVH Whole-Stack Hostile Review — Pass 3

## Scope

Pass 3 attacked cross-layer identity coherence after the first two whole-stack composition remediations. The question was whether individually admissible upstream results could be assembled from different deployments, subjects, products or consequence identities and still produce a simulated governed consequence.

## Preserved hostile failure

Workflow run `34614301892` preserved the pre-remediation result.

HARDEN-001 through HARDEN-009 regressions remained green. Whole-stack passes 1 and 2 also remained green. Pass 3 then failed 10 of 11 frozen attacks.

Observed failures demonstrated that the coordinator could accept green upstream states even when:

- distributed authority referred to another deployment;
- recovery authority referred to another deployment;
- contracted evidence referred to another deployment;
- policy-transition state referred to another deployment;
- contracted evidence referred to another patient/subject;
- contracted evidence referred to another product;
- contracted evidence referred to another product version;
- the authority consequence binding hash differed from the exact consequence;
- a required cross-layer identity binding was absent; or
- break-glass was used while the evidence subject was incoherent.

The all-coherent positive control passed.

## Finding

**WS-FR-003 — Individually valid cross-layer states were not identity-coherent at the final execution boundary.**

The failure was a composition defect, not evidence that the underlying HARDEN components had individually regressed. The whole-stack coordinator accepted status values without proving that they all described the same governed deployment and material consequence.

## Remediation

Commit `7f65b58267520fdc992925ead90233cb02717f75` added explicit identity-coherence checks before any upstream status can become execution-usable.

The coordinator now requires all declared component identities to be present and binds:

- distributed authority deployment;
- recovery authority deployment;
- contracted evidence deployment;
- policy-transition deployment;
- evidence subject to the Exact Clinical Commit patient reference;
- evidence product identifier and version to the Exact Clinical Commit; and
- authority consequence binding hash to the Exact Clinical Commit binding hash.

Missing identity evidence returns `INDETERMINATE`. A mismatch returns `PREVENTED`. These checks apply before the break-glass path reaches deployment enforcement.

## Re-verification

Workflow run `34614411599` re-ran HARDEN-001 through HARDEN-009 and whole-stack hostile passes 1, 2 and 3.

Result:

- HARDEN-001 through HARDEN-009: PASS
- WS-001 through WS-016: PASS
- WS2-001 through WS2-008: PASS
- WS3-001 through WS3-011: PASS

## Bounded conclusion

Within the declared ASVH reference-harness boundary, individually admissible upstream authority states are not sufficient for simulated consequence formation unless their declared deployment and material consequence identities are coherent at the final composition boundary.

## Explicit non-claims

This does not establish production identity-provider integrity, cryptographic attestation of external component outputs, real NHS deployment identity, production EPR route closure, distributed transaction atomicity, or objective truth of the underlying evidence. Those require separate evidence and remain outside this claim.
