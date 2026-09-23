# Scalar C4 Jacobi reduction

Claim label: `DERIVED`.

This is a second, disjoint alternative-space result in Wave 121. It audits
and sharpens the verified Wave 116 four-variable C4 marking. The incidence
application is in the rank-28, `q=16` row, not the rank-30 discriminant
experiment in the main derivation.

## 1. A primitive alternating vector already lies in `L`

Fix an induced C4 in cyclic order and put

```text
epsilon=(1,-1,1,-1),
d_C=sum epsilon_i u_i.
```

The coefficients are integral and sum to zero. Therefore `d_C` is an
integer combination of differences `u_i-u_j`, so

```text
d_C in M subset L.
```

On the cycle, the Gram matrix of the `u_i` has diagonal `28/9`, edge
entries `-8/9`, and opposite entries `1/9`. Multiplication by `epsilon`
gives `5 epsilon`, hence

```text
||d_C||^2=20.
```

The vector is primitive in `L`: if `d_C=k e` with `e in L` and `k>1`,
then the even integer `||e||^2` would equal `20/k^2`, which is impossible.

Its divisibility in `L` is one. Indeed the divisibility `s` divides 20. If
`s>1`, then `d_C/s in L*` has exact order `s` modulo `L` by primitivity.
But `L*/L` is 7-elementary, while `s` divides 20. Thus `s=1`.

## 2. Index 70 on `K`, index 10 on `L`

Define

```text
b_C=sqrt(7)d_C.
```

Since `d_C in L subset L*`,

```text
b_C in K=sqrt(7)L*.
```

Its norm and ordinary scalar Jacobi index are

```text
||b_C||^2=140,    m_K=70.
```

The vector `b_C` is primitive in `K`. Its divisibility is exactly seven:
for `x=sqrt(7)y in K`,

```text
<b_C,x>=7<d_C,y>,
```

and primitivity of `d_C` makes the values `<d_C,L*>` all of `Z`.

The Fricke partner is `b_C/sqrt(7)=d_C in L`, with

```text
m_L=||d_C||^2/2=10.
```

Wave 116 used

```text
h_C=sum epsilon_i g_i=3b_C.
```

That marking has norm 1,260 and index 630. The primitive marking reduces
both K and L indices by a factor of nine:

```text
630 -> 70,
90  -> 10.
```

No automorphism is used. Each induced C4 has the same alternating Gram
mode, and changing the chosen bipartite sign replaces `b_C` by `-b_C`;
the lattice theta sum is even in the elliptic variable.

## 3. Exact target coefficient

For `x=sqrt(7)y in K`, put `t_i=<y,u_i>`. Then

```text
<x,b_C>=7 sum epsilon_i t_i = 7 ell.
```

At norms 14, 16, and 18, the verified coordinate alphabet is
`t_i in {0,+1,-1}`. Each summand `epsilon_i t_i` is at most one, so

```text
ell=4  iff  t_C=(1,-1,1,-1).
```

Thus

```text
[q^7 zeta^28]+[q^8 zeta^28]+[q^9 zeta^28]
```

in the sum over all 2,079 C4 markings counts antipodal alternating-cycle
incidences exactly. The verified lower is 52,812; an upper of 51,975 would
contradict it.

At `q^10`, `zeta^28` is still a valid Jacobi coefficient, but the frozen
inputs do not prove that `ell=4` isolates the same unit-coordinate pattern.
No norm-20 incidence interpretation is claimed here.

## 4. Fricke normalization

Let `Phi_K` be the sum over cycles of the scalar theta series marked by
`b_C`, and `Phi_L` the partner marked by `d_C`. Direct specialization of
the verified Poisson calculation gives in the rank-28 row:

```text
Phi_K(-1/(7tau),z/(7tau))
 = -7^8 tau^22 exp(20 pi i z^2/tau) Phi_L(tau,z).
```

With the normalized Jacobi-Fricke slash:

```text
Phi_K || W_7 = -7^(-3) Phi_L.
```

The index changes from 70 to 10. At `z=0`, this is the verified scalar
Fricke relation.

## 5. The 140 components reduce to 20, then 11

A scalar index-70 theta decomposition normally uses residues modulo 140.
But `div_K(b_C)=7`, so every Fourier exponent is divisible by seven. Only

```text
r=7s,  s mod 20
```

can occur. Moreover

```text
theta_(70,7s)(tau,z)=theta_(10,s)(7tau,7z).
```

Thus write

```text
Phi_K=sum_(s mod 20) H_s(tau) theta_(10,s)(7tau,7z),
Phi_L=sum_(t mod 20) G_t(tau) theta_(10,t)(tau,z).
```

The coefficient vectors `H` and `G` have weight `43/2`. Evenness in `z`
gives `H_s=H_(-s)` and reduces 20 components to 11 independent ones.

The standard unary-theta S transformation gives the exact finite Fourier
coupling

```text
sqrt(-i tau/20) sum_s exp(-pi i s t/10) H_s(-1/(7tau))
 = -7^8 tau^22 G_t(tau).
```

This is the proof-producing modular problem that replaces Wave 116's raw
four-variable index-lattice determinant `1,023,942,465`.

## 6. Exact truncated coefficient null

For index 70, coefficient support requires

```text
4*70*n-r^2>=0.
```

At `r=28`, the margins for `n=7,8,9,10` are

```text
1176, 1456, 1736, 2016.
```

So support excludes none of the target coefficients.

The script constructs an exact nonnegative symmetric coefficient table
through the target shells using the verified scalar formal control
`x7=5868,x8=x9=0`:

```text
c(7, 28)=52812,
c(7,-28)=52812,
c(7,  0)=12093948.
```

These sum to `2079*x7=12199572`; all coefficients are nonnegative integers
and respect Fourier divisibility, symmetry, and support. This is not a
Jacobi form or an all-orders Fricke-compatible vector. It proves only that
the elementary coefficient cone cannot supply the needed upper bound.

## 7. Exact frontier

The remaining task is sharply smaller but still open:

1. construct the weight-`43/2`, 20-component K/L Fricke module;
2. prove a coefficient truncation or valence/Sturm bound;
3. impose componentwise lattice positivity on both sides; and
4. derive an exact dual upper certificate at most 51,975.

No such basis or certificate is claimed in Wave 121. Rank 28, Conway-99,
and novelty remain `UNKNOWN`.
