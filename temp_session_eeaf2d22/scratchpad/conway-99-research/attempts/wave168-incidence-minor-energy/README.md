# Wave 168: triangle incidence geometry and minor energy

Status: `DERIVED_STRATEGY`; independent verification is required before
promotion.

## Change of space

Every edge of a hypothetical `srg(99,14,1,2)` lies in a unique triangle.
Treat those triangles as blocks of a partial linear incidence geometry.
There are:

```text
99 points,
231 triangle blocks,
7 blocks through each point,
3 points in each block.
```

If `B` is the point-block incidence matrix and `A` the graph adjacency
matrix, then

```text
B*B^T = 7I+A.
```

The block-intersection graph

```text
K = B^T*B-3I
```

is 18-regular with exact spectrum

```text
18^1, 7^54, 0^44, (-3)^132.
```

## Exact prism-free translation

For two disjoint triangle blocks, common neighbors in `K` correspond exactly
to matching cross edges between the two triples. Three such neighbors form a
perfect matching and hence an induced triangular prism. Therefore

```text
P=0
```

is equivalent to every nonadjacent pair in `K` having at most two common
neighbors.

## New invariant: incidence-minor energy

For any eight-point set `S`, Cauchy-Binet gives

```text
det(7I+A[S])
  = sum over 8-block sets T of det(B[S,T])^2.
```

An induced cube and an induced Wagner graph have the same first block
intersection profile: 12 blocks meet the set twice, 32 meet it once, and 187
miss it. Nevertheless their exact minor energies differ:

```text
cube:   4,423,680,
Wagner: 4,439,040,
difference: 15,360.
```

Thus this higher-order incidence invariant distinguishes the two motifs where
the scalar profile does not.

The total eight-point energy is globally fixed by the spectrum:

```text
[t^8] (1+21t)(1+10t)^54(1+3t)^44.
```

The concrete next problem is to classify the nonzero `8 x 8` incidence
minors by partial-linear block configuration and determine whether the
prism-free codegree condition bounds the contribution of all other
eight-point types strongly enough to force a Wagner lower bound.

No sign strong enough for endpoint exclusion, literature novelty, graph, or
Conway-99 resolution is claimed.
