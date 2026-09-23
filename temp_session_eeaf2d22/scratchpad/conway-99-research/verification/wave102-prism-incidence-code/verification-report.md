# Wave 102 independent verification report

Verdict: **VERIFIED WITH CORRECTIONS**, scoped to a hypothetical
`srg(99,14,1,2)`.

The central parity-defect inequality, antipodal rounding, prism-overlap
bound, binary incidence factorization, rank bounds, and both local motifs
are correct.  The verifier found two strict strengthenings of the discovery
package:

1. if the total number of prisms is `P=3`, then `O>=4`, not merely `O>0`;
2. a nonzero vector in `ker(B^T)` has weight divisible by four, narrowing
   the discovery's even interval to the necessary candidate set
   `{36,40,44,48,52,56,60}`.

Neither strengthening resolves Conway-99 or proves a strict upper bound on
`n3`.

## Separation and frozen inputs

The discovery package manifest was frozen at

```text
d6f4a06214f2299e8618171d39287a714e4b14c541df39c27e5e90d9b0969d60
```

before its derivation or result was read.  The first independent result was
then emitted and frozen at

```text
690f7b950edfc8d0b75beac0f0a3e01692e194b002ed26fda81327de2dd554c8
```

Only after that freeze was the discovery result opened for comparison.  All
nine entries in the discovery manifest were subsequently rehashed
successfully.  The independently verified Wave 99 and Wave 100 manifests
were also frozen as direct dependencies of the rootwise inequality.

## 1. Exact parity defect

Let `f_v` be the number of induced triangular prisms containing vertex `v`,
and let

```text
O = #{v : f_v is odd}.
```

Each prism has six vertices, so

```text
sum_v f_v = 6P.
```

Consequently `O` is an even integer and

```text
sum_v floor(5 f_v/2)
  = (5 sum_v f_v - O)/2
  = 15P-O/2.
```

Substitution in the independently verified Wave 100 rootwise bound gives

```text
7*N14 <= 34650+15P-O/2
        = 55440-5*n3-O/2.
```

Because the norm-14 vectors occur in fixed-point-free antipodal pairs,
`N14` is even.  The exact even rounding is therefore

```text
N14 <= 2*floor((55440-5*n3-O/2)/14).
```

No division or rounding ambiguity remains: `O/2` is integral.

## 2. One, two, and three prisms

For `P=1`, the six prism vertices have odd rooted count and every other
vertex has count zero.  Thus `O=6`, `n3=4155`, and the refined inequality
gives `N14<=4950`.

Two distinct induced prisms share at most four vertices.  The verifier
exhausted all 60 labelled prism graphs on canonical overlapping supports.
Five shared vertices admit no gluing that respects the target
common-neighbor caps; four shared vertices do admit local gluings.  The
structural reason is also direct: deleting one prism vertex leaves degree
multiset `(2,2,2,3,3)`, so a restoration must attach the missing vertex to
the same three degree-two vertices.  Two different restorations would give
their two new vertices three common neighbors, exceeding either
`lambda=1` or `mu=2`.  Hence for `P=2`,

```text
O = |S1 symmetric-difference S2| >= 12-2*4 = 4.
```

For `P=3`, the verifier enumerated every three-set membership profile with
three six-subsets, pair intersections at most four, and `O<=2`.  There are
11 profiles up to permutations inside equal membership classes:

- all ten `O=2` profiles have no labelled three-prism gluing surviving the
  necessary `lambda/mu` caps;
- the unique `O=0` profile has 36 labelled survivors, all copies of the
  `3 by 3` rook graph `K3 square K3`.

The rook graph contains six induced prisms.  Thus it cannot occur as the
union of all prisms when the global total is `P=3`.  Both `O=0` and `O=2`
are excluded, and evenness of `O` yields the corrected conclusion

```text
P=3 implies O>=4.
```

This strengthening changes the seven-`N14` numerator by one relative to the
discovery's `O=2` row, but antipodal rounding still displays
`N14<=4956`.

