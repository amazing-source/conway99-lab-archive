# Wave 99: transition-pair moment

Status: `DERIVED`; independent verification required.

At the prism-free endpoint, a second-moment count of selected rooted
transitions strengthens the verified Wave 90 theorem from

```text
N14 <= 5544
```

to the candidate theorem

```text
N14 <= 4950.
```

In the additional rank-28 row, the verified Wave 86 modular identity would
then force

```text
407*N16 + 43*N18 >= 2165002.
```

The package proves no upper bound on `N16` or `N18`, so no endpoint or graph
is excluded.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave99-transition-pair-moment\exact_check.py `
  --verify attempts\wave99-transition-pair-moment\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave99-transition-pair-moment -p "test_*.py" -v
```
