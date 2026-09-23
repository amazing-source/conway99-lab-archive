# Wave 20 global Schur-projector obstruction

```yaml
role: proof_b
date_utc: 2026-07-23T16:00:21Z
git_commit: a121e789e03a32c3d29bce8947b16033c0061ce7
claim_label: DERIVED
scope: conditional global lower bound on induced N3 copies in a putative srg(99,14,1,2)
inputs:
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  STRUCTURE.md: 7dff67ec4b8796049ed5603b3733d3f4442a1fe607d258f45b835b8a1d7dad5c
  agents/2026-07-23-wave18-n3-57-structural.md: fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6
  verification/2026-07-23-wave18-n3-57-structural-audit.md: 8534456ac92fd704ad7b24f5d7d2c262ea31476132018e9d14a8e4779b27ae5d
method: exact triangle-incidence spectrum, a primitive spectral projector, Schur positivity, and an integral mod-four PSD lift
command: |
  cd attempts/wave20-global-obstruction
  python -m unittest -v test_exact_check.py
  python exact_check.py --output exact-checks.json
outputs:
  exact_checker: attempts/wave20-global-obstruction/exact_check.py
  hostile_tests: attempts/wave20-global-obstruction/test_exact_check.py
  exact_results: attempts/wave20-global-obstruction/exact-checks.json
limitations: conditional on target existence; discovery-agent DERIVED status only; no target resolution or literature-novelty claim
```

## Result and boundary

Conditional on a putative `srg(99,14,1,2)`, let `n3` be the number of induced
copies of two disjoint triangles joined by exactly two independent cross
edges. The derivation below gives

```text
n3 >= 705.
```

Combining this only with the already-audited identity
`induced_C6=209286+n3` would give

```text
induced_C6 >= 209991.
```

This is a discovery-agent derivation, not an independent verification. It
does not prove nonexistence, construct the graph, establish a formal proof, or
determine novelty. Conway-99 and novelty remain `UNKNOWN`.

The lane was isolated from the pending Wave 19 closure work and from the other
Wave 20 discovery lane. It used only the frozen parameters and public,
audited identities through Wave 18.

Discovery provenance is deliberately explicit. This lane first derived the
`E`-projector cubic and the endpoint 693, then the integral mod-two lift to
699. The orchestrator independently reconstructed all four projectors and all
mixed Schur triple traces, agreeing with every rational coefficient, and
noticed the stronger mod-four diagonal refinement. This lane independently
checked that refinement and incorporated it, producing 705. That
cross-checking occurred within discovery/orchestration, not in the frozen
verifier role, so it does not promote the claim beyond `DERIVED`.

## 1. Triangle incidence and the four eigenspaces

Let `mathcal T` be the set of graph triangles and let `N` be the
`99`-by-`231` vertex-triangle incidence matrix. Every graph edge lies in one
triangle and every graph vertex lies in seven triangles. Distinct triangles
meet in at most one vertex. Therefore

```text
N N^T = A + 7 I,
N^T N = 3 I + Gamma,
```

where `Gamma` joins two triangles when they intersect.

The frozen adjacency spectrum is

```text
14^1, 3^54, (-4)^44.
```

Thus the nonzero eigenvalues of `N^T N` are

```text
21^1, 10^54, 3^44,
```

and its remaining 132 eigenvalues are zero. It follows exactly that

```text
spec(Gamma) = 18^1, 7^54, 0^44, (-3)^132.
```

No association-scheme assumption is being made; this follows just from the
two incidence products.

## 2. The cross-edge matrix

Define

```text
C = Gamma^2 - 5 Gamma - 18 I.
```

Its entries have a direct interpretation.

- On the diagonal, `(Gamma^2)[T,T]=18`, so `C[T,T]=0`.
- If distinct triangles `T,U` meet at `x`, their five other common
  `Gamma`-neighbors are the five other graph triangles through `x`. A common
  triangle meeting them at two different points would require a forbidden
  extra edge inside the `7K2` neighborhood of `x`. Hence `C[T,U]=0`.
- If `T,U` are disjoint, a common `Gamma`-neighbor is the unique graph
  triangle on a cross-edge between `T` and `U`, and conversely. Hence
  `C[T,U]=r(T,U)`, their number of cross-edges.

