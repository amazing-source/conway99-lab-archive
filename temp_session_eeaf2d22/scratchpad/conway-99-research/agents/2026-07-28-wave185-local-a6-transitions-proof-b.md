# Wave 185 proof-B: local `A6` transition cells

## Status

`DERIVED`.  Under the independently verified Wave 181 equality face, the
prism-free rooted transition structure rules out the multiplicity-seven
global-root support.  The remaining four-set transitions satisfy exact
per-vertex and per-cell tables, and the number of distinct global roots
improves conditionally from `297..415` to

```text
349..415.
```

This is not yet an endpoint contradiction.  Independent verification is
required before promotion.

```yaml
role: proof_b
date_utc: 2026-07-29T00:31:51Z
git_commit: 6de5cb7cae6fe53ded33e1bd4915ed4f578058b2
claim_label: DERIVED
scope: >-
  Conditional on Wave181 equality Q=2079: exact transitions among the
  21 four-sets indexed by local projective A6 roots, exclusion of global-root
  multiplicity seven, and the conditional global-root interval 349 through
  415.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave64-rooted-transition-design/package-manifest.sha256: dd138310fcaa4e3e2d2989281f9c7487b498ad1d15901403b32919d7018bb905
  attempts/wave181-c4-conic-equality/package-manifest.sha256: 8ea0993ecdd2abe3cb82cd4ac05273c7b7992f6739ef99121b9ae3c04fce7be2
  verification/wave181-c4-conic-equality/package-manifest.sha256: 889c05b6726a5dcafb5f66203355185d258c7763483bb35d931b4bcf374c76af
  verification/wave183-root-support-girth-verifier/package-manifest.sha256: bec8649ee069fa4a2205ecb61cf90f70aca170dfc47976ef4833c9c6c6e18115
  verification/wave184-root-support-intersections-verifier/package-manifest.sha256: 134d106855805014514f07cf5df2fb3a78d06e6c555cedbe95ce50a533aa6a8f
method: >-
  Rooted K_{2,2,2,2,2,2,2} edge labels, induced-prism exclusion,
  canonical-C4 global-root support shapes, exact endpoint incidence,
  weighted line-graph capacity, and a local quotient compression. No graph,
  code, SAT, configuration, or isomorphism search.
command: >-
  Tiny standard-library Fraction and integer checks of the hand-derived
  transition table, quotient baseline, and multiplicity parameterization;
  no construction search.
outputs:
  - agents/2026-07-28-wave185-local-a6-transitions-proof-b.md
limitations:
  - Independent verifier promotion is pending.
  - Individual transition counts for a fixed pair of local roots are not
    determined by the proved first-moment equations.
  - The resulting 14-dimensional quotient compression and the type-five
    self-orthogonal code have not yielded a contradiction.
  - Wave181 equality, rank 11, the endpoint, and Conway-99 remain UNKNOWN.
```

## 1. Freeze the rooted four-sets

Fix a graph vertex `x`.  Its neighborhood is the disjoint union of seven
edges

```text
V_i={i_0,i_1},  1<=i<=7.
```

Every vertex `y` nonadjacent to `x` has two common neighbors with `x`, one
from each of two different `V_i`.  Write

```text
y=y_(i_alpha,j_beta).
```

For a local projective `A6` root `e={i,j}`, define its four-set

```text
Y_e={y_(i_alpha,j_beta): alpha,beta in {0,1}}.
```

The 21 sets `Y_e` partition the 84 nonneighbors of `x`.  Under Wave 181
equality, `Y_e` consists exactly of the four color-`e` nonneighbors of `x`.
Wave 183 gives the provisional possibilities

```text
global multiplicity 5: G[Y_e]=4K1,
global multiplicity 6: G[Y_e]=2K2,
global multiplicity 7: G[Y_e]=P4.                 (1)
```

Two local roots are nonorthogonal exactly when their `K7` edges are incident,
and orthogonal exactly when those edges are disjoint.

## 2. Prism-freeness forbids same-endpoint internal edges

Take two vertices of `Y_{ij}` that share their actual `V_i` endpoint:

```text
y=y_(i_alpha,j_0),  y'=y_(i_alpha,j_1).
```

If `y~y'`, then

```text
{i_alpha,y,y'} and {x,j_0,j_1}
```

are disjoint graph triangles.  Their cross edges are exactly

```text
x i_alpha,  j_0 y,  j_1 y'.
```

There are no other cross edges:

- `x` is nonadjacent to `y,y'`;
- `i_alpha` is nonadjacent to `j_0,j_1` because the local graph at `x` is
  `7K2`; and
