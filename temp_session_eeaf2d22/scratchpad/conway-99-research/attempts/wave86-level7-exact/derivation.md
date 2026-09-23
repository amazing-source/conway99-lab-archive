# Exact level-7 Fricke pair and a 5,868-vector lower bound

Claim label: `DERIVED` (discovery; independent verification required).

Everything is conditional on the verified Wave 66/71 transfer and the
Wave 71 row `q=16`.

## 1. The exact scalar modular space

Put

```text
A_k=E_k(chi,1),  B_k=E_k(1,chi),  chi=(-7/.),
```

for odd `k`.  Products of two such series of total weight 22 have trivial
character.  Exact generalized-Bernoulli and divisor-sum expansions give 15
independent products through `q^14`.

The group `Gamma0(7)` has index 8, two cusps, no elliptic points of order
two, two elliptic points of order three, and genus zero.  The standard
dimension formula gives

```text
dim M_22(Gamma0(7))=15.
```

The Sturm bound is

```text
floor(22*[SL2(Z):Gamma0(7)]/12)=floor(176/12)=14.
```

Thus coefficients `q^0,...,q^14` are exact coordinates on the full scalar
space.

## 2. Fricke normalization

For the normalized twisted Eisenstein series,

```text
A_k | W_7 = -i*7^((k-1)/2) B_k,
B_k | W_7 = -i*7^((1-k)/2) A_k.
```

The exact rational matrix on weight-22 products squares to the identity.

Write

```text
x_n=[q^n]Theta_K,  y_n=[q^n]Theta_L.
```

Poisson summation, rank 44, and `det(L)=7^16` give

```text
Theta_L=-7^3(Theta_K|W_7).                 (1)
```

The sign in (1) is essential: `i^(-22)=-1`.  The exact controls reject both
the opposite sign and the power `7^2`.

## 3. Exact positive-coefficient certificate

Insert

```text
x_0=y_0=1,  x_1=...=x_6=0
```

into the Fricke matrix and eliminate `x_14` using `y_0=1`.  Exact rational
elimination gives the identity

```text
x7+x8+x9 - 1997236/341
 = (180/217)x8
 + (2344/2387)x9
 + (1/2387)x11
 + (1118523/341)y1
 + (134113/341)y2
 + (9604/341)y3
 + (343/341)y4.                            (2)
```

Every coefficient on the right of (2) is positive.  Theta coefficients
count vectors and are nonnegative.  Therefore

```text
x7+x8+x9 >= 1997236/341 = 5856.997067...
```

Wave 71 independently proved

```text
x7+x8+x9 = 2 (mod 14).
```

The first permitted integer is consequently

```text
boxed: x7+x8+x9 >= 5868.                   (3)
```

For norms at most 18, Wave 71 identifies these coefficients with
`N14,N16,N18`, the counts of integral `-4` eigenvectors.  Hence (3) is

```text
N14+N16+N18 >= 5868.
```

## 4. Exact scalar boundary

The following first 15 coefficients satisfy every exact scalar relation,
are nonnegative, and are even away from the constant term:

```text
Theta_K:
1,0,0,0,0,0,0,5868,0,0,28852082,26264,582557668,
2681235704,12272379984

Theta_L:
1,0,0,0,0,358916,34393854,600737200,11946196274,
132636715536,1237054839912,9122211909000,56682577580992,
304577760235536,1443860798777424
```

The unique modular pair determined by this Sturm prefix remains integral,
even, and nonnegative through `q^50` in the exact replay.  This is only a
hostile scalar-feasibility control.  It is not asserted to be a theta
series, a lattice, or a marked-frame realization.

## Boundary

This package strengthens Wave 71 in the `q=16` row from "at least two short
vectors modulo 14" to at least 5,868 short vectors.  It does not exclude the
row.  Scalar theta series do not encode the signed-support compatibility
conditions.  Graph existence, Conway-99, and novelty remain `UNKNOWN`.
