# Wave 36 proof A: simultaneous block compatibility

```yaml
role: proof_a
date_utc: 2026-07-26T22:55:22Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: DERIVED
scope: "Conditional endpoint n3=4158: general one-triangle 60-block compatibility, component balance, and the published restricted core"
inputs:
  - "attempts/wave36-block-compatibility/input-freeze.sha256"
method: "Exact SRG block algebra, component Gram moments, spectral transfer, and exhaustive enumeration of the 60^3 individual block types in the Wave 35 restricted core"
command:
  - "python -B attempts/wave36-block-compatibility/exact_check.py --verify attempts/wave36-block-compatibility/exact-results.json"
  - "python -B -m unittest discover -s attempts/wave36-block-compatibility -p \"test_*.py\" -v"
outputs:
  - "attempts/wave36-block-compatibility/exact-results.json | sha256 adab814da773e5a4ce2b98b4b8aa20027dbec9d93d446d3e1e85adaa899339a9"
limitations: "No simultaneous 60-block design, compatible 60-vertex graph H, endpoint exclusion, or upper-bound improvement is obtained. The target remains UNKNOWN."
```

## 1. Frozen setup

Fix a graph triangle `T`.  At the prism-free endpoint the remaining vertices
split as

```text
T | X | Y = 3 | 36 | 60.
```

Write `R` for the `36 x 3` fibre-indicator matrix, `A_X` for the cubic
triangle-free graph on `X`, `B` for the `X-Y` incidence matrix, and `H` for
the graph induced by `Y`.  In this order the full adjacency matrix would be

```text
      [ J_3-I   R^T    0 ]
A  =  [   R     A_X    B ].
      [   0     B^T    H ]
```

Every column of `B` has two ones in each of the three twelve-point fibres.
Every row has ten ones.  The Wave 35 report used the `X-X` block of the SRG
equation.  This wave adds the missing `X-Y` and `Y-Y` blocks.

## 2. All three exact block equations

The equation

```text
A^2 = 12I - A + 2J
```

gives

```text
B B^T       = 12I - A_X + 2J - R R^T - A_X^2,       (1)
A_X B + B H = 2J - B,                                 (2)
B^T B + H^2 = 12I - H + 2J.                           (3)
```

Because every column of `B` has size six,

```text
(J/3)B = 2J.
```

Thus (2) is the intertwining relation

```text
B H = Q B,                 Q=J/3-I-A_X.               (4)
```

Equations (1)--(3), binary block shape, and a simple symmetric `H` are an
exact finite completion problem.  For a fixed core they are stronger than
the pairwise Gram equations alone.

## 3. A new pointwise mixed-equation cut

Let `b_y` be one column of `B`, and let `h_y` be column `y` of `H`.  Equation
(2) gives

```text
d(b_y) := 2*1 - (I+A_X)b_y = B h_y.                    (5)
```

The right side counts incidences among the eight `H`-neighbors of `y`.
Consequently every coordinate of `d(b_y)` is nonnegative.

For a selected point `x in b_y`,

```text
d_x = 1 - deg_{A_X[b_y]}(x).
```

Hence `A_X[b_y]` is a matching, recovering the Wave 35 individual-block
test.  For an unselected point,

```text
d_x = 2 - |N_X(x) intersect b_y|.
```

Therefore no outside `X` vertex may be adjacent to three selected points.
This second restriction was absent from the Wave 35 census.  Also

```text
sum_x d_x = 72 - 6 - 18 = 48,
```

as required for eight neighboring blocks of size six.

On the published restricted core the exhaustive counts change from

```text
old induced-matching survivors: 183980
new mixed-equation survivors:   151712
removed exactly:                 32268
```

The new survivors by their number `e_y` of internal `X` edges are

```text
e_y=0: 52868
e_y=1: 76036
e_y=2: 22104
e_y=3:   704
```

This is a strict necessary-condition improvement, not a 60-block design.

## 4. Pointwise triangle transfer

For a selected block let `e_y` be the number of `A_X` edges it induces.
The triangles through `y` split exactly as

```text
two X vertices and y:  e_y,
one X and one Y:       6-2e_y,
two Y vertices and y:  1+e_y.                         (6)
```

The middle term is `sum_{x in b_y} d_x`.  Every vertex of an
`srg(99,14,1,2)` lies in seven triangles, giving the last term.  Across all
sixty blocks, each of the 36 cross-fibre `X` edges occurs once, so

```text
sum_y e_y = 36.
```

It follows again, now pointwise, that `H` has

```text
(60+36)/3 = 32
```

triangles.  Moreover each `H` vertex lies in between one and four of them.

## 5. Component balance

Let `C` be a connected component of `A_X`.  Cross-fibre matchings show that
`C` contains `m` vertices in each fibre, hence `3m` vertices in total.  Put

```text
z_y = |b_y intersect C|.
```

Row degrees of `B` give

```text
sum_y z_y = 30m.                                      (7)
```

Apply (1) to the component indicator `1_C`.  Since

```text
A_X 1_C=3 1_C,
|C|=3m,
||R^T 1_C||^2=3m^2,
```

the exact second moment is

```text
sum_y z_y^2 = 1_C^T B B^T 1_C = 15m^2.               (8)
```

