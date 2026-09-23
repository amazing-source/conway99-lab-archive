# Wave 35 proof A: prism-free endpoint incidence reduction

```yaml
role: proof_a
date_utc: 2026-07-26T22:06:35Z
git_commit: 6d98cb5f73c1f56d227e97b1c3e70d363669bf87
claim_label: UNKNOWN
scope: "n3=4158, equivalently no triangular prisms and q(T)=12 for every triangle"
inputs:
  - "attempts/wave35-n3-4158-combinatorial/input-freeze.sha256"
method: "Direct triangle-fibre and block-incidence counting without the spectral-projector route"
command:
  - "python -B attempts/wave35-n3-4158-combinatorial/exact_check.py --verify attempts/wave35-n3-4158-combinatorial/exact-results.json"
  - "python -B -m unittest discover -s attempts/wave35-n3-4158-combinatorial -p \"test_*.py\" -v"
outputs:
  - "attempts/wave35-n3-4158-combinatorial/exact-results.json | sha256 07e1469e7690bd630385e734d387fa13a1eb537f0c578bf31270c3b7b8824b67"
limitations: "The reduction does not decide simultaneous 60-block compatibility or compatibility across the 231 base triangles. Endpoint and target remain UNKNOWN."
```

## 1. Frozen endpoint

Let `P` be the number of induced triangular prisms.  The exact
opposite-edge identity is

```text
n3 + 3P = 4158.
```

Thus `n3=4158` is equivalent to `P=0`.  For every graph triangle `T`, let
`a_j(T)` count disjoint triangles with exactly `j` cross edges and put
`q(T)=12-a_3(T)`.  The frozen local equations give

```text
(a0,a1,a2,a3) = (20+q,180-3q,3q,12-q).
```

Since the global prism count is zero, every nonnegative `a3(T)` is zero.
Consequently every triangle has

```text
q(T)=12,
(a0,a1,a2,a3)=(32,144,36,0).
```

This lane does not use a spectral projector.

## 2. Lemma 1: derangement holonomy

Fix `T={t0,t1,t2}` and let

```text
Xi = N(ti) \ T.
```

Each `Xi` has twelve vertices.  Its induced graph is a perfect matching:
the six other graph triangles through `ti`.

For `i != j`, every vertex of `Xi` has a unique neighbor in `Xj`.  Indeed,
for `x in Xi`, the nonedge `x,tj` has common neighbors `ti` and one unique
vertex of `Xj`.  Hence the edges between each pair of fibres form a perfect
matching.

The union of the three cross-fibre matchings is a two-factor on 36
vertices.  At every vertex, entering from one fibre forces departure to the
third, so every cycle length is divisible by three.  Its triangles are
exactly the transversal triangles in relation `R3` with `T`.  At the frozen
endpoint there are none.  Therefore:

```text
all cross-fibre cycle lengths are 6,9,12,...;
the twelve-point holonomy sigma_T has no fixed point.
```

The sign of this derangement did not yield a global parity contradiction;
that failed route is retained separately.

## 3. Lemma 2: the exact `T|X|Y` partition

Put

```text
X=X0 union X1 union X2, |X|=36,
Y=V(G) minus (T union X), |Y|=60.
```

Direct degree and common-neighbor counting gives:

| vertex cell | neighbors in `T` | neighbors in `X` | neighbors in `Y` |
|---|---:|---:|---:|
| `T` | 2 | 12 | 0 |
| `X` | 1 | 3 | 10 |
| `Y` | 0 | 6 | 8 |

In particular:

1. `G[X]` is cubic;
2. the endpoint makes `G[X]` triangle-free;
3. the `X-Y` bipartite graph has degrees `(10,6)`; and
4. `G[Y]` is 8-regular.

For `y in Y`, the nonedge `y,ti` has exactly two common neighbors, both in
`Xi`.  Thus every `y` determines a six-element block

```text
B_y = N(y) intersect X
```

containing exactly two points from every fibre.

## 4. Lemma 3: sixty triples of allowed pairs

Let `gi` be the perfect matching inside `Xi`.  Two vertices in the same
fibre already share `ti`.

- A pair in `gi` is adjacent, so it cannot share any `Y` neighbor.
- Every other same-fibre pair is nonadjacent and has exactly one further
  common neighbor, necessarily in `Y`.

Therefore, in each coordinate, the sixty blocks `B_y` use every edge of

```text
K12 minus gi
```

exactly once.  The endpoint local problem is consequently a 60-row
three-coordinate edge-bijection problem.

Moreover, `G[X][B_y]` is a matching.  Otherwise an edge `xy`, with
`x in X`, would have `y` and two vertices of `B_y` as common neighbors.
Thus each block contains zero, one, two, or three `X`-edges.

Finally, two distinct blocks meet in at most two points.  Three common
`X` neighbors would violate `lambda=1` if the corresponding `Y` vertices
were adjacent and `mu=2` if they were nonadjacent.

## 5. Lemma 4: exact block Gram

Let `A_X` be the 36-by-36 adjacency matrix of `G[X]`.  Let `R` be the
36-by-3 fibre-indicator matrix, and let `B` be the 36-by-60 incidence
matrix whose columns are the blocks `B_y`.

Restricting the defining common-neighbor equation to `X x X`, and splitting
the intermediate vertex over `T`, `X`, and `Y`, gives the exact identity

```text
B B^T = 12I - A_X + 2J - R R^T - A_X^2.       (1)
```

In particular, if `B_i` is the twelve-row restriction to fibre `Xi`, then

```text
B_i B_i^T = 9I + J - gi.                       (2)
```

Equations (1)--(2), the column shape `(2,2,2)`, the within-coordinate exact
edge cover, the per-column matching condition, and block intersections at
most two form a finite, exact one-triangle feasibility problem.  They are
strictly stronger than the row profile alone.

## 6. Restricted exact control

The checker normalizes two cross-fibre matchings to the identity, chooses
the third as the factor-0 involution in the canonical one-factorization of
`K12`, and chooses within-fibre factors `(1,2,3)`.

It verifies:

```text
G[X]: 36 vertices, 54 edges, cubic, triangle-free;
cross two-factor: six cycles of length six;
allowed coordinate pairs: 60,60,60;
individually valid block triples: 183980;
valid triples by internal X-edge count:
  0:68774, 1:90364, 2:24138, 3:704.
```

It also checks an explicit permutation of the first two 60-edge coordinate
sets whose 12-by-12 concurrence matrix is exactly the corresponding block
of (1).  This is a genuine pairwise positive control.

It is not a simultaneous three-coordinate design and is not an extension
certificate.

## 7. Failed routes and conclusion

The local sign route, a bounded swap heuristic, one proofless fixed-pair
SAT extension, and two failed full MiniCard runs are recorded in
`attempts/wave35-n3-4158-combinatorial/failed-routes.md`.  No negative solver
status is evidence.

Strongest justified conclusion:

```text
endpoint identities and the 60-block reduction: DERIVED
restricted individual-block census:            DERIVED
restricted X0-X1 pairwise control:              CANDIDATE, exactly checked
simultaneous three-fibre block system:           UNKNOWN
compatibility across all 231 triangles:         UNKNOWN
n3=4158 and Conway-99:                           UNKNOWN
```
