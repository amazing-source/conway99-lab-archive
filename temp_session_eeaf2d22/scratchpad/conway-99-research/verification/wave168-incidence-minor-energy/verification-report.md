# Wave 168 clean-room audit

## Verdict

The incidence reformulation and exact identities are
`VERIFIED_WITH_SCOPE`. The proposed minor-classification inequality remains
`UNPROVED`.

## 1. Blocks and incidence spectrum

Because `lambda=1`, every edge lies in one triangle. There are
`99*14/2=693` edges and hence 231 unmarked triangle blocks. Each point lies
on seven blocks.

For the `99 x 231` point-block incidence matrix `B`, two distinct point rows
meet in one column exactly when the points are adjacent. Thus

```text
B*B^T=7I+A.
```

The SRG restricted eigenvalues are 3 and -4 with multiplicities 54 and 44.
Therefore

```text
spec(B*B^T)=21^1,10^54,3^44,
rank(B)=99.
```

The Levi graph has spectrum

```text
+/-sqrt(21)^1, +/-sqrt(10)^54, +/-sqrt(3)^44, 0^132.
```

For `K=B^T*B-3I`, distinct blocks are adjacent exactly when they meet. Each
block has 18 neighbors, and the 132-dimensional kernel of `B` supplies the
last eigenspace:

```text
spec(K)=18^1,7^54,0^44,(-3)^132.
```

All counts and multiplicities are correct. Using edge-marked triangle
columns instead would incorrectly triple the Gram matrix; the attempt uses
one column per distinct triangle.

## 2. Prism translation

For disjoint blocks `L,M`, their common neighbors in `K` are in bijection
with graph edges between their point triples. Each cross edge lies in its
unique triangle block, and a common block cannot contain two points of a base
triangle.

The cross graph is a matching. If one point met two points of the opposite
triangle, that opposite edge would have a second common neighbor, contrary
to `lambda=1`.

Three cross edges are therefore a perfect matching and give exactly an
induced triangular prism. Every prism has a unique unordered pair of
triangular base faces. Hence

```text
P=0
iff
|N_K(L) intersect N_K(M)|<=2
for every disjoint block pair L,M.
```

No ordered-pair factor is missing.

## 3. Motif determinants

For the cube spectrum `3,1^3,(-1)^3,-3`,

```text
det(7I+A[Q3])
 =10*8^3*6^3*4
 =4,423,680.
```

For the Wagner graph as the eight-vertex Mobius ladder, its irrational
eigenvalues pair to give

```text
det(7I+A[W8])
 =10*6*8^2*34^2
 =4,439,040.
```

The exact difference is 15,360. Both motifs are triangle-free cubic graphs,
so both have 12 blocks meeting the point set twice, 32 meeting it once, and
187 missing it. The determinant therefore detects structure not contained in
that scalar profile.

Verdict: `VERIFIED`.

## 4. Global energy

For each eight-point row set `S`, Cauchy-Binet gives

```text
det(7I+A[S])
 = sum_(|J|=8) det(B[S,J])^2.
```

Summing principal minors yields the eighth elementary symmetric function of
the eigenvalues of `B*B^T`:

```text
sum_(|S|=8) det(7I+A[S])
 =[t^8](1+21t)(1+10t)^54(1+3t)^44.
```

This is a weighted identity over all induced eight-point types. The
cube/Wagner difference cannot be isolated without controlling the other
types.

Verdict: `VERIFIED_WITH_SCOPE`.

## 5. Neighborhood-triple Gram

Let `T` have 231 rows indexed by blocks and `binomial(231,3)=2,027,795`
columns indexed by unordered triples `C` of blocks, with

```text
T[L,C]=1 iff C is a subset of N_K(L).
```

Then

```text
(T*T^T)[L,M]
 = binomial(|N_K(L) intersect N_K(M)|,3).
```

The diagonal is `binomial(18,3)=816`. Adjacent blocks share exactly the five
other blocks through their common point and therefore have entry
`binomial(5,3)=10`. Under `P=0`, disjoint blocks share at most two neighbors
and have entry zero. Thus

```text
T*T^T=816I+10K.
```

Its real spectrum is

```text
996^1,886^54,816^44,786^132.
```

Modulo two the binary row code is self-orthogonal. Modulo three the Gram
reduces to `K=B^T*B`. These are Gram-level statements only; they do not imply
rank equality or code equivalence. The matrix is highly rectangular and its
columns do not have uniform weight.

Verdict: `VERIFIED_WITH_SCOPE`.

## Boundary

The determinant energy and code Gram are consistent with a hypothetical
graph. A successful continuation must classify column or minor
multiplicities, or derive a signed inequality for the other eight-point
types under the prism-free codegree constraint. No such inequality is
verified here. The rigorous interval remains `708<=n3<=4158`.
