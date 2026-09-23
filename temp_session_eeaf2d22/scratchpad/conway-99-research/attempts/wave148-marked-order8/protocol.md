# Wave 148 marked order-eight protocol

## Frozen scope

Assume only that a finite simple graph is

```text
srg(99,14,1,2).
```

Use the complete order-seven and order-eight locally admissible class streams
from Wave 147.  Do not assume an automorphism, transitivity, the prism-free
endpoint, or a value of `n3`.

Let `x_H` denote the number of induced copies of an unrooted class `H`.

## Marked-vertex rows

Fix an unrooted order-seven class `H` and a rooted isomorphism type `tau=(H,u)`
with one pointwise-labelled vertex.  Let:

- `m_tau` be the number of vertices of `H` belonging to that rooted type;
- `d_tau` be their common degree inside `H`.

Count triples consisting of:

1. an induced copy of `H`;
2. a marked vertex `u` of type `tau`; and
3. an eighth vertex `w` outside the copy adjacent to `u`.

The target degree is 14, so the exact row is

```text
m_tau*(14-d_tau)*x_H
  = sum_K e_vertex(tau,K)*x_K,                     (V)
```

where `e_vertex(tau,K)` counts ordered choices `(w,u)` in `K` such that
deleting `w` leaves rooted type `tau` and `wu` is an edge.

## Marked ordered-pair rows

Fix a pointwise-labelled ordered pair type `tau=(H,u,v)`, `u!=v`.  Let:

- `m_tau` be the number of ordered pairs in that rooted type;
- `c_tau` be their number of common neighbors inside `H`;
- `target_tau=1` when `uv` is an edge and `target_tau=2` otherwise.

Count triples consisting of an induced copy of `H`, a marked ordered pair of
type `tau`, and an outside vertex adjacent to both roots.  The exact row is

```text
m_tau*(target_tau-c_tau)*x_H
  = sum_K e_pair(tau,K)*x_K,                       (P)
```

where `e_pair(tau,K)` counts ordered choices `(w,u,v)` in `K` such that
deleting `w` leaves rooted type `tau` and `w` is adjacent to both roots.

Ordered pair roots are pointwise labelled.  No division by a root-swap or
graph automorphism is made.

## Rooted canonicalization

Roots occupy the first one or two labels and are fixed pointwise.  Free
vertices are partitioned by:

- degree inside the seven-vertex graph; and
- their adjacency bit-vector to the fixed roots.

Every rooted isomorphism preserves these signatures.  Canonicalization
enumerates every permutation within each signature cell, so it is exact
rather than a color-refinement heuristic.

## Aggregate controls

For every order-seven class, summing (V) over all vertex types must give

```text
(7*14-2|E(H)|)*x_H
```

on the left.  For every order-eight class `K`, the corresponding sum of
right coefficients must equal

```text
sum_w degree_K(w)=2|E(K)|.
```

Summing (P) over all ordered-pair types must agree on each order-eight class
with

```text
sum_w degree_K(w)*(degree_K(w)-1).
```

These are consistency controls, not substitutes for the individual rows.

## Evidence boundary

- Emit integer rows and hashes without invoking a solver.
- Discovery work cannot verify itself.
- A future numerical feasibility result is reconnaissance only.
- A strict bound requires an independently replayed exact rational
  certificate.
- Stop if free physical memory falls below 15%.

