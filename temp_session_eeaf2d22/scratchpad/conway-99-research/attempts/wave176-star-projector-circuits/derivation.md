# Star-projector and cross-circuit derivation

## 1. Conditional setting

Assume the still-surviving endpoint branch

```text
n3=4158,  P=0,  rank_F3(D)=11.
```

Use the verified centered factorization from Waves 171--175.  Write `z_T`
for the 231 singular columns in a nondegenerate 11-space `V` over `F_3`.
For each original graph vertex `x`, its seven triangle blocks have Gram
matrix

```text
J_7-I_7
```

and satisfy

```text
sum_(T contains x) z_T=0.
```

Their span `E_x` is therefore a nondegenerate six-space.

## 2. Canonical projectors

For a vector `z`, let `z tensor z` denote the self-adjoint rank-one map
`u -> (z,u)z`.  Define

```text
P_x=-sum_(T contains x) z_T tensor z_T.
```

On a star vector `z_U`,

```text
P_x z_U
  =-sum_(T != U) z_T
  =z_U.
```

The same operator vanishes on `E_x^perp`.  Hence `P_x` is precisely the
orthogonal projector onto `E_x`:

```text
P_x^2=P_x,  rank(P_x)=6,  tr(P_x)=6=0 in F_3.       (1)
```

Every triangle block lies in three vertex-stars, so

```text
sum_x P_x=-3 sum_T z_T tensor z_T=0.                (2)
```

## 3. A 65-dimensional trace-Gram target

Let `B` be the `99 by 231` point--triangle incidence matrix.  Let `L` be
the endpoint `N3` relation on triangle blocks: two blocks are related when
they are disjoint and have exactly two cross edges.  It is 36-regular.

The endpoint centered Gram entries are `0,1,2`, and `L` marks exactly the
entries equal to 2.  Therefore, entrywise over `F_3`,

```text
D^(o2)-D=2L.
```

The star relations give `BD=0`.  Taking traces of products of (1) gives

```text
G_P=(tr(P_x P_y))_(x,y)
   =B D^(o2) B^T
   =2 B L B^T.                                      (3)
```

The `P_x` are trace-zero self-adjoint endomorphisms.  This space is the
65-dimensional trace-zero hyperplane in `Sym^2(V)`, so

```text
rank_F3(B L B^T)<=65.                               (4)
```

The diagonal entries of `BLB^T` vanish.  If `x~y`, its integer `(x,y)`
entry is 12: each of the six outer triangles at `y` has two `N3`
partners in the outer `x`-star.  Also

```text
BLB^T 1
 =B L (3*1)
 =3*36*7*1
 =756*1.
```

After the 14 graph-neighbor contributions, the sum over the 84
nonneighbors of `x` is

```text
756-14*12=588,
```

with average 7.  These integer sums do not determine the nonedge entries
modulo three, so (4) is presently a target rather than a contradiction.

## 4. Nonadjacent stars force a cross relation

If `x` and `y` are nonadjacent, their seven-block stars are disjoint.  The
14 columns span at most the 11-dimensional ambient space, hence their
relation space has dimension at least three.  The two individual
seven-star circuits span only a two-space.  There is therefore a
genuinely cross-star relation.  Wave 174 gives dual distance at least
four, so its support lies between 4 and 14.

## 5. Adjacent stars reduce to four cycle types

Now let `x~y`.  Their stars share the unique triangle on the edge `xy`.
Remove this block, leaving six outer blocks on each side.

For an outer neighbor `u` of `x`, the SRG parameter `mu=2` says that the
common neighbors of `u` and `y` are `x` and exactly one outer neighbor of
`y`.  Thus every outer `x`-star triangle has two cross incidences with
outer `y`-star triangles.  The endpoint condition `P=0` prevents the two
vertices of one triangle from landing in the same opposite triangle.
The same holds with `x,y` reversed.  The cross-incidence graph is
therefore a simple 2-regular bipartite graph on `6+6` vertices.

Its cycle half-lengths must be one of

```text
(6), (4,2), (3,3), (2,2,2).                        (5)
```

Let `A` be its `6 by 6` biadjacency matrix.  In the ordering

```text
common block | six x-outer blocks | six y-outer blocks,
```

the 13-column Gram matrix has zero diagonal, entry 1 inside either star
and from the common block, and outer cross block

```text
J_6+A.                                              (6)
```

Exact row reduction of the four symbolic matrices (6) gives

```text
cycle type       6   4+2   3+3   2+2+2
Gram rank       10    10     8       9.             (7)
```

This is a four-case algebraic calculation, not a search for a graph.

## 6. Rank versus radical

Let `U=E_x+E_y`, let `r=dim(U)`, and let `g` be the rank in (7).  The
radical of the restricted form on `U` has dimension `r-g`.  Since the
ambient 11-space is nondegenerate,

```text
r-g <= dim(U^perp)=11-r,
r <= floor((11+g)/2).                               (8)
```

Together with `g<=r`, (8) yields:

```text
type        possible r   dim(E_x intersect E_y)   relation dim on 13
6              10                 2                       3
4+2            10                 2                       3
3+3           8 or 9            at least 3              at least 4
2+2+2         9 or 10           at least 2              at least 3
```

After quotienting by the two evident star circuits, every adjacent type
therefore has at least one genuinely cross-star relation.  Type `3+3`
has at least two independent cross-relation classes.

For types `6` and `4+2`, (8) forces `r=g=10`; the coefficient kernel is
exactly the Gram kernel.  Enumerating its 27 words, only to read the
already-derived three-dimensional kernel, gives exact minimum supports
outside the two-star circuit span:

```text
type 6:   8,
type 4+2: 4.                                        (9)
```

No candidate graph or code is enumerated in (9).

## Boundary

Every pair of distinct original vertices now forces a cross-star dual
relation.  This is substantially stronger than the 231-column global
dimension count, but it is not yet an inconsistency.  The projectors need
not commute, so their trace products cannot be replaced by intersection
dimensions.  The global compatibility of the pairwise circuits and the
nonedge residues in (3) remain open.  No endpoint exclusion, strict
`n3` bound, graph construction, or Conway-99 resolution follows.
