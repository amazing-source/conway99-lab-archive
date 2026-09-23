# Wave 90: prism-free norm-14 shell upper bound

Status: `DERIVED`; independent verification required.

At the prism-free endpoint, exact rooted transition counting proves

```text
N14 <= 5544,
```

where `N14` counts both signs of the norm-14 integer `-4` eigenvectors.

This does **not** bound `N16` or `N18`, so it does not yet contradict the
provisional Wave 86 lower bound on `N14+N16+N18`.

Run:

```powershell
python -B attempts/wave90-short-vector-count-upper/exact_check.py
python -B attempts/wave90-short-vector-count-upper/exact_check.py `
  --verify attempts/wave90-short-vector-count-upper/exact-results.json
python -B -m unittest discover `
  -s attempts/wave90-short-vector-count-upper `
  -p "test_*.py" -v
```

See `protocol.md` for the exact quantifiers and `derivation.md` for the
double-count proof.

