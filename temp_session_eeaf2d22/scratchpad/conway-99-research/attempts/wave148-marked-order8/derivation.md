# Derivation of the marked order-eight rows

## 1. Class variables

Let `H` be one of the 208 locally admissible unrooted order-seven classes and
let `K` be one of the 916 locally admissible unrooted order-eight classes
from Wave 147.  Write `x_H` and `x_K` for their induced-copy counts in a
hypothetical `srg(99,14,1,2)`.

The construction works with rooted isomorphism types, not a selected
labelling and not a graph automorphism orbit.

## 2. Marked vertices

Fix a rooted type `tau=(H,u)`.  Every copy of `H` contains `m_tau` vertices
of this rooted type.  The marked vertex has `d_tau` neighbors already inside
the copy.  Since its full degree is 14, exactly

```text
14-d_tau
```

vertices outside the seven-set are adjacent to it.  Counting an induced copy,
a mark of type `tau`, and an adjacent outside vertex gives

```text
m_tau*(14-d_tau)*x_H.                              (1)
```

Alternatively, first choose the induced order-eight class `K`, then choose a
deleted vertex `w` and a surviving marked vertex `u`.  Retain the choice when:

1. deleting `w` leaves unrooted class `H`;
2. the surviving rooted graph has type `tau`; and
3. `wu` is an edge.

Let the number of such choices inside `K` be `e_vertex(tau,K)`.  Then

```text
m_tau*(14-d_tau)*x_H
  = sum_K e_vertex(tau,K)*x_K.                    (V)
```

Every coefficient is a nonnegative integer obtained by direct enumeration.

## 3. Marked ordered pairs

Now fix a pointwise-labelled ordered pair type `tau=(H,u,v)`, with `u!=v`.
The target common-neighbor count is

```text
t_tau = 1 if uv is an edge,
t_tau = 2 if uv is a nonedge.
```

If `c_tau` common neighbors already lie inside `H`, exactly

```text
t_tau-c_tau
```

common neighbors lie outside the seven-set.  With `m_tau` ordered pairs of
this rooted type in every copy of `H`, double counting gives

```text
m_tau*(t_tau-c_tau)*x_H
  = sum_K e_pair(tau,K)*x_K.                      (P)
```

Here `e_pair(tau,K)` counts triples `(w,u,v)` in `K` for which deleting `w`
leaves rooted type `tau` and `w` is adjacent to both pointwise-labelled
roots.  No factor of two is divided out.

Local admissibility ensures `t_tau-c_tau>=0`.  It vanishes for 893 pair
types.  The enumerator independently finds no order-eight extension term in
exactly those same 893 rows.

## 4. Exact rooted canonicalization

For one or two pointwise-fixed roots, every free vertex receives the
signature

```text
(degree in H, adjacency bit-vector to the roots).
```

A rooted isomorphism preserves these signatures.  The checker places the
roots first, places signature cells in a fixed order, and enumerates every
permutation within each cell.  Minimizing the relabelled adjacency mask over
that complete set gives an exact rooted canonical key.

This reduces runtime but imposes no graph symmetry.

## 5. Aggregate controls

Summing (V) over all rooted vertex types of a fixed `H` gives

```text
sum_u (14-degree_H(u))
  = 7*14-2|E(H)|.                                  (2)
```

On a fixed order-eight class `K`, summing the right coefficients over all
rows counts, for each deleted `w`, one mark for every neighbor of `w`:

```text
sum_tau e_vertex(tau,K)
  = sum_w degree_K(w)
  = 2|E(K)|.                                       (3)
```

Similarly, summing (P) counts pointwise ordered pairs of neighbors of the
deleted vertex:

```text
sum_tau e_pair(tau,K)
  = sum_w degree_K(w)*(degree_K(w)-1).             (4)
```

The checker verifies (2)--(4) over all 208 and 916 class columns.  The test
suite separately reconstructs (3)--(4) from the compressed row artifact.

## 6. Exact artifact

The solver-neutral row artifact contains 944 vertex rows and 4,440 ordered
pair rows.  Its canonical uncompressed payload has SHA-256

```text
3bdfdafa7e1675bf1fe160f44f1fea0e53792b5c2e87e0bfb529a15bd1cc2a8f.
```

The compressed file is deterministic (`gzip` timestamp zero) and contains
only integer masks, multiplicities, coefficients, and row metadata.

## 7. Status wall

These equations complete the marked degree/common-neighbor linear layer
requested after Wave 147.  They have not been combined with the two PSD
blocks in an optimizer.  Consequently:

```text
combined feasibility:       UNKNOWN_NOT_RUN
strict n3 upper bound:       UNKNOWN
rational certificate:       NOT OBTAINED
graph construction:         none
Conway-99:                   UNKNOWN
```

