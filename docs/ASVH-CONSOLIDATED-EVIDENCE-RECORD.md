# ASVH Consolidated Evidence & Verification Record

**Status:** DRAFT FOR HOSTILE RED-TEAM REVIEW  
**Purpose:** consolidate the current ASVH reference-harness evidence into one bounded, auditable record without upgrading any claim beyond the underlying evidence.  
**Source branch:** `asvh-whole-stack-hostile-review`  
**Final whole-stack verification run:** `34632308295`

---

## 1. Executive determination

The ASVH reference harness has reached a defensible stopping point for its present local claim surface.

The accumulated engineering record demonstrates, **within the declared reference-harness inputs and trust assumptions**, a composed pre-consequence authority boundary that tests and constrains:

- exact clinical consequence binding;
- present-standing continuity through the consequence-formation interval;
- separation of authority determination, protected execution and consequence evidence;
- contracted evidence-source authority and provenance semantics;
- deployment-profile and protected-route enforcement inside the reference boundary;
- recovery/high-watermark semantics;
- verification-evidence integrity and reproducibility semantics;
- policy/ruleset transition and rollback handling;
- distributed execution-authority fencing semantics; and
- whole-stack composition against stale, incoherent, replayed, substituted, malformed, structurally meaningless and semantically unsupported authority evidence.

The final whole-stack verification run `34632308295` passed HARDEN-001 through HARDEN-009 and all accumulated whole-stack hostile passes through Pass 32.

This is **not** evidence of a production NHS deployment, production security certification, real EPR non-bypassability, external truth of supplied evidence, or production-grade external anchoring.

The engineering programme has therefore answered a narrower question than “is this safe for the NHS?” It has established that the proposed runtime-authority pattern can be made internally coherent and hostile-tested inside the reference implementation. The next evidential question is whether a real ambient-scribing deployment can expose authoritative, current and appropriately bound evidence at the pre-commit boundary.

---

## 2. What is being verified

The reference pattern separates four propositions that must not be collapsed:

1. **Authority determination** — whether the conditions represented to Runtime Authority support ALLOW, ESCALATE or REFUSE for the exact governed action.
2. **Protected execution authority** — whether an execution attempt is still entitled to rely on that determination for the exact consequence now being attempted.
3. **Consequence formation** — whether the governed target consequence actually formed, was prevented, or remains indeterminate.
4. **Evidence provenance** — what evidence was relied upon and whether it was admissible under a declared ControlContract.

A positive result in one proposition does not prove the others.

In particular:

- an Authority Receipt is determination evidence, not bearer execution authority;
- executor success is not itself independently established consequence evidence;
- timeout is not proof of prevention;
- a Runtime Context value is not authoritative merely because it is present; and
- cryptographic/reference integrity does not make semantically invalid content admissible.

---

## 3. Declared execution boundary

The hardened reference path is conceptually:

`Declared evidence sources -> Evidence Contract evaluation -> Runtime Authority determination -> Authority Receipt -> exact-consequence Protected Clinical Bind -> present-standing / policy / recovery / distributed fencing re-establishment -> protected execution route -> target consequence -> consequence reconciliation/evidence`

The decisive design principle is that **a previous ALLOW is insufficient by itself**. Outstanding authority remains conditional on exact consequence identity, current standing, applicable policy/rules, deployment profile, replay state and the other controls declared by the composition contract.

The reference harness deliberately distinguishes the point at which authority is determined from the point at which the consequence forms.

---

## 4. Hardening evidence chain

### HARDEN-001 — Exact Clinical Commit & Protected Execution Bind

Purpose: bind execution authority to the exact clinical consequence rather than treating ALLOW as reusable authority.

The initial frozen conformance suite passed, but hostile review exposed a critical weakness: a fabricated persisted Protected Clinical Bind with a forged receipt identifier and matching exact-commit binding could reach `EXECUTED`.

Preserved finding: **HC-H1-FR-001 — Fabricated persisted bind accepted.**

This finding established that structural validity and exact-action binding did not prove bind provenance. The failure was retained and later remediated in the reference harness. Subsequent whole-stack passes further constrained bind integrity, semantic identity, supported schemas/profiles and runtime-authority versions.

### HARDEN-002 — Present Standing / Authority Continuity

Purpose: test whether authority remains usable through the protected Consequence Formation Interval when relevant state can change after the original determination.

Controls are classified as `SNAPSHOT`, `PRESENT_AT_EXECUTION` or `CONTINUOUS`. Present/continuous conditions are re-established around atomic bind claim and immediately before consequence formation. Monotonic `(state_epoch, sequence)` high-watermark semantics prevent older accepted state from silently restoring authority inside the declared reference boundary.

