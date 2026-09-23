# Independent Wave 36 block-compatibility audit

```yaml
role: verifier
date_utc: 2026-07-26T23:09:48Z
git_commit: 697cc02bcbe16b69aaf08822298e03c66329c64c
claim_label: VERIFIED
scope: "Conditional endpoint one-triangle block equations, component balance and patterns, spectral transfer, and the frozen restricted-core 183980-to-151712 and fixed-pair 3600-to-3266-to-2939 censuses"
inputs:
  - "verification/wave36-block-compatibility/input-freeze.sha256"
method: "Clean-room block expansion and exact derivation; independent bitset reconstruction and enumeration; exhaustive six-vertex control; exact rational rank and trace arithmetic"
command:
  - ".\\.venv\\Scripts\\python.exe -B verification/wave36-block-compatibility/independent_check.py --verify verification/wave36-block-compatibility/independent-results.json"
  - ".\\.venv\\Scripts\\python.exe -B -m unittest discover -s verification/wave36-block-compatibility -p \"test_*.py\" -v"
outputs:
  - "verification/wave36-block-compatibility/independent-results.json"
limitations: "The historical LP/MILP/SAT executions are not reproducible from the retained target files, which contain no model builder, solver instance, raw log, or certificate. Their only justified status remains UNKNOWN. No simultaneous B, compatible H, endpoint exclusion, or improved n3 bound is verified."
```

## Verdict

The displayed general mathematics and both requested enumerations are
independently verified, conditional on the frozen Wave 35 endpoint premises.
No contradiction was found in:

- the three block equations and the pointwise `d(b)>=0` cut;
- component balance, the four surviving component partitions, and their block
  pattern restrictions;
- the characteristic-polynomial transfer, including its sign and exact kernel
  multiplicities;
- connectedness of `H`, its 32 triangles, and
  `C4(H)=171+C4(A_X)`;
- the restricted census `183980 -> 151712`; or
- the fixed-pair residual census `3600 -> 3266 -> 2939`.

The solver telemetry in `failed-routes.md` is not independently reproducible
from the retained files. This does not refute it, but it prevents promotion of
the reported LP point, finite-field ranks, clause count, or run statistics to
independently verified evidence. The conservative `UNKNOWN` status and its
restriction to one fixed pair certificate are correct.

## 1. Block equations and the mixed cut

With vertex order `T|X|Y`, the adjacency matrix is

```text
    [ J3-I  R^T   0 ]
A = [  R    A_X   B ].
    [  0    B^T   H ]
```

Expanding the `XX`, `XY`, and `YY` blocks of

```text
A^2 = 12I - A + 2J
```

gives exactly

```text
BB^T       = 12I-A_X+2J-RR^T-A_X^2,
A_X B+BH  = 2J-B,
B^T B+H^2 = 12I-H+2J.
```

Each column of `B` has six ones, so `JB=6J` and `(J/3)B=2J`.
Therefore

```text
BH=(J/3-I-A_X)B.
```

For a column `b=b_y`, its corresponding column of the mixed equation is

```text
d(b)=2*1-(I+A_X)b=Bh_y.
```

The right side counts, coordinate by coordinate, how many of the eight
`H`-neighbors of `y` contain a given point of `X`; it is nonnegative.
For selected `x`,

```text
d_x=1-deg_{A_X[b]}(x),
```

and for unselected `x`,

```text
d_x=2-|N_X(x) intersect b|.
```

Thus the selected subgraph is a matching and no outside point has three
selected neighbors. Since `b` has weight six and `A_X` is cubic,

```text
sum_x d_x = 72-6-18=48.
```

These statements use the full mixed equation only as a necessary condition;
they do not assert that a nonnegative target `d(b)` can be decomposed into
eight compatible neighboring blocks.

## 2. Pointwise triangles

Let `e_y` be the number of `A_X` edges induced by `b_y`.

- There are `e_y` triangles through `y` with their other two vertices in `X`.
- The sum of `d_x` over selected `x` is `6-2e_y`, which counts the triangles
  through `y` with one other vertex in each of `X` and `Y`.
- Every vertex of the SRG lies in `14*1/2=7` triangles, leaving `1+e_y`
  triangles wholly inside `Y`.

At the prism-free endpoint, `A_X` is triangle-free. Each of its 36
cross-fibre edges has its unique common neighbor in `Y`, while a within-fibre
edge already uses its unique common neighbor in `T`. Hence

```text
sum_y e_y=36.
```

Summing the `Y`-only triangle incidences gives

```text
sum_y (1+e_y)=96,
```

