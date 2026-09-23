# Wave 58 cross-incidence rank synthesis

Everything below is conditional on the prism-free `n3=4158` endpoint and an
arbitrary fixed graph triangle. No automorphism of the triangle, its fibres,
or a completed graph is assumed.

Write `X=X0 union X1 union X2`, with 12 vertices in each fibre, and let `Y`
be the remaining 60 vertices. Let `B` be the `36 x 60` X-to-Y adjacency
matrix, `A_X` the cubic graph on X, and `A_Y` the 8-regular graph on Y.
Each X vertex has ten Y neighbors and each Y vertex has two neighbors in each
X fibre, hence six X neighbors.

To avoid Wave 57's overloaded notation, this package writes

- `kappa` for the number of connected components of `A_X`;
- `q=C4(X)` for the number of four-cycles in `A_X`;
- `a=mult_Y(3)` and `b=mult_Y(-4)`.

## 1. The two Gram identities

For distinct `y,z in Y`, `(B^T B)_{yz}` is their number of common neighbors
in X. If they are adjacent, their unique common graph neighbor is split
between X and Y, so this number is

```text
1-(A_Y^2)_{yz}.
```

If they are nonadjacent, the corresponding number is

```text
2-(A_Y^2)_{yz}.
```

The diagonal is six. These three cases are exactly

```text
B^T B = 12I-A_Y+2J-A_Y^2.                       (1)
```

For `x,x' in X`, the fixed triangle contributes a common neighbor precisely
when the two vertices lie in the same fibre. The four distinct-pair cases
are:

| location/relation | common Y neighbors |
|---|---:|
| same fibre, adjacent | `0` |
| different fibres, adjacent | `1` |
| same fibre, nonadjacent | `1-(A_X^2)_{xx'}` |
| different fibres, nonadjacent | `2-(A_X^2)_{xx'}` |

The diagonal is ten. Therefore, with
`D=blockdiag(J12,J12,J12)`,

```text
B B^T = 12I-A_X+2J-D-A_X^2.                     (2)
```

These are the already verified Wave 36 block identities, rederived here
entrywise.

## 2. Kernel and rank

Split `R^36` into the three-dimensional fibre-indicator space `F` and its
33-dimensional orthogonal complement `W`. The quotient of `A_X` on `F` is
`J3`: the total constant vector has eigenvalue three, while the two
fibre-constant total-sum-zero vectors have eigenvalue zero.

On those two sum-zero vectors, equation (2) vanishes: `J` vanishes,
`D=12I`, and `A_X=0`. On `W`, both `J` and `D` vanish, and (2) factors as

```text
B B^T = (3I-A_X)(4I+A_X).                        (3)
```

Because `A_X` is cubic and symmetric, every eigenvalue lies in `[-3,3]`.
Thus `-4` cannot occur, and the only zero of (3) comes from eigenvalue three.
If `A_X` has `kappa` components, eigenvalue three has total multiplicity
`kappa`. One copy is the total constant vector in `F`, leaving `kappa-1`
copies in `W`. Consequently

```text
ker(B^T)
 = (two fibre-constant sum-zero vectors)
   direct-sum
   (the eigenvalue-3 space of A_X in W),

dim ker(B^T)=2+(kappa-1)=kappa+1,
rank(B)=35-kappa.                                 (4)
```

This is prior verified Wave 36 content, not a new Wave 58 identity.

The right kernel has dimension

```text
dim ker(B)=60-rank(B)=25+kappa.
```

If `Bv=0`, then `v` is orthogonal to constants because
`B^T 1_X=6 1_Y`. Equation (1) becomes

```text
(A_Y^2+A_Y-12I)v=0.
```

Hence `ker(B)` is the sum of the `3`- and `-4`-eigenspaces of `A_Y`, so

```text
a+b=25+kappa.                                    (5)
```

The trace on `im(B^T)` is `-26+4kappa`: constants contribute eight, and the
remaining transferred eigenvalues are `-1-lambda` for the nonkernel
eigenvalues `lambda` of `A_X`. Since `tr(A_Y)=0`, the kernel trace is
`26-4kappa`, giving

```text
3a-4b=26-4kappa.                                 (6)
```

Solving (5)-(6) yields the prior Wave 36 formulas

```text
a=18,   b=7+kappa.                               (7)
```

## 3. Component balance and the Wave 57 rows

Each cross-fibre perfect matching maps a component's part in one fibre
bijectively to its parts in the other fibres. A component therefore contains
`m` vertices in each fibre and has size `3m`.

For a component indicator `u` and
`z_y=|N(y) intersect component|`, equation (2), the row degree ten, and
Cauchy equality give

```text
sum_y z_y=30m,
sum_y z_y^2=15m^2,
z_y=m/2 for every y.
```

