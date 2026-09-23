# Wave 21 local-diagonal analysis at the first surviving endpoint

```yaml
role: proof_b
date_utc: 2026-07-23T18:34:27Z
git_commit: 74af1fa495971d04c7363ec05aa77ef15857b04a
claim_label: DERIVED
scope: conditional local consequences of n3=705 for A4=M(M o M)M
inputs:
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  attempts/wave20-global-obstruction/exact_check.py: a3cbe6dfe018965043903c368932f89f9fade30cf301ffe3454cd638966d00c8
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
method: exact Gram-tensor identities, harmonic cubic Schur kernels, centered PSD minors, and endpoint trace congruences
command: |
  cd attempts/wave21-local-diagonal
  python -m unittest -v test_exact_check.py
  python exact_check.py --output exact-checks.json
outputs:
  exact_checker: attempts/wave21-local-diagonal/exact_check.py
  hostile_tests: attempts/wave21-local-diagonal/test_exact_check.py
  exact_results: attempts/wave21-local-diagonal/exact-checks.json
limitations: discovery-agent derivation; endpoint survives; no matrix or graph construction; target and novelty UNKNOWN
```

## Result

This lane does **not** exclude the first endpoint left by Wave 20.  Its
strongest new universal endpoint consequence is

```text
n3=705  ==>  0 <= q(T) <= 8 for every triangle T.
```

It also gives a pointwise lower bound

```text
(A4)[T,T] >= (99/43)*(q(T)-2)^2,
```

which must be rounded up to a positive multiple of four.  At the endpoint,
the trace-square arithmetic sharpens to

```text
tr(A4^2) = 441*t,  t = 4 (mod 8),  t >= 60,
tr(A4^2) >= 26460.
```

These are conditional necessary consequences only.  A scalar relaxation
still has many solutions, including the particularly simple profile with
eight `q=3` triangles and 223 `q=2` triangles.  No matrix realizing that
profile is asserted.  The target and novelty remain `UNKNOWN`.

## 1. Frozen setup

Use only the independently checked Wave 20 objects.  The integral matrix

```text
M = 21E
```

is positive semidefinite of rank 44 and satisfies

```text
M^2=21M,  M1=0,  M[T,T]=4,
M[T,U] in {-2,-1,0,1} for T != U.
```

Put

```text
W=M o M,
A4=M W M.
```

Wave 20 proves that `A4` is an integral positive semidefinite matrix, every
row is nonzero, and every diagonal is a positive multiple of four.  It also
proves

```text
tr(A4)=84*(n3-693).
```

At `n3=705`, write `Delta=n3-693=12`.  Then

```text
sum_T q(T)=2n3/3=470,
sum_T (q(T)-2)=8,
tr(A4)=1008.
```

No automorphism, association scheme, triangle-graph catalog, or putative
graph instance is used below.

## 2. A local Gram-tensor formula for the diagonal

Because `M` is positive semidefinite of rank 44, choose vectors
`u_T in R^44` with

```text
<u_T,u_U>=M[T,U],  ||u_T||^2=4.
```

For each triangle define the symmetric quadratic tensor

```text
S_T = sum_U M[T,U] * (u_U u_U^T).
```

The Frobenius inner product of two rank-one tensors is

```text
<u_U u_U^T, u_V u_V^T> = M[U,V]^2 = W[U,V].
```

Consequently,

```text
<S_T,S_U> = (M W M)[T,U] = A4[T,U],
(A4)[T,T] = ||S_T||_F^2.                              (1)
```

Moreover,

```text
tr(S_T)=4*sum_U M[T,U]=0.
```

The anchored traceless tensor

```text
P_T = u_T u_T^T - I/11
```

has

```text
||P_T||_F^2 = 16-16/44 = 172/11.                     (2)
```

The Wave 20 row profile gives the exact Schur-cube row sum

```text
<S_T,P_T>
 = sum_U M[T,U]^3
 = 4^3+a_0(T)-a_2(T)-8a_3(T)
 = 6(q(T)-2).                                         (3)
```

Cauchy--Schwarz applied to (1)--(3) yields

```text
36(q(T)-2)^2
 <= (A4)[T,T]*(172/11),

(A4)[T,T] >= (99/43)(q(T)-2)^2.                      (4)
```

This is an exact local inequality.  Combining it with the positive
multiple-of-four condition gives:

| `q` | rational lower bound from (4) | integral diagonal lower bound |
|---:|---:|---:|
| 0 | `396/43` | 12 |
| 1 | `99/43` | 4 |
| 2 | 0 | 4 |
| 3 | `99/43` | 4 |
| 4 | `396/43` | 12 |
| 5 | `891/43` | 24 |
| 6 | `1584/43` | 40 |
| 7 | `2475/43` | 60 |
| 8 | `3564/43` | 84 |
| 9 | `4851/43` | 116 |
| 10 | `6336/43` | 148 |
| 11 | `8019/43` | 188 |
| 12 | `9900/43` | 232 |

At the endpoint all other 230 diagonal entries are at least four.  Hence any
single diagonal is at most

```text
1008-230*4=88.
```

Equation (4) then gives `(q(T)-2)^2 <= 3784/99 < 39`, so the integer range
`0<=q<=12` sharpens to

```text
q(T)<=8.                                               (5)
```

Also, a diagonal equal to four forces `q in {1,2,3}` using only the Wave 20
package.  The separate earlier `q!=1` theorem is not imported into this
lane.

## 3. Schur-cube and harmonic-cube kernels

The repeated Schur product theorem makes

```text
K=M o M o M
```

positive semidefinite, even though individual entries of `M` may be
negative.  Its exact local and global data are

