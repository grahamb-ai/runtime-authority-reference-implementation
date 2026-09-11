from dataclasses import replace
from datetime import datetime, timedelta, timezone

from app.hardening.deployment_enforcement import (
    BreakGlassAuthority,
    DeploymentBoundaryProfile,
    DeploymentEnforcer,
    RouteBinding,
)
from app.hardening.models import ExactClinicalCommit, ProtectedClinicalBind

NOW = datetime(2026, 9, 11, 14, 0, tzinfo=timezone.utc)


def commit(**changes):
    c = ExactClinicalCommit(
        schema_version="ECC-1.0", commit_id="H5-COMMIT", patient_ref="PAT-001",
        encounter_ref="ENC-001", consultation_ref="CON-001", clinician_ref="CLN-001",
        document_type="CLINICAL_NOTE", document_content="Approved note", execution_type="EPR_COMMIT",
        target_system="EPR-SIMULATOR", target_instance="ASVH-TEST-01", target_record_ref="ENC-001",
        product_identifier="AVT-001", product_version="1.0.0", workflow_context="AMBIENT_SCRIBING",
        intended_use="CLINICAL_DOCUMENTATION", runtime_policy_version="HC-POL-1.0",
        rule_catalogue_version="ASVH-RC-1.0",
    )
    return replace(c, **changes)


def bind_for(c):
    return ProtectedClinicalBind(
        schema_version="PCB-1.0", bind_id="BIND-H5", authority_receipt_id="REC-H5",
        commit_id=c.commit_id, commit_binding_hash=c.commit_binding_hash,
        runtime_authority_version="RA-1.0", runtime_policy_version=c.runtime_policy_version,
        rule_catalogue_version=c.rule_catalogue_version, materiality_profile=c.materiality_profile,
        canonicalisation_profile=c.canonicalisation_profile, issued_at=NOW.isoformat(),
        expires_at=(NOW + timedelta(minutes=5)).isoformat(), integrity_reference="test-integrity",
    )


def profile(**changes):
    p = DeploymentBoundaryProfile(
        profile_id="ASVH-DP-001", profile_version=3, deployment_id="ASVH-TEST-01",
        governed_consequence_type="CLINICAL_DOCUMENTATION_COMMIT",
        active_control_contract_version="CC-1.0",
        protected_routes=(
            RouteBinding("PRIMARY_EPR_COMMIT", "EPR:WRITE:CLINICAL_NOTE"),
            RouteBinding("SECONDARY_EPR_COMMIT", "EPR:WRITE:CLINICAL_NOTE"),
        ),
        break_glass_policy_version="BG-1.0", integrity_valid=True,
    )
    return replace(p, **changes)


def bg(c, **changes):
    b = BreakGlassAuthority(
        override_id="BG-001", authority_identity="DUTY-CONSULTANT", commit_binding_hash=c.commit_binding_hash,
        deployment_id="ASVH-TEST-01", issued_at=NOW.isoformat(),
        expires_at=(NOW + timedelta(minutes=2)).isoformat(), policy_version="BG-1.0", single_use=True,
    )
    return replace(b, **changes)


def run(c=None, b=None, p=None, **kwargs):
    c = c or commit(); p = p or profile(); enforcer = DeploymentEnforcer(profile())
    params = dict(
        supplied_profile=p, route_id="PRIMARY_EPR_COMMIT", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=b if b is not None else bind_for(c), original_decision="ALLOW",
        control_contract_version="CC-1.0", now=NOW,
    ); params.update(kwargs)
    return enforcer.enforce(**params)


def test_h5_001_primary_protected_route_forms(): assert run().status == "FORMED"
def test_h5_002_undeclared_route_prevented(): assert run(route_id="DIRECT_DB_WRITE").status == "PREVENTED"
def test_h5_003_declared_route_without_bind_prevented(): assert run(b=None, bind=None).status == "PREVENTED"
def test_h5_004_wrong_exact_commit_prevented():
    c = commit(); other = commit(document_content="Different note")
    assert run(c=other, b=bind_for(c)).status == "PREVENTED"
def test_h5_005_route_label_target_mismatch_prevented(): assert run(target_capability="EPR:ADMIN:WRITE").status == "PREVENTED"
def test_h5_006_undeclared_label_same_capability_prevented(): assert run(route_id="ALIAS_EPR_COMMIT").status == "PREVENTED"
def test_h5_007_stale_profile_version_prevented(): assert run(p=profile(profile_version=2)).status == "PREVENTED"
def test_h5_008_wrong_deployment_profile_prevented(): assert run(p=profile(deployment_id="OTHER")).status == "PREVENTED"
def test_h5_009_wrong_contract_version_prevented(): assert run(control_contract_version="CC-0.9").status == "PREVENTED"
def test_h5_010_substituted_contract_version_prevented(): assert run(control_contract_version="CC-PERMISSIVE").status == "PREVENTED"
def test_h5_011_profile_integrity_failure_prevented(): assert run(p=profile(integrity_valid=False)).status == "PREVENTED"
def test_h5_012_enforcement_unavailable_fails_closed(): assert run(enforcement_available=False).status == "PREVENTED"
def test_h5_013_refuse_without_breakglass_prevented(): assert run(original_decision="REFUSE", break_glass=None).status == "PREVENTED"
def test_h5_014_valid_breakglass_exact_scope_forms():
    c = commit(); r = run(c=c, b=None, bind=None, original_decision="REFUSE", break_glass=bg(c)); assert r.status == "FORMED" and r.original_decision == "REFUSE"
def test_h5_015_breakglass_wrong_commit_prevented():
    c = commit(); other = commit(document_content="Other")
    assert run(c=other, b=None, bind=None, original_decision="REFUSE", break_glass=bg(c)).status == "PREVENTED"
def test_h5_016_expired_breakglass_prevented():
    c = commit(); expired = bg(c, expires_at=(NOW - timedelta(seconds=1)).isoformat())
    assert run(c=c, b=None, bind=None, original_decision="REFUSE", break_glass=expired).status == "PREVENTED"
def test_h5_017_breakglass_declares_single_use(): assert bg(commit()).single_use is True
def test_h5_018_breakglass_evidence_preserves_original_refuse():
    c=commit(); r=run(c=c,b=None,bind=None,original_decision="REFUSE",break_glass=bg(c)); assert r.original_decision=="REFUSE" and r.break_glass_override_id=="BG-001"
def test_h5_019_alternate_undeclared_api_cannot_form_governed_route(): assert run(route_id="RAW_EPR_API").status == "PREVENTED"
def test_h5_020_evidence_names_exact_interface():
    r=run(); assert r.route_id=="PRIMARY_EPR_COMMIT" and r.target_capability=="EPR:WRITE:CLINICAL_NOTE" and r.deployment_profile_id=="ASVH-DP-001"
