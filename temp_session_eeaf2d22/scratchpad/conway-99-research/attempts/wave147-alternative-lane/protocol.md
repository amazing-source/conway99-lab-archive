# Wave 147 protocol

## Frozen target

Assume only that a finite simple graph satisfies

```text
srg(99,14,1,2).
```

Do not assume vertex transitivity, an automorphism, the prism-free endpoint,
or an `n3` value while constructing the model.

## Flag families

Use two pointwise-labelled ordered roots:

1. an ordered adjacent pair;
2. an ordered nonadjacent pair.

Add three unordered free vertices.  Retain every order-five flag satisfying
the necessary induced-subgraph caps:

```text
adjacent pair:    at most one common neighbor,
nonadjacent pair: at most two common neighbors.
```

For each root embedding `theta`, count free triples by their rooted flag
class.  Sum the resulting integer outer products.  No division by an
automorphism group is allowed.

## Coefficient convention

For each locally admissible unrooted class `H` of order five through eight,
enumerate:

- every ordered root embedding of the declared relation; and
- every ordered pair of free triples whose union is all vertices of `H`
  outside the roots.

The integer embedding total is the coefficient matrix `C_H`.  Hence

```text
M_sigma = sum_H x_H C_H.
```

The overlap size of the free triples is `8-|H|`.

## Order-eight class stream

Start from the frozen 208 order-seven classes.  Extend each class by every
one of the `2^7` possible neighborhoods of a new vertex, reject local
`lambda/mu` violations, and canonically quotient by every
degree-preserving permutation.  This is a complete orbit construction:
deleting any vertex from an order-eight graph leaves an order-seven class.

For each order-seven class `H`, include the ordinary deletion identity

```text
92*x_H = sum_K d(H,K)*x_K,
```

where `d(H,K)` counts vertices of `K` whose deletion gives `H`.

## Evidence rules

- The discovery package cannot verify itself.
- Numerical infeasibility, a negative floating eigenvalue, or solver status
  is not a bound.
- A strict upper bound requires a replayable rational SDP dual or a separate
  proof.
- A rational feasible point is a null control, not a graph.
- Stop computational work if free physical memory falls below 15%.

