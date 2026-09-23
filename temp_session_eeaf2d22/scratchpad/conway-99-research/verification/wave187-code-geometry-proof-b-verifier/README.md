# Wave 187 proof-B clean-room verification

Verdict: `VERIFIED_RELAXATION_BOUNDARY`.

The exact rational hostile control is feasible for all constraints it claims:

- ordinary ternary MacWilliams constraints with `B1=B2=B3=0` and
  `B_j>=A_j>=0` for all 232 weights;
- 231 marked singular scalar pairs of composition `(36,162)`;
- complete ternary coefficients nonnegative through total degree six;
- quadratic-type factorial moments through degree three;
- the displayed integral three-point Gram census.

It has

```text
B4 = 126079749915623/131414760
B4+...+B9 = 721437869830147204193861/3066344400
```

and first fails at

```text
B70=B07=-10151603437954385741/508426957500.
```

This is a rational relaxation witness only. It is not a linear code, a
231-point set, an endpoint graph, or evidence that one exists.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave187-code-geometry-proof-b-verifier\independent_check.py `
  --verify `
  verification\wave187-code-geometry-proof-b-verifier\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave187-code-geometry-proof-b-verifier\test_independent_check.py
```
