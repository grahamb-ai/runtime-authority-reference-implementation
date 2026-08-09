\# FlowSignal Runtime Authority — Reference Implementation



An inspectable reference implementation of deterministic runtime authority evaluation immediately before execution.



FlowSignal evaluates whether a proposed action remains permissible under the authority and admissibility conditions represented by the active policy-derived rule set.



The reference implementation produces one of three determinations:



\- \*\*ALLOW\*\* — authority and applicable admissibility checks pass.

\- \*\*ESCALATE\*\* — authority passes, but one or more applicable admissibility checks fail.

\- \*\*REFUSE\*\* — authority fails, or no policy rules apply to the proposed action.



> \\\*\\\*Status:\\\*\\\* Reference implementation / technical demonstrator.  

> This repository is not a production deployment.



\---



\## 1. What This Repository Is



This repository contains the reference implementation used to demonstrate the FlowSignal Runtime Authority model.



It provides inspectable code for the following execution path:



```text

Policy Document

\&#x20;     ↓

Document Parsing

\&#x20;     ↓

Deterministic Rule Extraction

\&#x20;     ↓

Active Runtime Rule Set

\&#x20;     ↓

Proposed Action

\&#x20;     ↓

Authority Evaluation

\&#x20;     ↓

Admissibility Evaluation

\&#x20;     ↓

ALLOW / ESCALATE / REFUSE

\&#x20;     ↓

Finalised Decision Record

```



The purpose of the implementation is to make the architectural proposition executable, inspectable and testable.



It is intentionally bounded.



It does not attempt to provide a production-ready policy platform, identity infrastructure, cryptographic evidence system, enterprise policy discovery service or general-purpose natural-language policy interpreter.



\---



\## 2. What It Demonstrates



The current implementation demonstrates:



\- ingestion of supported policy documents;

\- deterministic extraction of a constrained catalogue of policy rules;

\- preservation of source-document and source-excerpt provenance;

\- runtime evaluation of a proposed action;

\- separation of authority and admissibility checks;

\- authority-first evaluation and short-circuit behaviour;

\- deterministic ALLOW / ESCALATE / REFUSE outcomes;

\- default refusal where no policy rules apply to an action;

\- exact monetary-boundary evaluation;

\- evidence-requirement evaluation;

\- optional per-request delegation constraints;

\- persistence of evaluation results;

\- retrieval of previously persisted decision records;

\- dry-run assessment without persistence;

\- automated test coverage of the reference implementation;

\- a lightweight browser console for exercising the real backend.



\---



\## 3. What It Does Not Claim



This repository does \*\*not\*\* demonstrate or claim:



\- production readiness;

\- high availability;

\- production-scale performance;

\- large-scale concurrency;

\- multi-tenant isolation;

\- enterprise authentication or authorisation;

\- cryptographic signing of decision records;

\- cryptographic tamper evidence;

\- independent verification of submitted evidence;

\- automatic discovery of enterprise policy changes;

\- universal interpretation of arbitrary policy prose;

\- formal verification of the implementation;

\- complete policy coverage detection;

\- deployment within a live regulated environment.



The implementation should therefore be read as a reference implementation of the Runtime Authority execution model, not as a finished enterprise control plane.



\---



\## 4. Core Decision Model



A proposed action is evaluated along two dimensions.



\### Authority



Authority asks:



> \\\*\\\*Does this requester have the right to perform this action?\\\*\\\*



Current authority checks include:



\- whether the requester's role is authorised for the action;

\- whether an explicitly supplied delegation has expired.



A failed authority check produces:



```text

REFUSE

```



Authority is evaluated first.



If authority fails, admissibility is not evaluated.



\### Admissibility



Admissibility asks:



> \\\*\\\*Should this specific action proceed under the applicable runtime constraints?\\\*\\\*



Current admissibility checks include:



\- whether the amount is within the applicable ceiling;

\- whether evidence required at the relevant amount threshold is present.



Where authority remains valid but an applicable admissibility condition fails, the result is:



```text

ESCALATE

```



If authority and all applicable admissibility checks pass:



```text

ALLOW

```



The evaluation sequence is therefore:



```text

No applicable policy rules

\&#x20;       ↓

\&#x20;     REFUSE



Applicable policy rules

\&#x20;       ↓

Authority checks

\&#x20;  ↙          ↘

\&#x20;FAIL         PASS

\&#x20; ↓             ↓

REFUSE     Admissibility

\&#x20;            ↙       ↘

\&#x20;          FAIL      PASS

\&#x20;           ↓          ↓

\&#x20;       ESCALATE      ALLOW

```



\---



\## 5. Authority and Monetary Ceilings



