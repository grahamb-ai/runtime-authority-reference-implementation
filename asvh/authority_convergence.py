"""HARDEN-010 authority dependency convergence reference mechanism."""
from dataclasses import dataclass,field
from enum import Enum
from typing import Callable
import hashlib,json
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
    integrity_verified:bool; completeness_verified:bool; provenance_verified:bool; covered_authorities:frozenset[tuple[str,str]]; verifier_id:str=""; records_digest:str=""; recovery_context:str=""; attestation:str=""; trust_policy_digest:str=""
def recovery_records_digest(records):
    c=[{"source_id":r.source_id,"subject_id":r.subject_id,"revision":r.revision,"status":r.status.upper()} for r in records];c.sort(key=lambda x:(x["source_id"],x["subject_id"],x["revision"],x["status"]));return hashlib.sha256(json.dumps(c,separators=(",",":"),sort_keys=True).encode()).hexdigest()
@dataclass(frozen=True)
class RecoveryVerifier:
    trusted_verifier_ids:frozenset[str]; expected_context:str; verify_attestation:Callable[[RecoveryEvidence],bool]
    def verify(self,records,evidence):
        try:return evidence.verifier_id in self.trusted_verifier_ids and evidence.recovery_context==self.expected_context and evidence.records_digest==recovery_records_digest(records) and bool(evidence.attestation) and bool(self.verify_attestation(evidence)) and evidence.integrity_verified and evidence.completeness_verified and evidence.provenance_verified
        except Exception:return False
@dataclass(frozen=True)
class RecoveryTrustPolicy:
    verifier:RecoveryVerifier; required_authorities:frozenset[tuple[str,str]]; policy_revision:int=0; standing:str="UNKNOWN"
    def digest(self):
        p={"policy_revision":self.policy_revision,"standing":self.standing.upper(),"required_authorities":sorted([list(x) for x in self.required_authorities]),"trusted_verifier_ids":sorted(self.verifier.trusted_verifier_ids),"expected_context":self.verifier.expected_context};return hashlib.sha256(json.dumps(p,separators=(",",":"),sort_keys=True).encode()).hexdigest()
    def validate(self,records,evidence):
        ids={(r.source_id,r.subject_id) for r in records};return self.policy_revision>=0 and self.standing.upper() in POSITIVE and bool(self.required_authorities) and ids==set(evidence.covered_authorities)==set(self.required_authorities) and len(records)==len(set(records)) and evidence.trust_policy_digest==self.digest() and self.verifier.verify(records,evidence)
@dataclass(frozen=True)
class TrustPolicyPosition:
    policy_revision:int; policy_digest:str; standing:str; source_id:str=""; age_seconds:int=-1; authority_epoch:int=-1; attestation:str=""; observation_context:str=""; attempt_id:str=""
@dataclass(frozen=True)
class PolicyPositionVerifier:
    authoritative_source_id:str; expected_context:str; max_age_seconds:int; verify_attestation:Callable[[TrustPolicyPosition],bool]; expected_attempt_id:str=""
    def verify(self,p):
        try:
            if not p.source_id or not p.observation_context or not p.attempt_id:return False
            if not self.expected_attempt_id:return False
            if p.source_id!=self.authoritative_source_id or p.observation_context!=self.expected_context:return False
            if p.attempt_id!=self.expected_attempt_id:return False
            if p.policy_revision<0 or p.authority_epoch<0 or p.age_seconds<0 or p.age_seconds>self.max_age_seconds:return False
            if not p.policy_digest or not p.attestation or p.standing.upper() not in POSITIVE:return False
            return bool(self.verify_attestation(p))
        except Exception:return False
@dataclass(frozen=True)
class ConsequenceBind:
    policy_revision:int; policy_digest:str; authority_epoch:int; observation_context:str; source_id:str=""; attestation_digest:str=""; attempt_id:str=""
    def complete(self):
        return self.policy_revision>=0 and self.authority_epoch>=0 and bool(self.policy_digest) and bool(self.observation_context) and bool(self.source_id) and bool(self.attestation_digest) and bool(self.attempt_id)
    def digest(self):
        if not self.complete():raise ValueError("incomplete consequence bind")
        p={"policy_revision":self.policy_revision,"policy_digest":self.policy_digest,"authority_epoch":self.authority_epoch,"observation_context":self.observation_context,"source_id":self.source_id,"attestation_digest":self.attestation_digest,"attempt_id":self.attempt_id};return hashlib.sha256(json.dumps(p,separators=(",",":"),sort_keys=True).encode()).hexdigest()
def bind_from_position(p):
    if not p.source_id or not p.attestation or not p.observation_context or not p.attempt_id:raise ValueError("incomplete policy position")
    return ConsequenceBind(p.policy_revision,p.policy_digest,p.authority_epoch,p.observation_context,p.source_id,hashlib.sha256(p.attestation.encode()).hexdigest(),p.attempt_id)
