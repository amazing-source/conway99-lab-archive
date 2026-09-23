# Nonedge fourth-trace derivation and exact low-count census

Claim label: `DERIVED`, pending independent verification.

## 1. The exact nonedge cross Gram

Work over `F_3` in the frozen branch.  Let `x,y` be nonadjacent.  Their two
common neighbors are denoted `a,b`.  They are nonadjacent: otherwise the edge
`ab` would have both `x` and `y` as common neighbors, contradicting
`lambda=1`.

Write the seven triangles through each center as

```text
T_a,T_b,T_2,...,T_6,
U_a,U_b,U_2,...,U_6,
```

where the subscript `a` or `b` marks the contained common neighbor.  The two
marked triangles at either center are distinct because the two noncentral
vertices in one center-triangle are adjacent.

The centered Gram is `D=B^T A B`.  For two triangle blocks its entry is:

- zero on the diagonal, because a triangle has six ordered internal
  adjacencies;
- one for two triangles meeting in one point, because the four forced
  adjacencies reduce to one modulo three; and
- the number `j` of cross edges for disjoint triangles.

At `P=0`, a disjoint pair has `j<=2`.  Hence the `7 by 7` integer
representative

```text
C=(D_(T_i,U_j)) in {0,1,2}^{7 by 7}
```

contains the exact marked corner

```text
[1 2]
[2 1].                                             (1)
```

The diagonal entries in (1) come from the two intersections.  For
`T_a,U_b`, the edges `x-b` and `a-y` are already present.  A third cross edge
would violate `P=0`, proving the off-diagonal value two.  The other
off-diagonal entry is symmetric.

## 2. Exact row and column profiles

Write `T_a={x,a,alpha}`.  The vertex `alpha` is nonadjacent to `y`.  Its two
common neighbors with `y` are `a` and one vertex in an ordinary `y`-star
triangle.  The second vertex cannot lie in `U_a` or `U_b`, by `lambda=1`
and uniqueness of the center triangles.  Thus the `T_a` row has:

- one intersecting entry equal to one;
- the marked off-diagonal entry equal to two;
- one additional ordinary entry equal to two; and
- four ordinary entries equal to one.

Every marked row and column therefore has profile

```text
0^0 1^5 2^2.                                       (2)
```

For an ordinary triangle `T_i={x,u,u'}`, each of `u,u'` is nonadjacent to
`y` and has exactly two neighbors in `Gamma(y)`.  None is `a` or `b`, so
there are four such cross edges.  The fixed edges `x-a,x-b` contribute one
to each marked column.  Consequently the seven integer entries have total
six.  If `k` entries are two, then

```text
profile(T_i row)=0^(1+k) 1^(6-2k) 2^k,
0<=k<=3.                                           (3)
```

The same proof gives (3) for ordinary columns.  Equations (2)--(3) imply
`C*1=C^T*1=0` over `F_3`.

## 3. The fourth trace and the integer two-count

Let `Z_x,Z_y` be the two seven-column star frames.  Since

```text
P_x=-Z_x Z_x^*,
P_y=-Z_y Z_y^*,
C=Z_x^* Z_y,
```

cyclicity of trace gives

```text
g_xy=tr(P_xP_y)=tr(CC^T),
h_xy=tr(P_xP_yP_xP_y)=tr((CC^T)^2).               (4)
```

Let

```text
t_xy=#{(i,j): C_ij=2}.
```

This is exactly `(BLB^T)_(x,y)`: `L` selects the disjoint triangle pairs
with two cross edges.  The two intersecting cells have value one and do not
contribute.  The verified Wave 176 integer calculation therefore gives

```text
sum_(y nonadjacent to x) t_xy=588,
average t_xy over the 84 nonneighbors of x=7.       (5)
```

Also, the total integer sum of the entries of `C` is

```text
2*9+5*6=48.
```

If `s` is the number of one-entries, then `s+2t=48`, so (4) gives

```text
g_xy=s+t=-t=2t in F_3,                              (6)
```

in agreement with the verified trace Gram `2BLB^T`.

The six noncore two-entries forced by (1)--(2) prove the new necessary
bound