A monetary ceiling describes part of an actor's mandate, but evaluation of a specific transaction amount occurs in the admissibility phase.



For example:



```text

regional\\\_manager ceiling = 100,000 EUR

```



A request for:



```text

100,000 EUR

```



can pass the ceiling check.



A request for:



```text

100,001 EUR

```



fails that admissibility check and produces an ESCALATE rather than automatically treating the actor as fundamentally unauthorised.



This models exceeding a delegated ceiling as a recoverable condition requiring higher authority.



\---



\## 6. Policy Ingestion and Provenance



Policy documents are uploaded through:



```text

POST /api/v1/specs/upload

```



Supported file extensions are:



```text

.pdf

.docx

.txt

```



The parser extracts text from the supplied document and passes it to a deterministic rule extractor.



The current implementation uses:



\- `pdfplumber` for PDF text extraction;

\- `python-docx` for DOCX paragraph extraction;

\- UTF-8 text reading for TXT files.



Image-only/scanned PDFs are not OCR'd by this reference implementation.



Unsupported file extensions are rejected.



\### Deterministic extraction



The extractor is deliberately \*\*not an LLM\*\*.



It uses a defined catalogue of regular-expression patterns.



Sentences that do not match a recognised pattern are ignored rather than interpreted probabilistically.



Each extracted rule can retain:



```text

source\\\_document

source\\\_excerpt

```



allowing a runtime check to be traced back to the supplied policy wording from which its rule was extracted.



\---



\## 7. Supported Policy Grammar



The current extractor recognises a constrained set of sentence patterns.



It does \*\*not\*\* claim to understand arbitrary institutional policy prose.



\### Authority



\*\*A1 — authorised roles\*\*



```text

Authorized roles for <action>: <role>, <role>, ...

```



Example:



```text

Authorized roles for payment.release: regional\\\_manager, finance\\\_director, cfo.

```



\*\*A2 — role-specific monetary ceiling\*\*



```text

The <role> may approve <action> up to <amount>.

```



or equivalent supported phrasing such as:



```text

The <role> is authorized to release <action> up to <amount>.

```



Example:



```text

The regional\\\_manager may approve payment.release up to 100,000 EUR.

```



\### Admissibility



\*\*B1 — threshold-based evidence requirement\*\*



Example:



```text

Any payment.release above 50,000 EUR must be accompanied by invoice and purchase\\\_order.

```



\*\*B2 — unconditional evidence requirement\*\*



Example pattern:



```text

<action> requires <document>, <document>.

```



Unrecognised sentences do not automatically become executable rules.



\---



\## 8. Policy Replacement Semantics



The current reference implementation models \*\*one active extracted rule set at a time\*\*.



Uploading a policy through:



```text

POST /api/v1/specs/upload

```



replaces the currently persisted rule set rather than appending the new rules to it.



This makes it possible to demonstrate that the same proposed action can receive a different runtime determination after the active policy changes.



It should not be interpreted as a production policy-versioning architecture.



\---



\## 9. Policy Coverage Boundary



The implementation contains a coverage guard.



If \*\*no policy rule applies to the proposed action\*\*, the evaluator fails closed:



```text

REFUSE

```



with an invalid authority state.



However, this behaviour has an important boundary.



The current reference implementation evaluates the constraint types explicitly represented by the active rule set. It does not require every possible authority or admissibility constraint category to exist for every action that has some policy coverage.



For example, the presence of policy coverage for an action does not by itself require that an `authorized\\\_role`, `max\\\_amount` and `required\\\_evidence` rule all exist.



This is an explicit boundary of the current reference implementation and should not be interpreted as proof of policy completeness.



\---



\## 10. Per-Request Delegation



The request model can optionally contain delegation constraints, including:



```text

delegation\\\_max\\\_amount

delegation\\\_expires\\\_at

```



An explicit per-request monetary delegation can tighten an applicable policy ceiling.



It cannot increase an existing policy ceiling.



An expired supplied delegation causes the authority check to fail.



This reference implementation does not provide a production institutional delegation registry.



\---



\## 11. Decision Records



`POST /api/v1/orders/evaluate` evaluates the request and persists the resulting decision record.



The record contains information including:



\- decision;

\- authority state;

\- reason;

\- required action where applicable;

\- execution target;

\- checks performed;

\- runtime context snapshot;

\- policy source documents;

\- policy source excerpts associated with checks;

\- decision timestamp.



The API currently retains the field:



```text

sealed\\\_at

```



\### Meaning of `sealed\\\_at`



`sealed\\\_at` is retained as part of the current implementation's API and evidence format.



In this reference implementation, it records when the decision was finalised.



It does \*\*not\*\* mean that the decision record is:



