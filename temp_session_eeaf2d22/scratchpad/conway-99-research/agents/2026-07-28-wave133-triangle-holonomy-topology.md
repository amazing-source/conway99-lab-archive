# Wave 133 proof B: triangle holonomy and topological twist

```yaml
role: proof_b
date_utc: 2026-07-28T07:18:13Z
git_commit: aef7b93124f8caeb1a7487f58289436bc4118880
claim_label: CANDIDATE
scope: rooted-triangle permutation holonomy at the prism-free endpoint
inputs:
  - path: attempts/wave133-triangle-holonomy-topology/input-freeze.sha256
    sha256: 1857b018c782dd60c8fcd67616cd611d987cc0931c7c62bff4871d7c0e40f45f
method: exact fibre derivation, permutation identities, and finite topological controls
command: python -B attempts/wave133-triangle-holonomy-topology/exact_check.py --verify attempts/wave133-triangle-holonomy-topology/exact-results.json
outputs:
  - path: attempts/wave133-triangle-holonomy-topology/exact-results.json
    sha256: 15f37f5e52193b6ecf608df3944c15eaba891e16590867f4b71cbec2ef1f672a
limitations:
  - discovery cannot verify itself
  - controls are not a graph or SRG
  - endpoint and Conway-99 remain UNKNOWN
```

## Exact local invariant

For every graph triangle `T=(a,b,c)`, the three outside fibres have size
twelve, induce `6K2`, and are pairwise joined by perfect matchings.  Their
composition

```text
h_T=m_ZX o m_YZ o m_XY
```

is defined up to conjugacy; reversing orientation replaces it by its inverse.
A fixed point is exactly an induced triangular prism based at `T`.  Therefore
the endpoint makes every `h_T` a derangement.

A holonomy cycle of length `k` gives a cross-fibre cycle and triangle-link
component of length `3k`.  If `h(T)` is the cycle count and
`H=sum_T h(T)`, then

```text
sign(h_T)=(-1)^h(T),
product_T sign(h_T)=(-1)^H=(-1)^(chi+E-F).
```

This is the stronger exact necessary condition found in this lane.

## Exact null

Two partial 39-vertex triangle-star controls use the same within-fibre
one-factors `(1,2,3)`.  One has holonomy type `2^6`, sign `+1`, and six
cross cycles of length six.  The other has holonomy type `12`, sign `-1`,
and one cross cycle of length 36.  Both 36-vertex cores are cubic and
triangle-free, satisfy the inherited partial-star common-neighbor caps, and
have nonnegative forced Gram entries.

The topological control is endpoint-scale:

```text
231 abstract triangle vertices;
simple 36-regular relation graph with 4158 edges;
2079 quadrilateral faces, two per edge;
six C6 link components at every vertex;
H=1386, chi=-693;
global holonomy-sign product +1.
```

It is a connected nonorientable surface: odd `chi` rules out orientability.
Thus the tempting all-`222` parity proof fails at exactly the edge-twist
class.  An orientation double cover only squares the sign product and loses
the desired parity.

## Boundary

This is stronger than a local derangement control because it also realizes
the exact endpoint `E/F` counts, a simple 36-regular quotient, and all stated
link incidences.  It remains an abstract surface, not the `N3` relation of a
99-vertex graph.  A continuation must force orientability, constrain the
first Stiefel-Whitney class, or couple the twist data to the simultaneous
`B/H` equations.  The endpoint, the general bound, and Conway-99 remain
`UNKNOWN`.
