# Wave 45 clean-room verification protocol

Freeze time: 2026-07-27, before opening any file under
`attempts/wave45-flag-moment/`.

Role: verifier. Discovery claims are untrusted inputs and cannot be repaired
silently. This lane writes only under `verification/wave45-flag-moment/` and
`agents/2026-07-27-wave45-flag-moment-verifier.md`.

## Supplied claim, not yet accepted

The orchestrator reports that the frozen Wave 43 and Wave 44 count witnesses
each have an exact negative integer direction in a vertex-root `17 x 17`
matrix. It also reports a cutting-plane continuation. Neither statement is
evidence until the independent construction below is frozen and compared.

## Mathematical object

For a root type `tau`, let a `tau`-flag be an induced graph on four vertices
with its root labels fixed pointwise:

- `vertex`: one labelled root and three unlabelled vertices;
- `edge`: two ordered labelled roots required to be adjacent, and two
  unlabelled vertices;
- `nonedge`: two ordered labelled roots required to be nonadjacent, and two
  unlabelled vertices.

Unlabelled vertices may be permuted when canonicalizing a flag; labelled
vertices may not be moved or exchanged. The flag universe contains exactly
the locally admissible flags for `(lambda,mu)=(1,2)`: inside the flag, an
adjacent pair has at most one common neighbor and a nonadjacent pair has at
most two common neighbors. No automorphism of a hypothetical 99-vertex graph
is assumed.

For an actual graph `G` and an ordered root embedding `rho` of type `tau`,
let `z_rho[i]` count the unlabelled subsets that induce flag `i` with `rho`.
Define the finite integer Gram matrix

```text
M_tau(G) = sum_rho z_rho z_rho^T.
```

Therefore, for every integer vector `c`,

```text
c^T M_tau(G) c = sum_rho (c dot z_rho)^2 >= 0.
```

This is a finite exact outer-product identity, not an asymptotic flag-density
normalization.

## Linearization in induced-class counts

For a vertex root, a pair of four-vertex flags has union order four through
seven. For an ordered pair root, its union has order four through six.

For every locally admissible unrooted induced class `H` of an eligible order,
the clean implementation will count tuples `(rho,A,B)` where:

1. `rho` is a root embedding of the requested type in `H`;
2. `A` and `B` are the correctly sized unlabelled selections;
3. `rho union A union B` is all of `V(H)`;
4. the two induced rooted flags have indices `(i,j)`.

The resulting exact integer coefficient `a_tau,H[i,j]` gives

```text
M_tau = sum_H a_tau,H N_H,
```

where `N_H` is the number of induced copies of unrooted class `H`. The union
condition makes the representation unique and includes overlap terms rather
than incorrectly treating two selections as disjoint.

Unrooted classes will be independently enumerated through order seven and
canonicalized under all vertex permutations. Rooted flags will be
canonicalized independently under permutations fixing labels pointwise.
Coefficient streams will be serialized in a stable, explicitly documented
order and committed by SHA-256 before discovery inspection.

## Recovering lower-order counts from a seven-class witness

If a supplied aggregate witness gives only order-seven counts `x_J`, the
clean verifier will derive order-`m` counts using the exact deck identity

```text
sum_J x_J d_m(H,J) = binom(99-m,7-m) N_H,
```

where `d_m(H,J)` is the number of `m`-subsets of class `J` inducing `H`.
Every division must be exact and all resulting counts nonnegative. Failure is
a refutation of the aggregate witness as input to the Gram test.

## Independent controls

The Petersen and Clebsch graphs will be constructed from explicit adjacency
rules, not loaded from discovery output. For every root type:

1. compute `M_tau` directly as a sum of outer products;
2. enumerate all induced classes through the required union order;
3. evaluate the independently generated coefficient stream;
4. require exact entrywise equality;
5. require symmetry and exact nonnegative quadratic values for hostile test
   directions;
6. verify the all-ones identity

```text
1^T M_vertex 1 = n * binom(n-1,3)^2,
1^T M_edge 1 = (# ordered edges) * binom(n-2,2)^2,
1^T M_nonedge 1 = (# ordered nonedges) * binom(n-2,2)^2.
```

Petersen uses `(10,3,0,1)` and Clebsch uses `(16,5,0,2)`. Their smaller
common-neighbor parameters are compatible with the target local-admissibility
caps.

## Hostile tests

The verifier will reject:

- moving or swapping a fixed root label during flag canonicalization;
- counting unordered rather than ordered pair roots;
- omitting pairs of selections that overlap outside the labels;
- including a tuple whose union is not the full induced class;
- changing one coefficient, one witness count, one direction entry, or one
  right-hand-side/deck divisor;
- any nonintegral lower-order count derived from a seven-class witness;
- any coefficient stream whose canonical SHA-256 differs after freeze;
- any claimed negative direction whose exact integer quadratic value is not
  negative under the independently reconstructed matrix.

## Discovery comparison and status wall

Only after the clean coefficient stream, controls, and tests are frozen may
this lane open `attempts/wave45-flag-moment/`. Comparison will cover:

- flag descriptors and their index mapping;
- every sparse coefficient-stream record;
- canonical stream SHA-256 values;
- every supplied integer direction and exact quadratic value;
- Petersen and Clebsch controls;
- each cutting-loop iteration, including the witness attacked and the exact
  solver/certificate outcome.

A negative quadratic value refutes only the supplied aggregate count vector;
it does not refute the endpoint. A finite list of cuts is not a complete
search. The endpoint `n3=4158`, a strict upper bound, and Conway-99 remain
`UNKNOWN` unless a complete exact infeasibility or graph certificate is
independently reproduced.

No solver exit status, floating eigenvalue, model confidence, or absence of
another witness is a certificate. Memory must remain at least 15% free; this
lane starts no persistent background process.
