# Wave 121 independent vector-theta and scalar-Jacobi verification

Date UTC: 2026-07-28.

Verdict: **VERIFIED_SCOPED**, conditional on the frozen verified Waves 66,
71, 80, 86, 97, 101, 112, and 116 inputs.

No mathematical correction was required.  Several evidence boundaries are
important: exact-value orbit sums do not imply componentwise equality,
formal theta prefixes are not lattices, and a truncated nonnegative Jacobi
coefficient table is not a Jacobi form.

## Preinspection freeze

The discovery package manifest has SHA-256

```text
ab3ede13ea60315885ac077cd8e0b3e7b124f34329d51e82fa2f4d08434cf803
```

All 15 discovery files were frozen by path, length, and SHA-256 before
derivation or code inspection.  The verifier checks those bytes on every
replay.

## Orthogonal types and exact-value orbits

The imported code theorem identifies

```text
D_L=L*/L=O^-(14,7).
```

For `K`, rank 44 gives Milgram phase `-1`.  In dimension 30 over `F7`,
the normalized Gauss phase is

```text
Legendre(det)*(-1)^15.
```

Hence the determinant Legendre sign is `+1`.  A split 30-space has sign
`(-1)^15=-1`, so

```text
D_K=K*/K=O^-(30,7).
```

For a minus space of dimension `2m`, independent exact arithmetic gives

```text
Q=0 including zero: 7^(2m-1)-6*7^(m-1),
Q=a != 0:           7^(2m-1)+7^(m-1), for each a.
```

The zero, nonzero-isotropic, and six exact nonzero-value counts sum to
`7^(2m)` in dimensions 14 and 30.

The verifier confirms that only full exact-value aggregates are justified.
No finite discriminant isometry is assumed to lift to a lattice
automorphism or graph automorphism.

## Two new aggregate coefficient families

For `z=sqrt(7)y in K`, the class `y+L` has exact quadratic value `n mod 7`
when `z` contributes to `x_n`.  At exponent `7m`, the zero class is the
scaled `L` contribution `y_m`.  Therefore the nonzero-isotropic
`D_L` aggregate is

```text
x_(7m)-y_m.
```

Likewise `K*=(1/sqrt(7))L` and
`Theta_(K*)(tau)=Theta_L(tau/7)`.  At integer exponent `n`, the total
isotropic coefficient is `y_(7n)` and its zero class contributes `x_n`.
Thus the nonzero-isotropic `D_K` aggregate is

```text
y_(7n)-x_n.
```

The six anisotropic exact-value aggregates are ordinary residue
dissections, so scalar coefficient nonnegativity already controls them.

## Exact q=14 scalar reconstruction through y77

The clean-room checker independently regenerates the 15-dimensional
`M_22(Gamma0(7))` product basis, its Fricke transform, the transfer

```text
Theta_L=-7^4(Theta_K|W_7),
```

and the seven-variable parameterization in `x7,...,x13`, with `x14`
eliminated by `y0=1`.

It imposes

```text
x7,...,x14 >= 0,
y1,...,y77 >= 0,
x7-y1 >= 0,
x14-y2 >= 0,
y_(7n)-x_n >= 0 for 1<=n<=11.
```

The two independently verified Wave 101 primal optimizers satisfy every
new inequality exactly.  Since the old exact dual certificates remain
valid, both optima are unchanged:

```text
x7+...+x10 >= 389888/57, parity bound 6842,
x7+...+x11 >= 4675706896/9307, parity bound 502388.
```

This is a complete finite null for those two strengthened objectives, not
a lattice realization.

## Restricted identities and controls

Under `x7=x8=x9=0`, exact coefficient comparison gives

```text
x10-2729216
 = 440363*y1+32536*y2+1715*y3+49*y4,
```

and

```text
x10+x11-4144144
 = (6/7)*x11+280574*y1+13377*y2+343*y3.
```

All right-side terms are nonnegative.  The first bound is attained by the
formal prefix

```text
(x7,...,x14)
=(0,0,0,2729216,9904496,64688008,374547488,1753425792).
```

Every checked `x`, `y1,...,y77`, and orbit difference for this control is
a nonnegative even integer.  The second equality also has an exact
rational attaining control, but its `y` coefficients have denominators
seven and 49.  The verifier confirms that no parity or integrality rounding
is justified there.

