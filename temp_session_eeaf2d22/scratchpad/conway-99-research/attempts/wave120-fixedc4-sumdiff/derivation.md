# Fixed-C4 sums, differences, and the pairwise wall

Claim labels: `DERIVED` for the exact implications below,
`REFUTED_AS_A_RELAXATION` for the pairwise cap route, and `UNKNOWN` for
the actual caps and graph.

## 1. Common orientation

Fix an induced four-cycle and call its two nonadjacent positive anchors
`P={p1,p2}` and its two nonadjacent negative anchors `N={n1,n2}`.  For
each antipodal short-vector support through this cycle, choose the
representative

```text
x_C=(1,-1,1,-1).
```

This is only a sign convention after fixing a labelled cycle.  It assumes
no automorphism.

If `x` and `y` are two such vectors, then `x+y` and `x-y` remain integer
`-4` eigenvectors.  Their cycle restrictions are respectively

```text
(x+y)_C=(2,-2,2,-2),       (x-y)_C=0.             (1)
```

## 2. Exact real affine minimum

The `-4` primitive idempotent is

```text
E=(27I-9A+J)/63.
```

On an ordered induced C4 its principal Gram is

```text
E[C,C]=(3I-H+J/9)/7.
```

For `s=(1,-1,1,-1)`, exact inversion gives

```text
s^T E[C,C]^-1 s = 28/5.
```

Quadratic scaling therefore makes the exact real minimum in the affine
slice with coordinates `2s`

```text
(2s)^T E[C,C]^-1 (2s) = 112/5.                   (2)
```

Equation (2) is sharp in the real `-4` eigenspace.  It does not assert that
the minimum interpolant is integral.

## 3. Integer anchor equations sharpen 112/5 to 32

Let `z` be an integer `-4` eigenvector with `z_C=2s`.  At a positive anchor
`p`, the two negative cycle neighbours contribute `-4`, while

```text
(Az)_p=-4z_p=-8.
```

Thus the outside neighbours of `p` have signed sum `-4`.  Their total
negative mass is at least four.

The two positive anchors are nonadjacent and already have the two negative
anchors as their `mu=2` common neighbours.  No outside vertex is adjacent
to both.  Their outside negative-mass requirements are therefore disjoint,
forcing at least eight total units of outside negative mass.

The symmetric argument at the two negative anchors forces at least eight
units of outside positive mass.  Since an integer `a` satisfies
`a^2>=|a|`, the outside squared norm is at least 16.  The four anchors
already contribute 16, so

```text
boxed: ||z||^2 >= 32.                              (3)
```

The local anchor-equation relaxation attains equality formally: use eight
outside `-1` entries, four assigned to each positive-anchor fibre, and
eight outside `+1` entries, four assigned to each negative-anchor fibre.
This proves sharpness only for the stated local relaxation.  Whether a
full integer eigenvector of norm 32 exists is `UNKNOWN`.

The same argument applies to a sum of `r` same-oriented extensions.  Its
cycle coordinates are `r*s`; each positive anchor needs outside signed
sum `-2r`, and each negative anchor needs `+2r`.  Hence

```text
||x_1+...+x_r||^2 >= 4r^2+8r.                    (4)
```

For a norm-16 family this says

```text
sum_{i<j} <x_i,x_j> >= 2r(r-2).
```

Thus the anchor argument also supplies a family-wide moment inequality,
not only a two-vector estimate.

## 4. Pairwise inner-product intervals

Put `a=||x||^2`, `b=||y||^2`, and `k=<x,y>`.  Equation (3) and the global
minimum 14 for a nonzero integer `-4` eigenvector give

```text
a+b+2k = ||x+y||^2 >= 32,
a+b-2k = ||x-y||^2 >= 14.                         (5)
```

For `a,b in {16,18,20}`, the exact integer intervals from (5) are:

| `(a,b)` | allowed `k` from (4) |
|---|---:|
| `(16,16)` | `0..9` |
| `(16,18)` | `-1..10` |
| `(16,20)` | `-2..11` |
| `(18,18)` | `-2..11` |
| `(18,20)` | `-3..12` |
| `(20,20)` | `-4..13` |

If the difference norm is 14, 16, 18, or 20, the imported magnitude
classification says it is a balanced signed-unit vector.  Consequently
`x` and `y` have no opposite-sign overlap in those rows.  This is more
information than a bare minimum-distance bound, but it remains pairwise.

## 5. Exact size-40 null control

The file `witness.json` gives forty formal norm-16 signed supports.  Every
record contains:

- the same two positive and two negative cycle anchors;
- two positive vertices from each of the two ten-point N-anchor-only
  fibres and two from a 25-point zero-type pool;
- the sign-reversed choice from the P-anchor-only fibres and a disjoint
  26-point zero-type pool.

Thus every record has eight `+1` and eight `-1` entries, exactly the
fixed-C4 type counts from Wave 112, and it satisfies all four anchor
eigen-equations.  Positive and negative outside pools are globally
disjoint, so no two records have opposite-sign overlap.

For two records let `q` be their total overlap in the six two-point
blocks.  The witness has `0<=q<=5`, and

```text
<x,y>       = 4+q,
||x-y||^2   = 24-2q,
||x+y||^2   = 40+2q.                              (6)
```

The exact pair histogram is

| `q` | pairs | difference norm |
|---:|---:|---:|
| 0 | 92 | 24 |
| 1 | 230 | 22 |
| 2 | 222 | 20 |
| 3 | 157 | 18 |
| 4 | 62 | 16 |
| 5 | 17 | 14 |

The differences in the classified rows have respectively `10+10`,
`9+9`, `8+8`, and `7+7` unit profiles.

Subtract the common minimum interpolant of norm `28/5`.  The resulting
formal residual Gram has diagonal `52/5` and off-diagonal entry

```text
q-8/5.
```

Exact rational `LDL^T` elimination has forty positive pivots, so this Gram
is positive definite of rank 40, exactly the dimension of the coordinate
kernel.  It is therefore an actual 40-point spherical-code Gram in the
residual space.  The normalized off-diagonal inner products are

```text
-2/13, -3/52, 1/26, 7/52, 3/13, 17/52.
```

The 99-coordinate binary supports form a constant-weight-16 code of size
40 and minimum pair distance 14.  Therefore:

- pairwise PSD/Gram or spherical Delsarte constraints cannot prove a cap
  below 40;
- binary constant-weight/minimum-distance Delsarte constraints cannot
  prove a cap below 40.

In particular, neither relaxation can prove the needed caps 25 or 24.

The null control also survives (4) for every positive subset.  All
outside positive coordinates of the witness lie in globally positive
pools and all negative coordinates in disjoint negative pools.  A subset
of `r` records therefore has outside L1 mass `12r`, so its actual formal
squared norm is at least `4r^2+12r`, stronger than (4).  For all forty
records the exact pair histogram gives squared norm `9836`, while (4)
requires only `6720`.

## 6. What the witness does not do

The combinatorial signed supports and the residual spherical realization
share the same exact Gram, but they are not asserted to be one common
integer embedding.  The support records do not satisfy the 95 outside
eigen-equations, and the spherical realization need not retain unit
coordinates away from the fixed cycle.

Likewise, the binary supports are not proved to lie in the kernel code of
one target adjacency matrix.  Full low-norm support-graph structure,
dual-code constraints, three-point intersection data, or simultaneous
outside adjacency can still rule out the witness.

Thus the pairwise route is rigorously too weak, but the actual extension
caps and Conway-99 remain `UNKNOWN`.