Permitted interpretation: a prior ALLOW plus a valid Protected Clinical Bind is insufficient when a decisive present-standing condition is no longer in standing.

### HARDEN-003 — Consequence Evidence & Reconciliation

Purpose: separate execution attempt from evidence that the governed consequence formed.

Consequence states are:

- `FORMED`
- `PREVENTED`
- `INDETERMINATE`

The reference harness uses stable consequence identity and target read-back reconciliation. Lost acknowledgement or timeout is not directly mapped to prevention. Duplicate retry cannot create a second simulated governed consequence within the tested boundary.

### HARDEN-004 — Evidence Contracts & Authoritative Source Semantics

Purpose: test whether a runtime fact is **admissible evidence** for the fact used in authority determination. It explicitly does not test whether the underlying real-world assertion is objectively true.

Evidence statuses are:

- `VALID`
- `ABSENT`
- `STALE`
- `INVALID`
- `CONTRADICTORY`
- `UNVERIFIABLE`
- `REVOKED`

A versioned `ControlContract` defines permitted authoritative sources, required fields, temporal validity, deployment/product binding, predicates, conflict/source-substitution semantics, failure semantics and receipt requirements.

Key rule: the requesting AI system cannot make itself authoritative for a contracted external fact merely by asserting that fact.

The implemented controls are synthetic reference controls. `DEPLOYMENT_REGISTRY` and `TRAINING_REGISTRY` are **not claims about actual NHS authoritative systems**.

### HARDEN-005 — Deployment Boundary & Route Closure

Purpose: test deployment enforcement inside the reference harness.

Hostile review exposed same-version route-set substitution, profile identity substitution, ControlContract authority expansion, break-glass replay and future-issued break-glass acceptance. These failures were preserved before remediation.

The resulting bounded model binds execution to an exact active deployment profile, declared protected routes and active ControlContract version, with a separately governed break-glass authority domain.

This does **not** establish that all alternate routes to a real NHS EPR are closed.

### HARDEN-006 — Independence, Recovery & Authority-Service Failover

Purpose: prevent recovery/failover from silently restoring stale authority.

Preserved hostile failures included durable high-watermark read failure, local recovery-store replacement resurrecting stale authority, unsupported independence level, and boolean-as-integer authority counters.

The remediation introduced a second reference persistence anchor and explicit fail-safe semantics. That anchor is a **reference-harness model of an external recovery anchor**, not evidence that a production independent failure domain exists.

### HARDEN-007 — Evidence Pack Integrity & Reproducibility

Purpose: strengthen the evidential basis for verification claims by binding code, test inventory, policy/profile inputs and evidence artefacts to a run.

The design requires deterministic manifests, SHA-256 artefact digests, explicit completeness states and distinction between outcome reproduction and byte-for-byte evidence reproduction.

The final whole-stack run includes the HARDEN-007 regression path. The consolidated record does not independently elevate this into production notarisation, external timestamping, hardware signing or repository-owner independence.

### HARDEN-008 — Policy Transition & Outstanding Authority

Purpose: ensure outstanding authority does not silently survive a material policy/ruleset transition.

Preserved finding: **HC-H8-FR-001 — lexical policy-version comparison could permit rollback.** An accepted `10.0` followed by `2.0` could be ordered incorrectly by lexical string comparison.

Remediation changed ordering to dotted numeric version tuples and made non-comparable versions explicit rather than permissive.

### HARDEN-009 — Distributed Failure & Split-Brain Authority

Purpose: model distributed execution-authority fencing, stale-replica promotion, split-brain conflict handling, failover and pre-consequence re-establishment.

Preserved hostile findings included node substitution, lease substitution, impossible negative replica age and authority-epoch substitution at pre-consequence check.

The resulting bounded model uses monotonic authority epoch and lease identity, while requiring state/policy position and freshness to remain coherent.

It is a **reference-model distributed authority semantic**, not proof of production consensus, linearizability, quorum fencing, real network partitions or cloud-region isolation.

---

## 5. Whole-stack hostile review

Component-level PASS was deliberately not treated as system-level proof.

The whole-stack review attacked the composition after HARDEN-001 through HARDEN-009 had individually accumulated green evidence. Early whole-stack attacks demonstrated that individually functioning controls could still be bypassed when their results were not decisive at the final execution boundary.

The review therefore proceeded failure-first: freeze hostile condition, execute, preserve failure, remediate, rerun the full accumulated regression, and retain the original failure.

By closure at Pass 32, the accumulated suite constrained at least:

