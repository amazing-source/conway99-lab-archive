# Protocol correction 1

Recorded: 2026-07-24T00:26:46Z

The frozen protocol misinterpreted the assignment's `21E6^{-1}` as a possible
factor-2 scaled inverse/dual. The intended expression is twenty-one times the
inverse, `21 E6^{-1}`.

The original `protocol.md` is preserved byte-for-byte at its pre-correction
SHA-256
`f52683741f227d8e9c4f80b5474e73744a235b5e4383a2996a1439ed4b84742f`;
its mistaken interpretation and `G03` wording are not silently replaced.

Corrective query `R00`, executed in each usable discovery index with the same
per-service review cap as the frozen protocol, is:

`"21 E6 inverse" OR "21 E_6^{-1}" OR "21E6^{-1}"`

This query is a transparent correction to the frozen target, not post-hoc
synonym expansion. Its execution and results are recorded in the query ledger,
and the original defect is retained in `failures.md` and the run limitations.
