"""HARDEN-011 shared execution-authority reference controls.

SQLite stores model separate rollback domains. Executor proofs are verified against
an independently configured registry, not against caller-supplied secret material.
Reference-model evidence only; not production IAM/KMS/HSM/distributed-storage proof.
"""
from dataclasses import dataclass
import hashlib, hmac, os, sqlite3

def payload_digest(payload:str)->str:
    return hashlib.sha256(payload.encode()).hexdigest()

@dataclass(frozen=True)
class CapabilityRecord:
    token:str; bind_digest:str; attempt_id:str; payload_digest:str; executor_id:str

class SQLiteConsumptionAnchor:
    """Independent monotonic consumed-token anchor; use a separate rollback domain."""
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as c:
            c.execute("CREATE TABLE IF NOT EXISTS consumed(token TEXT PRIMARY KEY)")
    def is_consumed(self,token):
        with sqlite3.connect(self.path) as c:
            return c.execute("SELECT 1 FROM consumed WHERE token=?",(token,)).fetchone() is not None
    def mark_consumed(self,token):
        with sqlite3.connect(self.path,timeout=5,isolation_level="IMMEDIATE") as c:
            try:
                c.execute("INSERT INTO consumed(token) VALUES(?)",(token,))
                return True
            except sqlite3.IntegrityError:
                return False

class ExecutorIdentityRegistry:
    """Independent verifier-side registry of trusted executor credentials."""
    def __init__(self, trusted_secrets):
        self._trusted=dict(trusted_secrets)
    def verify(self,executor_id,token,proof):
        secret=self._trusted.get(executor_id)
        if secret is None: return False
        expected=hmac.new(secret.encode(),(executor_id+"|"+token).encode(),hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,proof)

class SQLiteExecutionAuthorityStore:
    def __init__(self,path,anchor=None):
        self.path=str(path); self.anchor=anchor
        with sqlite3.connect(self.path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS capabilities(
              token TEXT PRIMARY KEY, bind_digest TEXT NOT NULL, attempt_id TEXT NOT NULL,
              payload_digest TEXT NOT NULL, executor_id TEXT NOT NULL, consumed INTEGER NOT NULL DEFAULT 0)""")
    def issue(self,record):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO capabilities(token,bind_digest,attempt_id,payload_digest,executor_id,consumed) VALUES(?,?,?,?,?,0)",
                      (record.token,record.bind_digest,record.attempt_id,record.payload_digest,record.executor_id))
    def consume(self,token,bind_digest,attempt_id,payload_digest_,executor_id):
        if self.anchor and self.anchor.is_consumed(token): return False
        with sqlite3.connect(self.path,timeout=5,isolation_level="IMMEDIATE") as c:
            row=c.execute("""SELECT consumed FROM capabilities WHERE token=? AND bind_digest=? AND attempt_id=? AND payload_digest=? AND executor_id=?""",
              (token,bind_digest,attempt_id,payload_digest_,executor_id)).fetchone()
            if row is None or row[0]: return False
            # Anchor first: if process fails after this point the token fails closed.
            if self.anchor and not self.anchor.mark_consumed(token): return False
            cur=c.execute("UPDATE capabilities SET consumed=1 WHERE token=? AND consumed=0",(token,))
            return cur.rowcount==1

class ExecutionGateway:
    def __init__(self,store,executor_id,executor_secret,identity_registry=None):
        self.store=store; self.executor_id=executor_id; self._secret=executor_secret
        self.identity_registry=identity_registry or ExecutorIdentityRegistry({executor_id:executor_secret})
    def executor_proof(self,token):
        return hmac.new(self._secret.encode(),(self.executor_id+"|"+token).encode(),hashlib.sha256).hexdigest()
    def issue(self,bind,attempt_id,payload):
        if not bind.complete() or bind.attempt_id!=attempt_id: raise ValueError("BIND_ATTEMPT_MISMATCH")
        nonce=os.urandom(16).hex()
        token=hashlib.sha256((bind.digest()+"|"+attempt_id+"|"+payload_digest(payload)+"|"+self.executor_id+"|"+nonce).encode()).hexdigest()
        self.store.issue(CapabilityRecord(token,bind.digest(),attempt_id,payload_digest(payload),self.executor_id))
        return token
    def commit(self,sink,bind,attempt_id,payload,token,proof):
        if not self.identity_registry.verify(self.executor_id,token,proof): return "BLOCKED"
        if not self.store.consume(token,bind.digest(),attempt_id,payload_digest(payload),self.executor_id): return "BLOCKED"
        sink.append((attempt_id,payload))
        return "COMMITTED"