- no lower-layer positive result overriding adverse upstream authority state;
- recovery and evidence-contract status being decisive in composition;
- cross-layer deployment/subject/product/consequence identity coherence;
- composition-evidence integrity, producer identity and freshness;
- authority epoch, lease, policy, rules, ControlContract and deployment-profile version binding;
- Protected Clinical Bind integrity and single-use replay semantics across process/restart/reference-store boundaries;
- operational replay-store rollback/replacement inside the modelled failure domain;
- break-glass integrity, replay, temporal and semantic admission;
- trusted execution-time type semantics;
- exact-commit policy/rules coherence on ordinary and break-glass paths;
- positive exact-integer fence/version semantics;
- meaningful lease identity;
- deployment-profile structural semantics;
- malformed integrity-reference handling;
- exact boolean integrity semantics;
- protected-bind semantic identity;
- closed supported consequence/bind profiles; and
- closed supported runtime-authority versions.

Final verification run: **34632308295 — PASS**.

---

## 6. What the evidence supports

The following statement is supportable from the current reference-harness record:

> Within the inputs and trust assumptions implemented by the ASVH reference harness, consequence formation is defended against the tested classes of stale, incoherent, replayed, substituted, malformed, structurally meaningless and semantically unsupported authority evidence.

A second supportable statement is:

> Within the ASVH reference-harness boundary, contracted runtime facts are not accepted solely because a value is present in Runtime Context. Source authority, subject/context binding, temporal validity, required provenance and explicit failure semantics are evaluated against a versioned ControlContract.

And:

> Within the ASVH reference-harness boundary, authority determination, protected execution authority and consequence evidence are represented as separate propositions rather than being inferred from one another.

These statements must remain coupled to the phrase **within the declared reference-harness boundary**.

---

## 7. What the evidence does NOT support

The current evidence does not establish:

- that a real NHS Trust has deployed this architecture;
- that a real ambient-scribing supplier exposes the required evidence;
- that any synthetic reference registry corresponds to the authoritative NHS source for a real deployment;
- that external evidence is factually true;
- that a clinician is competent;
- that an ambient-scribing product is clinically safe or effective;
- regulatory compliance;
- organisational AI readiness;
- production IAM correctness;
- production key custody/rotation or KMS/HSM security;
- formal verification;
- production distributed consensus or linearizable fencing;
- real network/region/AZ isolation;
- real EPR route closure or platform-level non-bypassability;
- production consequence provenance or EPR transaction atomicity;
- external trusted-time integrity;
- production compatibility negotiation across versions; or
- availability/atomicity of a real external durable or monotonic replay/fencing service.

No public, commercial or technical statement should silently convert a reference-model PASS into any of those claims.

---

## 8. Critical unresolved boundary: Authority Receipt provenance

The protected bind carries `authority_receipt_id`, but the whole-stack coordinator is not supplied the originating Authority Receipt or an authoritative receipt registry.

Therefore the current whole-stack boundary cannot independently establish that the referenced receipt:

- was actually issued by the admitted Runtime Authority;
- corresponds to the asserted original determination;
- has not been substituted by an identifier collision or fabricated reference outside the current model; or
- remains admitted under a real external receipt-provenance authority.

This is an explicit residual boundary, not an implicit PASS.

A future real-world integration may need an authoritative receipt registry, signed receipt envelope, or other independently verifiable receipt-provenance mechanism. The appropriate production mechanism is **not demonstrated by the current harness**.

---

## 9. Reconnection to the NHS ambient-scribing objective

The hardening programme should not become the objective in its own right.

The original engineering objective is to determine whether an independent runtime verification point immediately before AI-assisted clinical documentation is committed to an EPR can evaluate whether the conditions required for that specific commit remain satisfied and preserve evidence of why execution was allowed, escalated or refused.

The hardening record strengthens the implementation hypothesis around that execution boundary. It does not by itself establish the NHS-side evidence perimeter.

The next phase must therefore move from **synthetic admissibility** to **real evidence availability**.

For every proposed runtime control, the project should establish:

1. the exact fact required at execution time;
2. why that fact is material to the governed commit;
3. whether it is `SNAPSHOT`, `PRESENT_AT_EXECUTION` or `CONTINUOUS`;
4. the party responsible for the fact;
5. the actual authoritative source in the target deployment;
6. how the source can expose the fact at runtime;
7. subject/product/deployment/version binding;
8. freshness and revocation semantics;
9. conflict/source-substitution semantics;
10. failure outcome (`ALLOW`, `ESCALATE`, `REFUSE` or explicit inability to determine);
11. what provenance can be retained in the Authority Receipt; and
12. whether the evidence can be independently revalidated before consequence formation.

