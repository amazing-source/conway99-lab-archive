# Precomparison independent reconstruction of the global Schur obstruction

```yaml
role: verifier
date_utc: 2026-07-23T16:17:04Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: DERIVED
scope: >
  Conditional necessary bound on the induced-N3 count of any putative
  srg(99,14,1,2), reconstructed before inspecting the submitted Wave 20
  report, checker, tests, JSON, or failure logs.
inputs:
  attempts/wave20-global-obstruction/independent-verifier/public-premise-freeze.yaml: TO_BE_HASHED_IN_FINAL_MANIFEST
method: >
  Exact triangle-incidence spectrum, combinatorial polynomial entries,
  fixed-triangle moments, spectral projector scaling, Schur positivity,
  an integral mod-2/mod-4 argument, and the PSD zero-diagonal lemma.
command: NONE_PRECOMPARISON_HUMAN_DERIVATION
outputs:
  attempts/wave20-global-obstruction/independent-verifier/independent-reconstruction.md: TO_BE_HASHED_IN_FINAL_MANIFEST
limitations:
  - This is a conditional necessary bound, not an existence or nonexistence proof for Conway-99.
  - It uses the previously public exact induced-C6 identity only for the final translation.
  - Novelty and literature status are out of scope and remain UNKNOWN.
  - Candidate content had not been inspected when this reconstruction was written.
```

## 1. Triangle-incidence spectrum

Assume that `G` is an `srg(99,14,1,2)` with adjacency matrix `X`.  Every
vertex lies on seven graph-triangles and every edge lies on its unique
graph-triangle.  Thus `G` has

```text
99*14/(2*3) = 231
```

graph-triangles.  Let `B` be the `99 x 231` vertex-by-triangle incidence
matrix, and let `Gamma` be the intersection graph of those 231 triangles.
Distinct graph-triangles cannot share an edge, so they meet in either zero or
one original vertices.  Consequently

```text
B B^T = 7 I + X,
B^T B = 3 I + Gamma.
```

The frozen SRG identity gives

```text
spec(X) = 14^1, 3^54, (-4)^44.
```

Hence the nonzero spectrum of `B B^T`, and therefore of `B^T B`, is

```text
21^1, 10^54, 3^44.
```

The remaining `231-99=132` eigenvalues of `B^T B` are zero.  Subtracting
`3I` proves

```text
spec(Gamma) = 18^1, 7^54, 0^44, (-3)^132.
```

In particular `Gamma` is 18-regular.

## 2. The polynomial matrix and its combinatorial entries

Put

```text
C = Gamma^2 - 5 Gamma - 18 I.
```

Its entries are:

- `C[T,T]=18-18=0`;
- if distinct triangles `T,U` meet at a vertex, their common
  `Gamma`-neighbors are exactly the other five graph-triangles through that
  vertex, so `C[T,U]=5-5=0`;
- if `T,U` are disjoint, every common `Gamma`-neighbor contains exactly one
  cross-edge between `T` and `U`, and the unique triangle on every cross-edge
  is such a common neighbor.  Therefore `C[T,U]=r(T,U)`, the number of graph
  edges between the two triangles.

The cross-edges form a matching.  Two cross-edges with a shared endpoint
would give an internal edge of one triangle a second common neighbor,
contrary to `lambda=1`.  Thus

```text
r(T,U) in {0,1,2,3}.
```

The polynomial sends the four `Gamma` eigenvalues as follows:

```text
18 -> 216,  7 -> -4,  0 -> -18,  -3 -> 6.
```

## 3. All fixed-triangle counts and the `q/n3` relation

For fixed `T`, let `a_r(T)` be the number of disjoint graph-triangles `U`
with `r(T,U)=r`.  There are `231-1-18=212` disjoint triangles.  The row sum
of `C` is

```text
18^2 - 5*18 - 18 = 216.
```

For the second binomial moment, choose an ordered pair `(x,y)` of distinct
vertices of `T` and an external neighbor `u` of `x`.  There are
`3*2*12=72` choices.  The pair `u,y` is nonadjacent, and its second common
neighbor supplies the uniquely paired cross-edge at `y`.  Every unordered
pair of cross-edges is obtained in the two possible orders.  Therefore the
correct unordered-pair total is `72/2=36`, not 72.  Hence

```text
sum_r a_r = 212,
sum_r r a_r = 216,
sum_r binom(r,2) a_r = 36.
```

Writing `p(T)=a_3(T)` and `q(T)=12-p(T)` gives the unique solution

```text
(a_0,a_1,a_2,a_3)
  = (20+q, 180-3q, 3q, 12-q),    0 <= q <= 12.
```

An induced `N3` is exactly an unordered disjoint triangle pair with two
cross-edges.  Consequently

```text
2 n3 = sum_T a_2(T) = 3 sum_T q(T),
sum_T q(T) = 2 n3 / 3.
```

This also proves `3 | n3`; the factor two on the left is the
ordered-fixed-side versus unordered-pair conversion.

