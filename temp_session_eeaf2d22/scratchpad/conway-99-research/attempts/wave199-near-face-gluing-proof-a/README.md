# Wave 199: near-face orientation gluing

This analytic package excludes the only integral near face left by the
Wave198 orientation certificate:

```text
Q0=7037.
```

Its 23-unit slack budget forces at least 48 multiplicity-five oriented
labels, while local four-fiber Hilton--Milner geometry allows at most 7.
Consequently the conditional bound improves to `Q>=7038`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave199-near-face-gluing-proof-a\exact_check.py --verify attempts\wave199-near-face-gluing-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave199-near-face-gluing-proof-a\test_exact_check.py
```

No search is performed.