Cauchy--Schwarz applied to the sixty integers `z_y` has the same right side,
so equality holds.  Therefore

```text
z_y=m/2 for every y.                                  (9)
```

In particular every `m` is even.  The case `m=2` is also impossible:
the cross two-factor is a six-cycle and the three within-fibre edges join
opposite vertices, giving `K_{3,3}`.  Same-side nonedges then have three
common `X` neighbors, contradicting `mu=2`.

Since the component parameters sum to twelve, only

```text
[12], [4,8], [6,6], [4,4,4]                           (10)
```

survive.  This is a complete reduction of the disconnected cases.

## 6. Exact disconnected block patterns

For component `C` and fibre `i`, write

```text
z_iy=|b_y intersect C intersect X_i| in {0,1,2}.
```

Further applications of (1) give, for `i != j`,

```text
sum_y z_iy       = 10m,
sum_y z_iy^2     = m^2+8m,
sum_y z_iy z_jy  = 2m(m-2).                           (11)
```

Together with `z_0y+z_1y+z_2y=m/2`, these moments force:

| `m` | count of `z_i=0,1,2` in each fibre | block patterns |
|---:|---|---|
| 4 | `(24,32,4)` | 12 permutations of `(2,0,0)` and 48 of `(1,1,0)` |
| 6 | `(12,36,12)` | 24 copies of `(1,1,1)` and 36 permutations of `(2,1,0)` |
| 8 | `(4,32,24)` | 12 permutations of `(2,2,0)` and 48 of `(2,1,1)` |
| 12 | `(0,0,60)` | 60 copies of `(2,2,2)` |

For `m=4` the double-coordinate orientations occur four times each and the
zero-coordinate orientations occur sixteen times each.  The `m=8` counts
are their coordinatewise complements.  For `m=6`, the orientation matrix
indexed by `(double coordinate, zero coordinate)` has all row and column
sums equal to twelve.

Thus:

- in the `4+8` case the two component patterns are coordinatewise
  complements;
- in the `6+6` case the two patterns are coordinatewise complements; and
- in the `4+4+4` case a block is only of balanced `AAA`, aligned `ABB`, or
  balanced `BBB` type, with `A=(2,0,0)` and `B=(1,1,0)` up to permutation.

These constraints are simultaneous across all sixty blocks; they are not
obtained by inspecting columns one at a time.

## 7. Spectral transfer to the 60-vertex graph

Let `c` be the number of components of `A_X`.  On the 33-dimensional
subspace orthogonal to the three fibre indicators, equation (1) becomes

```text
B B^T=(3I-A_X)(4I+A_X).
```

The cubic spectrum lies in `[-3,3]`.  Its only additional kernel occurs at
eigenvalue `3`, once for each component beyond the first.  Including the two
fibre-difference kernel vectors gives

```text
rank(B B^T)=35-c.                                     (12)
```

Transpose (4):

```text
H B^T = B^T Q.
```

Thus `H` acts on `im(B^T)` by eigenvalue `8` on constants and by
`-1-lambda` on every surviving nonquotient `A_X` eigenmode.  On `ker(B)`,
equation (3) reduces to

```text
H^2+H-12I=0,
```

so only eigenvalues `3` and `-4` occur.  Dimension and trace give their
exact multiplicities:

```text
spec(H on ker B)=3^18,(-4)^(7+c).                     (13)
```

Equivalently, if

```text
chi_X(t)=(t-3)^c t^2 f(t),
```

then the required characteristic polynomial is

```text
chi_H(t)=(-1)^(34-c)
         (t-8)(t-3)^18(t+4)^(7+c) f(-1-t).            (14)
```

There is exactly one eigenvalue `8`, so `H` must be connected.

Exact power traces through degree four are

```text
tr(H)   = 0,
tr(H^2) = 480,
tr(H^3) = 192,
tr(H^4) = 8568 + 8 C4(A_X).
```

The cubic and quartic traces reproduce

```text
triangles(H)=32,
C4(H)=171+C4(A_X).                                   (15)
```

For the published restricted core, `c=1` and `C4(A_X)=0`, so its required
`H` would be connected, have 32 triangles, and have exactly 171 four-cycles.

## 8. Exact completion boundary

For any fixed core, a complete finite certificate consists of:

1. two permutations matching the 60 allowed fibre-0 edges to the allowed
   edges in fibres 1 and 2;
2. all three cross-fibre concurrence blocks in (1);
3. the pointwise cut (5);
4. a simple symmetric 8-regular `H`; and
5. exact equations (2)--(3).

These data assemble a 99-by-99 binary adjacency matrix satisfying the full
SRG equation.  Conversely, every endpoint graph supplies such data.

The strengthened fixed-pair SAT and MILP scouts remained `UNKNOWN`; their
budgets and failure modes are retained separately.  The strongest justified
conclusion is:

```text
mixed-equation individual-block cut:       DERIVED
component partition and pattern reduction: DERIVED
spectral transfer and H moments:            DERIVED
restricted 151712-column census:            DERIVED
simultaneous 60-block B:                     UNKNOWN
compatible 60-vertex H:                     UNKNOWN
n3=4158 and Conway-99:                       UNKNOWN
```
