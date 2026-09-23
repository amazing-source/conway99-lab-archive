# Wave 33: exact finite extension criterion for the signed Fano support

```yaml
role: proof_a
date_utc: 2026-07-24T10:10:00Z
git_commit: b2595baa40d50e9c259051751fe27090bee6a449
claim_label: DERIVED
scope: >-
  Conditional on the independently verified Wave 32 actual-incidence
  rooted reduction, derive every forced cell degree, the simple
  2-(15,3,2) cross-design, the exact spectrum and small-cycle census of
  the 70-vertex induced graph, and a necessary-and-sufficient finite
  binary block criterion for extending the signed support to an
  srg(99,14,1,2). This does not construct or exclude an extension and is
  not sufficient for the full projector/lattice/Schur endpoint package.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  verification/wave33-continuation-protocol.md: b98b6bb8228b54b67cd949ee1bf6eb05ebd6ebe74f1cbc9e49b041a55e2d2fe6
  agents/2026-07-24-wave32-rooted-proof.md: 04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0
  attempts/wave32-rooted-vector/exact-results.json: 9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0
  verification/wave32-rooted-vector/audit.md: 36d83232d82e30205e0aefa30aedff0a517de1edb0adbaa54575ea68d04ce1a5
  verification/wave32-rooted-vector/independent-results.json: 4ed239e997e4485abdab4e26a2e28e2a981b6fff069c4d926ccff3d2241dbe6f
method: >-
  Count two-walks into the signed support; write the strongly regular
  identity in three-by-three blocks; derive the cross-design and exact
  invariant subspaces; calculate the induced-graph spectrum and cycle
  moments in exact quadratic arithmetic; and audit both directions of
  the finite block-matrix criterion. Retain a design-only hostile control
  and every failed route.
command: |-
  python -B -m unittest discover -s attempts/wave33-rooted-extension -p test_*.py -v
  python -B attempts/wave33-rooted-extension/exact_check.py --output attempts/wave33-rooted-extension/exact-results.json
outputs:
  attempts/wave33-rooted-extension/initial-derivation-freeze.md: f222b78c2be4f41f8e66ea05265aaa3c55206577e94cf3f9746625c78a54868b
  attempts/wave33-rooted-extension/input-freeze.sha256: 74f98a5a79f53c35b8dce47feab8812b9b8f82ef4414c9c4ace759183d37ba64
  attempts/wave33-rooted-extension/failed-routes.md: 1fb7b1ab26c0bcd08b0ac5d348e685b9616d396084145d6f4c1b7646b6dc3e1f
  attempts/wave33-rooted-extension/exact_check.py: 8712281e7b3819f466df9a35ec2303069737d75fe1af0f32e9eb9e6c1a543f8f
  attempts/wave33-rooted-extension/test_exact_check.py: 2149c793297b281d04011819c724f8236e2a386b1063b31feabc10a767ba0e71
  attempts/wave33-rooted-extension/exact-results.json: 193db8ee0c155cc3a97489b4471c4a82ae09823dd9344d043a81778e1a6ba5a1
limitations:
  - This discovery report cannot certify its own derivation.
  - No satisfying D,B pair is constructed.
  - No complete search or infeasibility certificate is supplied.
  - The criterion is complete for the graph extension, not for every
    projector, lattice, tensor, and Schur endpoint condition.
  - The hostile 2-design intentionally fails the fixed F-label coupling.
  - No automorphism is assumed beyond relabeling the forced Fano support.
  - Rooted endpoint existence, n3=708, Conway-99, and novelty remain UNKNOWN.
```

## Result and status wall

Assume the target strongly regular graph and the verified Wave 32 rooted
support.  Let `S` be the signed 14-set, `O` the 70 vertices with one
neighbor in each sign class, and `Q` the remaining 15 vertices.  Then:

```text
|S|,|O|,|Q| = 14,70,15,

equitable quotient =
[[4,10,0],
 [2, 9,3],
 [0,14,0]],

Q is independent,
O-Q incidence is a simple 2-(15,3,2) design.
```

The induced graph `D` on `O` is connected, 9-regular, and has forced
spectrum

```text
9^1,
(-1)^14,
(-1-sqrt(2))^6,
(-1+sqrt(2))^6,
3^27,
(-4)^16.                                             (1)
```

Consequently it has exactly

```text
315 edges,
56 triangles,
294 four-cycles,
det(D)=2^32 3^29.                                    (2)
```

Most importantly, after naming the 70 vertices by their already-forced
support neighborhoods, the rooted graph extension is equivalent to six
exact binary matrix equations in a `70 x 70` adjacency `D` and a
`70 x 15` incidence `B`.  This is a complete finite criterion for the
graph extension, not a solution:

