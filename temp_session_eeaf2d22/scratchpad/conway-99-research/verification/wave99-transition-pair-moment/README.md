# Wave 99 independent verification

Status: `VERIFIED SCOPED`.

The clean-room reconstruction verifies that, for a hypothetical
`srg(99,14,1,2)` in the prism-free branch `P=0` (equivalently
`n3=4158`),

```text
N14 <= 4950.
```

Under the additional rank-28 / `q=16` hypothesis, the independently
verified Wave 86 identity then gives

```text
407*N16 + 43*N18 >= 2165002.
```

The first conclusion does not require rank 28. The second requires both
`P=0` and rank 28. Neither conclusion excludes the branch or proves a
strict general upper bound on `n3`.

The verifier was frozen before the discovery derivation was opened. Its
precomparison code and result hashes are recorded in
`precomparison.sha256`. Discovery comparison was performed afterward by a
separate script that does not import or execute discovery code.

Reproduce:

```powershell
python -B verification\wave99-transition-pair-moment\independent_verify.py `
  --verify
python -B verification\wave99-transition-pair-moment\compare_discovery.py `
  --verify
python -B -m unittest discover `
  -s verification\wave99-transition-pair-moment -p "test_*.py" -v
```
