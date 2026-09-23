# Wave 205 proof A: nonedge fourth-trace obstruction

```yaml
role: proof_a
date_utc: 2026-07-29T20:11:56Z
git_commit: e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71
claim_label: DERIVED
scope: >-
  Conditional prism-free rank-11 endpoint: derive the exact nonedge
  two-star cross-Gram profiles, completely enumerate the normalized t=6
  and t=7 frontier, and test pair-local determination of
  h_xy=tr(P_xP_yP_xP_y).
inputs:
  attempts/wave205-fourth-trace-globalization/protocol.md: a1d45fc0a82b9944a9e020ded3945e75944e0e00202eacbb20eb05598e30bf4d
  verification/wave171-pq-centered-code/verification-report.md: 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f
  verification/wave176-star-projector-circuits/audit.md: f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05
  attempts/wave204-projector-fourth-order-proof-b/derivation.md: 2b4ddbec109ff7fba31371709be6616f681ca26ce79339d892f5e30729a060d0
  verification/wave204-global-compatibility-verifier/audit.md: eadad44ea0e7ac653defb7e5431c13b2ef06ae53eced0bbf6412f82fc3244c65
method: >-
  Exact SRG common-neighbor counting, centered-Gram expansion, complete
  normalized finite enumeration of 5-by-5 cores, modular row reduction and
  discriminants, four explicit 28-vertex adjacency certificates, and exact
  coordinate/projector reconstruction over F_3. No solver is used by the
  sealed checker.
command: >-
  .\.venv\Scripts\python.exe -B
  attempts\wave205-nonedge-fourth-trace-proof-a\exact_check.py --verify
  attempts\wave205-nonedge-fourth-trace-proof-a\exact-results.json
outputs:
  attempts/wave205-nonedge-fourth-trace-proof-a/exact-results.json: 48a09ca524d62a1d2b2ee352a4d6689dbf3fa3127c70b03e7358edad452e05cc
  attempts/wave205-nonedge-fourth-trace-proof-a/controls.json: e52c068f5fdba18110debdd1455195ec22145f07993437b5438e8f77ae03fdcf
  attempts/wave205-nonedge-fourth-trace-proof-a/exact_check.py: 3532d6ac65c46003ae313409fa5f6e7e3b99131a51982d2171eda2697f772297
limitations:
  - The controls contain 28 vertices and two stars, not a 99-vertex graph.
  - Unsaturated local pairs are not simultaneously completed outside the two-center ball.
  - The exhaustive census covers t=6 and t=7, not every larger t.
  - Lower-rank Gram-kernel words are not treated as true column relations.
  - Actual nonedge h values, rank 11, Conway-99, and novelty remain UNKNOWN.
```

## Derived theorem

For a nonedge `x,y`, label their two common neighbors `a,b` and the
corresponding star blocks first.  The centered `7 by 7` cross Gram has:

```text
marked corner [[1,2],[2,1]],
marked row and column profile 0^0 1^5 2^2,
ordinary row and column integer sum 6.
```

If an ordinary row contains `k` twos, its complete profile is

```text
0^(1+k) 1^(6-2k) 2^k,  0<=k<=3.
```

Let `t_xy` count entries equal to two.  Then

```text
t_xy=(BLB^T)_xy,
t_xy>=6,
average_(y nonadjacent to x) t_xy=7,
tr(P_xP_y)=2t_xy in F_3,
h_xy=tr((C C^T)^2).
```

Thus the new global scalar constraint is

```text
sum_(nonedges {x,y}) (t_xy-6)=4158.
```

It is a distribution identity, not a pointwise equality.

## Complete low-count census

Independent ordinary row and column relabeling leaves four exhaustive
boundary cases: the second marked two-entry is aligned with or distinct
from the first on each side.  At `t=6` the ordinary `5 by 5` core is binary;
at `t=7` it has one two-entry and is otherwise binary.  Exact margin
enumeration gives:

```text
t=6:   646 normalized labelled representatives,
t=7: 7,886 normalized labelled representatives.
```

The rank-11, determinant-two representatives whose Gram kernel—now
necessarily the true relation code—has minimum weight at least four are:

| `t` | `h=0` | `h=1` | `h=2` |
|---:|---:|---:|---:|
| 6 | 0 | 18 | 0 |
| 7 | 297 | 324 | 144 |

The counts are normalized labelled enumeration counts, not orbit counts.
Formal rank-12 rows are retained in the raw histogram but rejected as
ambient-impossible.

## Explicit controls and refutations

Four complete local adjacency certificates reproduce:

```text
t6_h1,
t7_h0,
t7_h1,
t7_h2.
```

Each has 28 vertices, two degree-14 centers, exactly two center common
neighbors, exact opposite-center `mu=2` for every exclusive neighbor,
at most one local common neighbor on an edge, at most two on a nonedge, and
the endpoint two-cross-edge cap for every selected disjoint block pair.

Every control has full Gram rank 11 and determinant two, embeds explicitly
in `diag(1^10,2)`, has 14 projectively distinct columns, and reproduces the
claimed rank-six projectors.  The `t6_h1` true relation code has minimum
weight six.  The three `t=7` controls all have `g=2`, intersection dimension
one, and true relation minimum weight at least four, but have all three
fourth traces.

Therefore:

```text
local projectivity and dual distance imply t_xy>=7: REFUTED
exact t_xy=7 and the listed pair data determine h_xy: REFUTED
```

## Inflection verdict

This is a well-sealed obstruction to the pair-local fourth-order route.
Advancement now requires a newly named invariant: the simultaneous
99-center extension law that assigns outside common neighbors to the
unsaturated pairs of overlapping 28-vertex two-center balls.

The controls satisfy only the claimed pair-local SRG consistency.  They do
not complete the unsaturated pairs, impose all 231 triangle blocks, realize
the global square-zero rank-11 Gram, or give a target graph.  No endpoint
exclusion or Conway-99 resolution follows.
