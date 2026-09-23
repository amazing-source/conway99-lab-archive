# Wave 21 integral-lattice extension of the global Schur obstruction

```yaml
role: proof_b
date_utc: 2026-07-23T18:34:50Z
git_commit: NOT_USED_PER_TASK_INSTRUCTION
claim_label: UNKNOWN
scope: >
  Independent attempt to strengthen the audited conditional bound n3>=705
  using the integral rank-44 projector lattice, the Schur lift, congruences,
  determinants, harmonic tensors, and equality-excess constraints.
inputs:
  agents/2026-07-23-wave20-global-schur.md: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
  verification/2026-07-23-wave20-global-schur-audit.md: 6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3
method: >
  Primitive projection-lattice duality, an integral positive endomorphism
  extracted from A=M(M o M)M, exact determinant/index factorization,
  even-lattice and mod-four constraints, harmonic-cubic positivity, and an
  exact dynamic program for all endpoint q profiles.
command: |
  cd attempts/wave21-lattice-extension
  python -B -m unittest -v test_exact_check.py
  python -B exact_check.py --output exact-results.json
outputs:
  attempts/wave21-lattice-extension/exact_check.py: 70111579d83bbd024eadc22e747261a7fa81849b7578b8481cafa595d2f7a5a4
  attempts/wave21-lattice-extension/test_exact_check.py: 4f2c4a90a007a964e29c8c5f34fdaac31eed0d11b480385c437349bfdf5495fa
  attempts/wave21-lattice-extension/exact-results.json: 18235cf32229bcdf1616a7560aa2389c830e7e23fa25f0a0fc02377c174dc53b
  attempts/wave21-lattice-extension/input-freeze.sha256: 55ad0e889fcce5031b70ecdb3f9af6794e9cd8b5b3cd8ca9971473f587e1de25
  attempts/wave21-lattice-extension/failed-runs.md: 7e90910e77d07896a486f93f75b5f358b5d95c71d4d0c7f7231ef32224132b69
limitations:
  - No value or lower bound was proved for the decisive lattice index h.
  - No putative 231-by-231 matrix M or 99-vertex graph is instantiated.
  - The classical even-unimodular signature obstruction is used only in the
    displayed conditional determinant refinement; this is a discovery report,
    not an independent verification.
  - A proposed numerical three-point SDP was not run after the dependency
    locator hung; this supplies no mathematical negative evidence.
  - No literature novelty or Conway-99 resolution claim is made.
```

## Result

No unconditional improvement over the independently audited bound

```text
n3 >= 705
```

was obtained.

The strongest new exact reduction is conditional on a finite lattice index.
Let

```text
U = im(M) over Q,
L = U intersect Z^231,
h = [L : 21 L*].
```

Then `h` is a positive integer with no prime divisors other than `3` and `7`.
If the first surviving endpoint `n3=705` exists, the derivation below forces

```text
h in {1,3,7,9}.
```

Consequently,

```text
h >= 21  ==>  n3 != 705.
```

Together with `3 | n3`, that additional premise would conditionally sharpen
the bound to `n3>=708` and the inherited induced-six-cycle count to at least
`209994`.  The audited Wave 20 data do **not** determine `h`, so this is a
reduction, not a stronger Conway-99 consequence.  Target existence and
novelty remain `UNKNOWN`.

## 1. Frozen audited input

Only the two named Wave 20 files were used as mathematical input.  Their
pre-work hashes are recorded in `input-freeze.sha256` and agree with the
hashes in the YAML header.

Write

```text
M = 21 E,
W = M o M,
mathcal A = M W M,
Delta = n3 - 693.
```

The independently audited premises used here are:

```text
M is integral symmetric positive semidefinite;
rank(M)=44;
M^2=21M;
M_ii=4;
M_ij in {0,1,-1,-2} for i != j;
M 1=0;
rank_F2(M)=44;
W is integral positive semidefinite;
mathcal A is integral positive semidefinite;
mathcal A mod 2 = M;
tr(mathcal A)=84 Delta.
```

No automorphism, catalog, graph construction, or solver-negative premise is
introduced.

## 2. The primitive projector lattice

Because `E=M/21` is a symmetric idempotent, it is the orthogonal projector
onto the rational 44-space `U`.  The lattice

```text
L = U intersect Z^231
```

is primitive in `Z^231`.

### Lemma 2.1: projected ambient lattice equals the dual

Exactly

