# Wave 36 construction: fixed-triangle prism clauses

```yaml
role: construction
date_utc: 2026-07-27T00:10:32Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: DERIVED
scope: >
  Exact P=0 clause strengthening for the five normalized rooted endpoint
  branches 4, 5, 8, 10, and 12.
inputs:
  code/root_model.py: 2a1f074f29f2e00e38437bf81418771d57ab41335605b9f3b9f2cae061a1624e
  code/sat_model.py: 45f0da74619b31a1a31cc407f702f8e86a0597ee73d29ec268528cd89980aef8
  code/matching_orbits.py: 1ba68393c385ef296458555b7c48533786ea592a50bec589be675f95fd550240
  code/wave35_n3_endpoint_root_scout.py: 04ef058c3a14ed8790773f015edc16f4ae1da1bcb011e3b795f0d16229f7ff7e
method: >
  Enumerate every triangular prism whose first triangle is one of the six
  coordinate-2 triangles fixed by a surviving joint branch, filter against
  the endpoint and branch units, and retain a deterministic clause catalog.
command: |
  $env:PYTHONPATH='code;attempts\wave36-rooted-branches'
  .venv\Scripts\python -B -m unittest discover -s attempts\wave36-rooted-branches -p "test_*.py" -v
outputs:
  attempts/wave36-rooted-branches/derived-clause-catalog.json: e6cd8b32fee88fff300ce153c728b7fe82f6aca9c29526d852ff4a4b564f9092
  attempts/wave36-rooted-branches/branch-04-prism-100k.json: 2da02b1b645dadb4c6cae84533549994cad5b1854fc2785cbbe6af580631f8c6
limitations:
  - Only six already fixed triangles per parent are used.
  - The branch-4 solver scout is BUDGET_UNKNOWN and non-evidentiary.
  - No endpoint exclusion, graph, proof certificate, or new upper bound is supplied.
```

## Exact clause lemma

Let

```text
T = {t0,t1,t2}
```

be one of the six triangles through coordinate 2 fixed by a surviving
normalized branch. Suppose three disjoint vertices

```text
U = {u0,u1,u2}
```

form a triangle and the three matching edges `ti--ui` are present.

These six required edges automatically form an **induced** triangular prism.
Indeed, if an off-matching cross edge `ti--uj` with `i != j` were also
present, the adjacent pair `ti,tj` would have both the third vertex of `T`
and `uj` as common neighbors, contradicting `lambda=1`.

At the endpoint `n3=4158`, equivalently `P=0`, every such six-edge pattern is
forbidden. If its unfixed residual-edge variables are

```text
x1, ..., xr,
```

the exact consequence is the clause

```text
not x1 or ... or not xr.
```

No completed-graph automorphism is assumed.

## Deterministic catalogs

Each parent has six fixed coordinate-2 triangles. Before fixed-unit filtering,
each triangle produces 64,932 distinct prism clauses. After removing clauses
already satisfied by the 84 endpoint units and branch units, every parent has:

```text
282,774 deduplicated active clauses
    606 clauses of length 3
282,168 clauses of length 5
```

The exact clause hashes are:

| parent | SHA-256 |
|---:|---|
| 4 | `f675391a81dd817fe45f805a9bc9309dba02910988b42988238b66e6c2f5ae2e` |
| 5 | `1215e64d0b8ebd5c898278acdd828cb657d8f1a1485fba4893e34316d94edaf5` |
| 8 | `bb9aac4e06e0d5f9b885aa0705b31d576d8cca7221075cfab938ce70f5716a53` |
| 10 | `eedd27d0322694661a4142a54fca80c95e416b09b2d59d6b21cf74beb4ef2af5` |
| 12 | `ac1aea55f24f3fd23045daa2195cadbd8c2a799b3a27f4755e1ad99290f238d7` |

Adding one catalog to the compact native formula yields:

```text
variables:          289,338
ordinary clauses:  568,776
AtMost constraints:  5,838
```

Eight focused tests pass. They check the full scaffold edge semantics, all
five deterministic catalogs, the 84 endpoint units, the six fixed triangles,
and the exact 33-case imported refinement:

```text
parent 4:   refined cases 15--18
parent 5:   refined cases 19--22
parent 8:   refined cases 36--41
parent 10:  refined cases 50--57
parent 12:  refined cases 68--78
```

## Solver boundary

The completed strengthened branch-4 MiniCard scout stopped at its exact
100,000-conflict budget:

```text
status:       BUDGET_UNKNOWN
decisions:    734,831
propagations: 107,662,397
```

This has zero mathematical evidentiary value. No model, graph, UNSAT proof, or
certificate was produced.

A longer fresh-solver sweep over all 33 refined cases remained nonterminal at
the publication cutoff and was excluded from the run report. Runtime is not
evidence. The rigorous verdict remains:

```text
n3=4158:   UNKNOWN
upper bound on n3: 4158
Conway-99: UNKNOWN
```

The next construction route should use per-case atomic journaling, parent
formula reuse for discovery, and fresh proof-producing reruns only for an
apparent negative result. The proposed wedge-compressed ternary clauses remain
an unverified continuation idea, not a current claim.
