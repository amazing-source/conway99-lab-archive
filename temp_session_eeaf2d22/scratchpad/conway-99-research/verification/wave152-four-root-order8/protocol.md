# Wave152 clean-room verification protocol

## Frozen discovery inputs

- `attempts/wave152-four-root-order8/four_root_scout.py`
  SHA-256 `84866de40a2c06b826da40cef7f2f212aca3a0fdfb56d38b7df8a0ec2cd4f766`
- `attempts/wave152-four-root-order8/four-root-scout.json`
  SHA-256 `c3633fe3337c1910774e13c9a0841b17bb3f55df1d9800c673979016e877ce95`

Both hashes were recorded before either artifact was inspected.

## Separation boundary

The verifier will not import or execute `four_root_scout.py`. It will derive
the four-root flag semantics independently, implement separate enumeration
and exact arithmetic, and use the stored JSON only as a sealed claim/candidate
record for comparison.

## Scope

Verify the nine flag universes formed from four pointwise-labeled roots and
one unordered free pair at union orders 6, 7, and 8. Re-evaluate the Wave150
`x6/x7/x8` pseudowitness. Independently replay at least the exact negative
certificates for root masks 3 and 12, including flag semantics, totals,
integer scaling, and hostile-mutation rejection.

Any successful negative certificate refutes only that finite pseudowitness.
It is not an endpoint infeasibility certificate and cannot resolve the
underlying conjecture.

## Resource boundary

The verifier uses small exact-integer matrices and standard-library code only.
It will not launch parallel solver jobs or memory-intensive searches. Host
free memory was 33.51% at the start, above the required 15% reserve.
