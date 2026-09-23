# Independent hostile-control audit

## Verdict

`VERIFIED_RELAXATION_BOUNDARY`.

The proof-B rational control satisfies every stated constraint through
complete total degree six and the quadratic three-point level. It first fails
at complete degree seven. This is a boundary result for the relaxation, not a
linear-code or graph existence result.

## 1. Integrity and separation

The proof report, discovery checker, and six direct mathematical inputs are
frozen by exact SHA-256. The clean-room checker does not import or execute the
discovery checker. The discovery implementation was compared only after the
independent transforms and Gram counts had been reconstructed.

## 2. Rational masses and the marked family

All 17 displayed typed masses are strictly positive exact fractions. Their
type totals are

```text
singular:   29524
norm plus:  29646
norm minus: 29403
total:      88573=(3^11-1)/2.
```

The singular cell `(36,162)` has mass exactly 231. It therefore represents
231 projective scalar pairs of primal weight 198. It is not the separate
family of 99 dual weight-seven star pairs.

For a scalar pair `(a,b)`, direct evaluation of the six complete moment
columns gives

```text
sum t = 88573
K10   = -231
K20   = -26565
K11   = -53130
K21   = -6083385
K30   = -2027795.
```

These exactly cancel the zero-word terms through complete strength three.

## 3. Ordinary MacWilliams transform

Each scalar-pair mass contributes two primal words of weight `a+b`; the zero
word contributes one. The primal total is exactly `3^11=177147`.

The verifier independently evaluates all 232 ternary Krawtchouk rows:

```text
B0=1
B1=B2=B3=0
B_j>=0 and B_j>=A_j for every 0<=j<=231.
```

The relevant exact values are

```text
B4 = 126079749915623/131414760
B4+...+B9 = 721437869830147204193861/3066344400.
```

Both are far above the verified lower bound 18018, so the ordinary
relaxation supplies no contradiction.

## 4. Complete ternary transform

The clean-room transform works in the exact cyclotomic ring

```text
Z[omega]/(omega^2+omega+1).
```

For each scalar pair it expands

```text
(1+u+v)^(231-a-b)
(1+omega*u+omega^2*v)^a
(1+omega^2*u+omega*v)^b
```

only through total degree seven. Swapping `(a,b)` is cyclotomic conjugation;
the pair contribution is its exact trace. No floating arithmetic is used.

All complete coefficients through total degree six are nonnegative. At degree
four the row is

```text
(B04,B13,B22,B31,B40)
=(0,0,126079749915623/131414760,0,0).
```

Degrees five and six are strictly positive. At degree seven exactly the two
edge cells are negative:

```text
B70=B07=-10151603437954385741/508426957500.
```

This is the precise stopping point of this sparse control.

## 5. Quadratic point types

The verifier independently enumerates the 88,573 projective representatives
of

```text
Q(x)=x0^2+x1*y1+...+x5*y5
```

and obtains the class sizes

```text
(singular,norm plus,norm minus)=(29524,29646,29403).
```

Canonical singular representatives give the complement counts:

```text
one point:       (9841,9963,9720)
orthogonal pair: (3280,3402,3159)
nonorthogonal:   (3280,3321,3240).
```

Five explicit singular triples independently reproduce:

```text
three orthogonal pairs: (1093,1215,972)
two orthogonal pairs:   (1093,1134,1053)
one orthogonal pair:    (1093,1134,1053)
no orthogonal, plus:    (1066,1107,1107)
no orthogonal, minus:   (1120,1080,1080).
```

The two no-orthogonal Gram representatives have determinants `2` and `1`
modulo three, so the determinant split is genuine.

## 6. Typed moments and triple census

Using `b=231-a-b` for each mass, the exact factorial moments are:

```text
singular:   29524,2273271,87133200,2233980128
norm plus:  29646,2301453,88521741,2242872288
norm minus: 29403,2245320,85771224,2174315184.
```

The first two nontrivial moments agree with the one- and two-point complement
counts. The third moments sum to

```text
6651167600=binom(231,3)*3280.
```

The proposed triple census is integral and nonnegative:

```text
three orthogonal pairs: 38192
two orthogonal pairs:       0
one orthogonal pair:    731808
no orthogonal, plus:    302968
no orthogonal, minus:   954827.
```

It has total `binom(231,3)=2027795`, orthogonal-pair incidence 846384,
wedge incidence 114576, and reproduces all three typed third moments.

These equations certify a moment census only. They do not show that any
231-point configuration realizes it.

## Boundary

The frozen constraints through complete degree six and quadratic degree three
cannot upper-bound `B4+...+B9` below 18018. The specific sparse control is
rejected at complete degree seven. No degree-nine float calculation was used.
No code, point set, endpoint graph, rank-11 exclusion, Conway-99 result, or
novelty claim follows.
