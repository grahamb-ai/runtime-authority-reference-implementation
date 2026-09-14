# ASVH Consolidated Evidence & Verification Record

**Status:** DRAFT — RED-TEAM CORRECTIONS APPLIED / NOT YET FROZEN  
**Purpose:** consolidate the current ASVH reference-harness evidence into one bounded, auditable record without upgrading any claim beyond the underlying evidence.  
**Source engineering branch:** `asvh-whole-stack-hostile-review`  
**Consolidation branch:** `asvh-consolidated-evidence-redteam`  
**Final whole-stack verification run:** `34632308295`

---

## 1. Executive determination

The ASVH reference harness has reached a defensible stopping point for its present local claim surface.

Within the declared reference-harness inputs and trust assumptions, the implementation remained consistent with its declared tested invariants after the accumulated hostile conditions represented by HARDEN-001 through HARDEN-009 and the whole-stack hostile review through Pass 32. The final verification run `34632308295` completed successfully across that accumulated suite.

The evidence supports a bounded pre-consequence authority model covering exact clinical consequence binding, present-standing continuity, separation of determination from execution and consequence evidence, evidence-contract semantics, deployment/profile enforcement inside the modelled boundary, recovery/high-watermark behaviour, policy transition, replay/fencing semantics and hostile whole-stack composition.

This evidence does **not** establish production NHS safety, a production security certification, real EPR non-bypassability, external truth of supplied evidence, production IAM/key custody, production distributed consensus, organisational independence, or production-grade external anchoring.

The local engineering question is therefore substantially closed. The next programme must answer two separate real-world questions:

1. **Determination Viability:** can a real ambient-scribing deployment expose authoritative, current, appropriately bound evidence at the pre-commit boundary so that the required runtime determination can be made?
2. **Enforcement Viability:** if such a determination can be made, can the real governed EPR consequence be conditioned on that current authority result without an equivalent execution route around it?

Success on Determination Viability does not imply success on Enforcement Viability.

---

## 2. Four propositions that must remain separate

The ASVH evidence model separates four propositions:

1. **Authority determination** — whether the admitted evidence supports `ALLOW`, `ESCALATE` or `REFUSE` for the exact governed action.
2. **Protected execution authority** — whether an execution attempt remains entitled to rely on that determination for the exact consequence now attempted.
3. **Consequence formation** — whether the governed target consequence actually became `FORMED`, was `PREVENTED`, or remains `INDETERMINATE`.
4. **Evidence provenance** — what evidence was relied upon and whether it was admissible under the applicable versioned ControlContract.

A positive result in one proposition does not prove the others. An Authority Receipt is determination evidence, not bearer execution authority. Executor success is not independently established consequence evidence. Timeout is not proof of prevention. Presence of a Runtime Context value does not make that value authoritative. Integrity-valid content may still be semantically inadmissible.

---

## 3. Declared reference execution boundary

The hardened reference path is conceptually:

`Declared evidence sources -> Evidence Contract evaluation -> Runtime Authority determination -> Authority Receipt -> exact-consequence Protected Clinical Bind -> present-standing / policy / recovery / fencing re-establishment -> protected execution route -> target consequence -> consequence reconciliation/evidence`

A previous `ALLOW` is insufficient by itself. Outstanding authority remains conditional on exact consequence identity, current standing, applicable policy/rules, deployment profile, replay state and the other controls declared by the composition contract.

---

## 4. NHS guidance-to-runtime engineering lineage

ASVH-TRACE-001 v1.0 is the engineering traceability source for the original ambient-scribing rule set. Its declared traceability chain is:

`NHS Guidance -> Runtime Context -> Runtime Rule -> Authority Receipt -> Verification Scenario`

It classifies runtime artefacts as **Direct**, **Contextual** or **Derived**. The consolidated evidence record imports that engineering lineage; it does **not** independently reinterpret NHS England guidance or claim that the later hardening controls themselves are directly mandated by NHS guidance.