```text
E Z^231 = L*.
```

For `z in Z^231` and `x in L`,

```text
<Ez,x> = <z,x> in Z,
```

so the left side lies in `L*`.  Conversely, an integral functional on the
primitive lattice `L` extends to an integral functional on `Z^231`; if `z`
represents that extension, its orthogonal projection `Ez` represents the
original functional on `U`.  This proves equality.

Multiplying by 21 gives

```text
M Z^231 = 21 L*.
```

Since `M Z^231` is integral and lies in `U`,

```text
21L subseteq 21L* subseteq L.
```

If `d=det(L)=[L*:L]`, then

```text
h = [L:21L*] = 21^44 / d.                 (1)
```

Thus `h` is a `3,7`-smooth integer.

### Lemma 2.2: `L` is even and has no norm-two vector

For `x in L`, `Mx=21x`.  Modulo two,

```text
x^T x = x^T M x = 0,
```

because the diagonal of the symmetric matrix `M` is even and off-diagonal
terms occur twice.  Hence `L` is even.

If an integral norm-two vector lay in `L`, the equation `M1=0` would force it
to be `e_i-e_j`.  But

```text
||E(e_i-e_j)||^2 = (8-2M_ij)/21,
```

which is at most `12/21` for the allowed off-diagonal entries, whereas a
vector already in `U` would have projected norm two.  This is impossible.
Thus the minimum nonzero norm of `L` is at least four.  This observation did
not by itself improve the endpoint.

## 3. The Schur lift as an integral endomorphism

Since `mathcal A mod 2=M` has binary rank 44 and
`rank_R(mathcal A)<=rank_R(M)=44`, `mathcal A` has real rank 44.  It is
therefore positive definite on `U`.

Define the operator on `U`

```text
B = mathcal A / 21.
```

For `x in L`,

```text
Bx = (MWMx)/21 = MWx in M Z^231 subseteq L,
```

because `Mx=21x`.  Hence `B` is an integral, self-adjoint, positive-definite
endomorphism of `L`, even though the ambient matrix `mathcal A/21` need not
be entrywise integral.

Its trace is

```text
tr(B) = 4 Delta.                           (2)
```

Also, since `W=M mod 2`,

```text
Bx = MWx = M^2x = x (mod 2L).
```

Thus

```text
B = I + 2C
```

for an integral endomorphism `C` of `L`.  Equation (2) gives

```text
tr(C)=2Delta-22,
```

which is even.  Expanding the determinant modulo four therefore gives

```text
det(B) = 1 + 2tr(C) = 1 (mod 4).           (3)
```

At `n3=705`, `Delta=12`, so `B` has rank 44 and trace 48.

## 4. Exact determinant/index factorization

Choose an integral basis matrix `X` for `L`, put

```text
G = X^T X,
Q = X^T W X,
```

and let `T` be the integral coordinate matrix of `B` in that basis.  The
bilinear identity

```text
<x,By> = 21 <x,Wy>
```

for `x,y in L` gives

```text
G T = 21 Q.
```

Taking determinants and using (1),

```text
det(B) = det(T) = h det(Q).                (4)
```

The matrix `Q` is an integral positive-definite Gram matrix.  It is even:
the diagonal of `W` is 16, while every off-diagonal contribution to
`x^T W x` occurs twice.

Both `h` and `det(B)` are odd, so `det(Q)` is odd.  Moreover `det(Q)` cannot
equal one.  Otherwise `Q` would define an even positive-definite unimodular
lattice of rank 44.  By the classical van der Blij signature lemma, the
signature of an even unimodular lattice is divisible by eight; positive
rank 44 has signature 44, a contradiction.  Therefore

```text
det(Q) >= 3.                               (5)
```

This is the only imported classical lattice fact in the endpoint
refinement, and it should be rechecked by a verifier before promotion.

## 5. The exact `n3=705` endpoint test

At `Delta=12`, positive-definite AM--GM applied to the 44 eigenvalues of `B`
gives

```text
det(B) <= (48/44)^44
       = (12/11)^44
       < 46.
```

Thus `det(B)<=45`.  Equations (3)--(5) and the `3,7`-smoothness of `h` leave
exactly

```text
h in {1,3,7,9}.
```

The checker enumerates all surviving determinant pairs.  In particular:

```text
h=1: det(Q) may begin at 5;
h=3: det(Q) may be 3,7,11,15;
h=7: only det(Q)=3 survives;
h=9: only det(Q)=5 survives.
```

