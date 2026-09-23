# Wave 24 next-endpoint index and characteristic-polynomial attack

```yaml
role: proof_a
date_utc: 2026-07-23T20:26:17Z
git_commit: c82f49be256f79fed45b7a4f1458d751d2ec0d9f
claim_label: DERIVED
scope: >-
  Conditional exact restrictions at n3=708 for a putative
  srg(99,14,1,2), together with an exact survivor showing that the current
  determinant/scaled-dual/endomorphism relaxation does not exclude 708.
inputs:
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
  verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md: 45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268
  verification/wave23-index-pranks/2026-07-23T192952Z-audit.md: bfd02ebc39515e27e9e2c79d8e286905086f5747a02a310036ce27dd29ff3116
  verification/wave23-endpoint-crosscheck/2026-07-23T200645Z-correction-audit.md: 791d74340c8a84a9993f9a5179c66baf0b2f7e431df5fb7eda2f593195f9bf53
method: >-
  Exact parameter specialization, an integral characteristic-polynomial
  pseudodeterminant lemma, a pointwise logarithmic determinant inequality,
  finite 3,7-smooth index exhaustion, an explicit rank-44 even-lattice
  relaxation, and local harmonic/diagonal endpoint checks.
command: |-
  cd attempts/wave24-n3-708-index
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave24-n3-708-index/exact_check.py: 60bec6067383de3d9b6ecf57a5ce2a532deaf4759cc65faf4c63a6b8ce98b709
  attempts/wave24-n3-708-index/test_exact_check.py: adfa00d30a5db9ec0dc30bbd4d028689edd03bbba154535e05c1b7e4df76ed75
  attempts/wave24-n3-708-index/exact-results.json: a4241cdeea64a8f6073037d564e72fb7ef545287d45aca4759cec6c31d26a463
  attempts/wave24-n3-708-index/input-freeze.sha256: 4353375bbbfc58d382b048066aec388dec5d5ff84a41e426ea01dbb10ffbb7af
  attempts/wave24-n3-708-index/failed-routes.md: 2411d4012cc6bf3f1d2a82d63cdc1538a6ca815ad269604fc46cb72cd4d82efb
  attempts/wave24-n3-708-index/failed-runs.md: c37aeaad4f3afdbb765fc0233a23f6735b93a904b504a8593c1fe5503a9b8715
limitations:
  - Discovery-agent derivation pending a fresh independent verifier.
  - The exact survivor is a coordinate-lattice relaxation, not a primitive
    sublattice of Z^231, a 231-vector projector Gram matrix, or a graph.
  - No value of rank_F3(M), rank_F7(M), or h is determined for a target.
  - No failed restricted search is treated as nonexistence evidence.
  - Target existence and literature novelty remain UNKNOWN.
```

## Result and status wall

This attack does **not** exclude `n3=708`.  It proves a sharper necessary
restriction on the index from the verified projector-lattice package:

```text
n3=708
  ==>
h in {9,21,49,81,189,441,729,1029}.
```

The main new ingredient is an exact characteristic-polynomial bound

```text
det(B) <= 3^8 = 6561.
```

This is much stronger than the trace-only or two-moment real-eigenvalue
bound at this endpoint.  It is still not a contradiction.  In fact, Section
6 gives exact rank-44 matrices satisfying the current
determinant/scaled-dual/endomorphism relaxation with

```text
h=9, det(Q)=9, det(B)=81, tr(B)=60.
```

That survivor is deliberately scoped: it is not shown to arise from a
primitive embedding in `Z^231`, from the 231 projector columns, from
`W=M o M`, or from a graph.  It proves only that the relaxed lattice
identities cannot by themselves reject the endpoint.

The publication-safe discovery status is therefore:

```text
conditional endpoint restriction: DERIVED
n3=708 exclusion:                 NOT OBTAINED
Conway-99 existence:              UNKNOWN
novelty:                          UNKNOWN
```

## 1. Frozen verified setup specialized to 708

Use the notation independently audited through Wave 23:

```text
M = 21E,
W = M o M,
A4 = M W M,
U = im(M) over Q,
L = U intersect Z^231,
h = [L:21L*],
B = A4/21 on U.
```

The exact inherited facts are:

```text
rank(L)=44;
L is even and has minimum at least four;
B is a positive-definite integral self-adjoint endomorphism of L;
B=I mod 2 End(L);
tr(B)=4Delta, where Delta=n3-693;
det(B)=h det(Q);
Q is even, integral, and positive definite of rank 44;
h=3^(44-rank_F3(M)) 7^(44-rank_F7(M));
h=1 mod 4 and h!=1;
det(Q)=1 mod 4 and det(Q)>=5.
```

At the next endpoint,

```text
n3=708,
Delta=15,
tr(A4)=84*15=1260,
tr(B)=4*15=60.
```

