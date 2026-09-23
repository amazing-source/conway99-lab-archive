# The alternating C4 vector and an index-70/index-10 Jacobi pair

Claim label: `DERIVED_AND_NULL_BOUNDARY`; independent verification required.

Everything below is conditional on a hypothetical
`srg(99,14,1,2)` and the frozen verified Waves 71, 96, 112, and 116.

## 1. A primitive norm-20 lattice vector

Fix an induced four-cycle in cyclic order and put

```text
epsilon=(1,-1,1,-1),
d_C=sum_i epsilon_i u_i.
```

Since `sum epsilon_i=0`, this is an integral sum of differences
`u_i-u_j`; hence

```text
d_C in M subset L.
```

The cycle Gram of the `u_i` is

```text
3I-H_C+J/9.
```

The alternating vector is a `-2` eigenvector of `H_C` and is killed by
`J`.  Therefore

```text
||d_C||^2 = epsilon^T(3I-H_C+J/9)epsilon
           = 5*||epsilon||^2
           = 20.                                      (1)
```

The vector is primitive in `L`.  If `d_C=k*l` with `k>=2`, then evenness
of `L` would give

```text
20=k^2*(a positive even integer),
```

which is impossible.

Now define

```text
b_C=sqrt(7)d_C.
```

Since `L subset L*`, this vector belongs to `K=sqrt(7)L*`, has norm 140,
and has Jacobi index 70.  For `x=sqrt(7)y in K`,

```text
<x,b_C>=7<y,d_C>.
```

Primitivity of `d_C` means the gcd of `<y,d_C>` over `y in L*` is one.
Thus `b_C` has exact divisibility seven in `K`, not divisibility one.

## 2. The exact short-shell coefficient

For the verified integral graph coordinate

```text
t_i=<y,u_i>,
ell_C(t)=sum_i epsilon_i t_i,
```

the K Fourier exponent is

```text
r=<x,b_C>=7 ell_C(t).                              (2)
```

Waves 71 and 96 prove that every graph vector of norm 14, 16, 18, or 20
has only coordinates `0,+1,-1`, with equally many plus and minus signs.
Consequently `ell_C(t)<=4`, and equality holds exactly when the four cycle
coordinates are

```text
(1,-1,1,-1).
```

Thus, in the aggregate Jacobi sum

```text
Psi_K(tau,z)
 = sum_C sum_{x in K}
   q^((x,x)/2) exp(2*pi*i*z<x,b_C>),
```

the four coefficients

```text
c_K(7,28), c_K(8,28), c_K(9,28), c_K(10,28)
```

exactly count antipodal alternating-C4 incidences on the norm-14 through
norm-20 shells.  The coefficient at `r=-28` counts the antipodal
orientation, so oriented incidence is twice the positive coefficient.

For rank 28, Wave 112 gives

```text
c_K(7,28)+c_K(8,28)+c_K(9,28) >= 52812.
```

A cap of 25 antipodal extensions per cycle would give only
`2079*25=51975`, a gap of 837.  For rank 30, Wave 96 similarly gives

```text
sum_{n=7}^10 c_K(n,28) >= 51315,
```

where a cap of 24 would give `2079*24=49896`, a gap of 1,419.  Neither cap
is proved here.

## 3. The C4 vectors are a tight frame

The outer product `d_C d_C^T` is independent of reversing the chosen
alternating orientation.  Let `S` be the sum of the corresponding
99-coordinate sign-vector outer products.

- A vertex lies in 84 induced C4s, one for every nonneighbor placed
  opposite it.
- An edge lies in 12 induced C4s.  Starting with an exclusive neighbor of
  one endpoint, the `mu=2` condition supplies one other common neighbor;
  `lambda=1` keeps that vertex exclusive.
- A nonedge is the diagonal of one induced C4.

Signs agree on a diagonal and disagree on a cycle edge.  Therefore

```text
S = 84I - 12A + (J-I-A)
  = 83I - 13A + J.                               (3)
```

On the `-4` eigenspace this acts by

```text
83-13(-4)=135.
```

Wave 71 gives `sum_i u_i u_i^T=7I`.  Combining this with (3),

```text
sum_C d_C d_C^T = 945 I.                         (4)
```

Equivalently, for an integer `-4` eigenvector `t`,

```text
sum_C ell_C(t)^2 = 135 sum_i t_i^2.              (5)
```

If `a_K(n)` counts K vectors of norm `2n`, equations (2) and (5) give the
exact second Jacobi moment

```text
sum_r r^2 c_K(n,r) = 13230*n*a_K(n).             (6)
```

For the L partner the corresponding formula is

```text
sum_r r^2 c_L(n,r) = 1890*n*a_L(n).              (7)
```

These are genuine new linear constraints, but the second moment alone is
too weak to prove the required incidence upper bound.

