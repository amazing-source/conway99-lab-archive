# Rooted prism parity through the triangle-incidence code

Claim label: `DERIVED`; independent verification required.

## 1. Incidence factorization

Every edge lies in one triangle because `lambda=1`, so the hypothetical
graph has

```text
99*14/(2*3) = 231
```

triangles. Over `F2`, let:

- `B` be the `99 by 231` vertex-triangle incidence matrix;
- `D` be the `231 by P` incidence matrix of the graph whose vertices are
  graph triangles and whose edges are induced triangular prisms;
- `H` be the `99 by P` vertex-prism incidence matrix.

A prism is the disjoint union of its two base triangles, so

```text
H = B D,
f mod 2 = H 1 = B(D 1).                              (1)
```

Every column of `D` has weight two. Thus `D1` is the odd-degree boundary of
the prism-edge set in the triangle graph, and has even weight. Equation (1)
places `f mod 2` in

```text
C0 = {Bz : wt(z) is even},
```

the even subcode of the binary triangle-incidence code.

The triangle Gram matrix is

```text
B B^T = I+A                                            (2)
```

over `F2`: diagonal entries are seven, adjacent pairs occur in one triangle,
and nonadjacent pairs occur in none. The SRG identity

```text
A^2 = 12I-A+2J
```

reduces to `A^2=A`. Its characteristic polynomial reduces to

```text
x^45 (x+1)^54,
```

so `rank_2(A)=54` and `rank_2(I+A)=45`. From (2),

```text
45 <= rank_2(B) <= 99,
44 <= dim(C0) <= 98.
```

The exact dual description is

```text
C0^perp = {x : B^T x is constant on all 231 triangles}.   (3)
```

In particular, any binary labelling whose sum is the same on every graph
triangle gives a congruence `x dot f=0`.

These checks are necessarily global. If `B^T x=0` and `S=supp(x)` is
nonempty, every triangle meets `S` evenly. Each vertex in `S` consequently
has exactly one other `S` vertex in each of its seven incident triangles,
so `G[S]` is 7-regular. Applying the restricted eigenvalue bounds `3` and
`-4` to

```text
chi_S^T A chi_S = 7|S|
```

gives

```text
36 <= |S| <= 60.
```

Also `|S|` is even. Vectors with constant triangle sum one are complements
of these kernel vectors. Hence every nontrivial universal parity check in
(3), apart from the all-ones total-parity check, uses at least 36 vertices.

## 2. Exact parity defect in the norm-14 bound

Wave 100's rootwise inequality is

```text
a14(v) <= 350+floor(5f_v/2).
```

Let

```text
O = #{v : f_v is odd} = wt(f mod 2).
```

Since `sum_v f_v=6P`,

```text
sum_v floor(5f_v/2)
 = (5 sum_v f_v - O)/2
 = 15P-O/2.
```

The scalar relaxation can therefore be replaced by

```text
7*N14 <= 34650+15P-O/2
        = 55440-5*n3-O/2.                              (4)
```

`O` is even, and `N14` is even by antipodality, so

```text
N14 <= 2*floor((55440-5*n3-O/2)/14).                   (5)
```

For one prism, exactly its six vertices are odd. Thus `P=1`,
`n3=4155`, and (5) gives

```text
N14 <= 4950,
```

strictly improving Wave 100's scalar `4952`.

## 3. Two- and three-prism controls

Two distinct induced prism supports cannot share five vertices. Deleting
one vertex from a prism leaves degree multiset

```text
2,2,2,3,3.
```

The missing vertex must attach to the three degree-two vertices. Two
different restorations of the same five vertices would therefore have
three common neighbors, contradicting `lambda=1` if the new vertices were
adjacent and `mu=2` if they were nonadjacent. Hence the overlap is at most
four.

For `P=2`, the parity support is the symmetric difference of two six-sets,
so

```text
O >= 12-2*4 = 4.
```

This improves the numerator in (4) by two, although antipodal rounding
leaves the displayed bound at `N14<=4954`.

Suppose instead that the whole graph had exactly three prisms and `O=0`.
Three distinct six-sets with zero symmetric difference partition their
nine union vertices into three size-three pairwise-intersection blocks.
Each union of two blocks must induce a prism.

The exact labelled census considers all 60 prism graphs on each pair of
blocks, enforces agreement on the shared blocks, and rejects any union that
already exceeds the target `lambda/mu` common-neighbor caps. There are 36
labelled survivors, all block-preservingly isomorphic to the `3 by 3` rook
graph. That graph contains six induced prisms, not three. Therefore

```text
P=3 implies O>0.
```

The rook branch is not itself contradictory. Every pair of rook vertices
already saturates its target common-neighbor count, so every outside vertex
has at most one rook neighbor. The 90 boundary edges and 90 outside
vertices force exactly one each, giving equitable quotient

```text
[[4,10],
 [1,13]]
```

with eigenvalues `14,3`, both allowed.

## 4. Why parity does not close the general case

On twelve vertices, take the Cartesian product `C4 box K3`: four disjoint
triangle layers joined cyclically by matching edges. It contains exactly
four induced prisms, one for each adjacent pair of layers, and every vertex
lies in two. Their rooted parity sum is therefore zero.

The motif respects every induced target cap:

```text
adjacent internal common-neighbor maximum    = 1
nonadjacent internal common-neighbor maximum = 2.
```

Its spectrum lies in the target interlacing interval. This is not a
99-vertex completion, but it proves that cycle-space and local
`lambda/mu` arguments alone cannot force `O>0` once four-prism cycles are
available.

Ordinary adjacency polynomials also stop here. The SRG adjacency algebra is
`span{I,A,J}`, so every diagonal `diag(p(A))` is constant. A nonconstant
rooted prism vector requires Hadamard products or explicit
triangle/prism-incidence tensors; ordinary walk-regular identities only see
scalar totals.

## 5. Remaining route

The next exact target is extension, not another scalar congruence:

- test whether `C4 box K3` can survive the full 99-vertex degree and
  common-neighbor closure;
- test whether the rook regular set can occur in the target;
- determine the actual binary rank and kernel of `B`; or
- constrain the triangle-prism graph beyond its ordinary cycle space.

The present result does not prove a strict `n3` upper bound.
