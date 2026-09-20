"""HARDEN-011 shared execution-authority reference store.

Reference-model control only: SQLite supplies durable/shared atomic consumption for
tests on one filesystem. Executor authentication is represented by an explicit
identity + secret proof. This is not production IAM/KMS/HSM or distributed DB evidence.
"""
from dataclasses import dataclass
import hashlib, hmac, os, sqlite3, threading

def payload_digest(payload:str)->str:
    return hashlib.sha256(payload.encode()).hexdigest()

@dataclass(frozen=True)
class CapabilityRecord:
    token:str; bind_digest:str; attempt_id:str; payload_digest:str; executor_id:str

class SQLiteExecutionAuthorityStore:
    def __init__(self,path):
        self.path=str(path)
        with sqlite3.connect(self.path) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS capabilities(
              token TEXT PRIMARY KEY, bind_digest TEXT NOT NULL, attempt_id TEXT NOT NULL,
              payload_digest TEXT NOT NULL, executor_id TEXT NOT NULL, consumed INTEGER NOT NULL DEFAULT 0)""")
    def issue(self,record):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO capabilities(token,bind_digest,attempt_id,payload_digest,executor_id,consumed) VALUES(?,?,?,?,?,0)",
                      (record.token,record.bind_digest,record.attempt_id,record.payload_digest,record.executor_id))
    def consume(self,token,bind_digest,attempt_id,payload_digest_,executor_id):
        with sqlite3.connect(self.path,timeout=5,isolation_level="IMMEDIATE") as c:
            cur=c.execute("""UPDATE capabilities SET consumed=1
              WHERE token=? AND bind_digest=? AND attempt_id=? AND payload_digest=? AND executor_id=? AND consumed=0""",
              (token,bind_digest,attempt_id,payload_digest_,executor_id))
            return cur.rowcount==1

class ExecutionGateway:
    def __init__(self,store,executor_id,executor_secret):
        self.store=store; self.executor_id=executor_id; self._secret=executor_secret
    def executor_proof(self,token):
        return hmac.new(self._secret.encode(),(self.executor_id+"|"+token).encode(),hashlib.sha256).hexdigest()
    def issue(self,bind,attempt_id,payload):
        if not bind.complete() or bind.attempt_id!=attempt_id: raise ValueError("BIND_ATTEMPT_MISMATCH")
        nonce=os.urandom(16).hex()
        token=hashlib.sha256((bind.digest()+"|"+attempt_id+"|"+payload_digest(payload)+"|"+self.executor_id+"|"+nonce).encode()).hexdigest()
        self.store.issue(CapabilityRecord(token,bind.digest(),attempt_id,payload_digest(payload),self.executor_id))
        return token
    def commit(self,sink,bind,attempt_id,payload,token,proof):
        expected=self.executor_proof(token)
        if not hmac.compare_digest(expected,proof): return "BLOCKED"
        if not self.store.consume(token,bind.digest(),attempt_id,payload_digest(payload),self.executor_id): return "BLOCKED"
        sink.append((attempt_id,payload))
        return "COMMITTED"
