"""HARDEN-010 authority dependency convergence reference mechanism."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import hashlib, json

class ConvergenceResult(str,Enum): ACTIVE="ACTIVE"; PREVENTED="PREVENTED"; INDETERMINATE="INDETERMINATE"
POSITIVE={"AUTHORISED","VALID","CLEAR","ACTIVE"}; PROHIBITIVE={"REVOKED","SUSPENDED","WITHDRAWN","SUPERSEDED","EXPIRED","INVALID"}; INDETERMINATE={"UNKNOWN","UNAVAILABLE","CONFLICT","INDETERMINATE"}
@dataclass(frozen=True)
class AuthorityDependency: source_id:str; subject_id:str; revision:int; status:str; age_seconds:int; required:bool=True
@dataclass(frozen=True)
class DependencyRequirement: subject_id:str; authoritative_source_id:str; required:bool=True
@dataclass(frozen=True)
class DependencyBasis: dependencies:tuple[AuthorityDependency,...]
@dataclass(frozen=True)
class RecoveredAuthorityRecord: source_id:str; subject_id:str; revision:int; status:str
@dataclass(frozen=True)
class RecoveryEvidence:
    integrity_verified:bool; completeness_verified:bool; provenance_verified:bool
    covered_authorities:frozenset[tuple[str,str]]
    verifier_id:str=""; records_digest:str=""; recovery_context:str=""; attestation:str=""

def recovery_records_digest(records):
    canonical=[{"source_id":r.source_id,"subject_id":r.subject_id,"revision":r.revision,"status":r.status.upper()} for r in records]
    canonical.sort(key=lambda x:(x["source_id"],x["subject_id"],x["revision"],x["status"]))
    return hashlib.sha256(json.dumps(canonical,separators=(",",":"),sort_keys=True).encode()).hexdigest()

@dataclass(frozen=True)
class RecoveryVerifier:
    """Reference verifier boundary. `verify_attestation` is injected; crypto implementation is out of scope."""
    trusted_verifier_ids:frozenset[str]
    expected_context:str
    verify_attestation:Callable[[RecoveryEvidence],bool]
    def verify(self,records,evidence):
        if evidence.verifier_id not in self.trusted_verifier_ids:return False
        if evidence.recovery_context!=self.expected_context:return False
        if evidence.records_digest!=recovery_records_digest(records):return False
        if not evidence.attestation:return False
        if not self.verify_attestation(evidence):return False
        return evidence.integrity_verified and evidence.completeness_verified and evidence.provenance_verified

@dataclass
class AuthorityConvergenceState:
    recovery_trusted:bool=False
    high_watermarks:dict[tuple[str,str],int]=field(default_factory=dict)
    revision_status:dict[tuple[str,str,int],str]=field(default_factory=dict)
    @classmethod
    def bootstrap(cls):return cls(recovery_trusted=True)
    @classmethod
    def recover(cls,records:tuple[RecoveredAuthorityRecord,...],evidence:RecoveryEvidence|None=None,verifier:RecoveryVerifier|None=None):
        if not records or evidence is None or verifier is None or not verifier.verify(records,evidence):return cls(recovery_trusted=False)
        identities={(r.source_id,r.subject_id) for r in records}
        if identities!=set(evidence.covered_authorities):return cls(recovery_trusted=False)
        state=cls(recovery_trusted=True)
        for r in records:
            if r.revision<0:return cls(recovery_trusted=False)
            identity=(r.source_id,r.subject_id); key=(r.source_id,r.subject_id,r.revision); status=r.status.upper(); prior=state.revision_status.get(key)
            if prior is not None and prior!=status:return cls(recovery_trusted=False)
            state.revision_status[key]=status; current=state.high_watermarks.get(identity)
            if current is None or r.revision>current:state.high_watermarks[identity]=r.revision
        return state
    def observe(self,dep):
        if not self.recovery_trusted:return ConvergenceResult.INDETERMINATE
        identity=(dep.source_id,dep.subject_id); previous=self.high_watermarks.get(identity)
        if previous is not None and dep.revision<previous:return ConvergenceResult.PREVENTED
        key=(dep.source_id,dep.subject_id,dep.revision); status=dep.status.upper(); prior=self.revision_status.get(key)
        if prior is not None and prior!=status:return ConvergenceResult.INDETERMINATE
        self.revision_status[key]=status
        if previous is None or dep.revision>previous:self.high_watermarks[identity]=dep.revision
        return ConvergenceResult.ACTIVE

def evaluate_dependency(dep,max_age_seconds=30):
    if dep.revision<0 or dep.age_seconds<0 or dep.age_seconds>max_age_seconds:return ConvergenceResult.INDETERMINATE
    s=dep.status.upper()
    if s in PROHIBITIVE:return ConvergenceResult.PREVENTED
    if s in INDETERMINATE or s not in POSITIVE:return ConvergenceResult.INDETERMINATE
    return ConvergenceResult.ACTIVE

def converge(basis,max_age_seconds=30,*,requirements=None,state=None):
    required=[d for d in basis.dependencies if d.required]
    if not required:return ConvergenceResult.INDETERMINATE
    if requirements is not None:
        expected={(r.authoritative_source_id,r.subject_id) for r in requirements if r.required}; actual={(d.source_id,d.subject_id) for d in required}
        if actual!=expected:return ConvergenceResult.INDETERMINATE
        if state is not None and state.recovery_trusted and state.high_watermarks and not expected.issubset(set(state.high_watermarks)):return ConvergenceResult.INDETERMINATE
    seen=set(); same={}; outcome=ConvergenceResult.ACTIVE
    for dep in required:
        identity=(dep.source_id,dep.subject_id)
        if identity in seen:return ConvergenceResult.INDETERMINATE
        seen.add(identity); ck=(dep.subject_id,dep.revision); prior=same.get(ck)
        if prior is not None and prior!=dep.status.upper():return ConvergenceResult.INDETERMINATE
        same[ck]=dep.status.upper()
        if state is not None:
            m=state.observe(dep)
            if m!=ConvergenceResult.ACTIVE:return m
        result=evaluate_dependency(dep,max_age_seconds)
        if result==ConvergenceResult.PREVENTED:return result
        if result==ConvergenceResult.INDETERMINATE:outcome=result
    return outcome

def consequence_time_converge(read_current:Callable[[],DependencyBasis],max_age_seconds=30,*,requirements=None,state=None):return converge(read_current(),max_age_seconds,requirements=requirements,state=state)
