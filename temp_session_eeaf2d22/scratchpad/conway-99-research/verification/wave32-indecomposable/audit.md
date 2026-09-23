# Wave 32 indecomposable-branch adversarial verification

Verdict: **PASS_SCOPED_WITH_NONBLOCKING_COVERAGE_GAPS**

```yaml
role: verifier
date_utc: 2026-07-24T09:11:17Z
git_commit: NOT_USED_NO_GIT_PER_TASK
claim_label: VERIFIED
scope: >-
  Independent adversarial verification of the necessary structural
  reductions for a rootless integrally indecomposable rank-44 n3=708
  endpoint: primitive row generation, the connectivity/decomposition
  equivalence under minimum four, the inherited Wave31 actual-incidence
  connectivity consequence, the unique forbidden {-2,-2,-1} norm-two
  motif, its mixed-trace normalization, exact endpoint pair counts, and
  corrected F3/F7 rank and hull statements. Motif forcing and endpoint
  existence remain unknown.
method: >-
  Blind candidate and premise hash freeze; clean-room standard-library
  reconstruction; nineteen exact tests; deterministic JSON; premise-dropping
  primitive, minimum, incidence, sign, trace, finite-field, pair-count, and
  full-size binary controls; then static candidate comparison without
  importing or executing discovery code.
command: >-
  python -B -m unittest discover -s
  verification/wave32-indecomposable -p test_independent_check.py -v
limitations:
  - No target graph, integral endpoint frame, or rootless indecomposable
    lattice is constructed or excluded.
  - The hostile pair-count object is not a positive-semidefinite projector.
  - The binary hostile control is finite-field only and does not preserve
    the endpoint integral entry counts.
  - No Git action or candidate executable replay was performed.
```

## Verdict

The submitted human reductions are correct at their stated boundary. The
fresh verifier closes the discovery package's nonblocking executable
coverage gaps for the odd-prime ranks, row-generation bridge, arbitrary
sign mutation, and connectivity-compatible binary control.

It does not close the branch:

```text
rootless decomposable actual endpoint:             VERIFIED IMPOSSIBLE upstream
surviving rootless actual endpoint indecomposable: VERIFIED reduction
{-2,-2,-1} motif forbidden by rootlessness:        VERIFIED reduction
actual incidence forces that motif:                UNKNOWN
rootless indecomposable endpoint:                   UNKNOWN
n3=708:                                            UNKNOWN
Conway-99 existence/nonexistence:                   UNKNOWN
novelty:                                           UNKNOWN
```

No assumption of `h=729`, an automorphism, an orbit structure, or a
catalogue realization enters the verification.

## Independence and provenance

Before opening any Wave 32 indecomposable candidate content, the verifier
froze:

- the candidate proof and all seven submitted attempt artifacts;
- the governing `AGENTS.md`;
- the verified Wave 20, 21, 28, and 31 premises; and
- the Wave 32 statement freeze.

The independent checker, tests, and first deterministic result were written,
passed, and hash-frozen before static candidate comparison. A comparison
addendum then strengthened the finite-field hostile control to include
quadratic singularity, zero row sum, and connected support, and explicitly
added the prose-only `rank(M mod p)` statements. The final suite still
imports no candidate module.

The submitted seven-entry artifact manifest and five-entry input freeze
validate independently. Candidate executables were never run.

## Obligation table

| Obligation | Verdict | Exact conclusion |
|---|---:|---|
| Primitive `X` implies row generation | PASS | `X^T Z^231=Z^44`; maximal-minor gcd is one. |
| Full rank can replace primitivity | REFUTED | `X=((2),(0))` has full rational rank but row lattice `2Z`. |
| Minimum-four split implies block-supported rows | PASS | A norm-four row has exactly one nonzero component. |
| Disconnected row support implies integral split | PASS | Component row spans generate the full lattice and are mutually orthogonal. |
| Indecomposable iff support connected | PASS | Exact under row generation and `min(S)>=4`. |
| Actual rootless support is connected | PASS | Wave31 gives `21|b` and `33|b`, hence `231|b`. |
| Unique switched norm-two motif | PASS | One switching class, absolute labels `{2,2,1}`, canonical signs `{-2,-2,-1}`. |
| Canonical motif is realizable as a positive Gram | PASS | Leading minors `4,12,20`; sum-vector norm two. |
| `-1 -> +1` mutation | PASS | All signed norms are `6,10,22`; no root remains. |
| Mixed trace normalization | PASS | One motif contributes exactly two to `tr(A_-1 A_-2^2)`. |
| Endpoint pair census | PASS | Unordered counts `2546,22161,708,1150`. |
| Pair counts/connectivity force motif | REFUTED | Exact connected labeled hostile control has all counts and zero motifs. |
| Correct `F3/F7` ranks | PASS | `rank G=m`, `rank S=rank M=44-m` for `m=v_p(h)`. |
| Universal code self-orthogonality | REFUTED | It holds only when `m=0`; all eight rows checked. |
| Full-size binary consistency | PASS | 231 singular nonzero rows, rank 44, zero sum, connected rank-44 idempotent shadow. |
| Actual motif trace | UNKNOWN | No checked identity forces it positive. |

## Primitive row generation and support connectivity

For a full-column-rank integral `231 x 44` basis matrix `X`, the row lattice
is `im(X^T)`. Its index in `Z^44` is the gcd of the `44 x 44` minors.
Primitivity of the column lattice makes every Smith invariant factor one,
so

```text
X^T Z^231 = Z^44.
```

