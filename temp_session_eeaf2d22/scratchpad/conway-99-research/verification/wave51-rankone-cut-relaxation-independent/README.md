# Wave51 clean-room verification: fixed 174-cut relaxation

Status: **VERIFIED**, narrowly scoped.

## Verdict

The fixed Wave51 rational relaxation is exactly feasible. Independent
substitution confirms that the stored rational point satisfies:

- all 170 Wave44 equations;
- nonnegativity of all 208 order-seven variables;
- `2079 <= h11/4 <= 4158`;
- all 17 selected Wave45 cuts;
- all 136 selected Wave47 cuts; and
- all 21 selected Wave49 cuts.

The witness has support 136 and `h11/4=4158`. Exactly 66 cuts are tight:
5 Wave45, 46 Wave47, and 15 Wave49. The other 108 have positive exact
slack, with minimum `133056`. Its largest denominator has 272 decimal
digits.

The active equality rows have exact rational rank 209. This was certified by
rank 209 modulo the prime `2147483647`; an integer matrix with rank 209
modulo a prime has rank at least 209 over the rationals, and the 209 columns
give the matching upper bound.

Therefore an infeasibility/Farkas certificate does not exist for this fixed
finite bundle: the exact witness is a direct countercertificate.

## Source-status correction

The source package selected this finite cut bundle, constructed the witness,
replayed it, and labeled its own work `VERIFIED`/`VERIFIED_SCOPED`. That is
not compliant with the repository's discovery/verifier separation, and
`VERIFIED_SCOPED` is not an allowed claim label. Chronologically, the source
result was a `CANDIDATE`.

This sibling package does not edit or silently repair the source. It is the
independent verifier that promotes only the fixed-bundle arithmetic to
`VERIFIED`.

## Adversarial checks

- All 14 source files are pinned by byte hash, and four nested package
  manifests are replayed.
- The 170 Wave44 rows are rebuilt in frozen family order and their hash table
  is recomputed.
- All 17 Wave45 and all 2,657 Wave47 cut self-hashes are checked.
- The Wave47 selection is checked to be exactly one index-zero cut for each
  of 17 sources and eight families.
- The Wave43 order-six deck is independently derived.
- All 21 Wave49 coefficient-family and selected-direction self-hashes are
  checked, followed by 5,691 exact quadratic reconstructions.
- The reconstructed 174-cut catalog matches the source catalog hash.
- Every stored fraction, equation residual, cut slack, bound, support count,
  and active-rank claim is independently replayed.

The source `probe.py` and its numerical optimizer are not imported.

## Scope wall

This witness is rational and aggregate. It is not an integer count vector or
a graph. It tests only 174 selected cuts, not all verified directions or the
full positive-semidefinite matrices. Full PSD feasibility, integer
feasibility, endpoint `n3=4158`, a strict upper bound, graph construction,
Conway-99, and novelty remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe verification\wave51-rankone-cut-relaxation-independent\verify.py --validate
.\.venv\Scripts\python.exe -m unittest verification\wave51-rankone-cut-relaxation-independent\test_verify.py
```

The verifier enforces a 15% free-physical-memory floor.
