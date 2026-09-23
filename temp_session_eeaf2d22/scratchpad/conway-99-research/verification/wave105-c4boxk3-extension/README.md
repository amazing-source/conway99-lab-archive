# Wave 105 verification

Verdict: `VERIFIED_WITH_CLARIFICATIONS`, within the frozen motif-conditional
scope.

The exact `C4 box K3` reduction, forced outside incidence counts
`(3,48,36)`, block equations, type-edge formulas, moment census
`(18,11,5,1)`, and six-graphical-filter census `(18,11,4,1)` reproduce
independently.

The 549-edge archived graph verifies all degrees and all 1,044 entries of
`DP=2J-P-PH`, with upper-triangle hash
`feb948f5d0095b4baaba139fddda02b6ededcb7898e0d1ead3d2c251c6786fde`.
It fails 2,525 nonlinear outside-pair equations, so it is only a linear-layer
witness.

The SAT formulation is logically complete conditional on the motif, and the
four `e(X0)=0,1,2,3` branches are encoding symmetry, not a target-graph
automorphism assumption. The four preserved 45-second runs are all
`UNKNOWN_TIMEOUT`.

The clarification is explicit: uniqueness of the forced incidence multiset
needs the triangle-free positive residual-pair support argument. The verifier
supplies and checks that missing justification.

No construction, exclusion, global Conway-99 result, or novelty claim follows.

Reproduce:

```powershell
python -B verification\wave105-c4boxk3-extension\independent_verify.py
python -B -m unittest discover `
  -s verification\wave105-c4boxk3-extension -p "test_*.py" -v
python -B -m unittest discover `
  -s attempts\wave105-c4boxk3-extension -p "test_*.py" -v
```
