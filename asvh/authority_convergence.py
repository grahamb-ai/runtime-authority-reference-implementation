"""HARDEN-010 authority dependency convergence reference mechanism."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

class ConvergenceResult(str, Enum):
    ACTIVE="ACTIVE"; PREVENTED="PREVENTED"; INDETERMINATE="INDETERMINATE"
POSITIVE={"AUTHORISED","VALID","CLEAR","ACTIVE"}
PROHIBITIVE={"REVOKED","SUSPENDED","WITHDRAWN","SUPERSEDED","EXPIRED","INVALID"}
INDETERMINATE={"UNKNOWN","UNAVAILABLE","CONFLICT","INDETERMINATE"}

@dataclass(frozen=True)
class AuthorityDependency:
    source_id:str; subject_id:str; revision:int; status:str; age_seconds:int; required:bool=True
@dataclass(frozen=True)
class DependencyRequirement:
    subject_id:str; authoritative_source_id:str; required:bool=True
@dataclass(frozen=True)
class DependencyBasis:
    dependencies:tuple[AuthorityDependency,...]
@dataclass(frozen=True)
class RecoveredAuthorityRecord:
    source_id:str; subject_id:str; revision:int; status:str
@dataclass(frozen=True)
class RecoveryEvidence:
    """Reference evidence declaration, not cryptographic verification."""
    integrity_verified:bool
    completeness_verified:bool
    provenance_verified:bool
    covered_authorities:frozenset[tuple[str,str]]

@dataclass
class AuthorityConvergenceState:
    recovery_trusted:bool=False
    high_watermarks:dict[tuple[str,str],int]=field(default_factory=dict)
    revision_status:dict[tuple[str,str,int],str]=field(default_factory=dict)

    @classmethod
    def bootstrap(cls):
        return cls(recovery_trusted=True)

    @classmethod
    def recover(cls, records:tuple[RecoveredAuthorityRecord,...], evidence:RecoveryEvidence|None=None):
        if not records or evidence is None:
            return cls(recovery_trusted=False)
        if not (evidence.integrity_verified and evidence.completeness_verified and evidence.provenance_verified):
            return cls(recovery_trusted=False)
        identities={(r.source_id,r.subject_id) for r in records}
        if identities != set(evidence.covered_authorities):
            return cls(recovery_trusted=False)
        state=cls(recovery_trusted=True)
        for record in records:
            if record.revision < 0:
                return cls(recovery_trusted=False)
            identity=(record.source_id,record.subject_id)
            current=state.high_watermarks.get(identity)
            status_key=(record.source_id,record.subject_id,record.revision)
            prior=state.revision_status.get(status_key)
            status=record.status.upper()
            if prior is not None and prior != status:
                return cls(recovery_trusted=False)
            state.revision_status[status_key]=status
            if current is None or record.revision > current:
                state.high_watermarks[identity]=record.revision
        return state

    def observe(self,dep:AuthorityDependency):
        if not self.recovery_trusted: return ConvergenceResult.INDETERMINATE
        identity=(dep.source_id,dep.subject_id); previous=self.high_watermarks.get(identity)
        if previous is not None and dep.revision < previous: return ConvergenceResult.PREVENTED
        key=(dep.source_id,dep.subject_id,dep.revision); status=dep.status.upper(); prior=self.revision_status.get(key)
        if prior is not None and prior != status: return ConvergenceResult.INDETERMINATE
        self.revision_status[key]=status
        if previous is None or dep.revision > previous: self.high_watermarks[identity]=dep.revision
        return ConvergenceResult.ACTIVE

def evaluate_dependency(dep,max_age_seconds=30):
    if dep.revision<0 or dep.age_seconds<0 or dep.age_seconds>max_age_seconds:return ConvergenceResult.INDETERMINATE
    status=dep.status.upper()
    if status in PROHIBITIVE:return ConvergenceResult.PREVENTED
    if status in INDETERMINATE or status not in POSITIVE:return ConvergenceResult.INDETERMINATE
    return ConvergenceResult.ACTIVE

def converge(basis,max_age_seconds=30,*,requirements=None,state=None):
    required=[d for d in basis.dependencies if d.required]
    if not required:return ConvergenceResult.INDETERMINATE
    if requirements is not None:
        expected={(r.authoritative_source_id,r.subject_id) for r in requirements if r.required}; actual={(d.source_id,d.subject_id) for d in required}
        if actual!=expected:return ConvergenceResult.INDETERMINATE
        if state is not None and state.recovery_trusted and state.high_watermarks:
            if not expected.issubset(set(state.high_watermarks)):
                return ConvergenceResult.INDETERMINATE
    seen=set(); same_revision={}; outcome=ConvergenceResult.ACTIVE
    for dep in required:
        identity=(dep.source_id,dep.subject_id)
        if identity in seen:return ConvergenceResult.INDETERMINATE
        seen.add(identity); ck=(dep.subject_id,dep.revision); prior=same_revision.get(ck)
        if prior is not None and prior!=dep.status.upper():return ConvergenceResult.INDETERMINATE
        same_revision[ck]=dep.status.upper()
        if state is not None:
            monotonic=state.observe(dep)
            if monotonic!=ConvergenceResult.ACTIVE:return monotonic
        result=evaluate_dependency(dep,max_age_seconds)
        if result==ConvergenceResult.PREVENTED:return result
        if result==ConvergenceResult.INDETERMINATE:outcome=result
    return outcome

def consequence_time_converge(read_current:Callable[[],DependencyBasis],max_age_seconds=30,*,requirements=None,state=None):
    return converge(read_current(),max_age_seconds,requirements=requirements,state=state)