## 4. Fricke changes index 70 to index 10

Define the L partner by marking each summand with `d_C`:

```text
Psi_L(tau,z)
 = sum_C sum_{x in L}
   q^((x,x)/2) exp(2*pi*i*z<x,d_C>).
```

It has weight 22 and index 10.  Direct Poisson summation gives

```text
Psi_K(-1/(7tau),z/(7tau))
 = -7^(qdisc/2) tau^22 exp(20*pi*i*z^2/tau) Psi_L(tau,z).   (8)
```

Here `qdisc` is the even 7-primary discriminant length, not the Fourier
variable.  Both lattice discriminants are even powers of seven, so the
Dirichlet character is trivial.

Equation (8) is an index-70/index-10 pair.  It is not a self-map of one
fixed Jacobi index.  Exact divisibility seven also means all K exponents
`r` are multiples of seven.  Writing `r=7s`, elliptic translation sends

```text
s -> s+20 lambda,
n -> n+7(s lambda+10 lambda^2).
```

Thus `n mod 7` is preserved.  The four target exponents `n=7,8,9,10`
occupy four different residue sectors; only `n=7` is in the simplest
oldform sector.

There is one useful forced L coefficient:

```text
c_L(10,20)=2079.                                  (9)
```

For a fixed cycle, a norm-20 vector `x` with `<x,d_C>=20` must equal
`d_C` by equality in Cauchy's inequality.  This contributes exactly once
per cycle.  Equation (9) is also the elliptic translate of
`c_L(0,0)=2079`.

## 5. An exact full-level basis and a hostile oldform direction

Use the standard cited structure theorem

```text
J_even,*^weak(SL2Z) = C[E4,E6,A,B],
A=phi_-2,1, B=phi_0,1.
```

At weight 22 and index 10 there are 34 monomials

```text
E4^a E6^b A^c B^d,
4a+6b-2c=22, c+d=10.
```

`exact_check.py` constructs these series through `q^10` over the rationals
and kills every negative-discriminant coefficient.  This contains every
reduced polar orbit: after elliptic reduction `|r|<=10`, so
`4*10*n-r^2<0` implies `n<5/2`.  The result is an explicit basis with

```text
dim J_22,10(SL2Z)       = 18,
dim J_22,10^cusp(SL2Z)  = 17.                    (10)
```

The basis coordinates in the 34 monomials are recorded in
`exact-results.json`.  This is a basis of a full-level subspace of the
needed level-seven space, not a basis of all
`J_22,10(Gamma0(7))`.

For each `s=1,...,5`, the checker finds an explicit cusp form

```text
psi_s in A^s J^weak
```

whose `q^1 zeta^4` coefficient is nonzero.  Its Fricke-compatible old lift

```text
delta Psi_L = psi_s(tau,z),
delta Psi_K = -7^(qdisc/2) psi_s(7tau,7z)          (11)
```

preserves both constant terms.  Since `A` has a double zero at `z=0`,
`s=1` preserves the scalar theta specializations, `s=2` also preserves the
second moment, and `s=5` preserves every Taylor moment through order eight.
Nevertheless (11) changes `c_K(7,28)`.

This is a hostile null control, not a graph deformation.  Its coefficients
are signed, and it introduces `q^7` K patterns corresponding to
`|ell|=6`, which the verified unit norm-14 shell forbids.  Therefore it
proves only:

> Modularity, Fricke, constants, scalar specialization, and low Taylor
> moments do not bound the target without positivity and graph-specific
> support zeros.

It does not prove that the full positive graph-compatible cone is
unbounded.

## 6. The smaller five-moment model

On all four verified unit shells, `ell_C` lies in
`{-4,-3,...,4}`.  Hence

```text
P(ell)
 = product_{j=0}^3 (ell^2-j^2)/(16-j^2)
```

is exactly one at `|ell|=4` and zero at the other possible values.  This is
an even degree-eight polynomial.  Summing `P(ell_C)` over vectors and
cycles gives oriented target incidence exactly.

The five even Taylor moments correspond to weights

```text
22, 24, 26, 28, 30.
```

This is smaller than constructing the full level-seven index-10 Jacobi
basis.  A proof-producing next model should combine:

1. these five K/L Fricke-paired moment series;
2. the exact second moments (6)-(7);
3. every short-shell Fourier support zero forced by the unit profiles;
4. coefficient nonnegativity and integrality; and
5. an exact dual bound on the incidence polynomial.

Only if this quotient remains too weak is the full
`J_22,10(Gamma0(7))` theta-decomposition basis justified.

## Boundary

No Jacobi upper certificate or rank exclusion is produced.  The
whole-level-seven basis, positivity cone, and exact dual remain open.
Conway-99 and literature novelty remain `UNKNOWN`.