```text
K[T,T]=64,
(K1)_T=6(q(T)-2),
1^T K 1=4*Delta.
```

At `Delta=12`, PSD Cauchy on `e_T` and `1` gives

```text
36(q(T)-2)^2 <=64*48,
```

which excludes `q=12` but permits `q=11`.

There is a stronger harmonic cubic kernel.  For vectors of squared norm four
in dimension `d=44`, define the traceless symmetric cubic tensor

```text
T(u)_{abc}
 =u_a u_b u_c
 -(4/(d+2))*(u_a delta_bc+u_b delta_ac+u_c delta_ab).
```

Direct contraction gives

```text
<T(u),T(v)>
 = <u,v>^3 - (3*4^2/(44+2))*<u,v>
 = <u,v>^3 - (24/23)*<u,v>.
```

It follows, as a Gram-matrix statement rather than a polynomial heuristic,
that

```text
H=23K-24M
```

is positive semidefinite.  Its data are

```text
H[T,T]=1376,
(H1)_T=138(q(T)-2),
1^T H 1=92*Delta.
```

At `Delta=12`,

```text
138^2(q(T)-2)^2 <=1376*1104,
```

so `q<=10`.

For completeness, center out the all-ones direction:

```text
r=H1,
R=H-r r^T/1104.
```

Writing `H=BB^T`, this is the Gram matrix obtained by orthogonally removing
the direction `B^T1`, hence `R` is positive semidefinite.  If `q(T)=10`,
then

```text
R[T,T]=1376-1104=272.
```

For distinct indices, the four possible `M[T,U]` values give

```text
H[T,U] in {-136,1,0,-1}.
```

Thus two `q=10` indices would have centered off-diagonal in

```text
{-1240,-1103,-1104,-1105},
```

whose absolute value always exceeds 272, contradicting the corresponding
PSD `2`-by-`2` minor.  Therefore the harmonic kernel alone permits at most
one `q=10` index.

The local `A4` budget (5) is stronger: it excludes every `q=9,10,11,12`
index.  The harmonic calculation remains useful as an independently derived
higher-Schur route and a regression target.

## 4. The 21 diagonal excess units do not yet contradict the endpoint

Write

```text
(A4)[T,T]=4(1+x_T),  x_T a nonnegative integer.
```

The endpoint trace says

```text
sum_T x_T=21.
```

The following scalar data satisfy every pointwise and aggregate condition
derived above:

```text
q profile:       223 entries q=2, 8 entries q=3,
diagonal profile: 210 entries 4, 21 entries 8.
```

Indeed, the `q` sum is `223*2+8*3=470`, the diagonal sum is
`210*4+21*8=1008`, and (4) requires only four at `q=2` or `q=3`.
The exact checker finds 22,113 aggregate `q` profiles when only the frozen
Wave 20 range, the local bounds, and the endpoint budgets are imposed.

This is deliberately called a **scalar relaxation witness**.  It does not
specify off-diagonal entries, does not make `A4` positive semidefinite, does
not enforce `A4 M=21A4`, and does not construct either `M` or the target
graph.  Its purpose is to prevent promotion of the local inequalities into a
false endpoint contradiction.

## 5. Exact Frobenius restrictions

The identity `A4 M=21A4` also yields a useful exact trace-square divisor.
With `A=A4`,

```text
tr(A^2)
 =tr(MWMMWM)
 =441*tr(MWMW)
 =441*t
```

for a nonnegative integer `t`.

At the endpoint, `A=M (mod 2)`.  An off-diagonal entry is odd precisely in
the `r=0` and `r=2` categories.  Their ordered count is

```text
(4620+470)+1410=6500,
```

so there are 3250 unordered odd off-diagonal entries.  Diagonal squares
vanish modulo eight; doubled squares of even off-diagonal entries also
vanish modulo eight; and each doubled odd square is two modulo eight.
Therefore

```text
tr(A^2)=2*3250=4 (mod 8).
```

Since `441=1 (mod 8)`,

```text
t=4 (mod 8).                                           (6)
```

Rank at most 44 and trace 1008 give

```text
t=tr(A^2)/441 >=1008^2/(44*441)=576/11.
```

The first integer satisfying this and (6) is 60, proving

```text
tr(A^2)>=441*60=26460.                                 (7)
```

The spectral moment relaxation is still feasible at equality in (7): take
22 copies of each positive number

```text
lambda_+ = (252+21*sqrt(21))/11,
lambda_- = (252-21*sqrt(21))/11.
```

They have total 1008 and squared total 26460.  This is not an integral-matrix
witness, but it shows that trace, rank, positivity, and (7) alone cannot
contradict the endpoint.

## 6. Retained failed routes and boundary

- The harmonic cubic gives a clean PSD refinement but is superseded at this
  endpoint by the local `A4` tensor inequality.
- Centered harmonic `2`-by-`2` minors exclude two `q=10` indices, but the
  stronger local budget excludes even one.
- The 21 diagonal excess units admit explicit scalar distributions; diagonal
  arithmetic alone is not a contradiction.
- `tr(A4^2)` has a stronger divisor/congruence lower bound, but the associated
  nonnegative spectral moment problem remains feasible.
- A tempting mod-eight refinement of each individual diagonal reduces to
  unrecorded pair data among the odd support of a row.  It is not determined
  by `q(T)` and the Wave 20 identities used here, so no such congruence is
  claimed.
- Row parity, `A4 M=21A4`, and PSD `2`-by-`2` minors were not enough to
  control those missing pair data without importing an unavailable
  association scheme.

The honest status is therefore:

```text
local endpoint refinements: DERIVED
n3=705 exclusion: UNKNOWN
Conway-99 target: UNKNOWN
literature novelty: UNKNOWN
```

