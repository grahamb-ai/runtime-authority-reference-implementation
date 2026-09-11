from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from .runtime import HarnessClock

VALID = "VALID"
ABSENT = "ABSENT"
STALE = "STALE"
INVALID = "INVALID"
CONTRADICTORY = "CONTRADICTORY"
UNVERIFIABLE = "UNVERIFIABLE"
REVOKED = "REVOKED"


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    control_id: str
    subject: str
    asserted_state: str
    evidence_source: str
    evidence_authority: str
    observed_at: str
    provenance_reference: str | None
    deployment_context: str | None = None
    product_identifier: str | None = None
    product_version: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    max_age_seconds: int | None = None
    integrity_valid: bool = True
    revoked: bool = False


@dataclass(frozen=True)
class ControlContract:
    contract_version: str
    control_id: str
    subject_type: str
    permitted_authoritative_sources: tuple[str, ...]
    required_fields: tuple[str, ...]
    expected_state: str
    on_absent: str
    on_stale: str
    on_invalid: str
    on_contradictory: str
    on_unverifiable: str
    on_revoked: str
    require_integrity: bool = True

    def outcome_for(self, status: str) -> str:
        if status == VALID:
            return "ALLOW"
        return {
            ABSENT: self.on_absent,
            STALE: self.on_stale,
            INVALID: self.on_invalid,
            CONTRADICTORY: self.on_contradictory,
            UNVERIFIABLE: self.on_unverifiable,
            REVOKED: self.on_revoked,
        }[status]


@dataclass(frozen=True)
class EvidenceEvaluation:
    control_id: str
    contract_version: str
    status: str
    outcome: str
    evidence_ids: tuple[str, ...]
    evidence_sources: tuple[str, ...]
    evidence_authorities: tuple[str, ...]
    provenance_references: tuple[str, ...]
    predicate_result: bool


