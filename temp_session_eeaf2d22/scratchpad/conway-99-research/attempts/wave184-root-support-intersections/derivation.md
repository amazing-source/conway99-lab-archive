# Sparse root-support intersections and a weight-four floor

## 1. Frozen setting

Assume the independently verified Wave 181--183 equality setting.  In
particular:

1. every nonedge `xy` has
   `R_x intersect R_y={rho_xy}`;
2. the 2,079 canonical quadrilaterals support distinct projective
   weight-four conic circuits;
3. every root support is `5K1`, `3K2`, or `C7`; and
4. the balanced outer circuit of one graph edge cannot serve another graph
   edge or a nonedge.

## 2. Two global-root supports meet in at most an edge

Let `r != s`.  If `X_r intersect X_s` contained a graph nonedge `xy`, then
both roots would belong to `R_x intersect R_y`, contradicting exact
nonedge-root uniqueness.

Thus `X_r intersect X_s` is a clique.  Wave 183 proves that every root
support is triangle-free, so

```text
|X_r intersect X_s|<=2,                           (1)
```

and equality in (1) can occur only on a graph edge.

If

```text
c_xy=|R_x intersect R_y|
```

for a graph edge, then (1) also gives the exact double-intersection identity

```text
number of root pairs meeting in two stars
  =sum_(xy in E(G)) binomial(c_xy,2).              (2)
```

## 3. Internal support edges inject into weight-four circuits

Let `xy` be an internal graph edge of `X_r`.  At each endpoint, `r` is a
difference of two local star columns.  Wave 182 excludes the shared triangle
block from both representations.  Equating the two representations gives a
relation on four distinct outer-star columns, with all four coefficients
nonzero.

The verified dual distance at least four makes this support a circuit.  Its
projective relation determines `r`, so two different roots on the same edge
give different circuits.  Wave 178--179 prove that balanced short outer
circuits on different graph edges are distinct and cannot equal a
nonedge-realizing circuit.  Therefore the root--internal-edge incidences
inject into new projective weight-four circuits.

The three support shapes have respectively zero, three, and seven graph
edges.  If `n_i` counts roots of multiplicity `i`,

```text
E=sum_(xy in E(G)) c_xy=3*n_6+7*n_7              (3)
```

is exactly the number of these edge-root circuits.

## 4. The arithmetic minimum is twelve

Wave 183 gives

```text
5*n_5+6*n_6+7*n_7=2079.
```

Modulo five,

```text
n_6+2*n_7=4 mod 5.                                (4)
```

Suppose `E<12`.  Equation (3) gives `n_7<=1`.

- If `n_7=0`, then `n_6<=3`, incompatible with
  `n_6=4 mod 5`.
- If `n_7=1`, then `n_6<=1`, incompatible with
  `n_6=2 mod 5`.

Hence

```text
E>=12.                                            (5)
```

This arithmetic bound is sharp before the remaining geometry:
`(n_5,n_6,n_7)=(411,4,0)` satisfies the incidence equation and (5) with
equality.

## 5. Weight-four enumerator consequence

Wave 181 equality already supplies 2,079 distinct projective weight-four
canonical conics.  Sections 3--4 supply at least 12 further projective
weight-four edge circuits, disjoint from that family.  Thus

```text
number of projective weight-four circuits>=2091.
```

Each projective ternary circuit has two nonzero scalar representatives, so

```text
B_4>=4182.                                        (6)
```

## Boundary

Equation (6) is conditional on Wave 181 equality.  No incompatible upper
bound on `B_4` is known.  The sparse intersections (1)--(2) expose a
block-side incidence target, but do not yet close it to a coherent
configuration or force a rank contradiction.

No strict `n3` improvement, rank-11 exclusion, graph construction, or
Conway-99 resolution follows.

