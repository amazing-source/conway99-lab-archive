# Wave 29 independent audit: exclusion of the single `S0` control

```yaml
role: verifier
date_utc: 2026-07-24T03:26:59Z
git_commit: 74b6f3adcee19ca2b0480258bb7bf51198bd085a
claim_label: VERIFIED
scope: >-
  Independent reconstruction of the exclusion of only
  S0=K12 orthogonal_sum LAMBDA(F) as the S-form of the frozen full
  n3=708 projector/Schur endpoint package.
inputs:
  agents/2026-07-24-wave29-s0-frame-exclusion.md: e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045
  attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256: 8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b
  agents/2026-07-24-wave28-orchestrator-brief.md: 6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e
  verification/wave28-theta-modular/audit.md: adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb
  verification/wave28-theta-modular/independent-results.json: 24298ae282c7baa252a39ffe96fc37b7c696cb51f14b9ddea2318a59b4335b7f
method: >-
  Fresh symbolic derivation, exact integer and rational arithmetic, complete
  enumeration of the row-alphabet and trace residues, premise-deletion
  controls, and an independently written Python standard-library checker.
command: >-
  python -B -m unittest -v test_independent_check.py
outputs:
  - verification/wave29-s0-frame-exclusion/independent_check.py
  - verification/wave29-s0-frame-exclusion/test_independent_check.py
  - verification/wave29-s0-frame-exclusion/independent-results.json
  - verification/wave29-s0-frame-exclusion/failure-ledger.md
limitations:
  - The Wave 28 independently verified K12 and LAMBDA(F) block data are frozen inputs rather than re-enumerated here.
  - The even-unimodular signature theorem is a frozen standard theorem.
  - No claim is made about another determinant-729 lattice or a nonorthogonal glue.
  - n3=708, Conway-99, and novelty remain UNKNOWN.
```

## Verdict

**PASS.** The discovery argument is independently reconstructed. The single
orthogonal lattice

```text
S0 = K12 orthogonal_sum LAMBDA(F)
```

cannot be the `S`-form of a full endpoint package satisfying the frozen
premises. The verifier promotes this scoped claim to `VERIFIED` and the
corresponding `S0` endpoint origin to `REFUTED`.

This does **not** exclude any other determinant-729 form, does not exclude
`n3=708`, does not settle Conway-99, and establishes no novelty claim.

## 1. Independence and frozen inputs

The verifier recorded byte hashes before opening any Wave 29 discovery
artifact. Both caller-supplied hashes matched:

```text
e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045
  agents/2026-07-24-wave29-s0-frame-exclusion.md
8cb5b0198ac9e787a8234820e648626dc27f900f53b7511068d5442d06d7a39b
  attempts/wave29-s0-frame-exclusion/artifact-manifest.sha256
```

All six prior frozen inputs also matched their stated hashes. The verifier
then wrote a new checker without importing or executing the discovery code.

The following single-lattice data come from the already independent Wave 28
audit and are treated as frozen premises here:

| block | rank | determinant | minimum | form |
|---|---:|---:|---:|---|
| `K12` | 12 | 729 | 4 | even, integral, positive definite |
| `LAMBDA(F)` | 32 | 1 | 4 | even, integral, positive definite |

The current audit checks the new implication from those block facts to the
endpoint exclusion; it does not repeat the 15-million-node norm enumeration.

## 2. The `63/168` row split

Write a row of the assumed integral endpoint matrix as `x=(u,v)` in the
displayed integral direct-sum basis. The endpoint diagonal gives

```text
x^T S0 x = 4.
```

If both integral components were nonzero, their block norms would each be at
least four, so the orthogonal sum would have norm at least eight. Hence every
row lies in exactly one block.

For a block `J`, the tight-frame identity is

```text
X_J^T X_J = 21 S_J^(-1).
```

Multiplication by `S_J` and taking traces yields

```text
4 n_J = tr(S_J X_J^T X_J) = 21 rank(J).
```

Therefore

