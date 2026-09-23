# Wave 202: the three-unit equality face

Conditionally on Wave201, this package characterizes the exact
`Q0=7059` face:

```text
3SL+2(SE2+eta+c2)+(L+delta+SF+a1)=3.
```

It derives all three symbolic partition classes, exact local formulas for
the weighted slack, and the bound of at most three multiplicity-one
nonprivate orientations. The attempted two-center baseline obstruction
survives, so no improvement beyond `Q>=7059` is claimed.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave202-three-unit-equality-face-proof-a\exact_check.py --verify attempts\wave202-three-unit-equality-face-proof-a\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave202-three-unit-equality-face-proof-a\test_exact_check.py
```

No construction search is performed.
