# Wave 110 verification

Verdict: `VERIFIED_WITH_EVIDENCE_BOUNDARY`, for the frozen conditional
encoding only.

The lex-CNF is equivalent to Boolean lexicographic order. The shared
power-of-two potential correctly proves that every same-pattern relabeling
orbit has a representative satisfying all 50 external-row comparisons at
once. Comparing only columns outside the row's own class is sufficient and
avoids an unsafe within-class canonicalization.

The `e(X0)=0,1,2,3` split covers all labelings and fixes no incompatible
canonical `X0` representative. The exact submission counts independently
reconstruct as 325,852 variables, 978,711 CNF clauses, 4,873 exact-cardinality
rows, and 9,746 native at-most constraints.

All four archived hashes match. Four fresh 45-second replays also returned
`UNKNOWN_TIMEOUT`, while preserving at least 56% free physical memory.

No graph, UNSAT, motif exclusion, Conway-99 result, or novelty claim follows.

Reproduce:

```powershell
python -B verification\wave110-c4boxk3-symmetry-sat\independent_verify.py
python -B -m unittest discover `
  -s verification\wave110-c4boxk3-symmetry-sat -p "test_*.py" -v
python -B -m unittest discover `
  -s attempts\wave110-c4boxk3-symmetry-sat -p "test_*.py" -v
```
