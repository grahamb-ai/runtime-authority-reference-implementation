# ASVH HARDEN-011 — Fourth-Order Boundary Result

Status: RED / BOUNDARY REACHED
Run: 35495242511

Preceding chain remained green:
- HARDEN-010 baseline: 225 passed.
- HARDEN-011 route closure: 10 passed.
- HARDEN-011 second order: 6 passed.
- HARDEN-011 third order: 5 passed.

Fourth-order: 0 passed / 4 failed.

Preserved findings:
1. Correlated rollback of both modeled SQLite rollback domains resurrected consumed authority.
2. Replacement of the modeled executor trust registry allowed a newly trusted secret to use an already-issued capability.
3. Loss/recreation of the modeled consumption anchor did not fail closed for an outstanding capability.
4. The reference API reports COMMITTED after local consumption/local append and has no durable UNRESOLVED vs externally CONFIRMED outcome state.

Interpretation:
These failures identify the limit of what the present self-contained Python reference model can establish. Repairing them by adding another local file/database/registry inside the same modeled trust domain would merely move the assumption and risk manufacturing a green result.

External properties now required for stronger evidence include:
- a genuinely independent rollback-resistant authority/consumption trust anchor;
- independently administered executor identity/key trust with lifecycle/revocation semantics;
- fail-closed behavior when that external trust anchor is unavailable;
- an actual EPR/external consequence protocol that can distinguish consumed authority from confirmed consequence formation and preserve an unresolved recovery state.

Classification: NOT DEMONSTRATED beyond the tested reference-model boundary. The prior 246-green result remains valid for its stated scope.

No remediation is applied to these fourth-order failures in the reference model pending an external integration boundary capable of testing the propositions honestly.
