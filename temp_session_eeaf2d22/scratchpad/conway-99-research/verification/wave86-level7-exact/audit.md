# Wave 86 independent level-seven theta audit

Date UTC: 2026-07-28.

Verdict: **VERIFIED_WITH_LITERATURE_CORRECTION**.

Conditional theorem verified:

```text
in the Wave 71 q=16 row,
N14 + N16 + N18 >= 5868.
```

This is conditional on a hypothetical `srg(99,14,1,2)` and the independently
verified Wave 66/71 lattice transfer.  It does not exclude the `q=16` row,
construct a lattice, or resolve Conway-99.  Graph existence and literature
novelty remain `UNKNOWN`.

The correction concerns source usage, not the mathematical inequality:
the printed Eq. (2.8) of the cited arXiv paper omits a normalization ratio.
The discovery's actual Fricke factors are nevertheless correct when derived
from that paper's Eqs. (2.5) and (2.7).  The verifier records the conversion
explicitly below.

## Frozen input

The discovery inventory was frozen at git commit
`fd88280eb25aecd8c40d9e82f572813f1c850ec5`.  Its package manifest has
SHA-256

```text
c6066fd10258578c15e511f3802217e4ff613ffe3d3b3b8f11e804f0316ac75d
```

All eleven entries in that manifest replay byte-for-byte.  The independent
implementation neither imports nor executes discovery code.

## Full scalar modular space

For `Gamma0(7)` the elementary group data are

```text
index = 8,  cusps = 2,  e2 = 0,  e3 = 2,  genus = 0.
```

Here `e2=0` because `-1` is not a square modulo seven, while the two roots
of `x^2+x+1` modulo seven give `e3=2`.  For even weight 22 the standard
dimension formula gives

```text
dim S_22 = -21 + 2(11-1) + 2 floor(22/3) = 13,
dim M_22 = dim S_22 + number of cusps = 15.
```

The index-eight Sturm bound is

```text
floor(22*8/12) = 14.
```

The verifier independently generated generalized-Bernoulli constants and
twisted divisor sums for

```text
C_k = E_k(chi,1),  T_k = E_k(1,chi),  chi=(-7/.),
```

then selected a 15-product basis of total weight 22 in a different order
from discovery.  Its coefficient matrix on `q^0,...,q^14` has exact rank
15.  Removing its last product lowers the rank to 14, so the incomplete
basis hostile control fails as intended.  Dimension 15 plus Sturm injectivity
proves that these products span all of `M_22(Gamma0(7))`, not a restricted
subspace.

## Fricke normalization and the printed-source correction

The slash convention used both here and in the theta calculation is

```text
(f|_k W_7)(tau) = 7^(-k/2) tau^(-k) f(-1/(7 tau)).
```

The primary source is Florez, Karabulut, and Vu,
*Eisenstein series whose Fourier coefficients are zeta functions of binary
Hermitian forms*, arXiv:2002.09819v1:
<https://arxiv.org/abs/2002.09819>.

Its Eq. (2.5) normalizes

```text
E_k(chi1,chi2)
 = (N1/(-2 pi i))^k (k-1)!/g(conj(chi1)) G_k(chi1,chi2),
```

while Eq. (2.7) transforms the unnormalized `G_k`.  Therefore conversion
from `G` to the q-normalized `E` contributes the ratio

```text
(N1/N2)^k g(chi2)/g(conj(chi1)).
```

Combining it with Eq. (2.7) gives

```text
E_k(chi1,chi2)|W_N
 = chi2(-1) (N1/N2)^(k/2)
   g(chi2)/g(conj(chi1))
   E_k(conj(chi2),conj(chi1)).
```

The paper's printed Eq. (2.8) omits this ratio and hence is not consistent
with its own Eq. (2.5).  It must not be used literally for the q-normalized
series.

For the real primitive odd character modulo seven,

```text
g(chi) = i sqrt(7),  chi(-1) = -1.
```

The corrected conversion consequently yields exactly

```text
C_k|W_7 = -i 7^((k-1)/2) T_k,
T_k|W_7 = -i 7^((1-k)/2) C_k.
```

