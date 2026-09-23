# Wave 43 proof-agent report: all rank-33 lifts

## Assignment

Generalize the Wave 42 component-equality and exact three-way-matching
reduction from canonical mask `51739` to every one of the 264 canonical
triangle-free rank-33 lifts. Seek an exact forced-Gram or component-parity
exclusion before attempting a full solver.

## Result

Classification: **DERIVED, pending independent verification**.

The complete labelled 18-bit lift census was reconstructed from the
SHA-frozen Wave 41 generator. Every one of the 264 rank-33 lifts has:

```text
component sizes:          12 + 24
component fibre balances: (4,4,4) + (8,8,8)
forced Gram minimum:      0
component Cauchy failures: 0
odd/nonuniform balances:   0
```

Consequently every outside column must meet the small component twice, so
the Wave 42 three-way-matching reduction applies to all 264 lifts without
an automorphism assumption. The exact candidate-census distribution is:

```text
(118718,49736,45032): 48
(131908,54560,49328): 48
(132196,54736,49520): 24
(132250,54560,49328): 48
(132402,54648,49424): 96
```

The triple in each row is support-legal, component-legal, and
mixed-nonnegative candidate counts.

## Null boundary

No lift is excluded. Positive candidate counts are not a simultaneous
60-column `B`, and the five numerical rows are not asserted to be five
isomorphism classes. The compatible outside graph `H`, endpoint, and target
remain unknown.

## Verification request

The verifier should independently regenerate the canonical quotient and all
264 masks, reconstruct `BB^T` from the graph identity without importing the
discovery helpers, compare the ordered mask stream and all per-mask component
and candidate counts, and attack the scope wall explicitly.