## 4. Exact zero-eigenspace projector

Let `E0` be the orthogonal projector onto the 44-dimensional zero eigenspace
of `Gamma`.  Lagrange interpolation gives

```text
E0 = ((Gamma-18I)(Gamma-7I)(Gamma+3I))/378.
```

The spectral relation

```text
Gamma^3 - 4 Gamma^2 - 21 Gamma = 18 J
```

reduces this to

```text
E0 = (21I + 4Gamma - Gamma^2 + J)/21.
```

Thus the integral matrix

```text
M = 21 E0 = 21I + 4Gamma - Gamma^2 + J
            = 3I - Gamma - C + J
```

satisfies

```text
M^2 = 21M.
```

Its combinatorial entries are exactly

```text
M[T,T] = 4,
M[T,U] = 0                    if T,U intersect,
M[T,U] = 1-r(T,U)             if T,U are disjoint.
```

Therefore the entry set is `{4,0,1,-1,-2}`.  In a fixed row, the odd
entries occur precisely at the disjoint pair types `r=0` and `r=2`, in
number

```text
a_0+a_2 = 20+4q >= 20.
```

Every row of `M` is consequently nonzero modulo two.

## 5. Schur positivity and the first lower bound

The matrix `M=21E0` is positive semidefinite.  By the Schur product theorem,

```text
W = M o M
```

(entrywise square) is positive semidefinite.  Define

```text
mathcal_A = M W M.
```

This is an integral positive-semidefinite matrix.  Cyclicity of trace and
`M^2=21M` give

```text
tr(mathcal_A) = tr(W M^2) = 21 tr(WM)
              = 21 sum_(T,U) M[T,U]^3.
```

For fixed `T`, the cubic row sum is

```text
4^3 + a_0*1^3 + a_2*(-1)^3 + a_3*(-2)^3
 = 64+a_0-a_2-8a_3
 = 6q(T)-12.
```

The 18 intersecting triangles and the `a_1` disjoint triangles contribute
zero and must not be silently omitted from the entry classification.
Summing over all fixed sides and using `sum q=2n3/3`,

```text
tr(mathcal_A)
 = 21 (6*(2n3/3) - 12*231)
 = 84 (n3-693).
```

Positive semidefiniteness first yields the algebraic necessary bound
`n3>=693`.

## 6. Modulo four and strict positivity of every diagonal entry

Entrywise, every integer satisfies `m^2 congruent m (mod 2)`.  Hence

```text
D = (W-M)/2
```

is an integral symmetric matrix.  Since `M[T,T]=4`,

```text
D[T,T] = (4^2-4)/2 = 6,
```

so `D mod 2` is symmetric with zero diagonal: it is an alternating bilinear
form over `F_2`.  Therefore

```text
z^T D z = 0 (mod 2)
```

for every integral vector `z`.

Let `m_T=M e_T`.  Using `W=M+2D`,

```text
mathcal_A[T,T]
 = m_T^T W m_T
 = (M^3)[T,T] + 2 m_T^T D m_T.
```

Now `M^3=441M`, so the first term is `441*4=1764`, divisible by four.
The alternating-form calculation makes the second term divisible by four.
Thus

```text
mathcal_A[T,T] = 0 (mod 4)    for every T.
```

Also

```text
W = M (mod 2),
mathcal_A = M W M = M^3 = 441M = M (mod 2).
```

Every row of `mathcal_A` is nonzero modulo two because every row of `M` is.
For a real PSD matrix, a zero diagonal entry forces its entire row and
column to vanish (equivalently, every corresponding `2 x 2` principal
minor has nonnegative determinant).  Therefore no diagonal entry of
`mathcal_A` is zero.  Each is a nonnegative integral multiple of four, so
in fact

```text
mathcal_A[T,T] >= 4    for all 231 triangles.
```

It follows that

```text
84(n3-693) = tr(mathcal_A) >= 4*231 = 924,
n3-693 >= 11.
```

Since `3 | n3` and `3 | 693`, the difference is a multiple of three.  The
first permitted difference at least eleven is twelve:

```text
n3 >= 705.
```

In particular the candidate gaps `Delta=n3-693` equal to `0,3,6,9` are all
impossible.  The arithmetic admits `Delta=12`; it does not construct a graph
at that value.

## 7. Induced-six-cycle translation and status boundary

Using the previously public exact identity

```text
induced_C6_count = 209286+n3,
```

the conditional necessary consequence is

```text
induced_C6_count >= 209991.
```

This establishes only a necessary condition on any putative target graph.
It neither constructs an `srg(99,14,1,2)` nor proves that none exists.

```text
global Schur argument:                 DERIVED, pending artifact audit
conditional necessary n3 bound:       n3 >= 705
conditional induced-C6 bound:         >= 209991
Conway-99 existence/nonexistence:      UNKNOWN
novelty/literature status:             UNKNOWN (out of scope)
```
