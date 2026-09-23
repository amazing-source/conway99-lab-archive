# Wave 43 branch-15 two-triangle limits and failed routes

## Exact closure does not move

The 40,800 new clauses simplify to 34,340 distinct active clauses at the Wave
42 closure. Every active clause still has four unassigned negative literals.
There is therefore no new generalized unit and no contradiction. The exact
fixed point remains 830 forced variables, 174 of them primary graph edges.

This null result is exact for the published clause family. It is not evidence
that branch 15 is satisfiable.

## Bounded failed-literal propagation does not use the new cuts

The 32 unfixed coordinate-triangle controllers with the largest active-cut
incidence were selected deterministically; ties were resolved by increasing
variable ID. Both polarities were propagated through the complete frozen
Wave 37 formula, the Wave 42 delta, and the new raw delta.

All 64 probes remained noncontradictory. Although positive assumptions caused
up to 100 additional assignments through the old formula, zero derivations
came from the new coordinate-pair rows. Thus:

```text
candidate implications:                 0
doubly failed variables:                0
coordinate-delta sourced derivations:   0
endpoint cases closed:                  0
```

Unprobed variables and deeper decision trees remain open. Extending shallow
lookahead without a proof-producing terminal strategy would be a diagnostic,
not a branch proof.

## The family is not the complete prism encoding

The exact family covers two triangles only when both are coordinate-anchored
and both controller variables are unfixed at the Wave 42 closure. It omits
prisms in which either triangle lacks a coordinate anchor. The prior static
complete-family estimate exceeds 24 billion residual-only prism clauses, so
blind materialization is not a bounded continuation on this host.

## No solver terminal

No target solver was launched. A short timeout or `NO CONCLUSION` proof trace
would not improve the mathematical status. Any future `UNSAT` claim must
retain its formula and proof and pass independent VeriPB/CakePB or an
equivalently rigorous proof-checking route. A candidate model must be decoded
and checked as a complete `srg(99,14,1,2)` and globally prism-free.

