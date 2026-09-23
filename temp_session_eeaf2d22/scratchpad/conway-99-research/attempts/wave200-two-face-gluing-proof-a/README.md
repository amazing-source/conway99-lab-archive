# Wave 200: two-face orientation gluing

This analytic package excludes both integer faces left by the Wave198
certificate below 7,039:

```text
Q0=7037,7038.
```

Their slack budget is at most 63. It forces at least 27
multiplicity-five selected orientations, but additive four-fiber loss
permits at most 4. Therefore the conditional bound is `Q>=7039`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave200-two-face-gluing-proof-a\exact_check.py --verify attempts\wave200-two-face-gluing-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave200-two-face-gluing-proof-a\test_exact_check.py
```

No search is performed.
