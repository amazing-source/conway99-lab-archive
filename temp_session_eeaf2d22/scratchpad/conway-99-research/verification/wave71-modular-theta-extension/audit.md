# Wave 71 independent modular-theta audit

Date UTC: 2026-07-27T23:31:32Z

Verdict: **VERIFIED_WITH_CORRECTION**.

The conditional modular-theta theorem passes.  One discovery boundary is
strictly sharpened: the norm-18 case with two same-sign edges per sign class
is impossible, so only zero or one such edge survives.

Everything here is conditional on a hypothetical
`srg(99,14,1,2)` and the independently verified Wave 66 package.  It does
not construct the graph or a lattice realization.  Conway-99 and literature
novelty remain `UNKNOWN`.

## Exact conditional result

Write

```text
S=2A-J+I,  r=rank_F7(S),  q=44-r.
```

Wave 66 gives

```text
q in {2,4,6,8,10,12,14,16},
M*/M = Z/9 direct_sum (Z/7)^q,
min(M*) >= 2.
```

The 99 centered frame vectors have one discriminant class
`alpha=[u_i]`.  Directly from their Gram matrix,

```text
q_M(alpha)=14/9=5/9 mod Z,
b_M(alpha,alpha)=28/9=1/9 mod Z.
```

Thus `alpha` has order nine and generates the 3-primary factor.  The unique
order-three subgroup `H=<3 alpha>` is isotropic and is its own orthogonal
complement inside `Z/9`.  The corresponding even overlattice

```text
L=M+Z(3u_0)
```

has index three and

```text
L*/L = (Z/7)^q,  det(L)=7^q,  level(L)=7.
```

It retains the marked 99-vector frame `3u_i`, with norm 28, inner product
-8 on graph edges and 1 on graph nonedges, zero sum, and frame operator
`63I`.

The scaled dual

```text
K=sqrt(7)L*
```

is an even positive-definite level-seven lattice with

```text
K*/K = (Z/7)^(44-q),  det(K)=7^(44-q),  min(K)>=14.
```

Both 7-primary lengths are positive, so the levels are exactly seven rather
than merely divisors of seven.

## Skoruppa theorem and normalization

