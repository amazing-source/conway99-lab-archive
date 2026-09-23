# Wave 32 rooted discovery correction ledger

## Prepublication verifier correction

The first frozen discovery package was audited byte-for-byte by the
independent verifier.  Its theorem derivation survived, but the hostile
partial-control metadata contained a false residual-degree list:

```text
v1 exact_check.py / exact-results.json: 8,12,14
independent reconstruction:             10,12,14
```

The exact v1 bytes remain identifiable as:

```text
exact_check.py       41e077321fa691a3916da50e992a09d43d4f2d252cae39030bc2d7663bd60e97
test_exact_check.py  38b7023a66c4b3305cfb080d27cbf39dd5330dab79eaa85eb7c0fcbd3104dd76
exact-results.json   6ff9844994c2605266feaad96b4a4ebaf193b5be437bd9e4b21dbf7b98860d99
artifact manifest    a2dd5896871dda4d0dc54b56d9cb081993079ad03241113e1a36bb0ab972d291
```

The verifier reconstructed the partial graph independently and obtained

```text
current outside degrees:    4^42,2^28,0^15
remaining degrees to 14:   10^42,12^28,14^15.
```

The repaired discovery checker now computes both distributions, asserts
them, and tests the corrected scope sentence.  It also makes the hostile
eigenvalue-three amplitude metadata depend on the supplied eigenvalue,
rather than reusing the actual eigenvalue-four prose and coordinate bound.

The designated independent verifier does not rely on this repaired
discovery code.  Its clean-room suite separately verifies the main
`46 -> 32 -> 16 -> 1` reduction and records the v1 defect.  Root exclusion,
partial-control extendibility, the rooted endpoint, `n3=708`, Conway-99,
and novelty remain `UNKNOWN`.
