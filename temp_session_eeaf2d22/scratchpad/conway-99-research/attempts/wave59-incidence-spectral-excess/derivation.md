# Wave 59 incidence and spectral-excess derivation

All claims are conditional on a prism-free hypothetical
`G=srg(99,14,1,2)`. This is discovery work pending an independent verifier.

## 1. Point--triangle incidence graph

Every edge of `G` lies in one triangle because `lambda=1`. There are

```text
99*14/2 = 693 edges,
693/3 = 231 triangles.
```

Every point lies in `14/2=7` triangles, while every triangle contains three
points. Let `N` be the 99-by-231 point--triangle incidence matrix. Its row
inner products give

```text
N*N^T = A + 7I,
```

where `A` is the adjacency matrix of `G`: a row has norm squared seven, two
adjacent points share their unique triangle, and two nonadjacent points
share no triangle.

The target adjacency spectrum is

```text
14^1, 3^54, (-4)^44.
```

Hence the nonzero squared singular values of `N` are

```text
21^1, 10^54, 3^44.
```

The incidence graph

```text
L = [[0,N],[N^T,0]]
```

is connected and `(7,3)`-biregular on `99+231=330` vertices. Its exact
spectrum is

```text
(+/-sqrt(21))^1,
(+/-sqrt(10))^54,
(+/-sqrt(3))^44,
0^132.
```

The zero multiplicity is `231-rank(N)=132`. The trace-square check is

```text
2*(21 + 54*10 + 44*3) = 1386 = 2*693.
```

## 2. Girth and diameter

The graph `L` is bipartite. A four-cycle would mean that two graph points lie
in two triangles, which is impossible. A six-cycle would give three graph
points whose three pairwise edges lie in three distinct triangles. The
points would form a graph triangle, but `lambda=1` forces those three edges
into the same unique triangle. Thus `girth(L)>=8`.

Every graph nonedge has exactly two common neighbors. The resulting graph
four-cycle has four distinct edge-triangles and lifts to an incidence
eight-cycle. Therefore

```text
girth(L)=8.
```

Point--point distances in `L` are at most four, and point--triangle distances
are at most five. For two graph triangles:

- relation `K` gives incidence distance two;
- relations `B` and `C` have a cross edge and give distance four;
- relation `D` has no cross edge, but any root point and target point have
  two common graph neighbors, giving distance six.

Relation `D` has positive valency below, so

```text
diameter(L)=6.
```

## 3. Rooted relation counts without transitivity

Fix a graph triangle `R`. Its other incident triangles number

```text
3*(7-1)=18.
```

There are 212 disjoint triangles. Each of the 36 graph edges leaving `R`
ends at an outside point that lies in six additional, disjoint triangles.
Thus

```text
2B + C = 36*6 = 216
```

counts root-to-disjoint-triangle cross edges.

The 12 outside neighbors at each root point form three sectors. Between two
sectors there is a perfect matching: for a point `y` adjacent to root point
`r_i`, the nonedge from `y` to another root point `r_j` has `r_i` as one
common neighbor and exactly one other common neighbor in the `r_j` sector.
There are 12 matching edges for each of the three sector pairs.

At the prism-free endpoint, the triangle on such a matching edge cannot
have a third root cross edge. Each matching edge therefore gives a distinct
relation-`B` triangle. Consequently

```text
K=18, B=36, C=144, D=32.
```

These are fixed-root counts derived from the parameters; no triangle
transitivity or target automorphism is assumed.

## 4. Exact distance layers

Around a point root, the incidence distance layers are

```text
1, 7, 14, 84, 84, 140.
```

The partition is equitable around every graph point, with intersection
array

```text
b = (7,2,6,2,5),
c = (1,1,1,2,3).
```

For example, a distance-four point is nonadjacent to the root and has
exactly two common graph neighbors with it. These give two predecessor
triangles; its other five incident triangles lie at distance five.

Around a triangle root, the layers are

```text
1, 3, 18, 36, 180, 60, 32.
```

The distance-four line layer is `B union C`. A `B` triangle has two point
neighbors in the preceding layer and a `C` triangle has one:

```text
c4(B)=2, c4(C)=1.
```

The next layer also has nonintegral average intersection values

```text
average c5 = (36*1 + 144*2)/60 = 27/5,
average b5 = (32*3)/60 = 8/5.
```

Thus `L` is distance-regular around every point, but not around a triangle,
and is not distance-biregular. This is not a contradiction to the existence
of a general semiregular bipartite graph.

Fiol's [Theorem 6](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v20i3p21/pdf/)
is the applicable spectral-excess framework for a semiregular bipartite
graph. Here its notation is in case (c):

```text
d=6 is even,
m(0)=132=231-99.
```

The ordinary regular spectral-excess theorem is not applied to `L`.

## 5. The regular triangle graph

Square the incidence construction on the triangle side:

```text
K = N^T*N - 3I.
```

This `K` is the 18-regular graph on the 231 graph triangles, with adjacency
equal to triangle relation `K`. Its spectrum is

```text
18^1, 7^54, 0^44, (-3)^132.
```

Its distance layers are

```text
1, 18, 180, 32,
```

corresponding to `I`, `K`, `B union C`, and `D`. Thus it is connected,
regular, has diameter three, and has four distinct eigenvalues. The ordinary
spectral-excess theorem applies to this graph.