- `j_0` cannot also meet `y'`, nor `j_1` meet `y`, because the edge
  `j_0j_1` already has its unique common neighbor `x`.

The six vertices would therefore induce a triangular prism, contrary to
`P=0`.  The same argument applies when the shared endpoint is in `V_j`.

Consequently an internal edge of `Y_{ij}` can only join opposite corners:

```text
(i_0,j_0)--(i_1,j_1),  or
(i_0,j_1)--(i_1,j_0).                              (2)
```

These two possible edges are disjoint.  In particular every vertex of
`G[Y_e]` has internal degree at most one.  The `P4` case in (1) is
impossible:

```text
n_7=0.                                             (3)
```

This is the first new conclusion.  It uses no search; it is also the
four-set form of the independently verified Wave 64 prohibition on pairing
two rooted labels whose other endpoints are mates.

## 3. Exact per-vertex transition table

Let `C_x` be the 12-regular graph induced by the 84 nonneighbors of `x`.
For `y in Y_e`, write `d_e(y)` for its internal degree in `Y_e`.

The rooted transition theorem says that `y` has:

1. one neighbor sharing each of its two actual base endpoints, hence two
   intersecting-label neighbors; and
2. ten neighbors with disjoint base labels.

By Section 2, neither intersecting-label neighbor lies in `Y_e`; both lie in
four-sets indexed by roots incident with `e`.

There is also a direct endpoint-profile derivation.  If `e={i,j}`, then the
total number of neighbors of `y` in cells whose root contains `i` is two,
and the corresponding total for `j` is two.  An internal neighbor is counted
in both totals.  Hence the off-diagonal incident-root degree is

```text
4-2*d_e(y).                                        (4)
```

Subtracting the two intersecting-label transitions from (4), and then from
the ten disjoint-label neighbors, gives the exact table:

| cell type | internal | incident transition | incident disjoint-label | orthogonal disjoint-label |
|---|---:|---:|---:|---:|
| multiplicity 5 | 0 | 2 | 2 | 8 |
| multiplicity 6 | 1 | 2 | 0 | 9 |

Each row sums to 12.  Thus the multiplicity-six matching case has no
disjoint-label edge at all to an incident-root cell.

On summing over the four vertices of one cell, the exact cell totals are:

| cell type | internal edges | edges to 10 incident-root cells | edges to 10 orthogonal-root cells |
|---|---:|---:|---:|
| multiplicity 5 | 0 | `8 transition + 8 disjoint = 16` | 32 |
| multiplicity 6 | 2 | `8 transition + 0 disjoint = 8` | 36 |

These are conservation laws, not an assertion that all ten target cells
receive the same number.

## 4. The weighted line-graph form

For an incident root pair `e,f`, let

```text
t_ef = number of selected edges whose rooted labels share their actual
       endpoint in the common K7 vertex,
b_ef = number whose labels choose opposite endpoints there.
```

Then

```text
sum_(f incident e) t_ef=8                         (5)
```

for every cell.  Moreover

```text
sum_(f incident e) b_ef =
  8  if e has multiplicity 5,
  0  if e has multiplicity 6.                     (6)
```

Symmetry of graph adjacency and (6) show that `b_ef` can be nonzero only
when both cells have multiplicity five.

There is a useful pair capacity.  Fix the shared `K7` vertex of `e,f`.
Disjoint rooted labels must choose opposite actual endpoints there.  For
each of the two orientations, the possible pairs form a `K_{2,2}`.  All
four cannot be selected: the two vertices on one side already share their
base endpoint, so the two vertices on the other side would give them two
additional common neighbors, contradicting `mu=2`.  Each orientation has
at most three selected pairs, whence

```text
b_ef<=6.                                           (7)
```

Thus the `b`-support is a weighted subgraph of the line graph `L(K7)`
induced by the multiplicity-five local roots.  Every one of its vertices
has weighted degree eight and every edge has weight at most six.  Its
underlying simple graph therefore has minimum degree at least two.

## 5. A conditional global root-count improvement

Let `n_5,n_6` count global roots of the two surviving multiplicities.
Equation (3) reduces the global incidence equation to

```text
5*n_5+6*n_6=2079.                                  (8)
```

Fix a multiplicity-five root `r`.  Its support `X_r` is a five-coclique.
At every `x in X_r`, (5)--(7) force at least two other multiplicity-five
roots through `x`, both nonorthogonal to `r` in the local `A6` geometry.

The companions belonging to two different vertices of `X_r` are distinct.
Indeed, if another root `s` occurred with `r` at two vertices `x,x'`, then
`s` would lie in `R_x intersect R_x'`.  But `x,x'` are nonadjacent and
verified exact nonedge-root uniqueness gives