```text
full rooted extension found:              NO
rooted graph excluded:                    NO
rooted endpoint:                     UNKNOWN
n3=708:                              UNKNOWN
Conway-99 existence/nonexistence:     UNKNOWN
novelty:                             UNKNOWN
```

## 1. Frozen rooted premises

For an `srg(99,14,1,2)` adjacency matrix `A`,

```text
A^2=12I-A+2J.                                        (3)
```

Wave 32 independently verified that a norm-two endpoint root transports to
a signed minus-four eigenvector `k` with seven `+1` entries, seven `-1`
entries, and 85 zero entries.  Write the sign classes as `P,R`.  Their
induced graph is bipartite and 4-regular; its `7 x 7` cross-incidence
matrix `C` is a symmetric `2-(7,4,2)` design, equivalently the complement
of a Fano-plane incidence matrix.

Every vertex outside `S=P union R` has either:

```text
one neighbor in P and one in R; or
no neighbor in S.
```

The former set has size 70 and is called `O`; the latter has size 15 and is
called `Q`.  This report uses no further symmetry.  Choosing a canonical
Fano incidence matrix is only a relabeling of the already-forced support.

The initial derivation was frozen before inspecting any sibling discovery
at `attempts/wave33-rooted-extension/initial-derivation-freeze.md`.

## 2. The full three-cell quotient

Fix `q in Q`.  It is nonadjacent to every one of the 14 support vertices,
so (3) gives two common neighbors with each of them.  Thus the number of
two-walks from `q` into `S` is

```text
14*2=28.
```

An `O` neighbor contributes its two support neighbors and a `Q` neighbor
contributes zero.  Hence

```text
2 deg_O(q)=28,
deg_O(q)=14,
deg_Q(q)=0.                                         (4)
```

Therefore `Q` is independent.

Now fix `o in O`.  Its two adjacent support vertices contribute one common
neighbor each; the other twelve support vertices contribute two each.
The total number of two-walks from `o` into `S` is

```text
2*1+12*2=26.
```

The two support neighbors of `o` each have four neighbors in `S`, every
`O` neighbor contributes two, and every `Q` neighbor contributes zero.
Therefore

```text
26=2*4+2 deg_O(o),
deg_O(o)=9,
deg_Q(o)=14-2-9=3.                                 (5)
```

Equations (4)--(5) give the equitable quotient

```text
K =
[[4,10,0],
 [2, 9,3],
 [0,14,0]].
```

Its characteristic polynomial is

```text
(x-14)(x-3)(x+4).
```

The hostile mutation `mu=3` would make (4) require 21 `O` neighbors at a
degree-14 vertex.  Thus the target value `mu=2` is active.

## 3. The simple `2-(15,3,2)` design

Let `B` be the `70 x 15` `O`-by-`Q` incidence matrix.  Equations (4)--(5)
give row weight three and column weight fourteen.  Two distinct vertices
of the independent set `Q` have exactly `mu=2` common neighbors, all in
`O`.  Hence

```text
B 1=3 1,
B^T 1=14 1,
B^T B=12I+2J.                                      (6)
```

The 70 row supports are distinct.  If two `O` vertices had the same three
`Q` neighbors, they would have at least three common neighbors.  This
exceeds both `lambda=1` and `mu=2`, whether the two vertices are adjacent
or not.  Thus the rows form a simple `2-(15,3,2)` design.

There is additional coupling to the signed support.  Let `F` be the fixed
`14 x 70` support-to-`O` incidence matrix.  Every column of `F` has one
entry in `P` and one in `R`; every row has weight ten.  Every pair
`(s,q)` with `s in S,q in Q` is nonadjacent and has two common `O`
neighbors, so

```text
F B=2J.                                             (7)
```

For fixed `q`, its 14 incident `O` columns therefore label a spanning
2-regular bipartite graph on `P union R`.  No label may repeat: two copies
of the same support pair together with `q` would give three common
neighbors.  The possible cycle types are exactly

```text
14;
10+4;
8+6;
6+4+4.                                             (8)
```

No one type is asserted to be forced.

For later spectral use, let `b_q` be a column of `B` and put

```text
w_q=5b_q-1_O.
```

Equation (6) gives the exact Gram data

```text
(w_q,w_q)=280,
(w_q,w_q')=-20 for q != q',
Gram(w_q)=300I-20J.                                (9)
```

Thus the centered `q`-neighborhoods span a 14-dimensional regular simplex.

## 4. The exact graph-extension criterion

