# Hostile-test ledger

The final suite contains 20 tests.

Core mathematical and integrity tests:

- regenerate all eleven positive partitions and all 10,395 distinct labelled
  matchings;
- reproduce the full matching-to-partition census;
- compare the singular 39-block reduction with a direct dense rank;
- use a legal matching target as a positive control for the vectorized
  matching-form checker and reject a one-entry diagonal mutation;
- reject malformed third-fibre matchings and nonbijective borders;
- inspect the unique all-odd `3+3` diagonal survivor and reject its illegal
  off-diagonal target;
- reject omitted local types, minimum-`F` undercounts, injected rank-25 hits,
  rank-floor inflation, endpoint inflation, and stale frozen inputs.

Post-freeze comparison tests:

- verify the specified discovery SHA exactly;
- replay every discovery/primary/secondary partition count comparison;
- reject a mutated primary canonical-target count.

The positive control tests only checker sensitivity. It is not a graph,
legal rank-25 completion, endpoint witness, or counterexample.
