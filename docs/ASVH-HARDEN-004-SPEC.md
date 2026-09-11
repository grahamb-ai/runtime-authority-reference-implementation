# ASVH-HARDEN-004 — Evidence Contracts & Authoritative Source Semantics

Status: FROZEN SPECIFICATION — implementation not yet demonstrated

## 1. Purpose

HARDEN-004 tests whether a runtime fact used in an ASVH authority determination is admissible as evidence for that fact. It does not test whether the underlying real-world assertion is objectively true.

The control objective is to prevent Runtime Authority from silently treating a value as authoritative merely because it is present in Runtime Context.

## 2. Boundary

FlowSignal evaluates evidence against a defined Evidence Contract. It does not create the underlying truth represented by that evidence and does not determine clinical correctness, product safety, professional competence, regulatory compliance, organisational AI readiness, or overall cybersecurity posture.

## 3. Evidence status model

Every evidence item presented to a contracted runtime control SHALL resolve to exactly one of:

- VALID
- ABSENT
- STALE
- INVALID
- CONTRADICTORY
- UNVERIFIABLE
- REVOKED

No status may silently degrade to VALID.

## 4. EvidenceItem EC-1.0

An EvidenceItem SHALL support the following fields where required by its ControlContract:

- evidence_id
- control_id
- subject
- asserted_state
- evidence_source
- evidence_authority
- observed_at
- valid_from
- valid_until and/or max_age
- provenance_reference
- product_identifier
- product_version
- deployment_context
- integrity_reference
- status

Not every field is globally mandatory. Required fields are declared by the applicable ControlContract.

## 5. ControlContract CC-1.0

A ControlContract SHALL define:

- control_id
- subject_type
- responsible_party
- permitted_authoritative_sources
- required_fields
- temporal_validity_rule
- deployment_binding_rule
- product_version_binding_rule
- runtime_predicate
- conflict_semantics
- source_substitution_semantics
- failure_semantics
- receipt_requirements

A requesting AI system MUST NOT become authoritative for a contracted fact merely by asserting that fact in its request.

## 6. Evidence contract invariants

EC-I01 Stable control identity — every contracted control has a stable control_id.

EC-I02 Subject binding — evidence is evaluated only for the subject to which it applies.

EC-I03 Source authority — evidence is accepted only from a source permitted by the ControlContract.

EC-I04 Provenance — decisive evidence retains a provenance reference sufficient for reconstruction inside the harness boundary.

EC-I05 Temporal validity — time-sensitive evidence has explicit validity semantics.

EC-I06 Deployment binding — deployment-specific evidence cannot be replayed across deployments unless the contract explicitly permits it.

EC-I07 Product/version binding — product/version-specific evidence cannot silently authorise a different product/version.

EC-I08 Integrity — where integrity is required by contract, failed integrity validation prevents VALID status.

EC-I09 Explicit failure semantics — ABSENT, STALE, INVALID, CONTRADICTORY, UNVERIFIABLE and REVOKED have explicit contract outcomes.

EC-I10 No self-authorisation — the action-proposing/requesting system cannot self-attest decisive external authority state unless explicitly designated authoritative for that control.

EC-I11 No implicit source substitution — the same asserted value from a different source is not automatically equivalent evidence.

EC-I12 Contradiction preservation — conflicting authoritative evidence is not silently resolved by arrival order or arbitrary source selection.

EC-I13 Receipt traceability — the Authority Receipt records the decisive control, evidence reference/source, evidence status and rule result used in determination.

EC-I14 Evidence-to-decision binding — the recorded evidence basis is bound to the determination it supported.

EC-I15 Unknown authority fails explicitly — an unrecognised evidence authority cannot be treated as trusted by default.

## 7. Reference control contracts

HARDEN-004 SHALL implement only bounded synthetic contracts sufficient to verify the evidence semantics. These are reference-harness controls, not claims about actual NHS authoritative systems.

### HC.PRODUCT.VERSION.AUTHORISED

Subject: AI_PRODUCT_VERSION

Reference permitted source: DEPLOYMENT_REGISTRY

Required fields:
- product_identifier
- product_version
- deployment_context
- asserted_state
- observed_at
- provenance_reference

Reference predicate: asserted_state == AUTHORISED

Reference failure semantics:
- ABSENT -> REFUSE
- STALE -> REFUSE
- INVALID -> REFUSE
- CONTRADICTORY -> REFUSE
- UNVERIFIABLE -> REFUSE
- REVOKED -> REFUSE

### HC.CLINICIAN.TRAINING.CURRENT

Subject: CLINICIAN

Reference permitted source: TRAINING_REGISTRY

The harness verifies only whether an authoritative record states that the specified training requirement is current. It does not assess competence.

Reference predicate: asserted_state == CURRENT

Reference failure semantics:
- ABSENT -> ESCALATE
- STALE -> ESCALATE
- INVALID -> REFUSE
- CONTRADICTORY -> ESCALATE
- UNVERIFIABLE -> ESCALATE
- REVOKED -> REFUSE

