from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DIGEST_ALGORITHM = "SHA-256"
REQUIRED_TEST_FILES = (
    "test-definition.json",
    "inputs.json",
    "observations.json",
    "result.json",
    "artefact-manifest.json",
)


def canonical_json(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> dict:
    raw = path.read_bytes()
    return {"path": path.name, "bytes": len(raw), "digest_algorithm": DIGEST_ALGORITHM, "sha256": sha256_bytes(raw)}


def safe_child(root: Path, relative: str) -> Path:
    root = root.resolve()
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("evidence path escapes declared run directory")
    return candidate


def build_test_manifest(test_dir: Path, protected_files: Iterable[str]) -> dict:
    entries = []
    for name in sorted(protected_files):
        path = safe_child(test_dir, name)
        if not path.is_file():
            raise FileNotFoundError(name)
        entries.append(digest_file(path))
    return {"digest_algorithm": DIGEST_ALGORITHM, "artefacts": entries}


def manifest_digest(manifest: dict) -> str:
    if manifest.get("digest_algorithm") != DIGEST_ALGORITHM:
        raise ValueError("unsupported digest algorithm")
    return sha256_bytes(canonical_json(manifest))


def evidence_root(test_manifest_digests: Iterable[tuple[str, str]]) -> str:
    pairs = list(test_manifest_digests)
    ids = [test_id for test_id, _ in pairs]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate test id")
    ordered = sorted(pairs, key=lambda item: item[0])
    return sha256_bytes(canonical_json(ordered))


@dataclass(frozen=True)
class VerificationResult:
    status: str
    reason: str
    evidence_root: str | None = None


def verify_test_pack(test_dir: Path, expected_files: Iterable[str]) -> VerificationResult:
    expected = tuple(expected_files)
    for name in expected:
        if not safe_child(test_dir, name).is_file():
            return VerificationResult("INCOMPLETE", f"required evidence artefact absent: {name}")
    try:
        manifest = json.loads((test_dir / "artefact-manifest.json").read_text(encoding="utf-8"))
    except Exception:
        return VerificationResult("INTEGRITY_FAILURE", "malformed artefact manifest")
    if manifest.get("digest_algorithm") != DIGEST_ALGORITHM:
        return VerificationResult("INTEGRITY_FAILURE", "unsupported digest algorithm")
    for entry in manifest.get("artefacts", []):
        try:
            path = safe_child(test_dir, entry["path"])
            raw = path.read_bytes()
        except Exception:
            return VerificationResult("INTEGRITY_FAILURE", "manifest path invalid or unavailable")
        if len(raw) != entry.get("bytes") or sha256_bytes(raw) != entry.get("sha256"):
            return VerificationResult("INTEGRITY_FAILURE", f"evidence artefact digest mismatch: {entry.get('path')}")
    return VerificationResult("COMPLETE", "test evidence pack complete and integrity-valid", manifest_digest(manifest))


def compare_reproduction(source: dict, reproduced: dict) -> VerificationResult:
    for field in ("git_sha", "suite_version", "test_inventory"):
        if source.get(field) != reproduced.get(field):
            return VerificationResult("REPRODUCTION_MISMATCH", f"reproduction field differs: {field}")
    if source.get("outcomes") != reproduced.get("outcomes"):
        return VerificationResult("REPRODUCTION_MISMATCH", "test outcomes differ")
    if source.get("evidence_root") != reproduced.get("evidence_root"):
        return VerificationResult("REPRODUCTION_MISMATCH", "outcomes reproduced but evidence root differs")
    return VerificationResult("COMPLETE", "outcomes and evidence root reproduced", source.get("evidence_root"))