Write the integral coordinate endomorphism as

```text
B=I+2C.
```

Then

```text
tr(C)=(60-44)/2=8.                              (1)
```

Every eigenvalue `mu` of `C` is real because `C` is self-adjoint for the
positive Gram form of `L`.  Positivity of `B` gives

```text
mu > -1/2.                                      (2)
```

These statements do not require `C` to be symmetric in the chosen integral
basis.

## 2. The nonzero characteristic coefficient forces `tr(C^2)>=8`

Let `r=rank(C)`.  Self-adjointness makes `C` diagonalizable, so its `r`
nonzero eigenvalues `mu_1,...,mu_r` are exactly the nonzero roots of its
characteristic polynomial, with multiplicity.  Because `C` is integral,

```text
char_C(t)=t^(44-r) p(t)
```

for a monic `p(t)` in `Z[t]` with `p(0)` a nonzero integer.  Therefore

```text
|product_i mu_i|=|p(0)|>=1.                     (3)
```

AM-GM applied to the positive numbers `mu_i^2` gives

```text
tr(C^2)=sum_i mu_i^2
  >= r (product_i mu_i^2)^(1/r)
  >= r.                                         (4)
```

Cauchy applied only to the nonzero eigenvalues and (1) gives

```text
tr(C^2)>=64/r.                                  (5)
```

For every integer `1<=r<=44`,

```text
max(r,64/r)>=8,
```

with equality only at `r=8`.  Hence

```text
tr(C^2)>=8,
tr(B^2)
 =44+4tr(C)+4tr(C^2)
 >=44+32+32
 =108.                                          (6)
```

The old congruence `tr(B^2)=4 mod 8` is consistent with 108 but does not
produce this strengthening on its own.  The active new premise is the
nonzero integral characteristic coefficient (3).

Equality in (4)--(6) forces the eight nonzero eigenvalues of `C` to be
`1`, so the sharp abstract equality spectrum is

```text
spec(C)=1^8,0^36,
spec(B)=3^8,1^36.
```

## 3. A logarithmic pseudodeterminant inequality

Put

```text
c=log(3)-2/3 > 0.
```

For every real `x>-1/2`, `x!=0`,

```text
log(1+2x)
  <= x log(3) - c log|x|.                       (7)
```

Here is a complete calculus check.

For `x>0`, subtract the left side from the right and call the result `F(x)`.
After multiplying its derivative by the positive denominator
`x(1+2x)`, its numerator factors exactly as

```text
(x-1)(2 log(3) x + c).
```

The second factor is positive.  Thus `F` decreases to `x=1` and increases
afterward, while `F(1)=0`.

For `-1/2<x<0`, first put

```text
g(x)=x log(3)-log(1+2x).
```

Because `log(3)<2`,

```text
g'(x)=log(3)-2/(1+2x)<0.
```

As `g(0)=0`, this gives `g(x)>0` on the negative interval.  Also
`|x|<1` and `c>0`, so `-c log|x|>0`; hence (7) is strict there.

The checker does not decide these signs by floating point.  It uses

```text
log(3)=2*atanh(1/2)
```

with an exact rational partial sum and geometric tail to certify

```text
2/3 < log(3) < 2.
```

Now apply (7) to the nonzero eigenvalues of `C`.  Zero eigenvalues contribute
the factor one to `det(B)`.  Equations (1) and (3) give

```text
log det(B)
 = sum_i log(1+2mu_i)
 <= 8 log(3) - c log|product_i mu_i|
 <= 8 log(3).
```

Therefore the exact determinant cap is

```text
det(B)<=3^8=6561.                               (8)
```

Equality can occur in this analytic inequality only for the abstract
spectrum `3^8,1^36` displayed above.

## 4. Exact index exhaustion

The verified determinant factorization and even-lattice floor give

```text
det(B)=h det(Q),
det(Q)>=5.
```

Equation (8) implies

```text
h<=floor(6561/5)=1312.                          (9)
```

The scaled-dual lattice supplies

```text
h=3^a 7^b,
h=1 mod 4,
h!=1.
```

Exhausting the finite range (9) gives exactly:

| `h` | `(a,b)` | `(rank_F3(M),rank_F7(M))` | largest possible `det(Q)=1 mod 4` |
|---:|---:|---:|---:|
| 9 | `(2,0)` | `(42,44)` | 729 |
| 21 | `(1,1)` | `(43,43)` | 309 |
| 49 | `(0,2)` | `(44,42)` | 133 |
| 81 | `(4,0)` | `(40,44)` | 81 |
| 189 | `(3,1)` | `(41,43)` | 33 |
| 441 | `(2,2)` | `(42,42)` | 13 |
| 729 | `(6,0)` | `(38,44)` | 9 |
| 1029 | `(1,3)` | `(43,41)` | 5 |

