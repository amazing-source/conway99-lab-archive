# Wave 32: exact boundary for the rootless indecomposable branch

```yaml
role: proof_b
date_utc: 2026-07-24T08:30:00Z
git_commit: f0783b82d9b0260f5461cd68c647f62f646cdd81
claim_label: UNKNOWN
scope: >-
  Structural reductions for the rootless integrally indecomposable endpoint
  branch under the frozen n3=708 projector package. The report proves that
  any surviving rootless endpoint must be indecomposable and forbids one
  exact three-row motif, but does not prove that actual incidence forces the
  motif. n3=708, Conway-99, and novelty remain UNKNOWN.
inputs:
  agents/2026-07-24-wave31-survivor-proof.md: 075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa
  verification/wave31-sign-commutant/audit.md: f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md: 642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de
  agents/2026-07-24-wave28-glue-discriminant.md: 3c1354a04f33602c6e339875c8de4f77d1874bd6e8f83dbcb712b91717d6c1ff
method: >-
  Primitive Smith generation, minimum-four support connectivity, the Wave 31
  incidence commutant, exhaustive signed three-row Gram arithmetic, a mixed
  adjacency-trace reduction, and hostile finite-field construction.
command: |-
  cd attempts/wave32-indecomposable
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
limitations:
  - Discovery cannot self-promote; every new reduction needs a verifier.
  - The actual-incidence value of the decisive mixed triple trace is UNKNOWN.
  - No graph, endpoint frame, rootless indecomposable lattice, or
    counterexample to Conway-99 is constructed.
  - No h=729 assumption is used.
```

## Result

The branch does not close. Its strongest exact reduction is:

```text
any surviving rootless actual endpoint is integrally indecomposable;
rootlessness forces tr(A_-1 A_-2^2)=0;
whether actual target incidence forces this trace positive is UNKNOWN.
```

Here `A_-1` and `A_-2` are the adjacency matrices on the 231 graph triangles
for the row-inner-product classes `M_ij=-1` and `M_ij=-2`.

The status wall is:

```text
rootless decomposable actual endpoint:           impossible by Wave 31
surviving rootless endpoint is indecomposable:   DERIVED
{-2,-2,-1} three-row motif is forbidden:         DERIVED
actual incidence forces the forbidden motif:     UNKNOWN
rootless indecomposable endpoint:                 UNKNOWN
n3=708:                                          UNKNOWN
Conway-99 existence/nonexistence and novelty:    UNKNOWN
```

## 1. The frame rows generate the endpoint lattice

Use the frozen primitive projector lattice

```text
L=U intersect Z^231
```

and let the columns of the integral `231 x 44` matrix `X` be an integral
basis of `L`. Since `L` is primitive, the Smith normal form of `X` has 44
unit invariant factors. Transposition preserves the nonzero Smith factors.
Therefore

```text
X^T Z^231=Z^44.                                  (1)
```

In coordinates, (1) says exactly that the 231 row vectors `x_i` of `X`
generate the full `S`-lattice, not merely a finite-index sublattice. Full
column rank alone would not suffice; primitivity is active.

This argument uses the primitive projector-lattice construction but not
actual graph incidence and not `h=729`.

## 2. Rootless decomposability is support disconnection

Suppose the even positive-definite form `S` has minimum at least four and an
integral orthogonal decomposition

```text
S=S_1 orthogonal_sum ... orthogonal_sum S_t.
```

Every frame row has `S`-norm four. Each nonzero orthogonal component has even
positive norm at least four, so exactly one component is nonzero. Hence every
row is block-supported. After grouping rows,

```text
M=XSX^T
```

is coordinate-block diagonal.

Conversely, if the nonzero-support graph of `M` is disconnected, the
`Z`-spans of the row sets in distinct components are mutually orthogonal.
Equation (1) says that their sum is the whole lattice; positive definiteness
makes their intersections zero. Thus they give a nontrivial integral
orthogonal decomposition.

Consequently, under minimum four,

```text
S integrally indecomposable
  iff the nonzero-support graph of M is connected.       (2)
```

The actual-incidence Wave 31 theorem rules out every proper coordinate
projector block: projector trace gives `21|b`, incidence transport gives
`33|b`, and hence `231|b`. Therefore the actual `M` support is connected.
Combining with (2), any surviving rootless endpoint is necessarily
indecomposable.

