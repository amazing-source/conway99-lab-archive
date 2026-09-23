# Wave 100: general pair-moment `N14` bound

Status: `DERIVED`; independent verification required after Wave 99.

The Wave 99 transition-pair moment extends from the prism-free endpoint to
every compatible prism count. The candidate general theorem is

```text
7*N14 <= 34650+15P = 55440-5*n3,
N14 <= floor((55440-5*n3)/7).
```

Because `N14` counts antipodal vectors, it is even, giving the slightly
sharper displayed form

```text
N14 <= 2*floor((55440-5*n3)/14).
```

This improves the verified Wave 94 coefficient from `-4*n3` to `-5*n3`,
but still bounds only the norm-14 shell. It does not prove a strict upper
bound on `n3`.

Reproduce:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave100-general-pair-moment\exact_check.py `
  --verify attempts\wave100-general-pair-moment\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave100-general-pair-moment -p "test_*.py" -v
```
