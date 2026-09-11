from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def _parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _version_key(value: str) -> tuple[int, ...]:
    if not isinstance(value, str) or not re.fullmatch(r"\d+(?:\.\d+)*", value):
        raise ValueError("non-comparable policy version")
    return tuple(int(part) for part in value.split("."))


def _strict_int(value) -> int:
    if type(value) is not int:
        raise ValueError("authority/state counter must be exact integer")
    if value < 0:
        raise ValueError("authority/state counter must be non-negative")
    return value


@dataclass(frozen=True)
class DistributedAuthorityGrant:
    cluster_id: str
    deployment_profile_id: str
    node_id: str
    authority_epoch: int
    lease_id: str
    issued_at: str
    expires_at: str
    state_epoch: int
    state_sequence: int
    policy_version: str
    role: str = "EXECUTION_AUTHORITY"


@dataclass(frozen=True)
class NodeObservation:
    node_id: str
    authority_epoch: int
    state_epoch: int
    state_sequence: int
    policy_version: str
    lease_id: str
    observed_at: str
    replica_age_seconds: int = 0


@dataclass(frozen=True)
class DistributedDecision:
    status: str
    reason: str
    node_id: str
    authority_epoch: int | None = None
    lease_id: str | None = None


class DistributedAuthorityStore:
    """Small durable reference store. It is not a production consensus system."""

    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        self.db = sqlite3.connect(self.path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS watermarks (
                cluster_id TEXT NOT NULL,
                deployment_id TEXT NOT NULL,
                authority_epoch INTEGER NOT NULL,
                lease_id TEXT NOT NULL,
                leader_node_id TEXT NOT NULL,
                state_epoch INTEGER NOT NULL,
                state_sequence INTEGER NOT NULL,
                policy_version TEXT NOT NULL,
                PRIMARY KEY (cluster_id, deployment_id)
            )
        """)
        self.db.commit()

    def close(self):
        self.db.close()

    def read(self, cluster_id: str, deployment_id: str):
        row = self.db.execute(
            "SELECT authority_epoch, lease_id, leader_node_id, state_epoch, state_sequence, policy_version FROM watermarks WHERE cluster_id=? AND deployment_id=?",
            (cluster_id, deployment_id),
        ).fetchone()
        if row is None:
            return None
        return {
            "authority_epoch": row[0], "lease_id": row[1], "leader_node_id": row[2],
            "state_epoch": row[3], "state_sequence": row[4], "policy_version": row[5],
        }

    def accept(self, grant: DistributedAuthorityGrant) -> tuple[bool, str]:
        ae = _strict_int(grant.authority_epoch)
        se = _strict_int(grant.state_epoch)
        ss = _strict_int(grant.state_sequence)
        _version_key(grant.policy_version)
        current = self.read(grant.cluster_id, grant.deployment_profile_id)
        if current is not None:
            if ae < current["authority_epoch"]:
                return False, "authority epoch behind high-watermark"
            if ae == current["authority_epoch"]:
                if grant.lease_id != current["lease_id"] or grant.node_id != current["leader_node_id"]:
                    return False, "conflicting grant at accepted authority epoch"
            if (se, ss) < (current["state_epoch"], current["state_sequence"]):
                return False, "state position behind high-watermark"
            if _version_key(grant.policy_version) < _version_key(current["policy_version"]):
                return False, "policy version behind high-watermark"
        self.db.execute(
            "INSERT INTO watermarks(cluster_id,deployment_id,authority_epoch,lease_id,leader_node_id,state_epoch,state_sequence,policy_version) VALUES(?,?,?,?,?,?,?,?) "
            "ON CONFLICT(cluster_id,deployment_id) DO UPDATE SET authority_epoch=excluded.authority_epoch, lease_id=excluded.lease_id, leader_node_id=excluded.leader_node_id, state_epoch=excluded.state_epoch, state_sequence=excluded.state_sequence, policy_version=excluded.policy_version",
            (grant.cluster_id, grant.deployment_profile_id, ae, grant.lease_id, grant.node_id, se, ss, grant.policy_version),
        )
        self.db.commit()
        return True, "accepted"


class DistributedAuthorityGate:
    def __init__(self, store: DistributedAuthorityStore, clock, *, cluster_id: str, deployment_profile_id: str, max_replica_age_seconds: int = 30):
        self.store = store
        self.clock = clock
        self.cluster_id = cluster_id
        self.deployment_profile_id = deployment_profile_id
        self.max_replica_age_seconds = max_replica_age_seconds

    def _now(self) -> datetime:
        now = self.clock.now()
        if isinstance(now, str):
            now = _parse_ts(now)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return now.astimezone(timezone.utc)

    def activate(self, node_id: str, grant: DistributedAuthorityGrant | None, observation: NodeObservation | None, *, authority_service_available: bool = True) -> DistributedDecision:
        if not authority_service_available:
            return DistributedDecision("INDETERMINATE", "authority service unavailable; local promotion prohibited", node_id)
        if grant is None or observation is None:
            return DistributedDecision("INDETERMINATE", "grant or distributed observation unavailable", node_id)
        try:
            ae = _strict_int(grant.authority_epoch)
            se = _strict_int(grant.state_epoch)
            ss = _strict_int(grant.state_sequence)
            _strict_int(observation.authority_epoch)
            _strict_int(observation.state_epoch)
            _strict_int(observation.state_sequence)
            _version_key(grant.policy_version)
            _version_key(observation.policy_version)
            now = self._now()
            issued = _parse_ts(grant.issued_at)
            expires = _parse_ts(grant.expires_at)
            observed = _parse_ts(observation.observed_at)
        except Exception:
            return DistributedDecision("INDETERMINATE", "distributed authority evidence malformed", node_id)
        if grant.cluster_id != self.cluster_id:
            return DistributedDecision("PREVENTED", "cluster identity mismatch", node_id, ae, grant.lease_id)
        if grant.deployment_profile_id != self.deployment_profile_id:
            return DistributedDecision("PREVENTED", "deployment identity mismatch", node_id, ae, grant.lease_id)
        if grant.node_id != node_id or observation.node_id != node_id:
            return DistributedDecision("PREVENTED", "node identity mismatch", node_id, ae, grant.lease_id)
        if grant.role != "EXECUTION_AUTHORITY":
            return DistributedDecision("PREVENTED", "grant role is not execution authority", node_id, ae, grant.lease_id)
        if now < issued:
            return DistributedDecision("PREVENTED", "grant not yet valid", node_id, ae, grant.lease_id)
        if now >= expires:
            return DistributedDecision("PREVENTED", "leadership lease expired", node_id, ae, grant.lease_id)
        if observed > now:
            return DistributedDecision("PREVENTED", "replica observation is future-dated", node_id, ae, grant.lease_id)
        if observation.replica_age_seconds > self.max_replica_age_seconds:
            return DistributedDecision("PREVENTED", "replica observation stale", node_id, ae, grant.lease_id)
        if observation.authority_epoch != ae or observation.lease_id != grant.lease_id:
            return DistributedDecision("PREVENTED", "observation does not match leadership grant", node_id, ae, grant.lease_id)
        if (observation.state_epoch, observation.state_sequence) < (se, ss):
            return DistributedDecision("PREVENTED", "observed state behind leadership grant", node_id, ae, grant.lease_id)
        if _version_key(observation.policy_version) < _version_key(grant.policy_version):
            return DistributedDecision("PREVENTED", "observed policy behind leadership grant", node_id, ae, grant.lease_id)
        accepted, reason = self.store.accept(grant)
        if not accepted:
            return DistributedDecision("PREVENTED", reason, node_id, ae, grant.lease_id)
        return DistributedDecision("ACTIVE", "distributed execution authority established", node_id, ae, grant.lease_id)

    def pre_consequence_check(self, node_id: str, grant: DistributedAuthorityGrant, observation: NodeObservation) -> DistributedDecision:
        current = self.store.read(self.cluster_id, self.deployment_profile_id)
        if current is None:
            return DistributedDecision("INDETERMINATE", "distributed high-watermark unavailable", node_id)
        try:
            _strict_int(grant.authority_epoch)
            _strict_int(observation.state_epoch)
            _strict_int(observation.state_sequence)
            _version_key(observation.policy_version)
            now = self._now()
            expires = _parse_ts(grant.expires_at)
        except Exception:
            return DistributedDecision("INDETERMINATE", "distributed execution evidence malformed", node_id)
        if now >= expires:
            return DistributedDecision("PREVENTED", "leadership lease expired before consequence formation", node_id, grant.authority_epoch, grant.lease_id)
        if grant.authority_epoch != current["authority_epoch"]:
            return DistributedDecision("PREVENTED", "node fenced by newer authority epoch", node_id, grant.authority_epoch, grant.lease_id)
        if grant.lease_id != current["lease_id"]:
            return DistributedDecision("PREVENTED", "node fenced by current lease identity", node_id, grant.authority_epoch, grant.lease_id)
        if node_id != current["leader_node_id"]:
            return DistributedDecision("PREVENTED", "node is not current execution leader", node_id, grant.authority_epoch, grant.lease_id)
        if (observation.state_epoch, observation.state_sequence) < (current["state_epoch"], current["state_sequence"]):
            return DistributedDecision("PREVENTED", "node state behind distributed high-watermark", node_id, grant.authority_epoch, grant.lease_id)
        if _version_key(observation.policy_version) < _version_key(current["policy_version"]):
            return DistributedDecision("PREVENTED", "node policy behind distributed high-watermark", node_id, grant.authority_epoch, grant.lease_id)
        return DistributedDecision("ACTIVE", "execution fence remains current", node_id, grant.authority_epoch, grant.lease_id)