Those cross-edges form a matching, since two with a common endpoint would put
an edge of the opposite triangle in two graph triangles. Consequently
`r(T,U)` lies in `{0,1,2,3}`.

On the four `Gamma` eigenspaces, `C` has eigenvalues

```text
216, -4, -18, 6
```

respectively.

## 3. The exact row distribution

Fix a graph triangle `T` and let `a_r(T)` be the number of disjoint triangles
with exactly `r` cross-edges to `T`. There are 212 disjoint triangles, so

```text
sum_r a_r = 212.
```

There are 36 graph edges leaving `T`. For each such edge `xy`, with `x` in
`T`, six of the seven triangles through `y` are disjoint from `T`; the seventh
contains `xy`. Thus

```text
sum_r r a_r = 36*6 = 216.
```

For the second binomial moment, choose an ordered pair of distinct vertices
`x,z` of `T` and one of the twelve external neighbors `y` of `x`. The
nonedge `y,z` has common neighbors `x` and a unique other vertex `w`. The
unique triangle on the edge `yw` is disjoint from `T` and supplies the paired
cross-edge at `z`. Reversing the chosen vertices of `T` counts the same
unordered cross-edge pair again. Therefore

```text
sum_r binom(r,2) a_r = 6*12/2 = 36.
```

Let `p(T)=a_3(T)` and `q(T)=12-p(T)`. Solving the three equations gives

```text
(a_0,a_1,a_2,a_3)
  = (20+q, 180-3q, 3q, 12-q).
```

The `r=2` pairs are precisely the induced `N3` pairs. Summing ordered
orientations gives

```text
2 n3 = sum_T a_2(T) = 3 sum_T q(T),
sum_T q(T) = 2 n3 / 3.
```

In particular, `3` divides `n3`. The global ordered pair counts are

```text
r=0: 4620 + 2n3/3,
r=1: 41580 - 2n3,
r=2: 2n3,
r=3: 2772 - 2n3/3.
```

This derivation includes the possible `q=0` rows; it does not use the
separate `q=0 or q>=2` gap.

## 4. The zero-eigenspace projector

The orthogonal projector onto the 44-dimensional zero eigenspace of `Gamma`
is

```text
E = (1/7) I + (1/21) J - (1/21) Gamma - (1/21) C.
```

Checking this on the four eigenspaces gives eigenvalues `0,0,1,0`, so `E` is
positive semidefinite and `E^2=E`. Its entries are especially simple:

```text
E[T,T]                 = 4/21,
E[T,U]                 = 0       if T,U intersect,
E[T,U]                 = (1-r)/21 if T,U are disjoint with r cross-edges.
```

Equivalently, the integral scaled projector

```text
M = 21 E
```

has rank 44, satisfies

```text
M^2 = 21 M,
M 1 = 0,
```

and has diagonal `4` and off-diagonal entries in `{0,1,-1,-2}`.

## 5. Schur positivity gives `n3>=693`

The Schur product theorem makes `E o E` positive semidefinite. For positive
semidefinite matrices `P,Q`,

```text
tr(PQ) = ||P^(1/2) Q^(1/2)||_F^2 >= 0.
```

Applying this to `P=E` and `Q=E o E` gives

```text
0 <= tr(E(E o E))
   = sum_(T,U) E[T,U]^3.
```

Substituting the complete ordered pair distribution yields

```text
sum_(T,U) E[T,U]^3
  = (4 n3 - 2772) / 9261
  = 4(n3-693) / 9261.
```

Therefore

```text
n3 >= 693.
```

This is a global inequality: it does not enumerate an equality profile or
assume an automorphism.

There is also a useful equality diagnostic. The Schur cube `E o E o E` is
positive semidefinite. Its row sum at `T`, after multiplying by `21^3`, is

```text
4^3 + a_0(T) - a_2(T) - 2^3 a_3(T)
  = 6(q(T)-2).
```

If `n3=693`, its all-ones quadratic form is zero, so positive semidefiniteness
would force every row sum to vanish and hence `q(T)=2` for all 231 triangles.
The full row multiset of `M` would then be

```text
4^1, 1^22, 0^192, (-1)^6, (-2)^10,
```

where the 192 zeros include the 18 intersecting triangles and 174 disjoint
`r=1` triangles.

## 6. Integral mod-four lift gives `n3>=705`

The Schur inequality can be sharpened without classifying the `q` profile.
Let