The verifier also evaluated the independently generated q-series at the
Fricke fixed point `tau=i/sqrt(7)` for weights `3,5,9,19`; all four ratios
match these formulas to relative error below `2e-12`.  Omitting the two
Gauss phases changes, for example, the product `C_3 C_19` factor from
`-7^10` to `+7^10`.

On an individual odd-weight, odd-character form, applying `W_7` twice gives
`-1=chi(-1)`.  Each weight-22 product contains two such factors, so its
square is `+1`.  The independently reconstructed rational 15-by-15 Fricke
matrix squares exactly to the identity.

## Poisson transfer, including sign and power

Use

```text
Theta_L(tau) = sum_{v in L} q^((v,v)/2).
```

For rank 44, weight 22, and `det(L)=7^16`, Poisson summation gives

```text
Theta_L|W_7
 = 7^(22/2) i^(-22) / sqrt(7^16) Theta_(sqrt(7)L*)
 = -7^3 Theta_K.
```

Because the weight-22 trivial-character Fricke operator squares to one,
this is equivalently

```text
Theta_L = -7^3 (Theta_K|W_7).
```

Thus the Fricke slash convention in the Eisenstein calculation is the same
one used in the Poisson calculation.  Reversing the transfer sign makes the
formal control's constant coefficient `-1`; replacing `7^3` by `7^2` makes
it `1/7`.

The theta normalization also fixes the norm indices:

```text
[q^7]Theta_K = N14,
[q^8]Theta_K = N16,
[q^9]Theta_K = N18.
```

This matches the independently verified Wave 71 short-vector bijection.

## Independently derived positive identity

Write

```text
x_n=[q^n]Theta_K,  y_n=[q^n]Theta_L.
```

The verifier imposed only

```text
x0=y0=1,  x1=...=x6=0,
```

and the exact Fricke relation.  Eliminating `x14` gives

```text
x14 = 1977312182
       -288 x7 +35 x8 +91 x9 -27 x10
       -7 x11 -4 x12 +5 x13.
```

The certificate was not copied from discovery.  The verifier solved the
seven-dimensional exact linear system expressing the coefficient vector of
`x7+x8+x9` in the seven nonnegative linear forms

```text
x8, x9, x11, y1, y2, y3, y4.
```

It independently obtains

```text
x7+x8+x9 - 1997236/341
 = (180/217)x8
 + (2344/2387)x9
 + (1/2387)x11
 + (1118523/341)y1
 + (134113/341)y2
 + (9604/341)y3
 + (343/341)y4.
```

All seven multipliers are strictly positive, and all theta coefficients are
nonnegative integers.  Hence

```text
S=x7+x8+x9 >= 1997236/341 = 5856.997...
```

The only imported arithmetic restriction used to round this inequality is
the verified Wave 71 relation

```text
S = 2 mod 14.
```

The preceding admissible value is `5854`, and the next is `5868`; therefore

```text
S >= 5868.
```

With the verified norm dictionary this is exactly

```text
N14+N16+N18 >= 5868.
```

## Finite scalar null

The verifier independently solved the seven equations

```text
x7=5868, x8=x9=0, y1=y2=y3=y4=0
```

inside the full Sturm coordinate space.  The resulting first 15
coefficients agree byte-for-byte with discovery.  Reconstructing the unique
modular pair from the independent product basis shows both scalar series
are integral, even away from the constant term, and nonnegative through
`q^50`.

This is only a finite formal scalar-feasibility control.  It is not a theta
series realization, lattice, marked frame, graph, or all-orders positivity
theorem.  It therefore does not weaken or negate the verified lower bound,
and it does not exclude `q=16`.

## Replay and boundary

```text
independent exact replay:        PASS
independent hostile tests:       12 passed
discovery manifest entries:      11/11 match
wrong Gauss phase:               rejected
wrong theta sign / 7-power:      rejected
incomplete modular basis:        rejected
free physical memory:            above 53%
```

The verified result is a substantial conditional lower bound in one rank
row, not a Conway-99 solution.  `q=16`, graph existence, Conway-99, and
novelty remain `UNKNOWN`.