The primary import is the Main Theorem of Nils-Peter Skoruppa,
*Reduction mod l of Theta Series of Level l^n*,
[arXiv:0807.4694v1](https://arxiv.org/abs/0807.4694).

Its hypotheses are met: `K` is positive definite, even, integral, and has
prime-power level with prime `7>=5`.  In Skoruppa's normalization,

```text
Theta_K = sum_x q^((x,x)/2),
```

and `e(K)` is the sum of the Gram elementary divisors, not their valuation
sum.  The Smith factors of `K` are

```text
1^q, 7^(44-q),
```

so

```text
e(K)=q+7(44-q)=308-6q,
weight=e(K)/2=154-3q.
```

The theorem therefore supplies an integral level-one modular form congruent
coefficientwise to `Theta_K` modulo seven.

## Independent finite-field calculation

The verifier independently generated `E4` and `E6` from divisor sums through
`q^14`, used every monomial `E4^a E6^b` of the exact weight, and row-reduced
over `F_7`.  Since every nonconstant coefficient of `E6` is divisible by
seven, `E6=1 mod 7`, but no basis monomial was omitted.

The exact rows are:

```text
q:                         2   4   6   8  10  12  14  16
weight:                  148 142 136 130 124 118 112 106
largest forced zero gap:  13  13  13  13  13  13  13   8
next coefficient mod 7:    6   6   6   6   6   6   6   2
min(K) upper bound:        28  28  28  28  28  28  28  18
```

After only the mandatory coefficients `q^1,...,q^6` vanish, the `q=16`
affine solution space gives the unique relation

```text
N14+N16+N18 = 2 mod 7.
```

The involution `x -> -x` makes every nonzero theta coefficient even, hence

```text
N14+N16+N18 = 2 mod 14.
```

No relation among these three coefficients is forced for `q<=14`.

## Exact short-vector dictionary

For `y in M*`, use the Wave 66 coordinates

```text
t_i=<y,u_i>=n_i+b/9,
sum n_i=-11b,
(A+4I)n=-2b*1,
7(y,y)=sum t_i^2.
```

Membership in `L*` forces `3|b`.  The two nonintegral classes `b=3,6 mod 9`
have unconstrained balanced energy 22, so they cannot occur at energy
14, 16, or 18.  The frame identity then gives a norm-preserving bijection,
through norm 18, between vectors of `K` and integer vectors

```text
t in Z^99,  At=-4t,  sum t_i=0.
```

Modulo two, the odd support of such a vector is a nonzero word of
`ker_F2(A)`, hence has size at least eight.  Independent exhaustive
enumeration of the magnitude profiles, sign distributions, and aggregate
signed edge-count matrices eliminates every mixed-magnitude profile.  The
only surviving magnitudes are:

```text
norm 14: seven +1 and seven -1;
norm 16: eight +1 and eight -1;
norm 18: nine +1 and nine -1.
```

For a unit signed support with sign-class size `s`, let `h` be the number of
same-sign edges in each class.  The eigenvector equations give

```text
e(P,N)=2h+4s,
e(P union N)=4s+4h.
```

The restricted-eigenvalue edge bound and the `lambda=1`, `mu=2` common
neighbor counts then give:

- Norm 14: a 4-regular bipartite graph on `7+7`, necessarily the incidence
  graph of the complementary Fano `2-(7,4,2)` design.  The 85 outside
  vertices split as 70 meeting one point of each side and 15 meeting none.
  The latter 15 are independent, and their neighborhoods form a
  `2-(15,3,2)` design on 70 blocks.
- Norm 16: a 4-regular bipartite graph on `8+8`.  The only spectral
  alternative, one same-sign edge on each side, makes its endpoints have
  two common opposite-side neighbors, contradicting `lambda=1`.
- Norm 18: either a 4-regular bipartite graph on `9+9`, or exactly one
  same-sign edge in each side.  In the latter case the four endpoints have
  cross-degree five, all other support vertices have cross-degree four, and
  each same-sign edge has exactly one opposite-side common neighbor.

## Recorded correction: the norm-18 h=2 case

Discovery retains `h=2` after proving that the two same-sign edges on each
side must be disjoint and that opposite-side common-neighbor counts saturate
the `lambda/mu` capacity.  Saturation yields an immediate final
contradiction.

Indeed, on one sign side, the opposite side has four vertices of cross
degree five and five of cross degree four.  It contributes

```text
4*C(5,2)+5*C(4,2)=70
```

common-neighbor incidences.  The two adjacent pairs and 34 nonadjacent pairs
on the first side permit exactly

```text
2*lambda+34*mu=2+68=70.
```

Thus no outside vertex can meet two vertices of that sign.  But the nine
vertices have 126 total degree incidences and 44 incidences inside the
18-point support, leaving

```text
126-44=82
```

incidences to only `99-18=81` outside vertices.  At most one incidence per
outside vertex is possible, a contradiction.  Therefore

```text
norm-18 surviving h values = {0,1},
```

not `{0,1,2}`.

## Independence and replay

All 14 discovery files, including two bytecode files, were frozen by path,
length, and SHA-256 before inspection.  Post-inspection replay left every
byte unchanged.  The discovery manifest and canonical JSON replay pass.

`independent_verify.py` neither imports nor executes discovery code.  It
reconstructs the elementary-divisor weights, exact `F_7` systems, magnitude
profiles, aggregate edge equations, and signed-support counts independently.
Only after its canonical result existed were discovery files read.

Results:

```text
independent deterministic replay: PASS
independent tests:                10 passed
discovery canonical replay:       PASS
discovery tests:                   7 passed
mathematical comparison:          13 fields, 1 correction
free physical memory:             above 57%
```

## Boundary

The correction narrows the forced norm-18 structures but does not exclude
all norm-14, norm-16, or norm-18 alternatives.  No graph, lattice
realization, or nonexistence certificate is produced.  The result is a
verified conditional reduction, not a Conway-99 solution.  Conway-99 and
novelty remain `UNKNOWN`.