```text
n_K = 21*12/4 = 63,
n_L = 21*32/4 = 168.
```

The integrality of the direct-sum coordinates is essential. A hostile control
with block minima two admits a mixed norm-four vector and correctly destroys
this step.

## 3. No hidden cross-block term

After permuting rows,

```text
X = [X_K  0
     0    X_L].
```

Because `S` is block diagonal, direct multiplication gives `M=XSX^T` block
diagonal. Entrywise squaring preserves every cross zero, so `W=M o M` is
block diagonal. The definitions

```text
Q=X^T W X,
B=S Q
```

then make `Q` and `B` block diagonal in the same coordinate split. There is
no omitted coupling term. The checker includes a fresh exact small-dimensional
matrix control for all four operations; the proof itself is the entrywise
block-zero calculation above.

The principal `Q` blocks inherit even integrality and positive definiteness.
Consequently their determinants are positive integers.

## 4. Determinant allocation

The frozen endpoint bounds give

```text
729 det(Q)=det(B)<=6525,
det(Q)>=5,
det(Q)=1 mod 4.
```

Since `det(Q)` is an integer no larger than `floor(6525/729)=8`, exact
enumeration leaves only

```text
det(Q)=5.
```

The positive integral block determinants are initially either

```text
(det(Q_K),det(Q_L))=(1,5) or (5,1).
```

The first allocation would make the rank-12 positive-definite form `Q_K`
even unimodular. Its signature would be 12, contradicting the standard
signature-divisibility-by-eight theorem. Thus

```text
det(Q_K)=5,  det(Q_L)=1.
```

No determinant factor is reversed:

```text
det(B_K)=det(S_K)det(Q_K)=729*5=3645,
det(B_L)=det(S_L)det(Q_L)=1*1=1,
det(B)=3645.
```

Deleting the rank-12 veto leaves the other allocation and gives
`det(B_K)=729`, exactly equal to the later cap. The strict contradiction then
disappears, confirming that the veto is active.

## 5. Row alphabet and block traces

From `S=21G^(-1)` and `G=X^T X`,

```text
M^2=XS G S X^T=21M.
```

For a row `i`, let `a,b,c,z` count off-diagonal entries `+1,-1,-2,0`.
The row sum and diagonal of the projector identity give

```text
4+a-b-2c=0,
16+a+b+4c=84,
a+b+c+z=230.
```

A fresh complete integer enumeration gives exactly 13 solutions:

```text
a=32-c, b=36-3c, z=162+3c, 0<=c<=12.
```

The cubic row sum is therefore

```text
sum_j M_ij^3 = 64+a-b-8c = 60-6c.
```

For either block, cyclicity of trace and the block split give

```text
tr(B_J)
 =tr(S_J X_J^T W_J X_J)
 =tr(M_J W_J)
 =sum_(i,j in J) M_ij^3.
```

Thus each block trace is a positive multiple of six. The checker additionally
attacked the immediate cross-zero, symmetry, and double-count couplings. The
forced sums

```text
sum_(i in K)c_i=626,
sum_(i in L)c_i=1674
```

give nonnegative even directed counts in every alphabet class. The `168`
cross-block zeros force `c_i>=2` on each `K12` row, consistent with the sum.
No hidden parity or block-size contradiction is being used or suppressed.

## 6. Both AM-GM thresholds are exact

The matrices `B_J=S_JQ_J` have positive real eigenvalues because they are
similar to the positive-definite symmetric matrices
`S_J^(1/2) Q_J S_J^(1/2)`. For the rank-32 block with determinant one,
AM-GM yields `tr(B_L)>=32`; its positive multiple-of-six residue strengthens
this to `tr(B_L)>=36`. Hence `tr(B_K)<=24`.

The checker enumerates all positive multiple-of-six pairs summing to 60 and
tests the exact integer condition

```text
det(B_J) rank(J)^rank(J) <= tr(B_J)^rank(J).
```

The unique surviving pair is

```text
tr(B_K)=24, tr(B_L)=36.
```