so `H` has `96/3=32` triangles. Because a matching on six points has between
zero and three edges, each vertex of `H` lies in between one and four
triangles.

## 3. Component balance

Let `C` be a component of `A_X`. Each cross-fibre perfect matching maps the
part of `C` in one fibre bijectively to the part in another. Thus `C` has
`m` points in each fibre and size `3m`.

For `z_y=|b_y intersect C|`, the row degree ten of `B` gives

```text
sum_y z_y=30m.
```

Let `u=1_C`. Since `A_X u=3u`, substituting `u` on both sides of the Gram
identity gives

```text
sum_y z_y^2
 =12(3m)-3(3m)+2(3m)^2-3m^2-9(3m)
 =15m^2.
```

Cauchy--Schwarz gives

```text
sum_y z_y^2 >= (sum_y z_y)^2/60 =15m^2.
```

Equality holds, so all sixty integers are equal:

```text
z_y=m/2.
```

Consequently `m` is even. An independent exhaustive check of all labelled
cubic triangle-free graphs on six vertices found the ten labellings of
`K3,3`; every one has a nonedge with three common neighbors. Thus `m=2`
contradicts `mu=2`. The complete surviving partitions of twelve are

```text
[12], [4,8], [6,6], [4,4,4].
```

## 4. Fibrewise component patterns

For `u_i=1_{C intersect X_i}` and
`z_iy=|b_y intersect C intersect X_i|`, the same Gram identity yields

```text
sum_y z_iy      =10m,
sum_y z_iy^2    =m^2+8m,
sum_y z_iy z_jy =2m(m-2),  i != j.
```

To see the second identity, `u_i^T A_X u_i=m` and
`||A_Xu_i||^2=3m`. For the cross identity,
`u_i^T A_Xu_j=m` and
`(A_Xu_i)^T(A_Xu_j)=3m`.

Because every `z_iy` is `0`, `1`, or `2`, write `n_r` for the number of
blocks with `z_iy=r` in a fixed fibre. The first two moments solve

```text
n_2=m(m-2)/2,
n_1=10m-2n_2,
n_0=60-n_1-n_2.
```

Combining these counts with
`z_0y+z_1y+z_2y=m/2` reproduces exactly:

| `m` | `(n0,n1,n2)` | patterns and counts |
|---:|---:|---|
| 4 | `(24,32,4)` | 12 permutations of `(2,0,0)` and 48 of `(1,1,0)` |
| 6 | `(12,36,12)` | 24 of `(1,1,1)` and 36 permutations of `(2,1,0)` |
| 8 | `(4,32,24)` | 12 permutations of `(2,2,0)` and 48 of `(2,1,1)` |
| 12 | `(0,0,60)` | 60 of `(2,2,2)` |

For `m=4`, each double orientation occurs four times and each zero
orientation of `(1,1,0)` occurs sixteen times. For `m=6`, the double/zero
orientation matrix has row and column sums twelve. The `m=8` statements are
the coordinatewise complements of the `m=4` statements.

An independent enumeration of component-pattern tuples summing to `(2,2,2)`
found:

- six compatible `4+8` tuples, all coordinatewise complements;
- seven compatible `6+6` tuples, all coordinatewise complements; and
- 21 compatible `4+4+4` oriented tuples: six balanced `AAA`, nine aligned
  `ABB`, and six balanced `BBB`.

This verifies the pattern classification without asserting that any such
aggregate pattern is realized by actual blocks.

## 5. Spectral transfer

The fibre-indicator space has quotient matrix `J3`, hence contributes one
eigenvalue `3` and two designated eigenvalues `0` to `A_X`. If `A_X` has
`c` components, eigenvalue `3` has total multiplicity `c`. On the
33-dimensional orthogonal complement of the fibre indicators,

```text
BB^T=(3I-A_X)(4I+A_X).
```

All eigenvalues of the cubic graph `A_X` lie in `[-3,3]`, so the only zeros
of this product come from eigenvalue `3`. Together with the two fibre
differences, this gives

```text
rank(B)=rank(BB^T)=35-c.
```

Transposing `BH=QB`, where `Q=J/3-I-A_X`, shows that `H` acts on
`im(B^T)` with eigenvalue `8` on constants and eigenvalue `-1-lambda` on
each remaining `A_X` eigenmode.

The kernel of `B` is invariant under `H`. If `v` is in this kernel, then
`B^T1=6*1` implies `v` is orthogonal to constants. The `YY` equation
therefore reduces to

```text
(H^2+H-12I)v=0.
```

Since `H` is symmetric, its kernel-space eigenvalues are `3` and `-4`.
Their total multiplicity is `60-(35-c)=25+c`. If their multiplicities are
`a,b`, respectively, the trace on the transferred space is `-26+4c`.
Using `tr(H)=0` gives

