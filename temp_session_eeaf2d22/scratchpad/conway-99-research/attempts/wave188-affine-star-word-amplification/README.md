# Wave 188: affine star-word amplification

Status: `DERIVED`, pending independent verification.

Assume the conditional prism-free rank-11 endpoint model. Wave 186 counted
circuits obtained from star translations. This package instead retains the
translated dual relation words themselves. That removes the circuit-
extraction collision and exposes the full `3 by 3` affine orbit of a
two-star relation.

The resulting conditional bounds are

```text
nonedge-realizing projective dual words of weights 4..9 >= 8316,
all projective dual words of weights 4..9              >= 9009,
B_4+B_5+B_6+B_7+B_8+B_9                              >= 18018.
```

No graph, code, SAT, cover, configuration, or isomorphism search is used.
The tiny exact checker enumerates only the coefficient-frequency triples
of two seven-term simplex representations and verifies the final scalar
inequality.

This is a stronger necessary condition for the conditional endpoint, not a
contradiction. Rank 11, endpoint existence, a strict `n3` improvement,
external novelty, and Conway-99 remain `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave188-affine-star-word-amplification\exact_check.py `
  --verify `
  attempts\wave188-affine-star-word-amplification\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  attempts\wave188-affine-star-word-amplification\test_exact_check.py
```
