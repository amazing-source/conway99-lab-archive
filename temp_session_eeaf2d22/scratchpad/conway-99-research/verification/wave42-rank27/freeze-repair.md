# Precomparison freeze repair

The first precomparison mathematical result was generated before any Wave 42
discovery file was opened and frozen at

```text
bb4c1fa6d8c46343df26caa475895906d22c8f80000e8225e6a1f4bb9eb760eb
```

After discovery comparison began, the required byte-for-byte full replay
failed.  The sole cause was that the JSON serialized wall-clock
`elapsed_seconds` fields for each lane and the whole run.  Those values are
necessarily nondeterministic.

The repair removes only those timing fields and the unused timer import and
assignments.  It does not change the graph construction, finite-field
arithmetic, rank reduction, permutation or matching enumeration, right
kernels, equality targets, vectorized minor filters, exact rank-at-most-one
predicate, all-odd pivot CSP, coverage accounting, theorem, or scope wall.

The repaired implementation and deterministic result receive a new freeze.
Both the failed original freeze and this repair are retained rather than
silently overwritten.