This is a structural reduction, not an exclusion of the indecomposable case.

## 3. A forbidden norm-two motif

Let three distinct frame rows have Gram matrix

```text
    [ 4 -2 -2 ]
H = [ -2 4 -1 ].
    [ -2 -1 4 ]
```

Its leading principal minors are

```text
4, 12, 20,
```

so it is positive definite. But

```text
(x_1+x_2+x_3)^T S (x_1+x_2+x_3)
 =12+2(-2-2-1)
 =2.                                             (3)
```

Thus (3) is a root and is impossible in the rootless branch.

The exact checker exhausts every edge label in

```text
{-2,-1,0,+1}^3
```

and every coefficient choice in `{+1,-1}^3` modulo global sign. The unique
edge-value multiset producing norm two is

```text
{-2,-2,-1}.                                     (4)
```

Changing the `-1` to `+1` raises the best displayed sum norm from two to six,
so the sign is active.

Once `X,S,M` exist, (3)--(4) are abstract exact Gram arithmetic. Actual graph
incidence is used only to translate the classes:

```text
M=-1  <=> disjoint triangle pair with r=2 cross-edges,
M=-2  <=> disjoint triangle pair with r=3 cross-edges.
```

Hence a rootless endpoint forbids an `r=2` pair having a common triangle
which is `r=3` from both endpoints.

## 4. The decisive mixed triple trace

Let `A_-1,A_-2` be the two class adjacency matrices. Direct expansion gives

```text
tr(A_-1 A_-2^2)
 =2 * #{unordered {-2,-2,-1} row triples}.       (5)
```

All entries counted in (5) are nonnegative. Rootlessness therefore requires

```text
tr(A_-1 A_-2^2)=0.                              (6)
```

At `n3=708`, the exact unordered pair census is

```text
M=+1:  2546,
M= 0: 22161,
M=-1:   708,
M=-2:  1150.
```

Equivalently, with `sum q(T)=472`, the degree sums are

```text
sum deg(+1)=5092,
sum deg(0)=44322,
sum deg(-1)=1416,
sum deg(-2)=2300.
```

These values do not determine (5). No valid incidence count or positivity
argument forcing (5) to be positive was obtained. This is the exact current
blocker.

## 5. Mod-two and odd-prime code shadows

Since every surviving determinant `h` is odd, `S mod 2` is a nondegenerate
alternating form. The quadratic refinement

```text
q(v)=v^T S v/2 mod 2
```

is defined, and every norm-four frame row is singular. Primitivity makes the
row residues span `F_2^44`. Moreover,

```text
M mod 2
```

is a symmetric rank-44 idempotent with zero diagonal and `M1=0`.

The checker constructs an exact hostile control with all 231 rows nonzero,
all rows singular, rank 44, zero row sum, and every one of these projector
properties. It uses eleven copies of the nine nonzero singular vectors in a
four-dimensional hyperbolic quadratic space, then pads by 66 duplicate
pairs. This is only a finite-field object, but it proves that the mod-two
shadow alone is consistent.

For `p=3,7`, primitivity still gives

```text
rank_Fp(X)=44,
X^T X=G=21S^-1.
```

However, integrality of `G` does **not** make it zero modulo `p`. If
`u=v_3(h)` and `v=v_7(h)`, the exact inherited identities are

```text
rank_F3(G)=u,       rank_F3(M)=44-u,
rank_F7(G)=v,       rank_F7(M)=44-v.
```

Thus the column code has a degenerate restricted dot product of the displayed
rank, not a universally self-orthogonal one. No valid code or incidence
bridge from these modular ranks to (5) was derived.

## 6. Boundary and retained failures

The diagonal-sign commutant from Wave 31 cannot be reused without a coordinate
block. A rational invariant subspace, a discriminant subgroup, or an
invariant sublattice of `B` is not such a block. Likewise, positive pair
counts do not imply the mixed triangle in (4).

The incomplete two-neighbor hostile-control exploration and every other
non-improvement are retained in
`attempts/wave32-indecomposable/failed-routes.md`.

The standard-library suite audits ten hostile tests, including deterministic
JSON, the exact 231-row binary construction, the sign mutation, and the
explicit `UNKNOWN` wall. It certifies only the displayed finite arithmetic;
a fresh verifier must reconstruct every prose bridge before promotion.
