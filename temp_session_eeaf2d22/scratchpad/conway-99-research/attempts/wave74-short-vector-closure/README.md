# Wave 74: short-vector outside-incidence closure

Status: **DERIVED — discovery, independent verification required**.

This addendum closes one of Wave 71's forced norm-18 branches.  If the two
same-sign edges on each \(9+9\) support are disjoint, the 81 outside vertices
must carry 82 incidences per sign side while no outside vertex may carry two.
That is impossible.  The already-rejected adjacent-edge shape is also
recomputed exactly.

Therefore a norm-18 integer \(-4\)-eigenvector can only have
\[
h\in\{0,1\},
\]
not \(h=2\).

The same exact moment calculation leaves:

- four outside histograms for norm 16, \(h=0\);
- 20 for norm 18, \(h=0\);
- six for norm 18, \(h=1\).

So this is genuine branch closure, not a full contradiction.  The norm-14,
norm-16, and remaining norm-18 alternatives survive.  Conway-99 and novelty
remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe attempts\wave74-short-vector-closure\exact_check.py --verify
.\.venv\Scripts\python.exe -m unittest -v attempts\wave74-short-vector-closure\test_exact_check.py
```

The checker is standard-library exact and refuses to run below 15% free
physical memory.