## 8. Conflict semantics

Where two evidence items both claim permitted authority and materially conflict, the evaluator SHALL use the ControlContract conflict rule. The default HARDEN-004 rule is CONTRADICTORY. It MUST NOT select the newest, oldest, first, last, most permissive or most restrictive value unless the contract explicitly defines that precedence rule.

## 9. Source substitution

Evidence from source B MUST NOT replace evidence required from source A merely because the asserted value is identical. Substitution is permitted only where the ControlContract explicitly identifies source B as permitted or defines a substitution/precedence rule.

## 10. Temporal semantics

The evaluator SHALL use the harness trusted clock abstraction established by the existing hardening path. Caller-supplied time does not establish evidence freshness. Boundary tests SHALL cover not-yet-valid, expired/stale and revoked evidence.

## 11. Runtime Authority integration

The evidence evaluator sits before or as part of deterministic rule evaluation:

ControlContract -> EvidenceItem(s) -> Evidence Evaluation -> Contracted Runtime Fact -> Runtime Rule -> ALLOW | ESCALATE | REFUSE -> Authority Receipt

A Runtime Context field alone is not sufficient evidence for a contracted fact.

## 12. Authority Receipt extension

For each decisive contracted control the receipt/evidence record SHALL preserve at minimum:

- control_id
- subject
- evidence_id or evidence-set reference
- evidence_source
- evidence_authority
- evidence_status
- provenance_reference
- temporal evaluation result where applicable
- runtime predicate result
- resulting control outcome

This records what the harness relied on. It does not prove the external assertion was objectively true.

## 13. Frozen conformance vectors

H4-001 permitted authoritative source, current evidence, matching subject/product/deployment -> expected contracted fact VALID.

H4-002 missing required evidence -> explicit ABSENT semantics; no silent ALLOW.

H4-003 stale evidence -> STALE; contract failure semantics applied.

H4-004 revoked evidence -> REVOKED; contract failure semantics applied.

H4-005 unknown authority -> UNVERIFIABLE/INVALID according to frozen evaluator rule; never VALID.

H4-006 requesting AI self-attests product authorisation -> rejected unless contract explicitly permits requester as authority.

H4-007 evidence for different clinician subject -> rejected.

H4-008 evidence for different deployment -> rejected.

H4-009 evidence for different product version -> rejected.

H4-010 identical value from non-permitted source -> rejected; no implicit source substitution.

H4-011 two permitted authoritative items conflict -> CONTRADICTORY; no arbitrary winner.

H4-012 evidence not yet valid -> INVALID/UNVERIFIABLE per frozen temporal rule; never current VALID.

H4-013 required provenance absent -> INVALID.

H4-014 required integrity check fails -> INVALID.

H4-015 valid product-version evidence plus valid training evidence -> deterministic aggregate result according to rule catalogue.

H4-016 product evidence VALID, training evidence STALE -> training contract semantics applied; aggregate must not mask the stale constituent.

H4-017 same evidence set and same contract/rules/clock -> deterministic identical outcome.

H4-018 mutate evidence after determination -> prior receipt remains reconstruction evidence for original determination; mutated evidence requires fresh evaluation.

H4-019 substitute ControlContract version after evidence evaluation -> prior result cannot be silently reused under new contract.

H4-020 receipt/evidence record reconstructs decisive source, authority, status, provenance and predicate result.

## 14. Baseline rule

The specification and H4-001..H4-020 test definitions are frozen before implementation. The first executable full run is preserved as BASELINE-004. Failures SHALL be retained and remediated explicitly; failing evidence SHALL NOT be deleted or rewritten into a clean history.

## 15. Exit criteria

HARDEN-004 may be marked VERIFICATION-EVIDENCED only when:

1. all H4-001..H4-020 pass in a pinned full run;
2. HARDEN-001, HARDEN-002 and HARDEN-003 regressions remain green;
3. hostile tests for self-attestation, source substitution, contradiction, subject/deployment/version replay and temporal failure pass;
4. baseline failures and remediation history are preserved;
5. evidence records are sufficient to reconstruct the bounded determination;
6. non-claims remain explicit.

## 16. Non-claims

A HARDEN-004 PASS SHALL NOT establish that:

- a synthetic reference source is an actual NHS authoritative source;
- external evidence is factually true;
- an AI product is clinically safe or effective;
- a clinician is competent;
- an organisation is AI-ready;
- regulatory compliance has been achieved;
- cybersecurity posture is adequate;
- real NHS/EPR source integration has been demonstrated;
- production cryptographic trust or identity infrastructure has been demonstrated.

## 17. Permitted claim after PASS

Within the ASVH reference-harness boundary, contracted runtime facts are not accepted solely because a value is present in Runtime Context. The harness verifies source authority, subject and context binding, temporal validity, required provenance and explicit failure semantics against a versioned ControlContract. Self-attested, stale, revoked, mismatched, contradictory or non-permitted-source evidence is prevented from silently becoming valid runtime authority evidence.
