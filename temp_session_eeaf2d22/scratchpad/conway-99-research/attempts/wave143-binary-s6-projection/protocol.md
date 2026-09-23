# Wave143 protocol

## Frozen question

In each Arf branch, add

```text
M6 = epsilon*2^27*(2024484+(512/3)n3)
```

to the Wave137 rational ordinary/distinguished-split projection.  Determine
the exact rational projection range, provide explicit witnesses at `n3=708`
and `n3=4158`, and inspect the integral formal-enumerator layer.

## Evidence rules

- A rational optimum needs both a replayed witness and an exact bounding
  inequality.
- A fixed target is only rationally feasible after its complete witness
  replays all ordinary, split, signed-moment, and shadow rows.
- Integral equality-lattice statements use exact HNF arithmetic and exclude
  inequalities unless explicitly stated.
- Integer solver timeout or `UNKNOWN` supports no negative inference.
- Formal enumerators do not construct codes or graphs.

## Status labels

- Rational projection range: `DERIVED`.
- Fixed rational target witnesses: `CANDIDATE_EXACT`.
- Integral equality residue: `DERIVED`.
- Nonnegative integral feasibility: `UNKNOWN_HARD_TIMEOUT`.
- Code, graph, Conway-99, and novelty: `UNKNOWN`.