| Runtime Rule | Primary Runtime Context | TRACE classification | Original verification scenarios | Relationship to later hardening |
|---|---|---|---|---|
| RA-AS-001 Target Commit Path Available | RC-006 Target Commit Path Available | Direct | AS-001, AS-004 | Later route/profile and protected-execution work tests how a declared commit path can be bound and defended inside the reference harness. |
| RA-AS-002 Output Reviewed | RC-003 Output Reviewed | Direct | AS-001, AS-002 | Later evidence-contract work tests whether the asserted state is admissible evidence; it does not assess review quality. |
| RA-AS-003 Output Approved | RC-004 Output Approved | Direct | AS-001, AS-003 | Later evidence/binding work does not convert approval into clinical correctness or prove the authority of a real-world approver. |
| RA-AS-004 Execution Type Identified | RC-008 Execution Type | Derived | AS-001, AS-007 | Exact-consequence and schema/profile hardening constrain how an execution request is represented and bound. |
| RA-AS-005 Intended Use Maintained | RC-005 Intended Use | Direct | AS-001, AS-005 | Evidence-contract and policy-transition work constrain source, context and version semantics for this class of fact. |
| RA-AS-006 Operational Context Valid | RC-009 Operational Context | Contextual | AS-001, AS-008 | Present-standing, recovery, policy and distributed-fencing hardening test changing operational state in the reference model. |
| RA-AS-007 Workflow Context Valid | RC-007 Workflow Context | Contextual | AS-001, AS-006 | Present-standing and cross-layer coherence tests constrain stale or substituted workflow/context state. |

ASVH-TRACE-001 also lists RC-001 Consultation Active, RC-002 Clinician Authenticated and RC-010 Approved Product Status as contextual Runtime Context elements. Their presence in the engineering catalogue does not establish the authoritative NHS source for those facts in any real deployment.

**Traceability boundary:** this consolidated record relies on the versioned ASVH traceability publication for the guidance-to-rule engineering mapping. It does not reproduce or independently revalidate every underlying NHS source passage. Passage-level source provenance must remain versioned in ASVH-METH-001 / ASVH-TRACE-001 and must be rechecked if the applicable guidance changes.

---

## 5. Hardening evidence chain

### HARDEN-001 — Exact Clinical Commit & Protected Execution Bind

The original frozen suite passed, but hostile review preserved a critical finding: a fabricated persisted Protected Clinical Bind with a forged receipt identifier and matching exact-commit binding could reach `EXECUTED`. That finding established that structural validity and exact-action binding did not prove bind provenance. Later remediation and whole-stack review added integrity, single-use, semantic identity and declared profile/version constraints.

### HARDEN-002 — Present Standing / Authority Continuity

The reference harness classifies controls as `SNAPSHOT`, `PRESENT_AT_EXECUTION` or `CONTINUOUS`. Present/continuous conditions are re-established around execution and immediately before consequence formation. Reference high-watermark semantics prevent older accepted state from silently restoring authority inside the declared boundary.

### HARDEN-003 — Consequence Evidence & Reconciliation

The harness separates `FORMED`, `PREVENTED` and `INDETERMINATE`. Lost acknowledgement or timeout is not mapped directly to prevention. Stable consequence identity supports reconciliation and duplicate-retry control inside the target simulator boundary.

### HARDEN-004 — Evidence Contracts & Authoritative Source Semantics

The harness evaluates whether a runtime fact is admissible under a versioned ControlContract; it does not establish that the underlying real-world assertion is objectively true. Evidence states include `VALID`, `ABSENT`, `STALE`, `INVALID`, `CONTRADICTORY`, `UNVERIFIABLE` and `REVOKED`. Synthetic `DEPLOYMENT_REGISTRY` and `TRAINING_REGISTRY` sources are reference controls only and are not asserted to be NHS authoritative sources.

### HARDEN-005 — Deployment Boundary & Route Closure

Hostile review preserved route-set substitution, profile identity substitution, ControlContract authority expansion and break-glass weaknesses before remediation. The resulting claim is bounded to exact active deployment-profile and declared-route enforcement inside the reference harness. Real EPR alternate-route closure remains NOT DEMONSTRATED.

### HARDEN-006 — Recovery / Reference Independence Semantics

Hostile review preserved high-watermark read failure, local recovery-store replacement, unsupported independence-level and counter-type failures. The remediation introduced a secondary reference persistence anchor. That anchor models stronger recovery separation inside the harness; it is not evidence of production infrastructure, organisational or cryptographic independence.