Let `A_S` be the fixed `14 x 14` Fano-complement support adjacency.
The columns of `F` are completely determined as a multiset:

```text
one column for each of the 28 support cross-edges;
two columns for each of the 21 support cross-nonedges.                (10)
```

Name the 70 `O` vertices by these columns, using an arbitrary copy label
for the duplicated columns.  This is a labeling, not an automorphism
assumption.  Let:

```text
D = 70 x 70 adjacency induced by O;
B = 70 x 15 O-Q incidence.
```

The full adjacency is

```text
    [ A_S  F  0 ]
A = [ F^T  D  B ].
    [  0  B^T 0 ]                                  (11)
```

Taking the six upper-triangular blocks of (3) gives:

```text
A_S^2+F F^T             =12I-A_S+2J,               (12a)
A_S F+F D               =2J-F,                     (12b)
F B                     =2J,                       (12c)
F^T F+D^2+B B^T         =12I-D+2J,                (12d)
D B                     =2J-B,                     (12e)
B^T B                   =12I+2J.                   (12f)
```

Equation (12a) is an exact identity for the fixed canonical `A_S,F`.

Conversely, suppose `D` is binary, symmetric, and zero-diagonal, `B` is
binary, and (12a)--(12f) hold.  Then the binary symmetric zero-diagonal
matrix (11) satisfies (3).  Its diagonal entries say every vertex has
degree 14.  Its off-diagonal entries say adjacent pairs have one common
neighbor and nonadjacent pairs have two.  Therefore (11) is an
`srg(99,14,1,2)`.

This proves:

> **Finite graph-extension criterion.** Up to relabeling only the already
> forced support and the two copies of each duplicated support label, the
> signed Fano support extends to an `srg(99,14,1,2)` if and only if binary
> matrices `D,B` satisfying (12) exist.

The unreduced raw binary space has

```text
binom(70,2)+70*15=2415+1050=3465
```

variables.  The equations impose far more structure, but no complete
enumeration is claimed.

This theorem is deliberately graph-scoped.  A passing pair would still
have to satisfy the frozen triangle-incidence projector, lattice, tensor,
and Schur endpoint conditions before it could realize the full `n3=708`
endpoint package.

## 5. Matchings forced by the block equations

Equation (12e) has an entrywise interpretation:

```text
number of D-neighbors of o inside N_O(q)
 =1 if o is adjacent to q,
 =2 otherwise.                                      (13)
```

Consequently every 14-vertex `q`-neighborhood induces a perfect matching
of seven `D` edges.  It also gives, from (9),

```text
D w_q=-w_q.                                         (14)
```

There are separate support-star matchings.  For fixed `s in S`, its ten
`O` neighbors consist of:

```text
four unique completions of support edges;
six completions, two for each of three support nonedges.
```

For a unique edge-completion `o`, the edge `(s,o)` already has the other
support endpoint as its unique common neighbor, so `o` has no `D` neighbor
sharing `s`.  For a nonedge-completion `o`, the edge `(s,o)` has no common
support neighbor and must have a unique common `O` neighbor.  Thus the six
nonedge-completions induce a perfect matching.

The two copies of one support nonedge cannot themselves be adjacent,
because they already share both support endpoints.  Therefore the 14
support-star matchings contribute 42 distinct `D` edges.  Their precise
pairing is not canonical and was not fixed in the theorem.

## 6. Exact spectrum of the induced 70-vertex graph

The spectrum in (1) follows from exact invariant subspaces, not numerical
diagonalization.

First, write the support adjacency in bipartite form using `C`.  Since

```text
C C^T=2I+2J,
```

the spectrum of `A_S` is

```text
4^1, (-4)^1, (sqrt(2))^6, (-sqrt(2))^6.             (15)
```

The minus-four vector is the signed vector `k`.  From (12a),

```text
F F^T=12I-A_S-A_S^2+2J.                            (16)
```

It follows that `rank(F)=13` and `ker(F^T)=span(k)`.  On the two
six-dimensional eigenspaces of (15), `F^T` is injective.

Equation (6) gives `rank(B)=15`.  Equation (7) implies that the
nonconstant part of `im(B)` is orthogonal to the nonconstant part of
`im(F^T)`:

```text
(F^T y,Bx)=y^T F Bx=0
```

whenever both `x` and `y` have coordinate sum zero.  Both full images
contain the constant vector, so their nonconstant dimensions are 14 and
12.  Together with the constant line they occupy 27 dimensions of
`R^70`; the orthogonal residual space has dimension 43.

Now:

- `D 1=9 1` by (5).
- For `x` of sum zero, (12e) gives `D(Bx)=-Bx`.  This is the
  14-dimensional eigenvalue `-1` space.
