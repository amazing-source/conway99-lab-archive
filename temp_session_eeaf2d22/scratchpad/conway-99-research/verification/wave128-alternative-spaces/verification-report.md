# Wave 128 verification report

Claim label: `VERIFIED`, scoped to the conditional necessary consequences.

## Preinspection and replay

The discovery package manifest has SHA-256
`851df7c40ab2056f6a5f927093707e5e9b578df2b18662e6b95fcf6335033038`.
All 11 sealed entries and all five imported manifest hashes matched before
the verifier executed.  The discovery JSON replayed byte-for-byte and its
12 tests passed.  The independent verifier's eight tests also passed.

## Independent reconstruction

From the motif adjacency alone, the verifier reconstructed three zero
incidence rows, four copies of each singleton, and 36 pair rows.  A displayed
13-row minor of `Q=[one P]` has determinant one, so `W=im_Z(Q)` is primitive.
Exact Bareiss elimination gives

```text
rank(Lambda)=74,
det(Lambda)=det(Q^TQ)=6191736422400=2^22 3^10 5^2.
```

The linear block equations independently give the coordinate action `C` in
`BQ=QC`.  Exact matrix arithmetic verifies

```text
G C = C^T G,
(C^T)^2-7C^T in G Mat_13(Z),       G=Q^TQ.
```

Therefore `C^T` acts on `A_W=Z^13/GZ^13`, and its polynomial is
`x(x-7)` there.

## Cokernel split

For `p != 7`, division by seven is valid and `E=C^T/7` is idempotent.
The `7`-eigenpart is the quotient by `im(1-E)`, while the zero-eigenpart
is the quotient by `im(E)`.  Multiplying either added relation by the unit
seven does not change its `p`-primary cokernel, giving the presentations

```text
A_U,p = coker [G | 7I-C^T],
A_K,p = coker [G | C^T].
```

A clean-room Euclidean integer Smith reduction, distinct from discovery's
local DVR elimination, gives

```text
SNF(G)             = 1^6, 3, 12, 24, 24, 72, 360, 11520
SNF([G|7I-C^T])    = 1^9, 3, 3, 180, 11520
SNF([G|C^T])       = 1^9, 8, 24, 24, 72.
```

These yield exactly the claimed primary groups and determinant factors.

## Quadratic phases

For `x=a/p^e in W*`, put `y=Gx`.  If `z` is an integral ambient lift, then
the complementary class is `z-x`.  Since `one=Qe_0` is characteristic in
the odd unimodular ambient lattice,

```text
z^2 = (z,one) = (x,one) = y_0 mod 2.
```

Thus the even complementary form is

```text
q_Lambda(x)=(y_0-x^TGx)/2 mod Z.
```

The verifier enumerated each primary module by exact lifting and reduced its
Gauss sum modulo the exact cyclotomic polynomial.  The phases are

```text
          p=2    p=3    p=5     product away from 7
U         -i     -1     -1      -i
K         +1     -1     +1      -1.
```

Milgram gives total phase `i` for positive rank 42 and `+1` for positive
rank 32.  Hence both seven-primary phases are `-1`.

## Seven-adic gluing

At seven, `Lambda` is unimodular.  The saturated rational eigensublattices
`U` and `K` are primitive orthogonal complements, so their discriminant
groups are anti-isometric and have equal order.  Combining this with
`[Lambda:U direct_sum K]=7^k` gives order `7^k` for each.

Self-adjointness gives `B Lambda subset 7U*`.  Both lattices have the same
relative covolume `7^(42-k)`, using the Wave 109 Smith index and
`v_7(det U)=k`; therefore equality holds:

```text
B Lambda = 7U*.
```

The same argument for `7I-B` gives `(7I-B)Lambda=7K*`.  Thus both
seven-primary groups have exponent seven and are `(Z/7)^k`.

For even `k` over `F_7`, the normalized phase is
`(-1)^(k/2) Legendre(det,7)`.  Phase `-1` is exactly the nonsplit
orthogonal type `O^-(k,7)`.

## Rootlessness and row survival

Because `Lambda subset one^perp`, every vector in it has even norm.  An
integer norm-two vector must be `+/-(e_i-e_j)`.  For `e_i-e_j`, coordinate
`i` of `D(e_i-e_j)` is `-D_ij`, hence is zero or minus one.  It cannot equal
the coordinate required by eigenvalue `3` or `-4`; multiplying by minus one
does not change the contradiction.  Therefore both minima are at least four.

For every imported `k=16,18,...,30`, the seven-primary length is at most the
relevant lattice rank and a nonsplit even-dimensional quadratic space over
`F_7` exists.  The derived local conditions therefore exclude no row.

## Verdict boundary

The finite-primary split, seven-primary exponent and type, determinant
formulas, and rootlessness are verified as conditional necessary facts.
No integral realization of `U` or `K`, no outside matrix `D`, and no graph
is constructed.  Motif extension, Conway-99, and novelty remain `UNKNOWN`.
