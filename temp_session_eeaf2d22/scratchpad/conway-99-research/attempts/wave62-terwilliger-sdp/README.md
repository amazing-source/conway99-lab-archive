# Wave 62: rooted signed-edge Terwilliger/SDP

Status: **DERIVED exact null result; pending independent verification**.

This package moves the prism-free endpoint into the association scheme of
the 84 signed edges of `K7`. The rooted scaffold group `C2 wreath S7` is used
only to average universally valid PSD certificates. No symmetry of a
hypothetical Conway graph is assumed.

The six scaffold orbitals have valencies

```text
1, 2, 1, 20, 20, 40
```

and common eigenspace multiplicities

```text
1, 6, 7, 14, 21, 35.
```

At the endpoint, all averaged residual edge counts depend on one integer
`0<=y<=42`. The exact spectral-projector SDP diagonalizes into six rational
scalar blocks. Every value of `y` survives. A bounded Schur/Terwilliger
extension checks 1,949 averaged matrices and 23,388 affine endpoint block
inequalities through total degree 24; none is negative.

The useful conclusion is architectural: one-point symmetry averaging is too
coarse. The next sound layer must retain two-root edge correlations or
triangle-root prism compatibility. The endpoint, a strict upper bound below
4158, and Conway-99 all remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave62-terwilliger-sdp\exact_check.py `
  --verify attempts\wave62-terwilliger-sdp\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave62-terwilliger-sdp -p "test_*.py" -v
```

All certificate calculations use Python's standard-library exact rational
arithmetic. No solver status or floating eigenvalue is evidence.
