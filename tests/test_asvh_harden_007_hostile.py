import json
from pathlib import Path

from app.hardening.evidence_integrity import canonical_json, evidence_root, verify_test_pack
from tests.test_asvh_harden_007 import PROTECTED, make_pack


def test_hostile_manifest_substitution_is_detected(tmp_path):
    d, _ = make_pack(tmp_path, "A")
    other, _ = make_pack(tmp_path, "B")
    (d / "artefact-manifest.json").write_bytes((other / "artefact-manifest.json").read_bytes())
    assert verify_test_pack(d, (*PROTECTED, "artefact-manifest.json")).status == "INTEGRITY_FAILURE"


def test_hostile_omitted_failure_changes_aggregate_root(tmp_path):
    _, pass_manifest = make_pack(tmp_path, "PASS")
    _, fail_manifest = make_pack(tmp_path, "FAIL", "FAIL")
    from app.hardening.evidence_integrity import manifest_digest
    full = evidence_root([("PASS", manifest_digest(pass_manifest)), ("FAIL", manifest_digest(fail_manifest))])
    dishonest = evidence_root([("PASS", manifest_digest(pass_manifest))])
    assert full != dishonest


def test_hostile_duplicate_shadowing_rejected():
    try:
        evidence_root([("H7-001", "good"), ("H7-001", "shadow")])
    except ValueError:
        return
    raise AssertionError("duplicate test id was accepted")


def test_hostile_manifest_path_escape_is_rejected(tmp_path):
    d, manifest = make_pack(tmp_path, "A")
    manifest["artefacts"][0]["path"] = "../outside.json"
    (tmp_path / "outside.json").write_text("forged")
    (d / "artefact-manifest.json").write_bytes(canonical_json(manifest))
    assert verify_test_pack(d, (*PROTECTED, "artefact-manifest.json")).status == "INTEGRITY_FAILURE"