class EvidenceContractEvaluator:
    def __init__(self, clock: HarnessClock):
        self.clock = clock

    def _required_present(self, item: EvidenceItem, contract: ControlContract) -> bool:
        for field in contract.required_fields:
            if not getattr(item, field, None):
                return False
        return True

    def _temporal_status(self, item: EvidenceItem) -> str | None:
        """Return explicit temporal failure rather than raising or trusting caller time.

        The harness clock is authoritative for this bounded reference test. An
        observation timestamp in the future is not current evidence. Malformed,
        timezone-incompatible or otherwise non-comparable timestamps are INVALID.
        """
        now = self.clock.now()
        try:
            observed = datetime.fromisoformat(item.observed_at)
            if observed > now:
                return INVALID
            if item.valid_from:
                valid_from = datetime.fromisoformat(item.valid_from)
                if now < valid_from:
                    return INVALID
            if item.valid_until:
                valid_until = datetime.fromisoformat(item.valid_until)
                if now > valid_until:
                    return STALE
            if item.max_age_seconds is not None and now - observed > timedelta(seconds=item.max_age_seconds):
                return STALE
        except (ValueError, TypeError):
            return INVALID
        return None

    def _invalid_collision(
        self,
        contract: ControlContract,
        evidence: tuple[EvidenceItem, ...],
    ) -> EvidenceEvaluation:
        """Represent an evidence-id collision as explicit INVALID evidence.

        An evidence_id is the reconstruction identity of an item. The same ID
        cannot legitimately denote two different payloads inside one evaluation.
        """
        unique_ids = tuple(dict.fromkeys(i.evidence_id for i in evidence))
        unique_sources = tuple(dict.fromkeys(i.evidence_source for i in evidence))
        unique_authorities = tuple(dict.fromkeys(i.evidence_authority for i in evidence))
        unique_provenance = tuple(dict.fromkeys((i.provenance_reference or "") for i in evidence))
        return EvidenceEvaluation(
            control_id=contract.control_id,
            contract_version=contract.contract_version,
            status=INVALID,
            outcome=contract.outcome_for(INVALID),
            evidence_ids=unique_ids,
            evidence_sources=unique_sources,
            evidence_authorities=unique_authorities,
            provenance_references=unique_provenance,
            predicate_result=False,
        )

    def evaluate(
        self,
        contract: ControlContract,
        items: Iterable[EvidenceItem],
        *,
        expected_subject: str,
        expected_deployment: str | None = None,
        expected_product_identifier: str | None = None,
        expected_product_version: str | None = None,
        requester_source: str | None = None,
    ) -> EvidenceEvaluation:
        supplied = tuple(items)
        if not supplied:
            return EvidenceEvaluation(contract.control_id, contract.contract_version, ABSENT, contract.outcome_for(ABSENT), (), (), (), (), False)

        # Evidence identity is stable within an evaluation. Exact duplicate
        # delivery is de-duplicated; the same ID carrying a different payload is
        # an identity collision and invalidates the evidence set.
        seen: dict[str, EvidenceItem] = {}
        deduplicated: list[EvidenceItem] = []
        for item in supplied:
            prior = seen.get(item.evidence_id)
            if prior is None:
                seen[item.evidence_id] = item
                deduplicated.append(item)
                continue
            if prior == item:
                continue
            return self._invalid_collision(contract, supplied)

        evidence = tuple(deduplicated)
        statuses: list[str] = []
        accepted: list[EvidenceItem] = []
        for item in evidence:
            if item.control_id != contract.control_id:
                statuses.append(INVALID); continue
            if item.evidence_source not in contract.permitted_authoritative_sources or item.evidence_authority not in contract.permitted_authoritative_sources:
                statuses.append(UNVERIFIABLE); continue
            if requester_source and item.evidence_source == requester_source and requester_source not in contract.permitted_authoritative_sources:
                statuses.append(UNVERIFIABLE); continue
            if item.subject != expected_subject:
                statuses.append(INVALID); continue
            if expected_deployment is not None and item.deployment_context != expected_deployment:
                statuses.append(INVALID); continue
            if expected_product_identifier is not None and item.product_identifier != expected_product_identifier:
                statuses.append(INVALID); continue
            if expected_product_version is not None and item.product_version != expected_product_version:
                statuses.append(INVALID); continue
            if not self._required_present(item, contract):
                statuses.append(INVALID); continue
            if contract.require_integrity and not item.integrity_valid:
                statuses.append(INVALID); continue
            if item.revoked:
                statuses.append(REVOKED); continue
            temporal = self._temporal_status(item)
            if temporal:
                statuses.append(temporal); continue
            accepted.append(item)

        if accepted:
            states = {item.asserted_state for item in accepted}
            if len(states) > 1:
                status = CONTRADICTORY
            elif any(s in {INVALID, REVOKED} for s in statuses):
                status = INVALID if INVALID in statuses else REVOKED
            elif any(s == STALE for s in statuses):
                status = STALE
            elif any(s == UNVERIFIABLE for s in statuses):
                status = UNVERIFIABLE
            else:
                status = VALID if next(iter(states)) == contract.expected_state else INVALID
        else:
            precedence = [REVOKED, INVALID, STALE, UNVERIFIABLE]
            status = next((s for s in precedence if s in statuses), ABSENT)

        return EvidenceEvaluation(
            control_id=contract.control_id,
            contract_version=contract.contract_version,
            status=status,
            outcome=contract.outcome_for(status),
            evidence_ids=tuple(i.evidence_id for i in evidence),
            evidence_sources=tuple(i.evidence_source for i in evidence),
            evidence_authorities=tuple(i.evidence_authority for i in evidence),
            provenance_references=tuple(i.provenance_reference or "" for i in evidence),
            predicate_result=(status == VALID),
        )


def product_contract(version: str = "CC-1.0") -> ControlContract:
    return ControlContract(version, "HC.PRODUCT.VERSION.AUTHORISED", "AI_PRODUCT_VERSION", ("DEPLOYMENT_REGISTRY",), ("product_identifier", "product_version", "deployment_context", "observed_at", "provenance_reference"), "AUTHORISED", "REFUSE", "REFUSE", "REFUSE", "REFUSE", "REFUSE", "REFUSE")


def training_contract(version: str = "CC-1.0") -> ControlContract:
    return ControlContract(version, "HC.CLINICIAN.TRAINING.CURRENT", "CLINICIAN", ("TRAINING_REGISTRY",), ("observed_at", "provenance_reference"), "CURRENT", "ESCALATE", "ESCALATE", "REFUSE", "ESCALATE", "ESCALATE", "REFUSE")
