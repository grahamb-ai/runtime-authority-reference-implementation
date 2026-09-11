from dataclasses import replace
from datetime import datetime, timedelta, timezone

from app.hardening.deployment_enforcement import BreakGlassAuthority, DeploymentBoundaryProfile, DeploymentEnforcer, RouteBinding
from app.hardening.models import ExactClinicalCommit, ProtectedClinicalBind

NOW = datetime(2026, 9, 11, 14, 0, tzinfo=timezone.utc)


def commit():
    return ExactClinicalCommit(
        schema_version="ECC-1.0", commit_id="H5-HOSTILE", patient_ref="PAT-001", encounter_ref="ENC-001",
        consultation_ref="CON-001", clinician_ref="CLN-001", document_type="CLINICAL_NOTE",
        document_content="Approved note", execution_type="EPR_COMMIT", target_system="EPR-SIMULATOR",
        target_instance="ASVH-TEST-01", target_record_ref="ENC-001", product_identifier="AVT-001",
        product_version="1.0.0", workflow_context="AMBIENT_SCRIBING", intended_use="CLINICAL_DOCUMENTATION",
        runtime_policy_version="HC-POL-1.0", rule_catalogue_version="ASVH-RC-1.0",
    )


def active_profile():
    return DeploymentBoundaryProfile(
        profile_id="ASVH-DP-001", profile_version=3, deployment_id="ASVH-TEST-01",
        governed_consequence_type="CLINICAL_DOCUMENTATION_COMMIT", active_control_contract_version="CC-1.0",
        protected_routes=(RouteBinding("PRIMARY_EPR_COMMIT", "EPR:WRITE:CLINICAL_NOTE"),),
        break_glass_policy_version="BG-1.0", integrity_valid=True,
    )


def bind_for(c):
    return ProtectedClinicalBind(
        schema_version="PCB-1.0", bind_id="BIND-H5-H", authority_receipt_id="REC-H5-H",
        commit_id=c.commit_id, commit_binding_hash=c.commit_binding_hash, runtime_authority_version="RA-1.0",
        runtime_policy_version=c.runtime_policy_version, rule_catalogue_version=c.rule_catalogue_version,
        materiality_profile=c.materiality_profile, canonicalisation_profile=c.canonicalisation_profile,
        issued_at=NOW.isoformat(), expires_at=(NOW + timedelta(minutes=5)).isoformat(), integrity_reference="test",
    )


def test_hostile_same_version_profile_cannot_add_bypass_route():
    c = commit(); active = active_profile(); enforcer = DeploymentEnforcer(active)
    forged = replace(active, protected_routes=active.protected_routes + (RouteBinding("RAW_EPR_API", "EPR:WRITE:CLINICAL_NOTE"),))
    result = enforcer.enforce(
        supplied_profile=forged, route_id="RAW_EPR_API", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=bind_for(c), original_decision="ALLOW", control_contract_version="CC-1.0", now=NOW,
    )
    assert result.status == "PREVENTED"


def test_hostile_same_version_profile_identity_substitution_rejected():
    c = commit(); active = active_profile(); enforcer = DeploymentEnforcer(active)
    forged = replace(active, profile_id="ATTACKER-PROFILE")
    result = enforcer.enforce(
        supplied_profile=forged, route_id="PRIMARY_EPR_COMMIT", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=bind_for(c), original_decision="ALLOW", control_contract_version="CC-1.0", now=NOW,
    )
    assert result.status == "PREVENTED"


def test_hostile_same_version_profile_cannot_expand_contract_authority():
    c = commit(); active = active_profile(); enforcer = DeploymentEnforcer(active)
    forged = replace(active, active_control_contract_version="CC-PERMISSIVE")
    result = enforcer.enforce(
        supplied_profile=forged, route_id="PRIMARY_EPR_COMMIT", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=bind_for(c), original_decision="ALLOW", control_contract_version="CC-PERMISSIVE", now=NOW,
    )
    assert result.status == "PREVENTED"


def test_hostile_breakglass_single_use_is_enforced_not_declarative():
    c = commit(); active = active_profile(); enforcer = DeploymentEnforcer(active)
    authority = BreakGlassAuthority(
        override_id="BG-REPLAY", authority_identity="DUTY-CONSULTANT", commit_binding_hash=c.commit_binding_hash,
        deployment_id=active.deployment_id, issued_at=NOW.isoformat(), expires_at=(NOW + timedelta(minutes=2)).isoformat(),
        policy_version=active.break_glass_policy_version, single_use=True,
    )
    kwargs = dict(
        supplied_profile=active, route_id="PRIMARY_EPR_COMMIT", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=None, original_decision="REFUSE", control_contract_version="CC-1.0", now=NOW,
        break_glass=authority,
    )
    first = enforcer.enforce(**kwargs); second = enforcer.enforce(**kwargs)
    assert first.status == "FORMED" and second.status == "PREVENTED"


def test_hostile_future_issued_breakglass_is_not_yet_authority():
    c = commit(); active = active_profile(); enforcer = DeploymentEnforcer(active)
    authority = BreakGlassAuthority(
        override_id="BG-FUTURE", authority_identity="DUTY-CONSULTANT", commit_binding_hash=c.commit_binding_hash,
        deployment_id=active.deployment_id, issued_at=(NOW + timedelta(minutes=5)).isoformat(),
        expires_at=(NOW + timedelta(minutes=10)).isoformat(), policy_version=active.break_glass_policy_version,
        single_use=True,
    )
    result = enforcer.enforce(
        supplied_profile=active, route_id="PRIMARY_EPR_COMMIT", target_capability="EPR:WRITE:CLINICAL_NOTE",
        commit=c, bind=None, original_decision="REFUSE", control_contract_version="CC-1.0", now=NOW,
        break_glass=authority,
    )
    assert result.status == "PREVENTED"