The next `3,7`-smooth index is 21, and `21*3>45`.  This proves the stated
conditional implication

```text
h>=21  ==>  n3 != 705.
```

It does not prove its premise.  Determining `h` requires new modular or Smith
data for the actual projector lattice; those data are not fixed by either
audited Wave 20 input.

## 6. Harmonic-cubic endpoint consequences

Let the rows of `M` be represented by norm-four vectors in dimension 44.
The exact degree-three harmonic projection gives the positive-semidefinite
integral kernel

```text
H = 23 (M o M o M) - 24 M.
```

The coefficient follows from the standard traceless symmetric-cubic
projection:

```text
t^3 - (3*4^2/(44+2)) t = t^3 - (24/23)t.
```

Its entries by Gram value are

```text
m:       4    1   0  -1   -2
H(m): 1376   -1   0   1  -136.
```

Using the audited row profiles,

```text
(H1)_T = 138(q(T)-2),
1^T H 1 = 92 Delta.
```

At `Delta=12`, positive-semidefinite Cauchy--Schwarz gives

```text
[138(q(T)-2)]^2 <= 1376*1104.
```

Hence `q(T)=11,12` are impossible at this endpoint.  Values through `q=10`
remain possible, and this restriction does not contradict
`sum_T q(T)=470`.

## 7. Traceless-contraction floor and exact non-improvement

Let

```text
mathcal T = sum_j x_j tensor x_j tensor x_j
Y_i = contraction of mathcal T with x_i.
```

Then

```text
||Y_i||^2 = mathcal A_ii,
<Y_i, x_i tensor x_i> = 6(q(i)-2).
```

The row sum `M1=0` makes `Y_i` traceless.  The traceless part of
`x_i tensor x_i` has squared norm

```text
16 - 16/44 = 172/11.
```

Therefore

```text
mathcal A_ii >= (99/43)(q(i)-2)^2.         (6)
```

Combining (6) with the audited facts that every diagonal is a positive
multiple of four gives exact local floors.  For example:

```text
q=0,2,3,4,5,6  ->  floor 12,4,4,12,24,40.
```

The standard-library dynamic program optimizes these floors over all 231
integer `q` values in `{0,2,3,...,12}` with sum 470.  Its exact minimum is

```text
924,
```

attained already by 223 values `q=2` and eight values `q=3`.  The available
Wave 20 trace at `Delta=12` is 1008, so this route gives no contradiction.
Allowing the already-forbidden value `q=1` does not change the minimum.

## 8. Retained failed and incomplete routes

1. **Index determination.**  The determinant argument becomes decisive at
   `h>=21`, but neither the audited real spectrum nor `rank_F2(M)=44`
   determines the 3- and 7-primary index.  A Smith/top-determinantal-divisor
   computation for the relevant integral eigenspace or direct modular ranks
   of `M` would be new necessary input.

2. **Mod eight.**  The Wave 20 alternating-form argument fixes every
   `mathcal A_ii` modulo four.  Its residue modulo eight depends on signed
   triple incidences among the odd support of a row and is not determined by
   `q(T)` or the one-point pair distribution alone.  No stronger universal
   diagonal floor was proved.

3. **Harmonic and iterated Schur lifts.**  The harmonic cubic excludes only
   `q=11,12` at the endpoint.  Higher one-point Schur/Gegenbauer traces were
   already reported weaker in Wave 20; no new exact trace contradiction was
   obtained here.

4. **Three-point SDP.**  A full triple-type spherical SDP was outlined, but
   the dependency locator hung and was aborted.  No solver was installed and
   no numerical output exists.  This unrun route is not evidence for or
   against the endpoint.

5. **Harness failures.**  One stale hostile-test expectation and one
   PowerShell-version metadata error are preserved in `failed-runs.md`.  The
   repaired standard-library suite passes 12/12.

## 9. Boundary

The exact projection-lattice and determinant lemmas are useful reductions,
but their decisive premise is unproved.  The strongest justified project
conclusion remains the independently audited conditional bound

```text
n3 >= 705,
induced_C6_count >= 209991.
```

This lane supplies no graph, no nonexistence proof, no unconditional stronger
bound, no formal-kernel proof, and no novelty determination.  Its primary
status is therefore `UNKNOWN`, with the displayed intermediate lemmas
remaining discovery-agent `DERIVED` claims pending independent audit.