@dataclass
class AuthorityConvergenceState:
    recovery_trusted:bool=False; recovery_policy_revision:int|None=None; recovery_policy_digest:str|None=None; high_watermarks:dict[tuple[str,str],int]=field(default_factory=dict); revision_status:dict[tuple[str,str,int],str]=field(default_factory=dict)
    @classmethod
    def bootstrap(cls):return cls(recovery_trusted=True)
    @classmethod
    def recover(cls,records,evidence=None,*,trust_policy=None):
        if not records or evidence is None or trust_policy is None or not trust_policy.validate(records,evidence):return cls(recovery_trusted=False)
        s=cls(True,trust_policy.policy_revision,trust_policy.digest())
        for r in records:
            if r.revision<0:return cls(recovery_trusted=False)
            identity=(r.source_id,r.subject_id);key=(r.source_id,r.subject_id,r.revision);status=r.status.upper();prior=s.revision_status.get(key)
            if prior is not None and prior!=status:return cls(recovery_trusted=False)
            s.revision_status[key]=status;current=s.high_watermarks.get(identity)
            if current is None or r.revision>current:s.high_watermarks[identity]=r.revision
        return s
    def policy_still_current(self,current,verifier):return self.recovery_trusted and self.recovery_policy_revision is not None and self.recovery_policy_digest is not None and verifier.verify(current) and current.policy_revision==self.recovery_policy_revision and current.policy_digest==self.recovery_policy_digest
    def observe(self,dep):
        if not self.recovery_trusted:return ConvergenceResult.INDETERMINATE
        identity=(dep.source_id,dep.subject_id);previous=self.high_watermarks.get(identity)
        if previous is not None and dep.revision<previous:return ConvergenceResult.PREVENTED
        key=(dep.source_id,dep.subject_id,dep.revision);status=dep.status.upper();prior=self.revision_status.get(key)
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
    req=[d for d in basis.dependencies if d.required]
    if not req:return ConvergenceResult.INDETERMINATE
    if requirements is not None:
        expected={(r.authoritative_source_id,r.subject_id) for r in requirements if r.required};actual={(d.source_id,d.subject_id) for d in req}
        if actual!=expected:return ConvergenceResult.INDETERMINATE
        if state is not None and state.recovery_trusted and state.high_watermarks and not expected.issubset(set(state.high_watermarks)):return ConvergenceResult.INDETERMINATE
    seen=set();same={};outcome=ConvergenceResult.ACTIVE
    for dep in req:
        identity=(dep.source_id,dep.subject_id)
        if identity in seen:return ConvergenceResult.INDETERMINATE
        seen.add(identity);ck=(dep.subject_id,dep.revision);prior=same.get(ck)
        if prior is not None and prior!=dep.status.upper():return ConvergenceResult.INDETERMINATE
        same[ck]=dep.status.upper()
        if state is not None:
            m=state.observe(dep)
            if m!=ConvergenceResult.ACTIVE:return m
        r=evaluate_dependency(dep,max_age_seconds)
        if r==ConvergenceResult.PREVENTED:return r
        if r==ConvergenceResult.INDETERMINATE:outcome=r
    return outcome
def consequence_time_converge(read_current:Callable[[],DependencyBasis],max_age_seconds=30,*,requirements=None,state=None,read_policy_position=None,policy_position_verifier=None):
    bind=None
    if state is not None and state.recovery_policy_revision is not None:
        if read_policy_position is None or policy_position_verifier is None:return ConvergenceResult.INDETERMINATE,None
        try:p=read_policy_position()
        except Exception:return ConvergenceResult.INDETERMINATE,None
        if not state.policy_still_current(p,policy_position_verifier):return ConvergenceResult.INDETERMINATE,None
        try:bind=bind_from_position(p)
        except Exception:return ConvergenceResult.INDETERMINATE,None
    try:result=converge(read_current(),max_age_seconds,requirements=requirements,state=state)
    except Exception:return ConvergenceResult.INDETERMINATE,None
    return result,(bind if result==ConvergenceResult.ACTIVE else None)
def final_bind_and_execute(*,expected_bind,read_policy_position,policy_position_verifier,execute):
    """Reference final bind. Callback invocation is not a production non-bypassability claim."""
    if expected_bind is None:return ConvergenceResult.INDETERMINATE
    try:
        if not expected_bind.complete():return ConvergenceResult.INDETERMINATE
    except Exception:return ConvergenceResult.INDETERMINATE
    try:p=read_policy_position()
    except Exception:return ConvergenceResult.INDETERMINATE
    if not policy_position_verifier.verify(p):return ConvergenceResult.INDETERMINATE
    try:current=bind_from_position(p)
    except Exception:return ConvergenceResult.INDETERMINATE
    try:
        if current.digest()!=expected_bind.digest():return ConvergenceResult.INDETERMINATE
    except Exception:return ConvergenceResult.INDETERMINATE
    try:return execute(expected_bind)
    except Exception:return ConvergenceResult.INDETERMINATE
