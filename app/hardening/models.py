from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any

MATERIALITY_PROFILE = "HC-MAT-1.0"
CANONICALISATION_PROFILE = "ECC-C14N-1"

MATERIAL_FIELDS = (
    "schema_version", "patient_ref", "encounter_ref", "consultation_ref",
    "clinician_ref", "document_type", "document_hash", "execution_type",
    "target_system", "target_instance", "target_record_ref",
    "product_identifier", "product_version", "workflow_context",
    "intended_use", "runtime_policy_version", "rule_catalogue_version",
    "materiality_profile", "canonicalisation_profile",
)


def normalise_document(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class ExactClinicalCommit:
    schema_version: str
    commit_id: str
    patient_ref: str
    encounter_ref: str
    consultation_ref: str
    clinician_ref: str
    document_type: str
    document_content: str
    execution_type: str
    target_system: str
    target_instance: str
    target_record_ref: str
    product_identifier: str
    product_version: str
    workflow_context: str
    intended_use: str
    runtime_policy_version: str
    rule_catalogue_version: str
    materiality_profile: str = MATERIALITY_PROFILE
    canonicalisation_profile: str = CANONICALISATION_PROFILE

    @property
    def document_hash(self) -> str:
        return sha256_text(normalise_document(self.document_content))

    def material_map(self) -> dict[str, Any]:
        data = asdict(self)
        data["document_hash"] = self.document_hash
        data.pop("document_content")
        return {field: data[field] for field in MATERIAL_FIELDS}

    def canonical_representation(self) -> str:
        return canonical_json(self.material_map())

    @property
    def commit_binding_hash(self) -> str:
        return sha256_text(self.canonical_representation())


@dataclass(frozen=True)
class AuthorityReceipt:
    receipt_id: str
    decision: str
    commit_id: str
    commit_binding_hash: str
    materiality_profile: str
    canonicalisation_profile: str
    runtime_authority_version: str
    runtime_policy_version: str
    rule_catalogue_version: str
    issued_at: str


@dataclass(frozen=True)
class ProtectedClinicalBind:
    schema_version: str
    bind_id: str
    authority_receipt_id: str
    commit_id: str
    commit_binding_hash: str
    runtime_authority_version: str
    runtime_policy_version: str
    rule_catalogue_version: str
    materiality_profile: str
    canonicalisation_profile: str
    issued_at: str
    expires_at: str
    use_semantics: str = "SINGLE_USE"
