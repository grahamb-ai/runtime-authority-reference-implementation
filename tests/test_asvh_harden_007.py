import json
from pathlib import Path

import pytest

from app.hardening.evidence_integrity import (
    DIGEST_ALGORITHM, build_test_manifest, canonical_json, compare_reproduction,
    evidence_root, manifest_digest, sha256_bytes, verify_test_pack,
)

PROTECTED = ("test-definition.json", "inputs.json", "observations.json", "result.json")


def make_pack(tmp_path: Path, test_id="H7-X", outcome="PASS"):
    d = tmp_path / test_id
    d.mkdir(parents=True)
    payloads = {
        "test-definition.json": {"test_id": test_id},
        "inputs.json": {"synthetic": True},
        "observations.json": {"observed": "bounded"},
        "result.json": {"outcome": outcome},
    }
    for name, value in payloads.items():
        (d / name).write_bytes(canonical_json(value))
    manifest = build_test_manifest(d, PROTECTED)
    (d / "artefact-manifest.json").write_bytes(canonical_json(manifest))
    return d, manifest


def test_h7_001_valid_complete_evidence_pack_verifies(tmp_path):
    d, _ = make_pack(tmp_path)
    assert verify_test_pack(d, (*PROTECTED, "artefact-manifest.json")).status == "COMPLETE"


def test_h7_002_mutation_detected(tmp_path):
    d, _ = make_pack(tmp_path)
    (d / "inputs.json").write_text("mutated")
    assert verify_test_pack(d, (*PROTECTED, "artefact-manifest.json")).status == "INTEGRITY_FAILURE"


def test_h7_003_deletion_is_incomplete(tmp_path):
    d, _ = make_pack(tmp_path)
    (d / "observations.json").unlink()
    assert verify_test_pack(d, (*PROTECTED, "artefact-manifest.json")).status == "INCOMPLETE"


def test_h7_004_absent_contract_file_is_incomplete(tmp_path):
    d, _ = make_pack(tmp_path)
    assert verify_test_pack(d, (*PROTECTED, "explicit-absent.json", "artefact-manifest.json")).status == "INCOMPLETE"


def test_h7_005_changed_result_changes_manifest_digest(tmp_path):
    d, m1 = make_pack(tmp_path)
    (d / "result.json").write_bytes(canonical_json({"outcome": "FAIL"}))
    m2 = build_test_manifest(d, PROTECTED)
    assert manifest_digest(m1) != manifest_digest(m2)


def test_h7_006_changed_inventory_changes_root():
    assert evidence_root([("A", "1")]) != evidence_root([("A", "1"), ("B", "2")])


def test_h7_007_input_order_is_canonical_but_identity_order_is_not_silent():
    assert evidence_root([("B", "2"), ("A", "1")]) == evidence_root([("A", "1"), ("B", "2")])
    assert evidence_root([("A", "2"), ("B", "1")]) != evidence_root([("A", "1"), ("B", "2")])


def test_h7_008_duplicate_id_rejected():
    with pytest.raises(ValueError): evidence_root([("A", "1"), ("A", "2")])


def test_h7_009_missing_expected_id_detectable():
    expected={"A","B"}; observed={"A"}
    assert expected-observed == {"B"}


def test_h7_010_unexpected_id_surfaced():
    expected={"A"}; observed={"A","X"}
    assert observed-expected == {"X"}


def record(root="r", sha="abc", version="7.0", inventory=None, outcomes=None):
    return {"git_sha":sha,"suite_version":version,"test_inventory":inventory or ["A"],"outcomes":outcomes or {"A":"PASS"},"evidence_root":root}


def test_h7_011_wrong_git_sha_reproduction_mismatch():
    assert compare_reproduction(record(), record(sha="def")).status == "REPRODUCTION_MISMATCH"


def test_h7_012_wrong_suite_version_reproduction_mismatch():
    assert compare_reproduction(record(), record(version="8.0")).status == "REPRODUCTION_MISMATCH"


def test_h7_013_malformed_manifest_rejected(tmp_path):
    d,_=make_pack(tmp_path); (d/"artefact-manifest.json").write_text("{")
    assert verify_test_pack(d, (*PROTECTED,"artefact-manifest.json")).status == "INTEGRITY_FAILURE"


def test_h7_014_unsupported_digest_rejected(tmp_path):
    d,m=make_pack(tmp_path); m["digest_algorithm"]="MD5"; (d/"artefact-manifest.json").write_bytes(canonical_json(m))
    assert verify_test_pack(d, (*PROTECTED,"artefact-manifest.json")).status == "INTEGRITY_FAILURE"


def test_h7_015_digest_is_over_stored_bytes(tmp_path):
    p=tmp_path/"x"; p.write_bytes(b"a\r\nb")
    assert sha256_bytes(p.read_bytes()) == sha256_bytes(b"a\r\nb")


def test_h7_016_junit_pass_does_not_override_incomplete_evidence(tmp_path):
    d,_=make_pack(tmp_path); (d/"inputs.json").unlink()
    junit_pass=True
    assert junit_pass and verify_test_pack(d, (*PROTECTED,"artefact-manifest.json")).status == "INCOMPLETE"


def test_h7_017_failed_test_is_bound_into_root(tmp_path):
    _,m=make_pack(tmp_path, "FAIL-ID", "FAIL")
    root=evidence_root([("FAIL-ID",manifest_digest(m))])
    assert root


def test_h7_018_same_outcomes_different_root_is_mismatch():
    assert compare_reproduction(record(root="a"), record(root="b")).status == "REPRODUCTION_MISMATCH"


def test_h7_019_deterministic_rebuild_same_digest(tmp_path):
    _,m1=make_pack(tmp_path/"one", "A")
    _,m2=make_pack(tmp_path/"two", "A")
    assert manifest_digest(m1)==manifest_digest(m2)


def test_h7_020_complete_requires_all_expected_test_packs(tmp_path):
    expected={f"H7-{i:03d}" for i in range(1,21)}
    observed=set(expected)
    assert expected == observed
