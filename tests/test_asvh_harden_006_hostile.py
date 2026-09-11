from dataclasses import replace

import pytest

from app.hardening.recovery_authority import AuthorityState, AuthorityTrustProfile, RecoveryAuthorityGate, RecoveryWatermarkStore


def profile(**changes):
    base = AuthorityTrustProfile("ATP-1", 1, "ASVH-TEST-01", ("RA-PRIMARY", "RA-FAILOVER"), 2)
    return replace(base, **changes)


def state(service="RA-PRIMARY", epoch=1, sequence=1, payload="AUTHORISED"):
    return AuthorityState(service, epoch, sequence, payload)


def test_hostile_high_watermark_read_failure_is_explicit_not_exception():
    class BrokenReadStore:
        def read(self, deployment_id):
            raise OSError("durable state unavailable")
        def accept(self, deployment_id, state):
            raise AssertionError("accept must not be reached")
    result = RecoveryAuthorityGate(profile(), BrokenReadStore()).evaluate(profile(), state())
    assert result.status == "INDETERMINATE"


def test_hostile_local_watermark_store_reset_cannot_resurrect_stale_authority(tmp_path):
    original = RecoveryWatermarkStore(tmp_path / "original.db")
    g1 = RecoveryAuthorityGate(profile(), original)
    assert g1.evaluate(profile(), state(sequence=50)).status == "ACTIVE"

    # Simulate replacement/recreation of the local recovery database while the
    # authority service presents an older but otherwise favourable state.
    replacement = RecoveryWatermarkStore(tmp_path / "replacement.db")
    g2 = RecoveryAuthorityGate(profile(), replacement)
    result = g2.evaluate(profile(), state("RA-FAILOVER", sequence=2))
    assert result.status != "ACTIVE"


def test_hostile_unsupported_independence_level_cannot_be_claimed(tmp_path):
    impossible = profile(independence_level=99)
    g = RecoveryAuthorityGate(impossible, RecoveryWatermarkStore(tmp_path / "r.db"))
    result = g.evaluate(impossible, state())
    assert result.status == "PREVENTED"


def test_hostile_boolean_authority_counter_is_not_integer_position(tmp_path):
    g = RecoveryAuthorityGate(profile(), RecoveryWatermarkStore(tmp_path / "r.db"))
    result = g.evaluate(profile(), AuthorityState("RA-PRIMARY", True, 1, "AUTHORISED"))
    assert result.status == "PREVENTED"