### HARDEN-007 — Evidence Pack Integrity & Reproducibility — STATUS RECONCILED

The earlier HARDEN-007 specification was labelled `FROZEN DESIGN — IMPLEMENTATION PENDING`. That historical status is superseded by the later remediation/verification record and must not be read as the current state.

Preserved first executable run `34610483182` contained a HARDEN-007 conformance failure caused by the H7-019 test fixture raising `FileNotFoundError`. It was classified as a **test-harness / fixture failure**, not evidence that the manifest algorithm had passed. The failure remains part of the record.

Remediation commit: `c8a9a9f1ebdf59332eced8a195c9feaf3355280a`.

Re-verification run `34610838030` passed HARDEN-001 through HARDEN-006 regressions, frozen H7-001 through H7-020, and the HARDEN-007 hostile review. The hostile review exercised manifest substitution, omission of a failing test from the aggregate root, duplicate-ID shadowing and path escape.

Current bounded status: **VERIFICATION-EVIDENCED WITHIN THE DECLARED REFERENCE-HARNESS BOUNDARY**. The evidence supports deterministic SHA-256 manifest/inventory integrity semantics as implemented. It does not establish external notarisation, external timestamping, hardware-backed signing, KMS/HSM trust, repository-owner independence, archival durability or NHS/supplier evidence-store integration.

### HARDEN-008 — Policy Transition & Outstanding Authority

A preserved hostile failure showed lexical policy-version ordering could mistake `2.0` as later than `10.0`. Remediation moved the bounded reference model to dotted-numeric comparison and explicit indeterminate handling for non-comparable values.

### HARDEN-009 — Distributed Failure & Split-Brain Authority

The reference model exercises authority epoch, lease identity, node coherence and freshness immediately before consequence formation. Preserved hostile failures included node, lease and authority-epoch substitution and impossible negative freshness. This is reference-model distributed-authority semantics, not production consensus, linearizability, quorum fencing or network-partition proof.

---

## 6. Whole-stack hostile review

Component-level PASS was not treated as system-level proof. The whole-stack review repeatedly demonstrated that individually functioning controls could still compose unsafely when an adverse upstream result was not decisive at the final execution boundary.

The review method was failure-first: freeze hostile condition, execute, preserve failure, remediate, rerun the accumulated regression, retain the original failure.

By closure at Pass 32, the accumulated review constrained cross-layer identity/coherence, evidence integrity and freshness, authority epoch/lease/policy/rules/ControlContract/profile binding, protected-bind integrity and replay, break-glass semantics, trusted execution-time semantics, exact-commit policy/rules coherence, type validity, meaningful identities and closed supported schema/profile/runtime-authority versions.

Final code verification run: **34632308295 — PASS** across HARDEN-001 through HARDEN-009 and the accumulated whole-stack hostile review through Pass 32.

---

## 7. Supported claims and explicit non-claims

Supportable bounded statement:

> Within the inputs and trust assumptions implemented by the ASVH reference harness, consequence formation is defended against the tested classes of stale, incoherent, replayed, substituted, malformed, structurally meaningless and semantically unsupported authority evidence.

Also supportable:

> Within the ASVH reference-harness boundary, contracted runtime facts are not accepted solely because a value is present in Runtime Context; source authority, subject/context binding, temporal validity, required provenance and explicit failure semantics are evaluated against a versioned ControlContract.

Also supportable:

> Within the ASVH reference-harness boundary, authority determination, protected execution authority and consequence evidence are represented as separate propositions rather than inferred from one another.

The evidence does **not** establish a real NHS deployment, a real supplier evidence perimeter, objective truth of external evidence, clinician competence, clinical safety/effectiveness, regulatory compliance, production IAM/key custody, formal verification, production distributed consensus, real EPR route closure, production consequence provenance, trusted external time, production compatibility negotiation, or availability/atomicity of a real external durable monotonic fencing service.

---

## 8. Independence classification

The word **independent** must be qualified.

**Demonstrated in the reference harness:** bounded logical/component separation of Runtime Authority behaviour from the action-proposing workflow, deterministic evaluation against declared inputs, and reference controls intended to prevent a caller from simply self-authorising decisive external facts.

