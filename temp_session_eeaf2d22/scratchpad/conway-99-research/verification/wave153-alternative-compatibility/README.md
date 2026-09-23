# Wave153 independent verification

Status:

```text
VERIFIED_WITH_SCOPE:
exact rational null witness for the complete safe-orbit bounded
pair-correlation projection only
```

The clean-room verifier rebuilt the 18 component graphs, the six-element
fibre-coordinate action, all 275 safe orbit representatives covering all
1,140 unordered triples, every allowed six-set, and every exact rational
witness. It replayed 173,250 pair equations, 9,900 row margins, and total
weight 60 in every lane. Nine hostile and structural tests pass.

Run:

```powershell
python verification/wave153-alternative-compatibility/independent_verifier.py
python -m unittest verification/wave153-alternative-compatibility/test_independent_verifier.py -v
```

The verifier never imports or executes the discovery implementation. See
`verification-report.md` for the reconstruction and exact scope.

This result does **not** certify a binary incidence design, a compatible
residual graph, endpoint existence or exclusion, a strict `n3` bound,
Conway-99, or external novelty.