- Transposing (12b), for a nonconstant `A_S` eigenvector `y` of
  eigenvalue `a`,

  ```text
  D(F^T y)=-(1+a)F^T y.
  ```

  Taking `a=+/-sqrt(2)` gives the two six-dimensional irrational
  eigenspaces.
- On the 43-dimensional joint orthogonal complement, (12d) reduces to

  ```text
  D^2+D-12I=0.
  ```

  Thus the remaining eigenvalues are 3 and -4.

Finally `D` has zero diagonal, hence trace zero.  The already-determined
eigenvalues have total trace `-17`.  If the residual multiplicities are
`m_3,m_-4`, then

```text
m_3+m_-4=43,
3m_3-4m_-4=17,
```

so

```text
m_3=27,
m_-4=16.
```

This proves (1).  Eigenvalue nine has multiplicity one, so `D` is
connected.

## 7. Exact edges, triangles, and four-cycles

Exact quadratic-arithmetic evaluation of (1) gives

```text
tr(D^0)=70,
tr(D)=0,
tr(D^2)=630,
tr(D^3)=336,
tr(D^4)=13062.                                      (17)
```

Thus:

```text
|E(D)|=tr(D^2)/2=315,
triangles(D)=tr(D^3)/6=56.
```

For a simple 9-regular graph on 70 vertices,

```text
tr(D^4)
 =2|E(D)|+4*70*binom(9,2)+8 C4(D),
```

so

```text
C4(D)=294.
```

There is a compatible purely combinatorial edge census.  Every `D` edge
has a unique common neighbor in the full graph.  Partition it by the cell
containing that neighbor:

```text
common neighbor in S: 14*3 = 42 edges;
common neighbor in Q: 15*7 =105 edges;
common neighbor in O: 315-42-105=168 edges.          (18)
```

The first two classes are disjoint, since an adjacent pair cannot have two
common neighbors.  Each edge in the last class belongs to its unique
all-`O` triangle; each such triangle contributes three edges.  Hence

```text
168/3=56
```

again.

The complete target triangle census is therefore

```text
two S, one O:    28;
one S, two O:    42;
two O, one Q:   105;
three O:         56;
total:          231.                                (19)
```

This equals `693*lambda/3`, as required.

## 8. Hostile exact controls

The checker constructs an abstract simple `2-(15,3,2)` design as the union
of two disjoint copies of the line design of `PG(3,2)`.  It has:

```text
70 distinct blocks,
row weight 3,
column weight 14,
pairwise column intersection 2,
B^T B=12I+2J.
```

This proves that (12f) alone is not contradictory.  In the deliberately
arbitrary row ordering against the fixed support labels, 135 of the 210
entries of `FB` differ from two, so (12c) fails.  It is not a candidate
extension.

The checker also combines that design with the 42 forced support-star
edges and runs the complete block validator.  Only the fixed `S-S` and
abstract `Q-Q` blocks pass; the assembled global identity fails.  This
ensures that a partial local control cannot be mistaken for a graph.

The non-certifying heuristic attempt to couple the hostile design, the
noncontradictory spectral route, the four surviving 2-factor types, and the
root-reflection boundary are preserved in
`attempts/wave33-rooted-extension/failed-routes.md`.

## 9. Replay and strongest objection

The standard-library-only suite passed:

```text
Ran 15 tests
OK
```

It checks all frozen hashes, the fixed Fano support and its 28/42 label
multiplicities, the exact equitable quotient, the active `mu=3` mutation,
the design and all four cycle types, the hostile 70-block design, the 42
forced support-star edges, all six criterion blocks, criterion rejection
of the hostile partial pair, exact quadratic spectral arithmetic, the
forced spectrum, both small-cycle derivations, the global triangle census,
the status wall, and deterministic LF-only JSON.

The strongest self-objection is the direct-sum step in Section 6.  A
verifier must independently establish `rank(F)=13`, `rank(B)=15`,
`FB=2J`, the one-dimensional constant intersection, and invariance of the
43-dimensional residual space.  Merely matching the final spectral moments
would not certify the derivation.  It must also audit both directions of
the block criterion and keep its graph-only scope explicit.

The publication-safe status is:

```text
partition/design/spectral reduction:   DERIVED, VERIFICATION PENDING
finite graph-extension criterion:      DERIVED, VERIFICATION PENDING
rooted extension or exclusion:         NOT OBTAINED
rooted endpoint:                       UNKNOWN
n3=708:                                UNKNOWN
Conway-99 existence/nonexistence:       UNKNOWN
novelty:                               UNKNOWN
```
