# Wave 52 independent coherent-closure audit

## Verdict

`VERIFIED` at the stated local scope. The discovery package correctly
computes the completion-free one-root 2-WL closures and correctly reports a
null result. It does not exclude the prism-free endpoint, construct a graph,
improve `n3 <= 4158`, or establish novelty. Those statuses remain `UNKNOWN`.

The discovery package was frozen before comparison. Its package manifest has
SHA-256
`4b25853eca8ed96f5beea74e4e51ef744259a8436510d23c443b8e3f140692b3`,
and its exact result has SHA-256
`75951c260b3a0dda55c2acc324fc6c60322778a72eabb049445d3a87f982e2e9`.
The verifier imports no discovery code.

## Independent mathematical derivation

Let the root graph triangle be `R={a,b,c}` in a putative
`srg(99,14,1,2)`.

Because adjacent vertices have exactly one common neighbor, the neighborhood
of any graph vertex is seven disjoint edges. Hence exactly seven graph
triangles contain that vertex. One is `R`, leaving six petals through each of
`a`, `b`, and `c`, or 18 petals total.

Petals through the same root vertex share that vertex and form a `K6`.
Petals through different root vertices cannot share an external vertex:
otherwise an adjacent pair such as `a,b` would have a second common neighbor
besides `c`. Thus the induced `K` graph is exactly `3K6`.

For a petal `P={a,x,x'}` and the opposite `b` sector, `x` and `b` are
nonadjacent. Their two common neighbors are `a` and one additional point in a
unique `b`-petal. The same is true for `x'`. The two additional points are
distinct by `lambda=1`, and prism-freeness prevents them from occupying the
same `b`-petal. Consequently `P` has exactly two `B` neighbors and four `C`
neighbors in that sector; `D` has degree zero. The same holds for all six
directed sector pairs.

The global relation valencies follow independently. There are
`99*14/6=231` graph triangles, so a root has `231-1-18=212` disjoint
triangles. If `d,c,b` count disjoint triangles with zero, one, or two cross
edges, then

```text
d + c + b = 212.
```

The 36 edges from a root vertex to an outside vertex are each counted in six
disjoint triangles, giving

```text
c + 2b = 216.
```

For each of the three pairs of root vertices, their two 12-point external
neighbor sets have a forced perfect matching: a point on one side is
nonadjacent to the opposite root vertex and therefore has exactly one
additional common neighbor there. This gives 12 cross-edge pairs per root
edge and

```text
b = 3*12 = 36.
```

Thus `(d,c,b)=(32,144,36)`, so the global relation valencies in the frozen
order `(I,K,D,C,B)` are `(1,18,32,144,36)`.

## Independent finite checks

2-WL colors ordered pairs. At each proper round the verifier replaces the
current color of `(u,v)` by that color together with the exact multiset of
color pairs `(color(u,w),color(w,v))` over every intermediate node `w`.
Stable colors were checked to have constant intersection counts.

| Check | Independent result |
|---|---:|
| Rooted partial object | 19 nodes |
| Partial color trajectory | `6` |
| Partial diagonal classes | `1,18` |
| Cap-incidence object | 163 nodes |
| Node roles | `1,18,36,108` |
| Cap-incidence trajectory | `26,38,47` |
| Stable nonzero intersection parameters | 1,036 |
| Canonical completion profiles | 64 |
| Exact-two caps per completion | all 36 pass |
| Distinct completion fingerprints | 39 |
| Stable completed-color range | 8 to 361 |
| Independent/discovery profile comparisons | all 64 pass |
| Independent/discovery fingerprint equivalences | all 4,096 pass |

The four factor types are the only cycle half-length partitions of a simple
2-regular bipartite graph on `6+6` vertices:
`(6)`, `(4,2)`, `(3,3)`, and `(2,2,2)`. The verifier explicitly constructs
each factor with 12 distinct edges and degree two at every endpoint.

The all-`(6)` profile has 13 stable colors, while all-`(2,2,2)` has 8.
Therefore a closure computed after selecting `B/C` edges genuinely depends on
arbitrary completion data. It is not a forced endpoint coherent
configuration.

## Hostile checks

The verifier rejected all five mutations:

1. deleting a selected `B` edge;
2. duplicating a selected endpoint pair;
3. changing one candidate-to-cap incidence;
4. collapsing a candidate's two endpoints;
5. lowering the verifier's 20 percent memory floor.

## Boundary

The 163-node object realizes incidence roles and cap membership, but 2-WL
does not assign Boolean truth values to candidate `B` nodes. The 64 canonical
profile triples are diagnostic representatives, not all labelled joint
completions. A positive local cap completion need not extend to any
99-vertex graph. No automorphism, transitivity, or association-scheme
assumption is used.
