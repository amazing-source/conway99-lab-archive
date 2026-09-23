# Wave 116 independent C4 Jacobi/theta verification

Date UTC: 2026-07-28.

Verdict: **VERIFIED_WITH_CLARIFICATIONS**, conditional on the frozen
verified Waves 66, 71, and 112 inputs.

The proposed change of mathematical space is sound: the four coordinates on
an induced four-cycle define a common matrix-index Jacobi theta sum, and a
degree-32 harmonic-theta reformulation is also exact on the three short
shells.  Neither formulation currently supplies an upper bound.

## Restricted projector

For a four-cycle in cyclic order, direct restriction of

```text
E_-4=(-A+3I+J/9)/7
```

gives

```text
E=E_-4[C]=(3I-H_C+J/9)/7
 =
[ 4/9   -8/63   1/63  -8/63 ]
[-8/63   4/9   -8/63   1/63 ]
[ 1/63  -8/63   4/9   -8/63 ]
[-8/63   1/63  -8/63   4/9  ].
```

The constant, alternating, and two zero-adjacency modes have eigenvalues

```text
13/63, 5/7, 3/7, 3/7,
```

so `E` is positive definite and

```text
det(E)=65/2401.
```

## Exact lattice-compatible markings

The naive marking is not merely unproved: the verified discriminant data
show that it is not lattice-compatible.  Indeed,

```text
K*=(1/sqrt(7))L,
[u_i]=alpha has order 9 in M*/M,
L/M=<3 alpha>.
```

Thus `u_i notin L`, so

```text
p_i=u_i/sqrt(7) notin K*.
```

Consequently `E/2` is not an ordinary lattice-Jacobi index.

The valid markings are

```text
a_i=3u_i/sqrt(7) in K*,
v_i=3u_i in L,
g_i=7a_i=3sqrt(7)u_i in K.
```

Their cycle Gram matrices are

```text
Gram(a)=9E,
G_L=Gram(v)=63E,
G_K=Gram(g)=441E=7G_L.
```

Independent exact arithmetic gives

```text
spec(G_L)={13,45,27,27}, det(G_L)=426465,
spec(G_K)={91,315,189,189}, det(G_K)=1023942465.
```

Modulo seven, the numerator of the `a_i` discriminant pairing has matrix

```text
[0 6 1 6]
[6 0 6 1]
[1 6 0 6]
[6 1 6 0],
```

of rank four and determinant four.  The four classes are therefore
independent and span a nondegenerate `(Z/7)^4` subgroup.  This verifies the
2,401-sector statement.  It does not identify or remove the orthogonal
complement in `K*/K`, so the small sector has not been proved to close as a
standalone scalar system.

## Common Jacobi sum

Every induced four-cycle has the same cyclic Gram `G_K`.  Therefore, after
choosing any cyclic labeling for each of the 2,079 cycles,

```text
Phi_K(tau,z)
 = sum_C sum_{x in K}
   q^((x,x)/2) exp(2*pi*i sum_j z_j<x,g_Cj>)
```

is a common weight-22, level-seven lattice Jacobi sum of matrix index
`G_K/2`.  Dihedral relabeling preserves that numerical index.  No graph
automorphism or cycle-orbit equivalence is used.

The normalizations are

```text
[q^0 z^0]Phi_K=2079,
Phi_K(tau,0)=2079 Theta_K(tau).
```

The number `1,023,942,465=det(G_K)` is the discriminant size of this raw
four-variable index lattice.  It is not a proved minimal basis dimension
for a useful optimization.

## Poisson and Fricke normalization

Let `q=44-r` denote the 7-primary discriminant length here, not the Fourier
variable.  Since `rank(K)=44`, `det(K)=7^(44-q)`, and `i^(-22)=-1`, Poisson
summation independently gives

```text
Phi_K(-1/(7tau),z/(7tau))
 = -7^(q/2) tau^22
   exp(pi*i*z^T G_L z/tau) Phi_L(tau,z).
```

After the normalized weight-22 Jacobi-Fricke slash,

```text
Phi_K || W_7 = -7^(q/2-11) Phi_L.
```

At `z=0`, solving for the partner recovers the independently verified scalar
normalization

```text
Theta_L=-7^(11-q/2)(Theta_K|_22 W_7).
```

The elliptic index changes from `G_K/2` to `G_L/2`; this is a `K/L` pair,
not a positivity involution within one fixed-index cone.

## Fourier coefficient and exact threshold

For norm 14, 16, or 18, write `t_i` for the verified integral graph
coordinate.  The valid `K` marking satisfies

```text
<x,g_i>=21t_i.
```

Thus the coefficients at Fourier pattern

```text
21(1,-1,1,-1)
```

select the alternating coordinate pattern.  For each vector/cycle incidence,
exactly one member of its antipodal pair has the selected sign.  Therefore

```text
c(7)+c(8)+c(9)       = antipodal C4 incidence,
2(c(7)+c(8)+c(9))    = oriented C4 incidence.
```

The Wave 112 lower count independently reduces to

```text
5868*18=105624 oriented incidences,
105624/2=52812 antipodal incidences.
```

A universal bound of 25 antipodal extensions per cycle would give

```text
2079*25=51975,
52812-51975=837,
```

and would contradict the rank-28 lower count.  The cap is not proved.

The exact projected Fourier norm is

```text
(21 epsilon)^T G_K^(-1)(21 epsilon)=28/5.
```

The three ordinary support margins `2n-28/5` are `42/5,52/5,62/5`.
Consequently the basic Jacobi support condition permits all three target
coefficients and provides no upper bound by itself.

## Degree-32 harmonic interpolation

On the target shells, `sum_i t_i^2<=18` and every `t_i` is integral, so each
coordinate lies in `{-4,-3,...,4}`.  The cardinal polynomial

```text
delta_s(T)=product_{m=-4,m!=s}^4 (T-m)/(s-m)
```

has degree eight and is exactly the indicator of `T=s` on this domain.
The product for the four signs `(1,-1,1,-1)` therefore has total degree 32
and exactly selects the desired pattern on norms 14, 16, and 18.

Harmonic decomposition turns the resulting shell sums into finitely many
weighted theta series of harmonic degrees at most 32.  This is an exact
reformulation, but weighted theta coefficients can be signed.  No
coefficientwise-positive upper cone, exact moment certificate, or
positive-semidefinite certificate has been produced.

## Replay and boundary

The supplied discovery manifest hash and all three prerequisite verifier
manifest hashes match their frozen values.  The independent implementation
does not import discovery code.

```text
independent deterministic replay: PASS
independent tests:                11 passed
discovery deterministic replay:   PASS
discovery tests:                   8 passed
free physical memory:             56.6%
```

No Jacobi basis, Jacobi Sturm bound, bounded exact optimization, or dual
upper certificate is present.  Hence:

```text
new upper bound:     not proved
rank 28 excluded:    no
Conway-99:           UNKNOWN
literature novelty:  UNKNOWN
```
