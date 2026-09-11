# ASVH-HARDEN-009 — Distributed Failure & Split-Brain Authority

Status: FROZEN SPECIFICATION — implementation not yet demonstrated

## 1. Purpose

HARDEN-009 tests whether more than one Runtime Authority node can simultaneously become execution-authoritative for the same protected deployment when they observe divergent distributed state, stale replicas, partitioned leadership information or failover during a consequence-formation interval.

The objective is not to implement a production consensus system. It is to model and verify the authority invariants that a distributed deployment would need to preserve.

## 2. Core principle

A Runtime Authority node is not execution-authoritative merely because it is healthy, reachable or locally believes itself to be leader.

Execution authority requires a current, externally fenced leadership grant whose epoch is not behind the strongest accepted distributed authority state.

## 3. Distributed Authority Grant

A `DistributedAuthorityGrant` SHALL bind:

- cluster_id
- deployment_profile_id
- node_id
- authority_epoch
- lease_id
- issued_at
- expires_at
- state_epoch
- state_sequence
- policy_version
- exact role `EXECUTION_AUTHORITY`

The authority epoch is monotonic and acts as the fencing value.

## 4. Node observations

Each node may hold a local `NodeObservation` containing:

- node_id
- observed authority epoch
- observed state epoch/sequence
- observed policy version
- observed leader/lease id
- observation time
- replica freshness

Local observation is evidence, not authority.

## 5. Activation requirements

A node SHALL NOT return ACTIVE unless all are true:

1. grant cluster/deployment/node identities match the node and expected deployment;
2. grant role is exactly EXECUTION_AUTHORITY;
3. grant is temporally valid against trusted harness time;
4. grant authority epoch is not below the distributed high-watermark;
5. state epoch/sequence is not below the strongest accepted state position;
6. policy version is not below the accepted policy high-watermark;
7. grant lease identity is current for the accepted authority epoch;
8. conflicting grants at the same authority epoch are not accepted;
9. replica freshness is within the declared maximum age;
10. partition or uncertainty that prevents establishing any of these conditions produces INDETERMINATE or PREVENTED, never ALLOW.

## 6. Consequence formation fencing

A node that was ACTIVE when a consequence began SHALL re-check its execution fence immediately before consequence formation.

If a newer authority epoch, different lease identity or incompatible state/policy position has been accepted since claim, the prior node SHALL be fenced and SHALL NOT form a new governed consequence.

## 7. Split-brain semantics

If two nodes present different grants for the same cluster/deployment:

- higher authority epoch wins if otherwise valid;
- lower authority epoch is fenced;
- two different grants with the same authority epoch are a conflict and SHALL NOT both become ACTIVE;
- loss of the authority service SHALL NOT cause independent local promotion.

## 8. Stale replica promotion

A promoted node SHALL NOT become ACTIVE merely because its leadership grant is newer if its required state position is behind the accepted state high-watermark.

Leadership freshness does not compensate for stale authority/state evidence.

## 9. Frozen conformance tests

H9-001 single valid leader grant becomes ACTIVE.
H9-002 lower authority epoch is fenced after higher epoch accepted.
H9-003 expired leadership lease is PREVENTED.
H9-004 future-issued grant is PREVENTED.
H9-005 wrong cluster identity is PREVENTED.
H9-006 wrong deployment identity is PREVENTED.
H9-007 grant for different node is PREVENTED.
H9-008 non-execution role is PREVENTED.
H9-009 stale replica state cannot be promoted by newer leadership grant.
H9-010 state rollback after activation prevents consequence formation.
H9-011 policy rollback after activation prevents consequence formation.
H9-012 newer authority epoch appearing after claim fences prior node.
H9-013 different lease identity at same epoch produces conflict.
H9-014 identical repeated grant is idempotently accepted.
H9-015 malformed authority epoch fails explicitly.
H9-016 malformed temporal state fails explicitly.
H9-017 authority service unavailable does not cause local self-promotion.
H9-018 two nodes cannot both be ACTIVE under conflicting same-epoch grants.
H9-019 newer leader with current state can replace prior leader.
H9-020 restart/recovery preserves the distributed authority and state high-watermarks within the reference store boundary.

## 10. Hostile review targets

The hostile suite SHALL attempt at least:

- same epoch, different node and different lease;
- higher leadership epoch paired with stale state;
- local clock rollback or caller-supplied time;
- replay of a previously valid lease after a newer epoch;
- boolean/non-integer authority epochs;
- authority service outage with cached grant;
- failover between claim and consequence formation;
- policy-version rollback masked by newer leadership epoch.

## 11. Evidence boundary

A successful HARDEN-009 run demonstrates only reference-harness fencing and distributed-state semantics. It does not demonstrate production consensus, linearizability, quorum durability, network partition handling in a real cluster, cloud failure-domain independence, or real EPR non-bypassability.

## 12. Permitted claim after PASS

> Within the declared ASVH reference-harness boundary, execution authority is fenced by a monotonic distributed authority epoch and current lease identity. A stale, superseded or conflicting Runtime Authority node cannot remain execution-authoritative solely because it is locally healthy or holds a cached prior grant. Leadership promotion does not override stale state or policy position, and authority is re-established before consequence formation.