```text
t_xy>=6 for every nonedge.                          (7)
```

Together with (5), this says

```text
sum_(nonedges {x,y}) (t_xy-6)=4158,
N_6=sum_(j>=8) (j-7)N_j.                            (8)
```

It does not force `t_xy=7`.

## 4. Complete normalized census at `t=6,7`

The five ordinary rows and five ordinary columns may be relabeled
independently.  Normalize the extra two-entry in the first marked row and
column to ordinary position zero.  The second marked row/column extra
two-entry is either aligned at zero or distinct at one.  This gives four
exhaustive boundary cases.

There are already six forced two-entries outside the ordinary `5 by 5`
core.  Therefore:

- at `t=6`, the core is binary;
- at `t=7`, the core has exactly one two-entry and is otherwise binary.

The checker enumerates every binary matrix with the required exact row and
column margins.  It finds:

```text
t=6:   646 normalized labelled representatives,
t=7: 7,886 normalized labelled representatives.    (9)
```

These are exhaustive representatives, not orbit counts: residual
permutations can repeat an isomorphism type.  Repetition does not affect any
universal conclusion.

For every matrix, the checker forms the full two-star Gram

```text
F=[J_7-I_7   C  ]
  [C^T       J_7-I_7],
```

computes its rank, quotient discriminant, Gram-kernel minimum weight, and
`h`.  A matrix is counted as an unambiguous local endpoint module only when

```text
rank(F)=11,
quotient determinant=2,
minimum Gram-kernel weight>=4.                     (10)
```

At rank 11 the actual column span must equal the full nondegenerate ambient
11-space.  Only in this case is the Gram kernel automatically the true
column-relation code.  The census deliberately makes no such inference at
lower rank.

The exact counts satisfying (10) are:

| `t` | `h=0` | `h=1` | `h=2` |
|---:|---:|---:|---:|
| 6 | 0 | 18 | 0 |
| 7 | 297 | 324 | 144 |

Thus:

1. projectivity and local dual distance do not imply `t>=7`; and
2. even fixing the exact global average value `t=7`, pair trace `g=2`,
   full rank 11, nonsquare ambient type, and true-relation distance at least
   four leaves every value `h=0,1,2`.

## 5. Explicit target-shaped controls

The package gives four complete 28-vertex adjacency certificates:

```text
t6_h1,
t7_h0,
t7_h1,
t7_h2.
```

Each certificate contains the two centers, their two common neighbors, and
all 24 exclusive neighbors.  Direct checking proves:

- both centers have degree 14 in the local graph;
- they have exactly the common-neighbor pair `a,b`;
- every exclusive neighbor has exactly two common neighbors with the
  opposite center;
- an edge has at most one common neighbor inside the local graph;
- a nonedge has at most two;
- every selected disjoint star-block pair has at most two cross edges;
- `B_local^T A_local B_local` gives the displayed full two-star Gram;
- the Gram has rank 11, determinant type two, and true-relation minimum
  weight at least four; and
- explicit coordinates in `diag(1^10,2)` reproduce both projectors and the
  claimed fourth trace.

The `t6_h1` relation code has minimum weight six.  The three `t=7` controls
have the same `t=7`, `g=2`, intersection dimension one, ambient rank 11,
and nonsquare discriminant, but have fourth traces zero, one, and two.

## 6. Inflection and scope wall

This is a well-sealed obstruction to the pair-local fourth-order route:

```text
the exact two-center SRG geometry, P=0 cross-edge cap, local rank-11
projectivity, pair trace, intersection dimension, and even t_xy=7
do not determine h_xy.
```

The newly named missing invariant is the simultaneous 99-center extension
law: the unsaturated pairs in overlapping 28-vertex two-center balls must
receive their outside common neighbors compatibly across the whole graph.
Neither the local profiles nor the scalar `t_xy` encode that law.

The controls do not complete to 99 vertices, impose all 231 triangles, give
the global square-zero rank-11 Gram, or satisfy `sum_x P_x=0`.  They are not
graphs with the target parameters.  Actual nonedge fourth traces, the
rank-11 endpoint, and Conway-99 remain `UNKNOWN`.