**Not demonstrated:** separate organisational control, separate cloud/account ownership, production infrastructure failure-domain independence, external key custody, independent evidence-source operation, independent receipt registry operation or external monotonic anchoring.

A real pilot must declare the independence level it actually implements rather than inherit a stronger independence claim from the reference architecture.

---

## 9. Gate 0 — Authority Receipt provenance: BLOCKING FOR ENFORCEMENT VIABILITY

The whole-stack coordinator currently receives `authority_receipt_id`, but not the originating Authority Receipt or an authoritative receipt registry capable of independently establishing the receipt's origin and admitted content.

Accordingly, the current composition cannot independently prove that a referenced receipt was issued by the admitted Runtime Authority, corresponds to the asserted determination, has not been substituted or fabricated outside the model, or remains valid under a real receipt-provenance authority.

**Gate 0 rule:** no real protected-execution pilot may claim that an exact-consequence Protected Clinical Bind is grounded in an admitted Runtime Authority determination until receipt provenance is independently verifiable at the bind/enforcement boundary.

Possible mechanisms include an authoritative receipt registry, a signed receipt envelope, or another independently verifiable provenance mechanism. The production mechanism is deliberately **not selected or demonstrated** by the current harness.

Failure to satisfy Gate 0 does not invalidate the determination experiment. It blocks progression from Determination Viability to a stronger Enforcement Viability claim.

---

## 10. Experiment 1 — Determination Viability

### Objective

Determine whether one real ambient-scribing workflow can supply the authoritative runtime evidence needed to make the declared pre-commit determination honestly and reproducibly.

### A. Guidance/control admission

For every proposed production runtime control, establish the versioned guidance/organisational basis, classify it as Direct/Contextual/Derived where applicable, identify why the fact is material to the exact governed commit, and record who owns the operational requirement.

### B. Source-authority confirmation

Before building an adapter, identify the responsible party and obtain explicit evidence that the named source is authoritative for the specific fact in that deployment. An API containing a value is not authoritative merely because it is convenient or available.

### C. Deployment-specific ControlContract

Record subject identity, responsible party, permitted authoritative source(s), required fields, product/deployment/version binding, provenance, integrity requirements, conflict/substitution rules, failure semantics and receipt requirements.

Each time-sensitive control must also define its **authority interval**: observation time, maximum age/validity, revalidation trigger and the event that invalidates outstanding authority. This is the deployment-specific answer to the evidence-to-consequence timing / TOCTOU problem.

### D. Read-only evidence ingestion and shadow determination

Use read-only adapters against formally supplied interfaces or deployment test environments, keeping synthetic and real evidence clearly distinguished. Run Runtime Authority at the intended pre-commit point in shadow mode and preserve Authority Receipts/discrepancies without claiming that execution was actually prevented.

### Decisive uncertainty rule

A decisive runtime condition that resolves to `ABSENT`, `STALE`, `INVALID`, `CONTRADICTORY`, `UNVERIFIABLE`, `REVOKED`, or otherwise cannot be established according to its ControlContract **must not silently become an executable ALLOW**. The exact `ESCALATE` or `REFUSE` treatment is contract-specific, but unresolved decisive authority is non-permissive for protected execution.

### Determination Viability exit gate

PASS requires that every decisive fact for the selected workflow has a named authoritative source, proven deployment binding, explicit temporal/failure semantics, runtime accessibility at the required point, and reproducible shadow determinations. Missing facts remain `NOT DEMONSTRATED`; they are not filled by assumption.

---

## 11. Experiment 2 — Enforcement Viability

### Prerequisites

Enforcement Viability cannot begin as a claim-bearing experiment until:

- Determination Viability has passed for the selected workflow; and
- **Gate 0 Authority Receipt provenance has passed**.

### A. Exact governed consequence

Freeze the exact EPR commit/action and its material fields. Recompute the actual attempted material fields at enforcement rather than relying solely on caller-declared values.

### B. Protected route and bypass inventory

Identify every known route capable of forming the same material consequence. Establish which route(s) are conditioned on current authority and explicitly list any routes that remain outside the protected perimeter.