## Abstract short-code upper

If two K vectors of norm at most 22 have the same evaluation word, their
difference lies in `7K`.  A nonzero such vector has norm at least

```text
49*14=686,
```

whereas the triangle inequality gives at most

```text
(sqrt(22)+sqrt(22))^2=88.
```

Thus short-range evaluation is injective.  Norms 20 and 22 have code
self-dots five and two modulo seven.  Each exact anisotropic value has at
most

```text
7^30(7^13+7^6)
```

short vectors.  This is rigorous and far too large to contradict the
lower bounds.  The signed/Hamming compositions of these shells remain
`UNKNOWN_UNDER_FROZEN_INPUTS`.

## Primitive scalar C4 marking

For cyclic `epsilon=(1,-1,1,-1)`,

```text
d_C=sum epsilon_i u_i
```

lies in `M subset L` and has norm 20.  Evenness makes it primitive.
Its divisibility in `L` divides 20; if greater than one, primitivity would
produce a nontrivial prime-to-seven order in the 7-elementary group
`L*/L`.  Hence its divisibility is one.

The K marking

```text
b_C=sqrt(7)d_C
```

is primitive, has norm 140, divisibility seven, and scalar Jacobi index 70.
Its L Fricke partner has index 10.

For the frozen unit-coordinate shells of norms 14, 16, and 18,

```text
<sqrt(7)y,b_C>=7 ell_C,
ell_C=4 iff t_C=(1,-1,1,-1).
```

Thus the positive `r=28` coefficients through `q^9` count antipodal C4
incidences exactly.  The frozen Wave 121 scope does not give this
interpretation at `q^10`, and the verifier preserves that warning.

In the rank-28 row, Poisson summation gives

```text
Phi_K(-1/(7tau),z/(7tau))
 = -7^8 tau^22 exp(20 pi i z^2/tau) Phi_L(tau,z),
Phi_K||W_7=-7^-3 Phi_L.
```

## Twenty components, eleven after evenness

Index 70 normally has 140 theta residues.  Divisibility seven leaves only
`r=7s`, `s mod 20`, and exact expansion verifies

```text
theta_(70,7s)(tau,z)=theta_(10,s)(7tau,7z).
```

Evenness pairs `s` with `-s`, leaving 11 independent components.  The
coefficient vectors have weight `43/2`.

The verifier reconstructs the unary-theta phase symbolically:

```text
theta_(10,s)(-1/tau,z/tau)
 = sqrt(-i tau/20) exp(20 pi i z^2/tau)
   sum_t exp(-pi i s t/10) theta_(10,t)(tau,z).
```

The finite Fourier square is exactly 20 times residue negation.  Comparing
theta components gives the submitted K/L coupling with factor `-7^8`.

## Truncated null and exact boundary

Jacobi support permits `r=28` at `q^7,q^8,q^9,q^10`.  The submitted finite
table

```text
c(0,0)=2079,
c(7,-28)=52812,
c(7,0)=12093948,
c(7,28)=52812
```

is symmetric, nonnegative, integral, divisible-by-seven in `r`, obeys
support, and specializes to `2079*x7` for `x7=5868`.  It is not an
all-orders Fricke-compatible component vector or a Jacobi form.  It only
proves that elementary support and coefficient positivity do not close
the target.

## Post-independent Wave 124 comparison

After the canonical verifier result existed, shared marking, index,
divisibility, and coefficient claims were compared with sealed Wave 124.
They agree.  This is a consistency comparison, not evidence for either
package.  Wave 124 separately uses verified Wave 96 to extend the
coefficient interpretation through norm 20 and derives a C4 tight-frame
identity; neither extension is imported into this frozen Wave 121 verdict.

## Replay

```text
independent deterministic replay: PASS
independent tests:                12 passed
discovery main replay:            PASS
discovery scalar replay:          PASS
discovery tests:                  16 passed
post-independent comparisons:     13/13 passed
```

Final boundary:

```text
rank 30 excluded:     no
rank 28 excluded:     no
lattice constructed: no
graph constructed:   no
Conway-99:            UNKNOWN
literature novelty:   UNKNOWN
```