Until these questions are answered for a real supplier/Trust workflow, the corresponding production control remains **NOT DEMONSTRATED**.

---

## 10. Candidate real-world evidence-contract workstream

The existing HARDEN-004 synthetic controls provide useful shapes, not NHS source answers.

Candidate facts for real deployment discovery include, subject to the applicable guidance and local deployment design:

- product/deployment identity and currently admitted version;
- clinician/user identity and role/entitlement where material;
- consultation/encounter/workflow identity;
- reviewed/approved output state where the governed workflow requires it;
- intended-use/workflow-context state;
- monitoring or operational state where it is a declared execution condition;
- escalation-path availability where an ESCALATE outcome requires a reachable authority path;
- target commit-path identity and availability; and
- current policy/rules/profile basis used by the execution boundary.

These are **candidate evidence-discovery questions**, not assertions that NHS guidance mandates FlowSignal fields or that a particular NHS system is authoritative for them.

---

## 11. Proposed next verification phase

### Phase A — Evidence perimeter discovery

Select one real ambient-scribing workflow and identify the supplier, Trust/EPR boundary, exact governed commit and systems that can authoritatively expose each required runtime fact.

Output: a deployment-specific Evidence Source Register and draft ControlContracts.

### Phase B — Adapter / evidence ingestion

Build read-only adapters for the agreed authoritative evidence sources. Preserve provenance and avoid allowing the proposing AI system to self-attest decisive external authority state.

Output: evidence fixtures captured from real interfaces or formally supplied schemas, with synthetic/test environments clearly distinguished from production evidence.

### Phase C — Shadow runtime determination

Run Runtime Authority immediately before the target commit in non-enforcing/shadow mode. Compare available evidence with the ControlContracts and classify each decision as ALLOW, ESCALATE, REFUSE or unable-to-determine under the declared rules.

Output: Authority Receipts and discrepancy register without claiming that execution was actually prevented.

### Phase D — Protected execution pilot

Only after the evidence perimeter is demonstrated should the project test whether the target execution route can be technically bound to a positive current authority result and whether alternate routes remain outside or inside the protected perimeter.

Output: deployment-specific enforcement evidence and explicit bypass inventory.

### Phase E — Consequence reconciliation

Test whether the real target system can provide authoritative evidence that the exact governed commit formed, was prevented, or remains indeterminate.

Output: deployment-specific Consequence Evidence model.

---

## 12. Red-team attack against this consolidated record

Before this record is treated as an external-facing technical evidence pack, the following attacks were applied to the **claims**, not just the code.

### RT-DOC-01 — “32 hostile passes proves production safety”

**Attack:** infer production safety/security from the size of the hostile suite.  
**Result:** REJECTED. Test count is not a production assurance level. The claim remains bounded to tested reference-harness properties.

### RT-DOC-02 — “Route closure proves EPR non-bypassability”

**Attack:** convert HARDEN-005 route/profile enforcement into a claim that a real supplier cannot bypass FlowSignal.  
**Result:** REJECTED. Real EPR/supplier alternate-route closure is not demonstrated.

### RT-DOC-03 — “Evidence Contract proves the fact is true”

**Attack:** treat source-admissibility validation as objective truth.  
**Result:** REJECTED. HARDEN-004 explicitly evaluates admissibility under contract, not real-world truth.

### RT-DOC-04 — “Authority Receipt proves the note was written”

**Attack:** use an Authority Receipt as consequence evidence.  
**Result:** REJECTED. HARDEN-003 explicitly separates receipt and consequence evidence.

### RT-DOC-05 — “Reference anchor proves independent external anchoring”

**Attack:** market the secondary SQLite/reference anchor as an independent production trust anchor.  
**Result:** REJECTED. It is a reference model only.

### RT-DOC-06 — “Distributed tests prove consensus/failover safety”

**Attack:** elevate HARDEN-009 into a production distributed-systems claim.  
**Result:** REJECTED. No production consensus, linearizability, quorum or network-partition proof exists.

### RT-DOC-07 — “Synthetic registry is the NHS authoritative source”

**Attack:** map `DEPLOYMENT_REGISTRY` or `TRAINING_REGISTRY` directly to an NHS source without deployment evidence.  
**Result:** REJECTED. Actual authoritative sources remain a deployment-discovery question.

### RT-DOC-08 — “Green final run erases historical failures”

**Attack:** present only the final PASS.  
**Result:** REJECTED. Preserved failures are part of the evidence chain and materially explain what the final controls now mean.

