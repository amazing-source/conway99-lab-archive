# Wave 43 all-rank-33-lifts verifier

Status: `VERIFIED_SCOPED`. The all-`222`, `r3=12` endpoint branch, the
prism-free endpoint, and Conway-99 remain `UNKNOWN`.

This implementation binds but does not import the frozen Wave 41 source. It
independently enumerates all 4,050 normalized quotient forms, recovers the
canonical rank-eleven quotient, reconstructs every endpoint-pairing mask, and
uses batched dense Gaussian elimination over `F7`.

Exact independent census:

```text
endpoint-pairing masks:                262,144
triangle-free masks:                    37,378
rank_F7(3I-A_X) = 32 / 33 / 34: 264 / 7,348 / 29,766
canonical K39-rank-33 masks:                264
```

For each of the 264 masks, the verifier independently reconstructs the forced
`BB^T`, components, fibre balances, Cauchy moments, integer kernel vectors,
modular Gram rank, four-cycle count, and all 216,000 candidate pair triples.
Every complete per-mask record matches discovery exactly.

The five numerical candidate-census rows occur with multiplicities
`48, 48, 24, 48, 96`. These are numerical census classes, not a claim of five
isomorphism classes. No completed-graph automorphism was used.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave43-all-rank33-lifts\independent_check.py `
  --verify verification\wave43-all-rank33-lifts\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s verification\wave43-all-rank33-lifts -p "test_*.py" -v
```

Every lift survives these necessary filters. The package constructs neither a
simultaneous sixty-column incidence matrix `B` nor a compatible outside graph
`H`; it does not exclude the endpoint or improve the general upper bound.