Thus `m` is even. The verified Wave 36 `m=2` census leaves only `K3,3`,
which has a nonedge with three common neighbors and violates `mu=2`. The
complete partitions of the 12 per-fibre units are therefore

```text
[12], [4,8], [6,6], [4,4,4],
```

so `kappa` is 1, 2, or 3. Equation (7) collapses Wave 57's 18 multiplicity
rows to exactly

| `a` | `b` | `kappa` | component units |
|---:|---:|---:|---|
| 18 | 8 | 1 | `[12]` |
| 18 | 9 | 2 | `[4,8]` or `[6,6]` |
| 18 | 10 | 3 | `[4,4,4]` |

All three had Wave 57 fourth-moment interval `0<=q<=89`; none is eliminated
by that ledger.

## 4. Four-cycle bounds

Every vertex of the cubic triangle-free `A_X` has three unordered neighbor
pairs, giving 108 wedges. Each neighbor pair is nonadjacent. In the ambient
SRG it has exactly two common neighbors; one is the wedge center, leaving at
most one other center. Thus each wedge lies in at most one four-cycle. Every
four-cycle has four wedges, so

```text
4q <= 36*binom(3,2)=108,
q <= 27.                                          (8)
```

This improves Wave 57's moment-localizer ceiling 89 without excluding any
surviving multiplicity row.

For finer component information, coordinate relabeling fixes the internal
matching in fibre zero and both cross matchings from fibre zero. The remaining
data for a component with `m` points per fibre are two perfect matchings and
one cross-fibre permutation. This is a complete labelled normalization, not
an assumed graph automorphism.

The exact censuses impose connectedness, cubicity, triangle-freeness, and
maximum A_X-nonedge codegree two:

| `m` | raw normalized configurations | accepted | possible component `C4` |
|---:|---:|---:|---|
| 4 | 216 | 50 | `{2,4,6}` |
| 6 | 162,000 | 34,640 | `{0,1,2,3,4,5,6,7,9}` |

Consequences:

- `kappa=1`: `0<=q<=27`;
- `kappa=2`, partition `[6,6]`:
  `q in {0,1,...,16,18}`;
- `kappa=2`, partition `[4,8]`: the `m=4` component gives 2, 4, or 6
  cycles, while the 24-vertex component has at most 18 by the wedge bound,
  so `2<=q<=24`;
- overall `kappa=2`: `0<=q<=24`;
- `kappa=3`: summing three values from `{2,4,6}` gives exactly

```text
q in {6,8,10,12,14,16,18}.                       (9)
```

## 5. Positive scoped controls

The controls here are deliberately separated; none constructs a simultaneous
`B` or `A_Y`.

- `kappa=1`: the verified Wave 36 restricted core is connected, has `q=0`,
  and has required Gram rank 34. Wave 57 has its `(a,b,q)=(18,8,0)` scalar
  control.
- `kappa=2`: two enumerated `m=6`, `q=0` components give a 36-vertex cubic
  triangle-free A_X with components `[18,18]`. Wave 57 has its
  `(18,9,0)` scalar control.
- `kappa=3`: three enumerated `m=4`, `q=4` components give components
  `[12,12,12]` and total `q=12`. The integer residual roots
  `(-3,-2,-1,0,1,2)` with multiplicities

```text
(5,6,8,1,9,2)
```

  exactly match the required residual power sums through degree four for
  `(a,b,q)=(18,10,12)`.

Thus component structure plus Wave 57 scalar moments still leaves all three
rows alive.

## 6. Restricted Wave 40 replay

The checker independently replays all `2^18=262,144` endpoint-pairing masks
over the canonical verified rank-11 all-`222` quotient. Exactly 37,378 masks
are triangle-free. Every one has component sizes `[12,24]`, hence
`kappa=2`, and all satisfy the A_X nonedge-codegree cap. Their four-cycle
distribution is supported on

```text
{4,5,6,7,8,9,10,11,12,14}.
```

This is a positive restricted realization of the `kappa=2` local lane. It
does not exclude `kappa=1` or `kappa=3`: the census uses one canonical
rank-11 quotient and the joint Wave 40 assumptions `all edge types 222` and
`r3=12`, and it does not enumerate all endpoint cores or construct the 60
columns of B.

## 7. Conclusion

Wave 58 supplies a useful synthesis, not a contradiction:

```text
Wave 57 multiplicity rows: 18 -> 3
universal C4(X) ceiling:    89 -> 27
kappa=2 ceiling:            24
kappa=3 exact C4(X) set:    {6,8,10,12,14,16,18}
```

The rank and multiplicity formulas are prior verified Wave 36 results.
Separate exact controls survive for all three component counts. The
prism-free endpoint and Conway-99 remain `UNKNOWN`.
