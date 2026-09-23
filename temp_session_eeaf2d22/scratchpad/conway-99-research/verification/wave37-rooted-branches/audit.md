# Wave 37 rooted-branch adversarial audit

Verdict: **PASS for the scoped conditional clause package**.

The six fixed-triangle clause families for each surviving parent branch are
sound consequences of `P=0`, and all five submitted catalogs were reproduced
without importing the discovery implementation. This does not exclude the
endpoint: the only completed solver artifact is `BUDGET_UNKNOWN`, with no
candidate and no proof.

## Independent reconstruction

The verifier rebuilt from definitions:

- the 84 lexicographic residual labels and 3,486 named edge variables;
- the 945 normalized shared-fiber matchings and their 12 parent orbits;
- the 10,395 oriented refinement states and their 78 orbits;
- the 84 endpoint nonedge units;
- the five endpoint-compatible parents `4,5,8,10,12`; and
- every active prism clause for every one of the six fixed triangles.

The endpoint-compatible part of the independently reconstructed refinement is
exactly 33 cases:

| parent | refined cases |
|---:|:---|
| 4 | 15--18 |
| 5 | 19--22 |
| 8 | 36--41 |
| 10 | 50--57 |
| 12 | 68--78 |

This is a normalized conditional cover. It uses the stabilizer of the
normalized data; it assumes no automorphism of a completed graph.

## The `lambda=1` prism lemma

Let `T={t0,t1,t2}` and `U={u0,u1,u2}` each be triangles, with matching edges
`ti--ui`. If an off-matching edge `ti--uj` existed for `i!=j`, then the
adjacent pair `ti,tj` would have two common neighbors: the third vertex of
`T` and `uj`. This contradicts `lambda=1`.

The verifier also checked all six possible off-matching cross edges in the
six-vertex pattern. Every one causes such a violation. Thus the required
six-edge pattern is automatically an induced triangular prism.

## Catalog results

Every parent independently gives:

```text
six fixed triangles
64,932 raw clauses per triangle
47,129 active clauses per triangle after fixed units
282,774 deduplicated active clauses
  606 clauses of length 3
282,168 clauses of length 5
```

The reproduced canonical hashes are:

| parent | SHA-256 |
|---:|:---|
| 4 | `f675391a81dd817fe45f805a9bc9309dba02910988b42988238b66e6c2f5ae2e` |
| 5 | `1215e64d0b8ebd5c898278acdd828cb657d8f1a1485fba4893e34316d94edaf5` |
| 8 | `bb9aac4e06e0d5f9b885aa0705b31d576d8cca7221075cfab938ce70f5716a53` |
| 10 | `eedd27d0322694661a4142a54fca80c95e416b09b2d59d6b21cf74beb4ef2af5` |
| 12 | `ac1aea55f24f3fd23045daa2195cadbd8c2a799b3a27f4755e1ad99290f238d7` |

These are partial prism families: they cover prisms meeting one of the six
already fixed triangles in a parent. They do not encode every possible prism.

## Solver boundary

The retained branch-4 result reached its exact 100,000-conflict budget and is
correctly labeled `BUDGET_UNKNOWN`. It has neither a candidate path nor a
candidate hash. No SAT assignment, UNSAT proof, or graph certificate exists.
The longer nonterminal 33-case process has no retained result and contributes
no evidence.

The independent suite passed five tests in 21.134 seconds.

Final scoped status:

```text
fixed-triangle conditional clauses: VERIFIED
all-prism endpoint formula:          NOT PROVIDED
n3=4158 endpoint:                    UNKNOWN
upper bound on n3:                   4158
Conway-99:                           UNKNOWN
```
