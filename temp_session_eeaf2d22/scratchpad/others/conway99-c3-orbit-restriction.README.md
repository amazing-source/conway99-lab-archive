# Conway-99 C3 orbit restriction in Lean 4

This standalone Lean 4.27.0 project formalizes the arithmetic and matrix core of
the following restriction:

> If a hypothetical Conway 99-graph has a fixed-point-free automorphism of order
> three, then its 33 vertex-orbits contain either 6 or 27 internal triangles.

The matrix-facing main theorem is
`Conway99C3Orbits.triangularOrbitCount_eq_six_or_twentySeven`. The clean
arithmetic interface is
`count_eq_six_or_twentySeven_of_trace_eigenvalueMultiplicities_and_congruence`;
it assumes only the named range, spectral trace/multiplicity, and triangle-orbit
congruence hypotheses.

## Formalized

- The quotient identity is stated as
  `B * B = 12 I - B + 6 J`.
- A nonzero, zero-sum eigenvector satisfying the quotient identity has
  eigenvalue `3` or `-4`.
- The quotient diagonal classification (`0` for an independent orbit and `2`
  for a triangular orbit) implies `trace B = 2t`.
- The spectral trace formula and `0 ≤ t ≤ 33` imply
  `t ∈ {6, 13, 20, 27}`.
- The triangle-action congruence `3 ∣ (231 - t)` removes 13 and 20.

## Explicit graph-to-matrix hypotheses

This project does not yet construct the quotient matrix from a `SimpleGraph
(Fin 99)` and its automorphism. In `C3QuotientCertificate`, the following remain
certificate fields:

1. quotienting the strongly-regular adjacency identity;
2. quotient regularity (eigenvalue 14 on the all-one vector);
3. classification of each three-vertex orbit as independent or triangular;
4. the trace formula from symmetry/diagonalizability and eigenvalue
   multiplicities;
5. the action-on-triangles congruence, including the claim that exactly the
   internal orbit triangles are setwise fixed.

These boundaries prevent the final theorem from claiming graph facts that have
not been mechanically connected to the pinned Formal Conjectures graph
definition.

## Build

The dependency is pinned to Formal Conjectures commit
`e751934294a381afd2d5fc1124c5953c8e25f9fa`, whose manifest pins Mathlib commit
`a3a10db0e9d66acbebf76c5e6a135066525ac900`.

Install [elan](https://github.com/leanprover/elan), then run:

```sh
lake exe cache get
lake --wfail build
```

The principal theorems use no `sorry`, `admit`, custom axioms, or native
evaluation. Their printed axiom set is exactly
