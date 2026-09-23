# Wave 24 theorem-applicability and boundary notes

## 1. Frozen premises and endpoint specialization

The verifier uses only the byte-frozen Wave 20, Wave 21, and Wave 23 audits
listed in `preinspection-freeze.sha256` and the discovery package frozen
there.  For a putative `srg(99,14,1,2)`, those audited premises give a
rank-44 even lattice `L`, a positive-definite integral endomorphism `B`
self-adjoint for the Gram form of `L`, and

```text
B = I + 2C,
tr(B) = 4(n3-693),
det(B) = h det(Q),
h = 3^(44-rank_F3(M)) 7^(44-rank_F7(M)),
Q even, integral, positive definite of rank 44,
h = 1 mod 4, h != 1,
det(Q) = 1 mod 4, det(Q) >= 5.
```

At `n3=708`, direct substitution gives

```text
Delta=15, tr(A4)=1260, tr(B)=60, tr(C)=8.
```

The local identities independently specialize to

```text
sum q(T)=2*708/3=472,
sum(q(T)-2)=10,
sum diagonal excess units=1260/4-231=84.
```

No unproved modular rank is assigned a value.

## 2. Nonzero characteristic coefficient

Positive-form self-adjointness means that, after conjugating by a positive
square root of the Gram matrix, `C` is similar over the reals to a symmetric
matrix.  Hence `C` is diagonalizable with real eigenvalues.  Let `r=rank(C)`.
Its characteristic polynomial has the form

```text
char_C(t)=t^(44-r) p(t),
```

where `p` is monic with integer coefficients and `p(0)` is a nonzero
integer.  Consequently, for the nonzero eigenvalues `mu_i`,

```text
|product mu_i|=|p(0)|>=1.
```

This is precisely where integrality and diagonalizability enter.  Applying
AM-GM to `mu_i^2` and Cauchy to their sum gives

```text
sum mu_i^2 >= r,
sum mu_i^2 >= 8^2/r.
```

The minimum of `max(r,64/r)` over all integers `1<=r<=44` is exactly eight,
attained only at `r=8`.  Thus

```text
tr(C^2)>=8,
tr(B^2)=44+4tr(C)+4tr(C^2)>=108.
```

The hostile rational matrix `C=(2/11)I_44` has trace eight but
`tr(C^2)=16/11`; it confirms that the integral characteristic coefficient is
an active premise.

## 3. Pointwise logarithmic inequality

Write

```text
L=log(3), c=L-2/3.
```

The exact atanh series certificate proves `2/3<L<2`, so `c>0`.  For
`x>0`, set

```text
F(x)=xL-c log(x)-log(1+2x).
```

Multiplication by the positive denominator `x(1+2x)` gives

```text
x(1+2x)F'(x)=(x-1)(2Lx+c).
```

The second factor is positive.  Hence `F` decreases to `x=1`, increases
after `x=1`, and has minimum `F(1)=0`.

For `-1/2<x<0`, put

```text
g(x)=xL-log(1+2x).
```

Then

```text
g'(x)=L-2/(1+2x)<L-2<0.
```

Since `g(0)=0`, this gives `g(x)>0`; also `-c log|x|>0`.  Therefore, on both
nonzero domains,

```text
log(1+2x) <= x log(3)-c log|x|.
```

Zero eigenvalues of `C` are handled separately and contribute `log(1)=0`.
Positivity of `B` ensures every nonzero eigenvalue lies in `(-1/2,infinity)`.
Summing over the nonzero eigenvalues and using the integral
pseudodeterminant gives

```text
log det(B)
 <= 8 log(3)-c log|product mu_i|
 <= 8 log(3).
```

Thus `det(B)<=3^8=6561`.  This argument would be invalid without real
eigenvalues and positive-form self-adjointness.  The verifier's integral
hostile control containing a skew block has trace eight and determinant
`17*3^8`, but is not self-adjoint and has nonreal eigenvalues.

## 4. Determinant residues and finite index list

The congruence `B=I+2C` gives

```text
det(B)=1+2tr(C)=1 mod 4.
```

The frozen even-Gram congruence gives `det(Q)=1 mod 4`; the rank-44
even-unimodular signature obstruction excludes `det(Q)=1`, so
`det(Q)>=5`.  The factorization then yields

```text
h<=floor(6561/5)=1312.
```

Together with the Smith formula, `h=1 mod 4`, and the global scaled-dual
obstruction `h!=1`, exhaustive multiplication of powers of three and seven
leaves exactly

```text
{9,21,49,81,189,441,729,1029}.
```

The associated modular ranks and the largest possible
`det(Q)=1 mod 4` values are reproduced in `independent-results.json`.
Dropping either `h!=1` or `h=1 mod 4` makes excluded values reappear in the
hostile tests.

## 5. Exact abstract survivor

The independent checker reconstructs the displayed `E8` and `A2` matrices
and emits every entry of the resulting 44-by-44 matrices in
`survivor-certificate.json`:

```text
S = E8^5 direct_sum A2^2,
Q = (E8^-1)^5 direct_sum A2^2,
G = 21 S^-1,
B = S Q,
C = (B-I)/2.
```

Exact elimination and multiplication give

```text
det(S)=9, det(Q)=9, det(B)=81,
tr(B)=60, tr(C)=8, tr(C^2)=32, rank(C)=2,
SG=21I, GB=21Q, B=SQ, B=I mod 2.
```

The base blocks are positive definite.  Therefore `S`, `Q`, and `G` are
positive definite, and `GB=21Q` proves both Gram-self-adjointness and
positivity of `B`.  All three Gram matrices are integral and even.

For the minimum, each `21E8^-1` block is an even positive-definite integral
form, so every nonzero norm is a positive even integer times 21 and is at
least 42.  Each remaining `G` block has form

```text
14(a^2+ab+b^2),
```

whose nonzero minimum is 14.  Hence the full `G` lattice has minimum at
least 14.

## 6. Local endpoint consequences

For the positive-semidefinite harmonic Gram matrix

```text
H=23(M o M o M)-24M,
```

the frozen identities specialize to

```text
H_TT=1376,
(H1)_T=138(q(T)-2),
1^T H 1=1380.
```

At `q=12`, PSD Cauchy fails by exactly

```text
1380^2-1376*1380=5520,
```

so `q<=11`.  A single `q=11` is not excluded by that Cauchy inequality.
After removing the all-ones component, its diagonal is `1291/5`.  For two
`q=11` indices, each possible original off-diagonal
`-136,-1,0,1` yields a negative centered two-by-two determinant.  Thus at
most one `q=11` index exists.

The profile with 221 values equal to two and ten values equal to three
satisfies the scalar `q` sum and every local diagonal lower bound.  It is
only a scalar profile, not a matrix or graph.

## 7. Semantic wall

The matrices in `survivor-certificate.json` verify an abstract
coordinate-lattice package only.  They do not prove:

- a primitive embedding of the `G` lattice into `Z^231`;
- 231 norm-four projector columns with the required entry and row data;
- a projector/Hadamard or `W=M o M` origin;
- an `srg(99,14,1,2)` graph.

Accordingly, the verified promotion is limited to the conditional index
restriction and the existence of a survivor of the stated relaxation.
`n3=708` is not excluded; target existence and novelty remain `UNKNOWN`.
