from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class PolicyState:
    policy_id: str
    policy_version: str
    ruleset_version: str
    deployment_profile_id: str
    deployment_profile_version: int


@dataclass(frozen=True)
class OutstandingAuthority:
    authority_id: str
    policy_id: str
    policy_version: str
    ruleset_version: str
    deployment_profile_id: str
    deployment_profile_version: int
    exact_commit_hash: str
    issued_at: str
    expires_at: str
    invalidated: bool = False
    break_glass: bool = False


@dataclass(frozen=True)
class PolicyTransition:
    transition_id: str
    from_policy_version: str
    to_policy_version: str
    from_ruleset_version: str
    to_ruleset_version: str
    deployment_profile_id: str
    deployment_profile_version: int
    effective_at: str
    transition_class: str
    compatibility_explicit: bool
    reason: str
    break_glass_compatible: bool = False


@dataclass(frozen=True)
class TransitionDecision:
    status: str
    reason: str
    authority_id: str
    active_policy_version: str
    active_ruleset_version: str
    transition_id: str | None = None
    revalidation_required: bool = False


class PolicyHighWatermark:
    def __init__(self):
        self._max_version: dict[tuple[str, str], str] = {}
        self._invalidated: set[str] = set()
        self._transition_fingerprints: dict[str, PolicyTransition] = {}

    def mark_invalidated(self, authority_id: str):
        self._invalidated.add(authority_id)

    def was_invalidated(self, authority_id: str) -> bool:
        return authority_id in self._invalidated

    def accept_transition(self, transition: PolicyTransition) -> bool:
        prior = self._transition_fingerprints.get(transition.transition_id)
        if prior is not None and prior != transition:
            return False
        self._transition_fingerprints[transition.transition_id] = transition
        return True

    def accept_policy(self, state: PolicyState):
        key = (state.policy_id, state.deployment_profile_id)
        prior = self._max_version.get(key)
        if prior is None or state.policy_version >= prior:
            self._max_version[key] = state.policy_version

    def is_rollback(self, state: PolicyState) -> bool:
        prior = self._max_version.get((state.policy_id, state.deployment_profile_id))
        return prior is not None and state.policy_version < prior


class PolicyTransitionGate:
    def __init__(self, watermark: PolicyHighWatermark, clock):
        self.watermark = watermark
        self.clock = clock

    def evaluate(self, authority: OutstandingAuthority, active: PolicyState, transition: PolicyTransition | None) -> TransitionDecision:
        now = self.clock.now()
        if isinstance(now, str):
            now = _parse_ts(now)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        def result(status: str, reason: str, *, revalidate: bool = False, tid: str | None = None):
            return TransitionDecision(status, reason, authority.authority_id, active.policy_version, active.ruleset_version, tid, revalidate)

        try:
            if now >= _parse_ts(authority.expires_at):
                return result("PREVENTED", "outstanding authority expired")
        except Exception:
            return result("INDETERMINATE", "authority temporal state malformed")

        if authority.invalidated or self.watermark.was_invalidated(authority.authority_id):
            return result("PREVENTED", "outstanding authority previously invalidated")

        if authority.policy_id != active.policy_id:
            return result("PREVENTED", "policy identity mismatch")
        if (authority.deployment_profile_id, authority.deployment_profile_version) != (active.deployment_profile_id, active.deployment_profile_version):
            return result("PREVENTED", "deployment profile mismatch")
        if self.watermark.is_rollback(active):
            return result("PREVENTED", "active policy state is behind accepted high-watermark")

        same_basis = authority.policy_version == active.policy_version and authority.ruleset_version == active.ruleset_version
        if same_basis and transition is None:
            self.watermark.accept_policy(active)
            return result("ALLOW", "outstanding authority remains on unchanged policy basis")

        if transition is None:
            return result("INDETERMINATE", "policy basis changed without transition semantics")

        if not self.watermark.accept_transition(transition):
            return result("INDETERMINATE", "contradictory transition identity", tid=transition.transition_id)
        if (transition.deployment_profile_id, transition.deployment_profile_version) != (active.deployment_profile_id, active.deployment_profile_version):
            return result("PREVENTED", "transition deployment scope mismatch", tid=transition.transition_id)
        if transition.from_policy_version != authority.policy_version or transition.from_ruleset_version != authority.ruleset_version:
            return result("PREVENTED", "transition source basis does not match outstanding authority", tid=transition.transition_id)
        if transition.to_policy_version != active.policy_version or transition.to_ruleset_version != active.ruleset_version:
            return result("PREVENTED", "transition target basis does not match active policy", tid=transition.transition_id)
        try:
            effective = _parse_ts(transition.effective_at)
        except Exception:
            return result("INDETERMINATE", "transition effective time malformed", tid=transition.transition_id)

        if now < effective:
            if same_basis:
                self.watermark.accept_policy(active)
                return result("ALLOW", "transition not yet effective; existing policy basis remains active", tid=transition.transition_id)
            return result("PREVENTED", "future transition cannot authorise changed policy basis early", tid=transition.transition_id)

        transition_class = transition.transition_class
        if authority.break_glass and not transition.break_glass_compatible:
            return result("PREVENTED", "break-glass authority requires separate transition semantics", tid=transition.transition_id)
        if transition_class == "NON_MATERIAL":
            if not transition.compatibility_explicit:
                return result("PREVENTED", "non-material transition lacks explicit compatibility", tid=transition.transition_id)
            self.watermark.accept_policy(active)
            return result("ALLOW", "explicitly compatible non-material transition", tid=transition.transition_id)
        if transition_class == "REVALIDATE":
            self.watermark.accept_policy(active)
            return result("REVALIDATE", "outstanding authority requires new determination", revalidate=True, tid=transition.transition_id)
        if transition_class == "INVALIDATE":
            self.watermark.mark_invalidated(authority.authority_id)
            self.watermark.accept_policy(active)
            return result("PREVENTED", "outstanding authority invalidated by policy transition", tid=transition.transition_id)
        return result("INDETERMINATE", "unsupported or ambiguous transition semantics", tid=transition.transition_id)

    def revalidate(self, authority: OutstandingAuthority, active: PolicyState, new_authority_id: str, now: str, expires_at: str) -> OutstandingAuthority:
        return OutstandingAuthority(
            authority_id=new_authority_id,
            policy_id=active.policy_id,
            policy_version=active.policy_version,
            ruleset_version=active.ruleset_version,
            deployment_profile_id=active.deployment_profile_id,
            deployment_profile_version=active.deployment_profile_version,
            exact_commit_hash=authority.exact_commit_hash,
            issued_at=now,
            expires_at=expires_at,
            invalidated=False,
            break_glass=authority.break_glass,
        )