## 3. Binary incidence code

Let `B` be the `99 by 231` vertex-triangle incidence matrix, and let `D` be
the `231 by P` incidence matrix of the graph whose vertices are graph
triangles and whose edges are induced prisms.  A prism is the disjoint union
of its two base triangles, so over `F2`

```text
H = B D,
f mod 2 = B D 1.
```

Every vertex is in seven triangles.  Two vertices occur in a common graph
triangle exactly when they are adjacent.  Therefore

```text
B B^T = I+A.
```

The SRG identity reduces modulo two to `A^2=A`.  Reducing its characteristic
polynomial gives `x^45(x+1)^54`; idempotence makes the two primary spaces
semisimple.  Hence

```text
rank_2(A)   = 54,
rank_2(I+A) = 45,
45 <= rank_2(B) <= 99.
```

The image of even-weight triangle vectors has dimension `rank(B)-1`.
Indeed, every column of `B` has odd weight three, while every vector in
`ker(B)` has even weight because `1^T B z = wt(z)` modulo two.  Thus

```text
44 <= dim(C0) <= 98,
C0^perp = {x : B^T x is constant on all triangles}.
```

These are dimension ranges, not an actual rank computation for a target
graph.

## 4. Triangle-parity check weights

Suppose `B^T x=0`, and let `S` be the support of `x`, with size `s>0`.
Every graph triangle meets `S` evenly.  Therefore:

- `G[S]` is 7-regular and triangle-free;
- every outside vertex has an even number `d` of neighbors in `S`;
- restricted-eigenvalue bounds give `36<=s<=60`;
- summing outside degrees gives `sum d=7s`;
- the integer SRG identity gives `sum d^2=2s(s-22)`.

For even `d`, `d^2` is congruent to `2d` modulo eight.  Therefore

```text
2s(s-22) = 14s (mod 8),
2s(s-29) = 0 (mod 8).
```

Since `s` is even and `s-29` is odd, `s` is divisible by four.  The
necessary nonzero kernel-check weights are consequently

```text
36, 40, 44, 48, 52, 56, 60.
```

Constant-one triangle checks are their complements, together with the
all-ones vector, so their necessary weights are

```text
39, 43, 47, 51, 55, 59, 63, 99.
```

These are necessary candidates only; the verifier does not assert that
codewords of any listed weight actually exist.

## 5. The two null motifs and the extension boundary

The `O=0` three-prism gluing forces the nine-vertex rook graph.  Every pair
inside it already realizes exactly the target common-neighbor count.
Therefore an outside vertex has at most one rook neighbor.  There are
exactly 90 boundary edges and 90 outside vertices, so every outside vertex
would have exactly one rook neighbor.  The resulting equitable quotient is

```text
[[4,10],
 [1,13]]
```

with eigenvalues `14,3`, compatible with the ambient spectrum.  This is a
necessary local consequence, not a 99-vertex extension.

The separate four-prism parity-null control is the 12-vertex Cartesian
product `C4 square K3`.  Exact enumeration gives:

```text
12 vertices, 24 edges, degree 4
4 induced prisms
2 prisms through every vertex
maximum adjacent internal common neighbors    1
maximum nonadjacent internal common neighbors 2
spectrum 4, 2^2, 1^2, 0, (-1)^4, (-3)^2
```

Its non-leading eigenvalues are at most three and all eigenvalues are at
least negative four, so induced-subgraph interlacing does not reject it.
This motif proves only that this collection of local cap and spectral tests
cannot force nonzero rooted parity.  It does **not** prove that the motif
extends to an `srg(99,14,1,2)`, that the actual target incidence code has
such a four-prism cycle, or that a full graph exists.

## Final boundary

Wave 102 supplies a verified conditional refinement of the norm-14 shell
bound and exact small-`P` parity information.  It does not bound `n3`
strictly, control `N16` or `N18`, exclude the graph, construct the graph, or
resolve Conway-99.  Literature novelty remains `UNKNOWN`.
