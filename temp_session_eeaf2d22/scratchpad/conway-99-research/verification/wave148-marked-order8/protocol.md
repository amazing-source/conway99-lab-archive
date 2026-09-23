# Wave148 clean-room marked order-eight protocol

Status: `PREPARED_AWAITING_DISCOVERY_MANIFEST`.

This protocol was derived without inspecting any `attempts/wave148-*` path
and without communicating with a Wave148 discovery agent. It freezes what an
independent verifier will accept as the marked order-eight equations.

## Inputs

The checker may use only:

1. the frozen target `srg(99,14,1,2)`;
2. the published Wave147 order-seven and order-eight class streams;
3. the published Wave147 ordinary deletion artifact; and
4. first-principles graph enumeration.

No Wave148 code, result, labels, row order, or model builder may be imported
before its sealed manifest is handed off.

## Root conventions

All graph copies are induced and unlabelled, but marks are pointwise fixed.

- A vertex-root type is an order-seven graph with one marked vertex.
- A pair-root type is an order-seven graph with an **ordered** pair of
  distinct marked vertices.
- Rooted canonicalization may permute only unmarked vertices. It must never
  swap or move a marked root.
- Coefficients count concrete markings. No automorphism-group division is
  permitted.

For an unrooted order-seven class `H`, let `m(tau,H)` be the number of
vertex or ordered-pair markings of rooted type `tau`.

## Marked degree rows

For a vertex-root type `tau=(H,u)`, double-count triples

```text
(S,u,x)
```

where `G[S]` is an induced copy of `H`, `u` is the marked vertex, `x` is
outside `S`, and `x~u`.

The exact target row is

```text
(14-deg_H(u))*m(tau,H)*x_H
  = sum_K a(tau,K)*x_K,
```

where `a(tau,K)` counts ordered choices `(x,u)` in the order-eight class
`K` such that deleting `x` leaves rooted type `tau` and `x~u`.

The complementary non-neighbor row follows from this row and ordinary
deletion:

```text
(78+deg_H(u))*m(tau,H)*x_H
  = sum_K (d(tau,K)-a(tau,K))*x_K.
```

It is therefore a derived control, not a required independent row.

## Marked common-neighbor rows

For an ordered pair-root type `tau=(H,u,v)`, let

```text
target(u,v) = 1 if u~v, else 2
c_H(u,v) = number of common neighbors of u,v inside H.
```

Double-count quadruples `(S,u,v,x)` with `x` outside `S` adjacent to both
marked vertices. The exact row is

```text
(target(u,v)-c_H(u,v))*m(tau,H)*x_H
  = sum_K b(tau,K)*x_K,
```

where `b(tau,K)` counts ordered choices `(x,u,v)` in `K` such that deleting
`x` leaves rooted type `tau` and `x` is adjacent to both roots.

The residual must be nonnegative. If it is zero, every right-hand
coefficient must also be zero.

## Required coefficient invariants

For every order-eight class `K`:

```text
sum_tau a(tau,K) = 2*|E(K)|

sum_tau b(tau,K)
  = sum_x deg_K(x)*(deg_K(x)-1).
```

The first identity counts oriented edges `(x,u)`. The second counts ordered
neighbor pairs `(x,u,v)`.

For every order-seven class `H`:

```text
sum_vertex_types m(tau,H) = 7
sum_pair_types   m(tau,H) = 7*6 = 42.
```

Every order-eight deletion column must still sum to eight in the ordinary
Wave147 layer.

## Small exact semantic controls

The clean-room checker fixes these coefficients:

1. Degree row, empty order-seven graph to one-edge order-eight graph:
   coefficient `2`.
2. Ordered nonedge common-neighbor row, empty order-seven graph to a
   two-edge path plus five isolates: coefficient `2`.
3. Ordered edge common-neighbor row, one-edge order-seven graph to a
   triangle plus five isolates: coefficient `6`.

These are direct marking counts and are independent of any row ordering.

## Rook-graph positive control

Re-evaluate the same coefficient tensors on the `3 x 3` rook graph with
parameters `srg(9,4,1,2)`.

- Count all 36 induced order-seven subsets and all 9 induced order-eight
  subsets.
- Use `k=4`, `lambda=1`, `mu=2`, and ordinary deletion multiplier `9-7=2`.
- Every marked degree and marked common-neighbor row must hold exactly.
- Zero-residual pair rows must have zero evaluated right side.

This control tests row semantics on a realized SRG without asserting that the
order-99 target exists.

## Handoff audit

After a sealed Wave148 manifest arrives, the verifier will:

1. freeze and replay every manifest hash;
2. reject any convention inconsistent with the rooted equations above;
3. translate discovery labels to clean-room rooted canonical keys;
4. compare complete row dictionaries, not just dimensions;
5. run hostile mutations of a degree coefficient, pair coefficient, root
   ordering, multiplicity, and residual;
6. replay the rook control; and
7. preserve `UNKNOWN` for every solver/bound claim lacking an exact
   certificate.

No Wave148 artifact is verified by this preparation package.