In particular, trace 18 fails for the `K` block and trace 30 fails for the
`L` block using exact integer powers. Removing the multiple-of-six residue
allows the arithmetically compatible pair `(28,32)` and destroys the final
contradiction.

## 7. `C_K` is not assumed positive semidefinite

Block restriction of `B=I+2C` gives an integral matrix

```text
C_K=(B_K-I_12)/2,
tr(C_K)=(24-12)/2=6.
```

It is self-adjoint for the positive-definite block form `G_K`, hence real
diagonalizable. Positivity is used only for `B_K`: every eigenvalue of
`B_K=I+2C_K` is positive. Thus every eigenvalue `mu` of `C_K` is real and

```text
mu > -1/2.
```

Negative eigenvalues in `(-1/2,0)` are allowed.

If `r=rank(C_K)`, diagonalizability and integral characteristic coefficients
give

```text
char_CK(t)=t^(12-r)p(t),
```

with `p` monic in `Z[t]` and `p(0)` a nonzero integer. Therefore

```text
|product_(mu_i nonzero) mu_i|=|p(0)|>=1.
```

This is the characteristic pseudodeterminant. A hostile control
`C=(1/2)I_12` has the same trace and positive `B=2I`, but its pseudodeterminant
is `2^-12`; it gives `det(B)=4096>729`. It is excluded exactly by the
integrality premise.

## 8. Fresh pointwise logarithmic proof, including negative `mu`

Set

```text
L=log(3), c=L-2/3.
```

The positive-term identity

```text
log(3)=2 sum_(k>=0) (1/2)^(2k+1)/(2k+1)
```

and a rational geometric tail bound prove exactly `2/3<L<2`, hence `c>0`.

For `x>0`, define

```text
F(x)=xL-c log(x)-log(1+2x).
```

Fresh symbolic expansion verifies

```text
x(1+2x)F'(x)=(x-1)(2Lx+c).
```

The second factor is positive, so `F` decreases to and then increases from
its global minimum `F(1)=0`.

For the previously delicate interval `-1/2<x<0`, define

```text
g(x)=xL-log(1+2x).
```

Then

```text
g'(x)=L-2/(1+2x)<L-2<0.
```

As `g(0)=0`, this orientation gives `g(x)>0` for every negative `x` in the
domain. Also `-c log|x|>0` because `c>0` and `|x|<1`. Therefore, strictly on
the negative interval and weakly on the positive interval,

```text
log(1+2x)<=xL-c log|x|.
```

This proves the required pointwise inequality throughout
`(-1/2,infinity)\{0}` without a PSD assumption.

## 9. Final contradiction

Apply the pointwise inequality to each nonzero eigenvalue of `C_K`; zero
eigenvalues contribute `log(1)=0`. Using trace six and the integer
pseudodeterminant,

```text
log det(B_K)
 <= L sum_i mu_i - c log|product_(mu_i nonzero)mu_i|
 <= 6L.
```

Hence

```text
det(B_K)<=3^6=729.
```

But the independently checked determinant allocation gives

```text
det(B_K)=3645>729.
```

The contradiction is exact.

## 10. Hostile controls and test result

The checker removes each of the 11 named premises in turn; every deletion
fails closed at the first stage that needs it. Additional controls verify:

- lowering both block minima to two destroys the row-support split;
- omitting the rank-12 veto leaves equality rather than contradiction;
- omitting the trace residue leaves `(28,32)` and no logarithmic contradiction;
- omitting `C_K` integrality permits determinant 4096; and
- swapping the determinant allocation is caught by the rank-12 veto.

The independent suite result is:

```text
Ran 27 tests
OK
```

`independent-results.json` regenerates byte identically.

## Status wall

```text
S0 full projector/Schur endpoint origin:  REFUTED (VERIFIED)
all other h=729 lattices:                 UNKNOWN
n3=708:                                  UNKNOWN
Conway-99:                               UNKNOWN
novelty:                                 UNKNOWN
```
