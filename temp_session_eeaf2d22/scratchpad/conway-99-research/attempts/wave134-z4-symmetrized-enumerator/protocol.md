# Wave134 protocol

## Frozen scope

Assume only that a hypothetical adjacency matrix satisfies the full
`srg(99,14,1,2)` equations. This lane assumes no rank endpoint, root
normalization, graph automorphism, motif count, or value of `n3`.

The investigated object is

```text
C=row_Z4(A)
```

and its exact three-variable symmetrized weight enumerator. The binary
minimum-distance and high-weight consequences are imported only from the
sealed Wave131 and Wave132 packages.

## Discovery/verification separation

- `discover_rational.py` asks an exact rational-arithmetic solver for a
  primal enumerator.
- `exact_check.py` reconstructs the Smith/type calculation, forced word
  tables, sparse transform, zero rows, totals, and every stored
  coefficient independently with standard-library rational arithmetic.
- The integral scout is separately bounded. A timeout remains `UNKNOWN`
  and is not evidence of infeasibility.

## Claim boundary

- Smith/type, torsion symmetry, transform factorization, and forced
  aggregate word counts: `DERIVED`.
- Any replayed rational point: `CANDIDATE`.
- Integral feasibility, realizability by a quaternary code, graph
  existence, and Conway-99: `UNKNOWN`.

No discovery process promotes its own output to `VERIFIED`.
