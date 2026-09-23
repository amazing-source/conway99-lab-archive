# Derivation of the rooted relation caps

Everything below is conditional on a prism-free
`srg(99,14,1,2)`. It uses no automorphism of the putative graph.

## The `3K6` partition

Let the root triangle be

```text
R={a,b,c}.
```

Every graph vertex has degree 14, and its neighbors split into seven paired
edges because every edge belongs to a unique triangle. Besides `R`, exactly
six graph triangles therefore contain each of `a`, `b`, and `c`. These
eighteen triangles are distinct.

Two triangles in the same sector share its root vertex and are in relation
`K`. Triangles in different sectors cannot share a graph vertex. For example,
a common external vertex of an `a`-petal and a `b`-petal would be a second
common neighbor of adjacent vertices `a,b`, whereas their unique common
neighbor is `c`. Thus the `K` graph induced on the eighteen petals is `3K6`.

## Cross-sector `B` degree

Take an `a`-petal

```text
P={a,x,x'}.
```

The external point `x` is nonadjacent to `b`; otherwise `x` would be a common
neighbor of `a,b` distinct from `c`. Because nonadjacent graph vertices have
exactly two common neighbors, `x` and `b` have common neighbors `a` and one
additional point `y`. The point `y` lies in exactly one of the six
`b`-petals. Applying the same argument to `x'` gives a point `y'` in a
`b`-petal.

The points `y,y'` are distinct. If they were equal, that point and `a` would
be two common neighbors of the adjacent pair `x,x'`, contradicting
`lambda=1`.

Moreover, `y,y'` cannot lie in the same `b`-petal. If they did, that petal and
`P` would have the three cross edges

```text
a-b, x-y, x'-y',
```

which is the forbidden triangular-prism relation at the endpoint.

Hence `P` has one extra cross edge to exactly two distinct `b`-petals. Those
two pairs have two total cross edges and are in relation `B`. Its other four
`b`-petal pairs have only the root edge `a-b` and are in relation `C`.
Repeating this in both directions proves that `B` is a simple 2-regular
bipartite graph between the two six-petal sectors. The same proof applies to
each of the three sector pairs.

Therefore every petal has, inside the other eighteen root-neighbors,

```text
K-degree 5,
D-degree 0,
C-degree 8,
B-degree 4.
```

Together with itself and the root, this is the known local row
`(I,K,D,C,B)=(1,5,0,8,4)`.

## What is not forced

A simple bipartite 2-factor on `6+6` vertices can have cycle half-length
partition

```text
(6), (4,2), (3,3), or (2,2,2).
```

Nothing in the preceding one-root derivation selects one partition, aligns
the three sector-pair factors, or makes their local symmetries extend to the
remaining 212 graph triangles. Those choices must remain variables.

The completion-free incidence template records all 108 possible cross-sector
`B` pairs and the 36 degree-two caps. Its 2-WL closure is therefore forced
only as a constraint-template closure. A closure computed after selecting a
2-factor is conditional on that selection.