Exact Gram--Schmidt orthogonalization against the spectrum gives

```text
p0(x) = 1,
p1(x) = x,
p2(x) = 3x^2/4 - 15x/4 - 27/2,
p3(x) = x^3/18 - 35x^2/36 + 19x/12 + 25/2.
```

The normalization is `||pi||^2=pi(18)`. In particular,

```text
p3(18)=50,
actual excess=32.
```

The strict inequality is consistent and certifies that the triangle graph is
not distance-regular. It does not certify nonexistence.

## 6. Exact walk tables and defect matrix

The common-`K`-neighbor counts give

| relation | `I` | `K` | `B` | `C` | `D` |
|---|---:|---:|---:|---:|---:|
| `K^2` | 18 | 5 | 2 | 1 | 0 |
| `N^T A N` | 6 | 4 | 2 | 1 | 0 |

Using `A^2=-A+12I+2J` and `N^T J N=9J`,

```text
K^3 = 4*N^T*A*N + 25K + 48I + 18J.
```

Therefore

| relation | `I` | `K` | `B` | `C` | `D` |
|---|---:|---:|---:|---:|---:|
| `K^3` | 90 | 59 | 26 | 22 | 18 |

Substitution in the predistance polynomials yields

| relation | `I` | `K` | `B` | `C` | `D` |
|---|---:|---:|---:|---:|---:|
| `p2(K)` | 0 | 0 | `3/2` | `3/4` | 0 |
| `p3(K)` | 0 | 0 | `-1/2` | `1/4` | 1 |

Writing `A_D` for the distance-three matrix,

```text
E = p3(K)-A_D = (A_C-2A_B)/4.
```

The same defect transfers with opposite sign at distance two:

```text
p2(K)-A_distance_2 = -E.
```

Thus `p0(K)+p1(K)+p2(K)+p3(K)=J` remains exact. The normalized Frobenius
data are

```text
||p3(K)||^2 = 50,
||A_D||^2 = 32,
<p3(K),A_D> = 32,
||E||^2 = 18.
```

The orthogonal projection of `A_D` onto the four-dimensional polynomial
adjacency algebra is

```text
(16/25)*p3(K).
```

Its residual has normalized squared norm `288/25`, and the angle cosine
between `A_D` and `p3(K)` is exactly `4/5`. This is the precise smaller
spectral-excess obstruction found in this wave.

For the integral signed defect

```text
F=A_C-2A_B=4E,
```

the row sum is 72, `trace(F)=0`, and `trace(F^2)=66528`. It has eigenvalue
72 and is nonzero with trace zero, so it is indefinite; the hoped-for PSD
contradiction is unavailable. Also, no proof shows that `F` commutes with
`K`, so simultaneous diagonalization would be an unjustified coherent-
configuration assumption.

There is a genuine PSD rank constraint. Give each triangle the binary vector
of unordered pairs of its 18 `K`-neighbors. The Gram matrix is

```text
binom(K^2 entry,2) = 153I + 10K + A_B.
```

Since `lambda_min(K)=-3` and every eigenvalue of the 36-regular `A_B` lies
in `[-36,36]`, this Gram matrix is at least `87I`. Hence it is positive
definite of rank 231. The feature space is much larger than 231, so this is a
new exact rank condition but not a contradiction.

## 7. Ihara--Bass and exact short cycles

Let `H` be the nonbacktracking matrix on the 1,386 oriented incidences. The
Ihara--Bass determinant specializes to

```text
det(I-uH) =
  (1-u^2)^363
  (1+2u^2)^132
  (1-13u^2+12u^4)
  (1-2u^2+12u^4)^54
  (1+5u^2+12u^4)^44.
```

The first exact traces are

```text
tr(H^2)=tr(H^4)=tr(H^6)=0,
tr(H^8)=33,264,
tr(H^10)=665,280,
tr(H^12)=6,020,784,
tr(H^14)=69,854,400.
```

Lengths below twice the girth cannot support a repeated-vertex tailless
nonbacktracking closed walk. Dividing by twice the length gives the exact
simple-cycle counts

```text
C8  = 2,079,
C10 = 33,264,
C12 = 250,866,
C14 = 2,494,800.
```

The eight-cycle count independently agrees with `4158/2`, since each graph
four-cycle is indexed by its two nonedge diagonals. All moments are integral
and nonnegative; no Ihara obstruction appears.

## 8. Cage comparison and boundary

The edge-root Moore tree for a `(7,3)`-biregular graph of girth eight gives
at least

```text
points: 1+2+12+24 = 39,
lines:  1+6+12+72 = 91,
total: 130.
```

The target incidence graph has `99+231=330` vertices, an excess of 200 over
this bound. Moore equality would have the generalized-quadrangle layer sizes
for order `(2,6)` and diameter four; the target is far from equality and has
diameter six. The bound gives no contradiction.

The useful exact output of this wave is therefore:

1. a point-side distance-regular but triangle-side nonregular incidence
   geometry;
2. an exact spectral-excess gap of 18 in the regular triangle graph;
3. the signed defect `(A_C-2A_B)/4` and distance-matrix projection residual
   `288/25`;
4. a full-rank 231 pair-neighborhood Gram constraint;
5. exact short nonbacktracking cycle counts.

No endpoint exclusion, full graph, strict `n3` upper bound, or novelty claim
follows.

