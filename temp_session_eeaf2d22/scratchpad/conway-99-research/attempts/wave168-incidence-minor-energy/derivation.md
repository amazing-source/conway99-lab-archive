# Derivation

Let `G` be a hypothetical `srg(99,14,1,2)` with adjacency matrix `A`.

## 1. Partial linear triangle geometry

The parameter `lambda=1` says that every edge lies in exactly one triangle.
At a vertex, its 14 incident edges are paired by these triangles, so every
point lies on seven triangle blocks. Counting incidences gives

```text
99*7/3 = 231
```

blocks.

Two distinct points lie in at most one block, and they lie in exactly one
block precisely when they are adjacent in `G`.

Let `B` be the `99 x 231` binary point-block incidence matrix. Diagonal
entries of `B*B^T` are seven and off-diagonal entries are the numbers of
blocks through point pairs. Hence

```text
B*B^T = 7I+A.                                      (1)
```

## 2. Spectra

The SRG identity is

```text
A^2 = 12I-A+2J.
```

Therefore the adjacency spectrum is

```text
14^1, 3^54, (-4)^44.
```

Equation (1) gives

```text
spec(B*B^T) = 21^1, 10^54, 3^44.
```

In particular, `B` has real rank 99. The bipartite Levi graph with adjacency
matrix

```text
[ 0   B  ]
[ B^T 0  ]
```

has spectrum

```text
+/-sqrt(21)^1, +/-sqrt(10)^54, +/-sqrt(3)^44, 0^132.
```

On the 231 blocks define

```text
K=B^T*B-3I.
```

Its off-diagonal entry is one exactly when two blocks meet. Each block has
three points, and each point lies on six other blocks; partial linearity
prevents duplicates. Thus `K` is the adjacency matrix of an 18-regular
block-intersection graph.

The nonzero eigenvalues of `B^T*B` are those of `B*B^T`, while its kernel has
dimension `231-99=132`. Hence

```text
spec(K) = 18^1, 7^54, 0^44, (-3)^132.              (2)
```

## 3. Prism-free endpoint in block space

Let `L,M` be disjoint triangle blocks. A common neighbor of `L,M` in the
block-intersection graph is a triangle block meeting each of them. It meets
each in exactly one point and corresponds to an edge between the point
triples `L` and `M`. Conversely, every such cross edge belongs to its unique
triangle block, giving a common neighbor in `K`.

The cross graph between the two triples is a matching. If one point of `L`
were adjacent to two points of `M`, those two adjacent points would have both
that point and the third point of `M` as common neighbors, contradicting
`lambda=1`.

It follows that

```text
(K^2)[L,M] is in {0,1,2,3}.
```

The value three is a perfect matching between the two triangle blocks. The
six points then induce exactly a triangular prism. Conversely, the two
triangular faces of every induced prism give such a block pair. Therefore

```text
P = number of unordered disjoint block pairs (L,M)
    with (K^2)[L,M]=3.                              (3)
```

At the endpoint, (3) becomes the exact block-graph condition

```text
K[L,M]=0 => (K^2)[L,M]<=2.                          (4)
```

No association-scheme closure for `K` is assumed.

## 4. Eight-point Cauchy-Binet energy

For an eight-point set `S`, let `B_S` be the eight selected rows of `B`.
Then

```text
B_S*B_S^T = 7I+A[S].
```

Cauchy-Binet yields

```text
det(7I+A[S])
  = sum_{T subset blocks, |T|=8} det(B[S,T])^2.     (5)
```

Both the cube `Q3` and the Wagner graph `W8` are triangle-free, 3-regular
graphs on eight vertices. Their induced point sets therefore have the same
first incidence profile:

```text
12 blocks meet S twice,
32 blocks meet S once,
187 blocks miss S.
```

Their adjacency spectra nevertheless give different values in (5). For the
cube,

```text
det(7I+A[Q3])
  = 10*8^3*6^3*4
  = 4,423,680.
```

For the Wagner graph,

```text
det(7I+A[W8])
  = 10*8^2*6*34^2
  = 4,439,040.
```

Thus

```text
det(7I+A[W8])-det(7I+A[Q3]) = 15,360.               (6)
```

Summing (5) over all eight-point sets gives the eighth elementary symmetric
function of the eigenvalues of `B*B^T`:

```text
sum_{|S|=8} det(7I+A[S])
  = [t^8](1+21t)(1+10t)^54(1+3t)^44.               (7)
```

Equation (7) is an exact global conservation law. Turning it into a Wagner
lower bound requires classifying or bounding the contributions of the other
eight-point induced types under (4).

## 5. A compatible code object

For each block `L`, define a binary row `T_L` indexed by three-subsets of
block vertices, with a one when the three blocks all lie in `N_K(L)`.
Then

```text
<T_L,T_M> = binomial(|N_K(L) intersect N_K(M)|,3).
```

The diagonal is `binomial(18,3)=816`. Adjacent blocks have exactly five
common block neighbors, all through their shared point, giving ten. Under
`P=0`, disjoint blocks have at most two common neighbors, giving zero.
Therefore

```text
T*T^T = 816I+10K.                                   (8)
```

Using (2), its eigenvalues are

```text
996^1, 886^54, 816^44, 786^132.
```

Modulo two, all row inner products vanish, so the row space is
self-orthogonal. Modulo three, (8) reduces to `K`. These observations are
consistent rather than contradictory; their value is to expose exact
higher column-multiplicity constraints for a code or design attack.

## Boundary

Equations (3)--(8) change the proof space and distinguish cube from Wagner
at higher order. They do not yet assign a useful sign to the remaining
eight-point configurations. The proposed minor classification is a strategy,
not an endpoint proof.
