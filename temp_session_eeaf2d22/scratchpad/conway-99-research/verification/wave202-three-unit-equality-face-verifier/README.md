# Wave202 three-unit equality-face verifier

This package independently verifies the exact conditional `Q0=7059`
certificate face and its three analytic slack-partition classes.  It
also derives the surviving raw-variable formulas, local equality
conditions, center-size restriction, and multiplicity-one cap.

The result is deliberately a null equality-face checkpoint:

```text
Q0=7059 is not excluded,
Q>=7059 remains unchanged.
```

Run:

```powershell
.\.venv\Scripts\python.exe -B verification\wave202-three-unit-equality-face-verifier\independent_check.py --verify verification\wave202-three-unit-equality-face-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave202-three-unit-equality-face-verifier\test_independent_check.py
.\.venv\Scripts\python.exe -B verification\wave202-three-unit-equality-face-verifier\source_comparison_check.py --verify verification\wave202-three-unit-equality-face-verifier\source-comparison-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave202-three-unit-equality-face-verifier\test_source_comparison_check.py
```

No graph, configuration, family, cover, SAT, LP, enumeration,
isomorphism, or brute-force search is used.