```text
W = M o M,
A_4 = M W M.
```

Both `M` and `W` are positive semidefinite, so `A_4` is a symmetric positive
semidefinite integer matrix.

Entrywise squaring preserves every integer modulo two:

```text
W = M (mod 2).
```

Together with `M^2=21M`, this gives

```text
A_4 = M W M = M^3 = M (mod 2).
```

Every row of `M mod 2` is nonzero: for any `T`, the `a_0(T)=20+q(T)` entries
with `r=0` are equal to `1`. Hence every row of `A_4` is nonzero.

The diagonal has a stronger congruence. Write

```text
D = (W-M)/2.
```

This is an integral symmetric matrix. Since

```text
D[T,T] = (4^2-4)/2 = 6,
```

`D mod 2` is symmetric with zero diagonal. Every such characteristic-two
bilinear form is alternating:

```text
v^T (D mod 2) v = 0
```

for every vector `v`, because each off-diagonal term occurs twice. Now

```text
A_4 = M^3 + 2 M D M.
```

Since `M^3=441M`, reducing a diagonal entry modulo four gives

```text
(A_4)[T,T]
  = M[T,T] + 2 row_T(M) D row_T(M)^T
  = 0 (mod 4).
```

A positive semidefinite matrix with a zero diagonal entry has the whole
corresponding row zero. Every row here is nonzero, so every diagonal entry is
positive. The preceding congruence therefore forces

```text
(A_4)[T,T] >= 4
```

for all 231 triangles, and

```text
tr(A_4) >= 4*231 = 924.
```

On the other hand, cyclicity of trace, `M^2=21M`, and the already computed
entrywise cubic sum give

```text
tr(A_4)
  = tr(M^2 W)
  = 21 tr(MW)
  = 21 sum_(T,U) M[T,U]^3
  = 84(n3-693).
```

Thus

```text
84(n3-693) >= 924,
n3-693 >= 11.
```

Because both `n3` and 693 are multiples of three,

```text
n3-693 >= 12,
n3 >= 705.
```

This also excludes the Schur equality case and the next three multiples
`696,699,702` in one global argument.

## 7. Additional exact algebra, not needed for the bound

The matrix `M` has exact rational rank 44 and nonzero eigenvalues all equal to
21. The sum of its principal `44`-by-`44` minors is therefore `21^44`, which
is odd. At least one such minor is odd, while every larger minor vanishes over
the integers. Hence

```text
rank_F2(M)=44.
```

Since `A_4 mod 2=M` and `rank_R(A_4)<=rank_R(M)=44`, the lift `A_4` also has
exact real and binary rank 44. This is consistent with the trace obstruction
but has not yet improved 705.

## 8. Checks, hostile mutations, and retained failures

The standard-library checker uses `fractions.Fraction` throughout. It
reconstructs all four projectors, all forty displayed mixed Schur traces,
the row profiles for every `q` from 0 through 12, the global pair
distribution, the Schur cubic, the integral trace identity, and the mod-four
threshold. Eighteen tests include hostile mutations of:

- the zero-eigenspace multiplicity;
- the sign of the `C` coefficient in `E`;
- one `C` eigenvalue;
- the ordered/unordered `N3` factor;
- the number of triangle indices;
- the nonzero-row premise;
- the mod-four diagonal premise; and
- the zero-diagonal premise in the characteristic-two alternating form.

The first test run retained one non-mathematical stale expected value after
the mod-four strengthening (`462` rather than `924`). The implementation was
correct; the test expectation was repaired, and the full 18-test replay
passes. The failure is preserved in
`attempts/wave20-global-obstruction/failed-runs.md`.

Exact routes that did not improve the result are retained in
`attempts/wave20-global-obstruction/failed-routes.md`. In particular:

- the exact opposite-edge compression has Ritz values
  `12,28/17,-21/5` but gives no useful `n3` upper bound;
- all other mixed primitive-projector triples are weaker in the feasible
  interval;
- Gegenbauer inequalities through degree 60 reproduce only `n3>=693`; and
- fourth-moment pinching gives an upper endpoint above the trivial 4158.

The strongest objection is status, not arithmetic: this is a new
discovery-agent proof and needs a verifier who independently reconstructs the
combinatorial entries, Schur argument, and mod-four lift. Until that happens,
the honest label is `DERIVED`, and both target and novelty remain `UNKNOWN`.