No one of these ranks is inferred to occur in a target.  The table is an
exact list of survivors of the stated arithmetic conditions.

## 5. Local identities at the new endpoint

The verified row parameter satisfies

```text
sum_T q(T)=2n3/3=472,
sum_T(q(T)-2)=472-2*231=10.                     (10)
```

Every diagonal of `A4` is a positive multiple of four.  Writing

```text
A4[T,T]=4(1+x_T)
```

there are now

```text
sum_T x_T=1260/4-231=84                         (11)
```

diagonal excess units.  The inherited local tensor inequality remains

```text
A4[T,T]>=(99/43)(q(T)-2)^2,
```

rounded upward to a positive multiple of four.  Unlike at 705, the budget
(11) alone does not exclude any one value `0<=q<=12`.

The harmonic cubic Gram kernel

```text
H=23(M o M o M)-24M
```

has

```text
H[T,T]=1376,
(H1)_T=138(q(T)-2),
1^T H 1=92Delta=1380.
```

PSD Cauchy at `q=12` would require

```text
138^2*10^2 <= 1376*1380.
```

The left side exceeds the right by exactly `5520`, so

```text
q(T)<=11.                                       (12)
```

Centering out the all-ones direction at `q=11` gives diagonal

```text
1376-(138*9)^2/1380=1291/5.
```

For two such indices, every possible centered off-diagonal, obtained from
`H[T,U]` in `{-136,1,0,-1}`, has absolute value strictly larger than
`1291/5`.  The corresponding two-by-two PSD minor is negative.  Hence there
can be at most one `q=11` index.

These local restrictions still do not close the endpoint.  The scalar
profile

```text
221 entries q=2,
10 entries q=3
```

satisfies (10), (12), and all pointwise diagonal lower bounds.  No graph or
matrix realization of that profile is asserted.

## 6. An exact survivor of the coordinate-lattice relaxation

This section makes the remaining obstruction concrete.  Let `E8` denote the
displayed positive-definite even unimodular rank-eight Gram matrix in the
checker, and let

```text
A2 = [[2,-1],[-1,2]].
```

Define rank-44 block matrices

```text
S = E8^5 direct_sum A2^2,
Q = (E8^(-1))^5 direct_sum A2^2,
G = 21 S^(-1),
B = S Q.
```

Every entry is integral.  The matrices `S`, `Q`, and `G` are even,
symmetric, and positive definite.  Blockwise,

```text
S G = 21I,
G B = 21Q,
B = I_40 direct_sum (A2*A2) direct_sum (A2*A2).
```

The exact invariants are:

```text
det(S)=h=9,
det(Q)=9,
det(B)=81=9*9,
tr(B)=40+10+10=60,
B=I mod 2.
```

Moreover,

```text
C=(B-I)/2
```

has rank two, trace eight, and trace square 32.  The lattice with Gram `G`
has minimum at least 14: its `E8`-dual blocks are scaled by 21, and each
two-dimensional block has quadratic form

```text
14(a^2+ab+b^2).
```

Thus the survivor also respects the inherited evenness and minimum-four
condition.

This is an exact hostile control against overclaiming the determinant route.
It does **not** supply:

- a primitive embedding of the `G` lattice in `Z^231`;
- 231 norm-four generators with Gram matrix `M`;
- the fixed row distributions of `M`;
- a matrix `W=M o M`; or
- a graph.

It therefore does not establish consistency of the full endpoint, much less
target existence.  It does establish that a contradiction must use at least
one of those omitted structural bridges.

## 7. Exact replay, hostile checks, and boundary

The standard-library checker uses integers and `fractions.Fraction`.  Its 15
tests cover:

- all frozen input hashes;
- endpoint traces and local budgets;
- every possible rank in the pseudodeterminant trace-square floor;
- a Cauchy-only hostile relaxation;
- exact rational bounds `2/3<log(3)<2`;
- the determinant cap and all eight index survivors;
- the active `det(Q)>=5` signature premise;
- the complete explicit `E8/A2` coordinate-lattice survivor;
- the harmonic `q=12` gap and two-`q=11` minor;
- a surviving scalar `q` profile; and
- deterministic JSON serialization.

The replay is:

```text
Ran 15 tests
OK
```

A discarded floating scan and every non-excluding route are retained in the
two ledgers.  Neither is used as mathematical evidence.

The precise next obstruction is now:

> Determine whether the eight remaining index/rank cases are compatible
> with a primitive 231-column projector Gram matrix having the exact
> `n3=708` row data and `Q=X^T(M o M)X`, or derive an exact incompatibility
> from that additional structure.

Until such a bridge is proved and independently checked, the correct status
is a sharp conditional restriction, not an endpoint exclusion.