```text
R_x intersect R_x'={r}.
```

Therefore every multiplicity-five root has at least ten distinct
multiplicity-five companions.  In particular

```text
n_5>=11.
```

Reducing (8) modulo six gives `n_5=3 mod 6`, so in fact

```text
n_5>=15.                                           (9)
```

All nonnegative solutions of (8)--(9) are

```text
(n_5,n_6)=(15+6u,334-5u),  0<=u<=66.
```

If `R=n_5+n_6` is the number of distinct global roots, then

```text
R=349+u,
349<=R<=415.                                      (10)
```

The lower endpoint in (10) is arithmetic only; no root system or graph
realizing it is asserted.

## 6. Exact quotient identity and association-scheme shadow

Let `S` be the `84 by 21` cell-incidence matrix and define

```text
M_x=S^T C_x S.
```

Thus `(M_x)_{ef}` is the number of graph edges between distinct cells, while
`(M_x)_{ee}` is twice the number of internal edges.  Let `N` be the
`7 by 21` unsigned vertex-edge incidence matrix of `K7`.

If `B` is the `14 by 84` rooted endpoint-incidence matrix and `L=7K2` is
the base local graph, the strongly regular identity in the base/residual
block is

```text
B C_x=2J-B-LB.
```

Collapsing mate pairs and then cells gives the exact quotient equation

```text
N M_x=16J-8N.                                     (11)
```

Since

```text
N N^T=5I+J,
P=N^T(5I+J)^(-1)N,
```

equation (11), symmetry, and regularity yield

```text
M_x=(8/3)J-8P+K_x,
K_x=(I-P)M_x(I-P).                                (12)
```

The fixed part has entries

```text
0 on the diagonal,
8/5 on incident root pairs,
16/5 on orthogonal root pairs.
```

It has eigenvalues `48` on constants and `-8` with multiplicity six.
All integral nonuniformity is carried by the 14-dimensional
`ker(N)` block `K_x`.

If `a_x` is the number of multiplicity-six roots in `R_x`, then

```text
tr(K_x)=4*a_x.                                    (13)
```

After normalization by four, `K_x/4` is a compression of `C_x` inside
`ker(B)`.  The exact rooted spectrum puts all its eigenvalues in `[-4,3]`.
Equivalently,

```text
12I-K_x/4-(K_x/4)^2
```

is positive semidefinite.  This is a compact local association-scheme
target, but its trace bound has ample slack for every `0<=a_x<=21`.

## 7. The surviving tensor target

Wave 182's global frame identity is

```text
sum_r m_r r tensor r=0.
```

With (3), its characteristic-three reduction becomes

```text
sum_(m_r=5) r tensor r=0.                         (14)
```

If `S_5` is the set of multiplicity-five roots, the map

```text
v |--> (<r,v>)_(r in S_5)
```

therefore has self-orthogonal image in `F_3^(n_5)`.  Because the ambient
11-space is nondegenerate and the roots are projectively distinct, this is
a projective ternary self-orthogonal code whose dimension is the dimension
of `span(S_5)`.

This recoding does not currently contradict (9).  For example, at the
smallest surviving length `n_5=15`, ordinary self-orthogonality only gives
dimension at most seven.

## 8. Failed routes retained

1. **A uniform 21-cell quotient is not forced.**  Equations (4), (11)
   determine exact incident/orthogonal totals but not each `M_ef`.
   Dividing totals by ten would introduce a nonexistent local symmetry.
2. **The first quotient spectrum survives.**  The fixed `48,-8^6`
   eigenvalues are compatible with the rooted residual spectrum, and the
   14 free Ritz values may remain anywhere in `[-4,3]`.
3. **The pair cap is six, not four.**  Each of the two `K_{2,2}`
   orientations may contain a three-edge path without violating the
   immediate common-neighbor equations.  Claiming a matching would be an
   unjustified strengthening.
4. **The frame identity is not itself a contradiction.**  Equation (14)
   supplies a projective self-orthogonal code target, but no valid bound
   yet excludes the lengths in (9).

## Boundary

The Wave 181 equality face is narrower: multiplicity seven is impossible,
the local four-set transitions factor through a weighted `L(K7)` system,
and at least 349 distinct global roots are necessary.  Nevertheless the
integer transition matrices, the 14-dimensional compression, and the
type-five frame code all remain feasible at the level proved here.

No strict improvement to `n3<=4158`, no rank-11 exclusion, no graph
construction, and no Conway-99 resolution follows.
