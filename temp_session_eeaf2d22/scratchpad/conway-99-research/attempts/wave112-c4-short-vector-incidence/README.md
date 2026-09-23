# Wave 112: four-cycle short-vector incidence target

Status: `DERIVED`; independent verification required.

The target contains exactly 2,079 induced four-cycles. Every allowed
short-vector support contains at least:

```text
norm 14:        21 alternating C4s
norm 16:        20 alternating C4s
norm 18, h=0:   18 alternating C4s
norm 18, h=1:   26 alternating C4s
```

In the rank-28 row, `N14+N16+N18>=5868`. Therefore some four-cycle must lie
in at least 52 oriented short vectors, or 26 antipodal supports.

A universal local upper bound of 25 antipodal extensions per four-cycle
would contradict the modular lower bound and exclude rank 28. This package
does **not** prove that cap; it isolates it as a precise alternative-space
target and derives the exact `51,20,20,4` partition around a normalized
cycle.

Reproduce:

```powershell
python -B attempts\wave112-c4-short-vector-incidence\exact_check.py `
  --verify attempts\wave112-c4-short-vector-incidence\exact-results.json
python -B -m unittest discover `
  -s attempts\wave112-c4-short-vector-incidence -p "test_*.py" -v
```

Rank 28, Conway-99, and novelty remain `UNKNOWN`.