### RT-DOC-09 — “Receipt ID proves receipt provenance”

**Attack:** treat `authority_receipt_id` as independent proof that an admitted receipt exists.  
**Result:** REJECTED. Receipt provenance is an explicit unresolved boundary.

### RT-DOC-10 — “The hardening programme proves the original NHS guidance mapping”

**Attack:** infer that because the implementation is hardened, every runtime control is directly mandated by NHS guidance.  
**Result:** REJECTED. The hardening record tests FlowSignal’s technical implementation hypothesis. Guidance-to-control traceability must remain separately sourced and versioned.

**Document red-team conclusion:** the consolidated evidence remains defensible only if the reference-harness qualifier, synthetic-source qualifier, consequence/receipt separation, real-EPR non-bypassability limitation and receipt-provenance gap remain prominent. Removing any of those materially overstates the evidence.

---

## 13. Admission gate for a real NHS/supplier pilot

A proposed pilot should not be represented as execution-authority verification until the following minimum facts are resolved:

| Gate | Required evidence | Current consolidated status |
|---|---|---|
| Exact governed consequence | Exact EPR commit/action and material fields identified | Reference model demonstrated; deployment-specific instance required |
| Authoritative evidence sources | Named source and responsible party for every decisive runtime fact | NOT DEMONSTRATED for a real deployment |
| Runtime accessibility | Evidence available at the pre-commit decision point | NOT DEMONSTRATED for a real deployment |
| Freshness/revocation | Explicit temporal semantics for decisive evidence | Contract model demonstrated; real values required |
| Receipt provenance | Originating determination independently verifiable | NOT DEMONSTRATED at whole-stack boundary |
| Protected route | Target commit path technically conditioned on current authority | Reference model demonstrated; real route closure NOT DEMONSTRATED |
| Alternate-route inventory | Known paths capable of forming same consequence | NOT DEMONSTRATED for a real deployment |
| Consequence evidence | Target can establish FORMED/PREVENTED/INDETERMINATE | Simulator demonstrated; real EPR evidence NOT DEMONSTRATED |
| External anchoring/fencing | Required if production claim depends on rollback/failover resistance | NOT DEMONSTRATED by current harness |

---

## 14. Current stopping determination

The local ASVH hostile-review sequence is closed at Pass 32 for the present claim surface.

Further local hostile passes should not be opened merely to increase test count. A new pass is justified when one of the following materially changes:

- the composition contract;
- an external trust anchor or receipt registry is introduced;
- durable/replay stores change;
- a real EPR/supplier topology is integrated;
- a new authoritative evidence source is admitted;
- the policy/rule/version compatibility contract changes; or
- the public/technical claim surface expands.

The next high-value work is **deployment evidence discovery**, not another synthetic attack.

---

## 15. Proposed bounded external summary

> FlowSignal has built and hostile-tested a reference implementation of an independent runtime verification point for AI-assisted clinical documentation. Within the declared reference-harness boundary, the implementation separates authority determination from protected execution and consequence evidence, binds authority to an exact clinical consequence, re-establishes selected current conditions before consequence formation, applies versioned evidence contracts, and preserves failure-first verification evidence. The accumulated HARDEN-001 through HARDEN-009 and whole-stack hostile review closed at Pass 32 with the final regression suite green. This does not establish NHS deployment, clinical safety, regulatory compliance, production non-bypassability or the truth of external evidence. The next verification step is to establish, with a real supplier/Trust workflow, which authoritative runtime evidence can actually be exposed and independently revalidated immediately before EPR commit.

---

## 16. Red-team questions for independent review

An independent reviewer should try to falsify this record by answering:

1. Where does the document imply a production property from a reference-model test?
2. Which asserted control lacks a traceable evidence source or preserved failure record?
3. Which whole-stack positive outcome can still be assembled from individually valid but mutually incoherent evidence?
4. Can a receipt identifier be substituted without independent receipt provenance?
5. Can the same real EPR consequence be formed through a route outside the declared protected route?
6. Which runtime facts are currently supplied by synthetic sources that would be unavailable or non-authoritative in a real Trust?
7. Can an external state change after the final check but before consequence formation without detection?
8. Which fail-safe result is operationally indistinguishable from an outage and therefore needs an explicit escalation/service design?
9. Does any claim depend on trusted time, durable monotonic state, signing authority or identity infrastructure that the harness only models locally?
10. Can the original NHS guidance-to-runtime-control traceability be independently reconstructed without relying on FlowSignal’s interpretation?

Any material failure against those questions should be preserved and should reopen the relevant evidence boundary rather than being explained away.