\- cryptographically signed;

\- cryptographically sealed;

\- independently notarised;

\- cryptographically tamper-evident.



Cryptographic receipt integrity is outside the implemented scope of this release.



\---



\## 12. API



All primary endpoints are under:



```text

/api/v1

```



| Method | Endpoint | Purpose |

|---|---|---|

| `POST` | `/specs/upload` | Upload a supported policy document and replace the active extracted rule set |

| `POST` | `/orders/evaluate` | Evaluate an action, persist the decision record and return it |

| `POST` | `/orders/assess` | Evaluate using the same decision logic without persisting the resulting record |

| `GET` | `/orders/{id}` | Retrieve a previously persisted decision record |

| `GET` | `/health` | Service liveness check |



\---



\## 13. Project Structure



```text

runtime-authority-reference-implementation/

│

├── main.py

│

├── app/

│   ├── enums.py

│   ├── config.py

│   ├── database.py

│   │

│   ├── engines/

│   │   ├── types.py

│   │   ├── parser.py

│   │   ├── extractor.py

│   │   ├── authority.py

│   │   ├── admissibility.py

│   │   └── evaluator.py

│   │

│   ├── models/

│   │   ├── rule.py

│   │   ├── order.py

│   │   └── schemas.py

│   │

│   └── routers/

│       ├── specs.py

│       └── orders.py

│

├── tests/

├── alembic/

├── demo-ui/

│   ├── index.html

│   └── styles.css

│

├── alembic.ini

├── requirements.txt

├── pyproject.toml

├── .env.example

└── README.md

```



\### Engine isolation



The core engine layer uses standard-library dataclasses and is deliberately separated from:



\- FastAPI;

\- Pydantic;

\- SQLModel;

\- HTTP transport;

\- database persistence.



Conceptually:



```text

HTTP request

\&#x20;    ↓

AuthorityEnvelope

\&#x20;    ↓

OrderData

\&#x20;    ↓

Evaluator

\&#x20;    ↓

BindRecordData

\&#x20;    ↓

Persistence / HTTP response

```



This allows the core decision logic to be tested independently of the web server and database.



\---



\## 14. Running Locally



\### Requirements



A Python environment and PostgreSQL instance are required for the normal local configuration.



A local PostgreSQL database can, for example, be started with Docker:



```bash

docker run --name authority-pg \\\\

\&#x20; -e POSTGRES\\\_PASSWORD=postgres \\\\

\&#x20; -e POSTGRES\\\_DB=authority\\\_poc \\\\

\&#x20; -p 5432:5432 \\\\

\&#x20; -d postgres:16

```



The password shown above is a local development example only.



\### Install dependencies



```bash

python -m venv venv

```



Linux/macOS:



```bash

source venv/bin/activate

```



Windows:



```text

venv\\\\Scripts\\\\activate

```



Then:



```bash

pip install -r requirements.txt

```



Create the local environment configuration from:



```text

.env.example

```



Do not commit the resulting `.env` file.



\---



\## 15. Database Schema



Schema evolution is managed using Alembic migrations under:



```text

alembic/versions/

```



For a new database:



```bash

alembic upgrade head

```



The application also calls `create\\\_tables()` during startup for local reference-implementation convenience.



This is not intended as the migration strategy for a production deployment.



\---



\## 16. Run the API



Start the application with:



```bash

fastapi dev main.py

```



The local Swagger interface is then available at:



```text

http://localhost:8000/docs

```



The liveness endpoint is:



```text

http://localhost:8000/health

```



\---



\## 17. Example Evaluation



First upload the bundled sample policy:



```bash

curl -X POST http://localhost:8000/api/v1/specs/upload \\\\

\&#x20; -F "file=@tests/fixtures/sample-policy.txt"

```



Then evaluate an action:



```bash

curl -X POST http://localhost:8000/api/v1/orders/evaluate \\\\

\&#x20; -H "Content-Type: application/json" \\\\

\&#x20; -d '{

\&#x20;   "action": "payment.release",

\&#x20;   "target": "SAP\\\_PAYMENT\\\_RELEASE",

\&#x20;   "requester": {

\&#x20;     "id": "user-42",

\&#x20;     "role": "regional\\\_manager"

\&#x20;   },

\&#x20;   "context": {

\&#x20;     "amount": 250000,

\&#x20;     "currency": "EUR"

\&#x20;   },

\&#x20;   "evidence": \\\[

\&#x20;     "invoice",

\&#x20;     "purchase\\\_order"

\&#x20;   ]

\&#x20; }'

```



Under the bundled reference policy, a regional manager's applicable ceiling is lower than this amount.



Where authority remains valid but the amount exceeds that ceiling, the expected determination is:



```text

ESCALATE

```



with a required action explaining the need for higher approval.



\---



\## 18. Dry-Run Assessment



The endpoint:



```text

POST /api/v1/orders/assess

```



uses the same evaluation logic as `/evaluate` but does not persist the resulting decision record.



This allows callers to inspect the determination without creating a persisted record.



\---



\## 19. Demonstration Console



A lightweight React-based demonstration console is included under:



```text

demo-ui/

```



It provides a browser interface for:



1\. binding a supported policy;

2\. composing a proposed action;

3\. submitting the action to the FastAPI backend;

4\. viewing the ALLOW / ESCALATE / REFUSE determination;

5\. inspecting the resulting decision record.



There is \*\*no separate in-browser decision engine\*\*.



Policy ingestion and runtime evaluation are performed by the FastAPI backend.



The demonstration UI is not a production frontend.



\---



\## 20. Tests



The repository contains automated tests covering the reference implementation, including:



\- extractor behaviour;

\- evaluator behaviour;

\- API behaviour;

\- decision coverage;

\- extraction coverage;

\- boundary conditions;

\- policy coverage behaviour;

\- persistence-related behaviour.



Run:



```bash

pytest

```


A complete local verification run of the current publication candidate produced:



```text

52 passed, 1 warning

```



The warning is a dependency deprecation warning and does not represent a test failure.



This result represents the automated test suite included in this repository. It should not be interpreted as formal verification, production certification, or proof of correctness beyond the tested behaviours.
```

Linting can be run with:



```bash

ruff check .

```



The public verification repository contains captured test and runtime evidence from the implementation.



A passing captured test run should not be interpreted as formal verification or proof of production correctness.



\---



\## 21. Verification Evidence



The companion **FlowSignal Runtime Authority Evidence** repository is published at:

https://github.com/grahamb-ai/runtime-authority-evidence

It contains captured artefacts demonstrating selected behaviours of this reference implementation.

The evidence set identifies implementation revision:

`ea36ac1`

as the source revision reviewed alongside the captured evidence.



The evidence includes examples of:



\- ALLOW;

\- ESCALATE;

\- REFUSE;

\- repeated equivalent evaluations;

\- exact monetary boundaries;

\- unknown-action refusal;

\- policy-change behaviour;

\- malformed-request handling;

\- unsupported-file handling;

\- automated test execution;

\- direct persistence inspection;

\- policy provenance.



The intended relationship is:



```text

Architecture / proposition

\&#x20;         ↓

Reference implementation

\&#x20;         ↓

Automated tests

\&#x20;         ↓

Captured verification evidence

```



Once a public release of this repository is frozen, the evidence repository should identify the exact source commit used to generate the corresponding evidence release.



\---



\## 22. Current Implementation Boundaries



The current implementation intentionally makes several simplifying assumptions.



\### Policy interpretation



Only the documented deterministic sentence patterns are recognised.



Arbitrary natural-language policy interpretation is not implemented.



\### Policy completeness



The engine evaluates constraints represented by the active extracted rule set.



It does not currently establish that the supplied policy is complete for every possible institutional authority or admissibility dimension.



\### Source authority



`source\\\_document` and `source\\\_excerpt` provide traceability to the supplied policy artefact.



The implementation does not independently prove that the supplied document:



\- is institutionally authoritative;

\- is the current approved version;

\- has not been superseded;

\- was issued by an authorised policy owner;

\- has cryptographic integrity.



\### Evidence



Evidence is currently represented by request-supplied evidence identifiers.



The implementation does not independently establish the authenticity, integrity or freshness of the underlying evidence artefacts.



\### Security



The reference implementation is configured for local demonstration and development.



For example, CORS is intentionally permissive for the local demonstration console.



Production authentication, authorisation, secrets management, network controls and deployment hardening are outside this release.



\---



\## 23. Design Principle



The implementation separates the proposed action from the authority determination made about that action.



The application or agent proposes an action.



The Runtime Authority evaluates the action against the currently represented authority and admissibility conditions.



The resulting determination is:



```text

ALLOW

ESCALATE

REFUSE

```



The reference implementation therefore demonstrates a distinct pre-execution decision boundary rather than embedding the authority determination inside the requesting agent or workflow.



\---



\## 24. Repository Status



This repository should be treated as a bounded, inspectable reference implementation.



Future capabilities may include richer policy sources, stronger policy provenance, external evidence verification, cryptographic decision-record integrity, enterprise identity integration and broader runtime context.



Those capabilities should not be inferred from the current implementation until they are implemented and evidenced.



\---



\## FlowSignal



\*\*Execute with Authority. Defend with Evidence.\*\*