```text
a+b=25+c,
3a-4b=26-4c,
```

so

```text
a=18, b=7+c.
```

Write

```text
chi_X(t)=(t-3)^c t^2 f(t),  deg(f)=34-c.
```

The transferred roots are `-1-lambda` for the roots `lambda` of `f`.
Therefore

```text
product_lambda (t+1+lambda)
  =(-1)^(34-c) f(-1-t),
```

which verifies both the sign and

```text
chi_H(t)=(-1)^(34-c)
         (t-8)(t-3)^18(t+4)^(7+c)f(-1-t).
```

No other transferred or kernel eigenvalue can be `8`, so an 8-regular `H`
has eigenvalue `8` with multiplicity one. The multiplicity of the degree
eigenvalue equals the number of connected components, hence `H` is
connected.

For a cubic triangle-free graph on 36 vertices,

```text
tr(A_X)=0,
tr(A_X^2)=108,
tr(A_X^3)=0,
tr(A_X^4)=540+8*C4(A_X).
```

Substitution in the displayed spectrum gives

```text
tr(H)=0,
tr(H^2)=480,
tr(H^3)=192,
tr(H^4)=8568+8*C4(A_X).
```

Thus `H` has `192/6=32` triangles. For an 8-regular graph on 60 vertices,

```text
tr(H^4)=60*8*(2*8-1)+8*C4(H),
```

so

```text
C4(H)=171+C4(A_X).
```

The reconstructed restricted core is connected and has no four-cycle, so
its required values are 32 triangles and 171 four-cycles.

## 6. Independent restricted enumerations

The checker reconstructs the normalized core from the circle
one-factorization, within-fibre rounds `(1,2,3)`, identity matchings on
`X0-X1` and `X1-X2`, and round zero on `X2-X0`. It uses bitsets, not the
discovery implementation.

It independently obtains:

```text
core vertices/edges/degrees/components: 36/54/{3}/1
core triangles/four-cycles:             0/0
upper-triangle SHA-256:
  f97aa806e08ddeb789be3f1fc604879a1630a6f1b8a21d899dbcd57772c998c5
rank_Q(BB^T):                           34

raw allowed triples:                    216000
old induced-matching survivors:         183980
new d(b)>=0 survivors:                  151712
removed:                                 32268
```

The new survivors by internal edge count are exactly

```text
e=0: 52868
e=1: 76036
e=2: 22104
e=3:   704
```

The independent rejection counts by number of negative coordinates are
`30940`, `1316`, and `12` for one, two, and three negatives. The full
transfer-signature distribution also matches the target JSON.

For the frozen Wave 35 `X0-X1` permutation, the checker first verifies the
entire forced `X0-X1` Gram block. Extending each of its sixty rows by each
of the sixty allowed `X2` pairs gives:

```text
raw choices:             3600
old-cut choices:         3266
mixed-cut choices:       2939
```

These are residual candidate variables, not a selection of sixty compatible
columns and not an extension certificate.

## 7. Solver evidence boundary

The target directory contains only:

```text
exact-results.json
exact_check.py
failed-routes.md
input-freeze.sha256
run-report.yaml
test_exact_check.py
```

It retains no fixed-pair model generator, MPS/CNF instance, solver log,
fractional LP witness, or UNSAT/SAT certificate. Accordingly:

- the independently reproduced `2939` mixed-cut choices verify the stated
  input scope of the strengthened fixed-pair scout;
- a CaDiCaL budget return of `None` would correctly be `UNKNOWN`;
- a 60-second integer-program timeout with no incumbent would correctly be
  `UNKNOWN`;
- even a future contradiction for this model would concern only the fixed
  Wave 35 pair certificate; and
- the exact historical solver telemetry is not independently verified here.

The target report appropriately makes no feasibility, infeasibility, endpoint,
or global Conway-99 claim from those runs.

## Final classification

```text
block equations and d(b)>=0:                    VERIFIED, conditional
pointwise triangle transfer:                    VERIFIED, conditional
component balance/partitions/patterns:          VERIFIED, conditional
spectral transfer/sign/multiplicities/moments:  VERIFIED, conditional
restricted 183980 -> 151712 census:             VERIFIED
fixed-pair 3600 -> 3266 -> 2939 census:         VERIFIED
historical LP/MILP/SAT telemetry:               UNKNOWN, not reproducible
simultaneous 60-column B and compatible H:      UNKNOWN
n3=4158, improved upper bound, Conway-99:       UNKNOWN
```
