# Wave158: independent cube/Wagner verification

Status:

```text
VERIFIED_WITH_SCOPE:
41580 - n3 + 12*C8 - 4*W8 >= 0
for every hypothetical srg(99,14,1,2)
```

The clean-room verifier independently rebuilt:

- the root-mask-12 signed flag covariance table;
- the unique order-six class and its `N9=41580-n3` formula;
- explicit cube and Wagner/Möbius-ladder isomorphisms;
- the root embedding count `R=1014552`;
- symbolic and endpoint gcd reductions;
- the endpoint and strict-bound logic.

Run:

```powershell
python verification/wave158-general-cube-wagner/independent_verifier.py
python -m unittest verification/wave158-general-cube-wagner/test_independent_verifier.py -v
```

Ten hostile and structural tests pass. The verifier parses the independent
formula source as static AST and never imports or executes the Wave157
discovery script.

See `verification-report.md` for the proof reconstruction. Novelty, a strict
bound below 4158, endpoint status, graph construction, and Conway-99 all
remain `UNKNOWN`.