Let the support graph have vertices the 231 rows and

```text
i adjacent to j iff i != j and M_ij=x_i^T S x_j != 0.
```

If it disconnects, the integer spans of distinct components are mutually
orthogonal and generate the whole lattice, hence give an integral direct
sum. Conversely, in an integral orthogonal split with minimum at least four,
the nonzero components of a norm-four row have norms at least four. Exactly
one can be nonzero, so every row is block-supported and the graph
disconnects.

Therefore

```text
S integrally indecomposable
  iff the row nonorthogonality graph is connected.
```

The minimum premise is active: a norm-four vector can straddle two
orthogonal norm-two components if it is deleted.

For actual target incidence, a coordinate projector block of size `b`
satisfies

```text
21 divides b   by projector trace,
33 divides b   by the Wave31 incidence commutator.
```

Only `b=0,231` lies in the allowed range. Thus actual rootless support is
connected and the endpoint is forced into the indecomposable branch. This
is a branch reduction, not an endpoint exclusion.

## The forbidden motif and trace

For three distinct rows with switched Gram

```text
[ 4 -2 -2 ]
[-2  4 -1 ]
[-2 -1  4 ],
```

the leading principal minors are `4,12,20`, while the sum of all matrix
entries is two. The row sum is therefore a norm-two lattice vector, which
rootlessness forbids.

The independent checker exhausts the complete endpoint alphabet and every
row-sign choice. The only raw placements are the three permutations of
`(-2,-2,-1)`, all in one switching class. The positive-one mutation has
signed norms exactly `{6,10,22}`.

If `A_-1` and `A_-2` are the class adjacency matrices, then

```text
tr(A_-1 A_-2^2)
 = sum_(i,j,k) A_-1(i,j) A_-2(j,k) A_-2(k,i).
```

The unique `-1` edge has two orientations, so

```text
tr(A_-1 A_-2^2)
 = 2 * #{unordered {-2,-2,-1} motifs}.
```

Rootlessness requires this trace to vanish. Whether actual target incidence
forces it positive is the exact unresolved blocker.

## Exact endpoint pair counts

At `n3=708`,

```text
sum_T q(T)=2*708/3=472.
```

The ordered counts are

```text
M=+1: 231*20+472 = 5092
M=-1: 3*472      = 1416
M=-2: 231*12-472 = 2300
M= 0:             44322.
```

Dividing by two gives

```text
M=+1:  2546
M= 0: 22161
M=-1:   708
M=-2:  1150.
```

The total is `binom(231,2)=26565`. These counts are independent of the
eight determinant rows.

They do not determine the mixed trace. The verifier constructs a connected
231-vertex labeled graph with exactly these four multiplicities and no
forbidden motif. It is deliberately not claimed to be an endpoint Gram or
projector.

## Correct finite-field ranks

Write `m=v_p(h)` for `p=3` or `7`. The elementary discriminant group gives
a local form

```text
S ~ U orthogonal_sum pV,
rank(U)=44-m,
rank(V)=m.
```

Thus

```text
rank_Fp(S)=44-m,
rank_Fp(G=21S^-1)=m.
```

Primitivity gives `rank_Fp(X)=44`. Since `X` is injective and `X^T` is
surjective over the field,

```text
rank_Fp(M=XSX^T)=rank_Fp(S)=44-m.
```

The column-code hull has dimension `44-m`. It is self-orthogonal only when
`m=0`, not universally. The exact `(rank S,rank G)` rows at `(3,7)` are:

```text
h=9:     (42,2), (44,0)
h=21:    (43,1), (43,1)
h=49:    (44,0), (42,2)
h=81:    (40,4), (44,0)
h=189:   (41,3), (43,1)
h=441:   (42,2), (42,2)
h=729:   (38,6), (44,0)
h=1029:  (43,1), (41,3).
```

Full rank of `X` does not force equal Gram rank over a finite field.
Explicit isotropic one-column controls over both fields make this premise
failure concrete.

## Full-size binary hostile control

The clean-room construction starts with the nine nonzero singular vectors
in each of eleven four-dimensional hyperbolic quadratic spaces. Their total
outer product is the polar hyperbolic form and their sum is zero. It then
adds:

```text
10 doubled singular bridge rows,
56 doubled singular filler rows.
```

The resulting 231 rows satisfy:

```text
all rows nonzero and quadratically singular,
row sum zero,
rank(X)=44,
X^T X = 22 hyperbolic planes,
M=XSX^T symmetric alternating,
M^2=M,
rank(M)=44,
M1=0,
support graph connected.
```

This is stronger than the submitted finite-field control because it also
preserves support connectivity. It still has only `806` odd pairs rather
than the endpoint's `3254`; it is not an integral endpoint realization.

## Static candidate comparison

No blocking proof defect was found. Five nonblocking coverage observations
are retained in `failed-objections.md`:

1. the corrected odd-prime ranks are prose-only in the submitted package;
2. row generation and connectivity equivalence are largely prose in the
   submitted checker;
3. the submitted sign mutation checks only one coefficient choice;
4. the submitted binary control does not combine its shadow with connected
   support; and
5. the submitted tests import discovery code and are not independent.

The fresh verifier supplies all five checks. It does not promote motif
forcing, endpoint nonexistence, Conway-99, or novelty.

## Reproduction

The standard-library suite reports:

```text
Ran 19 tests
OK
```

The result JSON is deterministic, UTF-8, and LF-only. Its candidate
manifest validation is static and does not execute discovery code.
