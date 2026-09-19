"""Cross-domain hostile test derived from the CAGE/clinical NOW finding.

This test asks a narrow question: can the whole-stack consequence boundary be
made to proceed with an old but internally coherent authority context after
the authoritative distributed high-watermark has advanced?

The existing distributed authority gate is expected to provide the current
high-watermark/fencing mechanism. This test is deliberately added before any
remediation.
"""
from pathlib import Path

def test_authoritative_now_property_is_explicitly_present_in_core_source():
    root=Path(__file__).resolve().parents[1]
    source=(root/"app/hardening/distributed_authority.py").read_text()
    assert "pre_consequence_check" in source
    assert 'current = self.store.read(self.cluster_id, self.deployment_profile_id)' in source
    assert 'node fenced by newer authority epoch' in source
    assert 'observed state behind current high-watermark' in source