A protected primary route with an equivalent unprotected route is not evidence of non-bypassability.

### C. Present-standing revalidation

Re-establish every `PRESENT_AT_EXECUTION` / `CONTINUOUS` condition required by the deployment contract immediately before consequence formation. A stale earlier ALLOW must not restore authority after material state changes.

### D. Consequence evidence

Determine whether the real target can authoritatively distinguish `FORMED`, `PREVENTED` and `INDETERMINATE` for the stable consequence identity. Timeout or lost acknowledgement must not be treated as prevention without authoritative reconciliation.

### Enforcement Viability exit gate

PASS requires independently verifiable receipt provenance, exact-consequence binding, a documented and tested execution perimeter, explicit residual bypass inventory, current-state revalidation and deployment-specific consequence evidence. Anything less is a narrower partial result, not a production non-bypassability claim.

---

## 12. Real NHS / supplier pilot admission gate

| Gate | Required evidence | Current status |
|---|---|---|
| Guidance lineage admitted | Versioned source/engineering lineage for each proposed runtime control | Engineering traceability exists in ASVH-TRACE-001; deployment-specific revalidation required |
| Exact governed consequence | Exact EPR action and material fields identified | Reference model demonstrated; real deployment NOT DEMONSTRATED |
| Source authority confirmed | Responsible party confirms each decisive source is authoritative for that fact | NOT DEMONSTRATED |
| Runtime accessibility | Decisive evidence available at required pre-commit point | NOT DEMONSTRATED |
| Freshness / authority interval | Freshness, revocation, invalidation and revalidation semantics defined | Contract model demonstrated; real deployment values NOT DEMONSTRATED |
| Independence level declared | Actual logical/infrastructure/organisational separation explicitly stated | Reference logical separation demonstrated; stronger production independence NOT DEMONSTRATED |
| **Gate 0 receipt provenance** | Originating determination independently verifiable at bind/enforcement boundary | **NOT DEMONSTRATED — BLOCKS ENFORCEMENT VIABILITY** |
| Protected route | Target commit technically conditioned on current authority | Reference model demonstrated; real route NOT DEMONSTRATED |
| Alternate-route inventory | Known equivalent consequence-forming routes enumerated/tested | NOT DEMONSTRATED |
| Consequence evidence | Target can establish FORMED/PREVENTED/INDETERMINATE | Simulator demonstrated; real EPR NOT DEMONSTRATED |
| External anchoring/fencing | Required where rollback/failover resistance forms part of production claim | NOT DEMONSTRATED |

A pilot may proceed as an evidence-discovery or shadow-determination exercise before all enforcement gates are green, provided its claim surface is explicitly limited. It must not be represented as protected execution if Gate 0 or route closure remains unresolved.

---

## 13. Red-team disposition after corrections

The four red-team defects identified in the first consolidated draft have now been addressed in the document:

1. HARDEN-007 status is reconciled against its later remediation and verification evidence rather than left apparently contradictory with its earlier design-only specification.
2. NHS guidance-to-runtime engineering lineage is explicit and separated from later hardening controls; the document does not pretend to have independently revalidated every NHS source passage.
3. Authority Receipt provenance is elevated from a residual footnote to **Gate 0**, blocking stronger Enforcement Viability claims until independently demonstrated.
4. The real-world programme is split into **Determination Viability** and **Enforcement Viability**, with success/failure criteria and no implication that the first proves the second.

The engineering baseline remains GREEN within its declared reference-harness boundary. This consolidated record remains **DRAFT / NOT YET FROZEN** until the remaining document-level red team is accepted and deployment-specific facts begin to replace `NOT DEMONSTRATED` entries.

---

## 14. Stopping determination

The local ASVH hostile-review sequence remains closed at Pass 32 for the current reference-harness claim surface. New local hostile passes should be opened only when the composition contract, receipt-provenance mechanism, external trust anchor, durable store, production integration topology, authoritative evidence source or declared claim surface materially changes.

The next useful falsification work is therefore not additional synthetic test count. It is to determine, against one real ambient-scribing workflow, whether **Determination Viability** exists and, only if that is demonstrated and Gate 0 is satisfied, whether **Enforcement Viability** exists.
