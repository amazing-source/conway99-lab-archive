# Wave 81 independent verification

Status: `VERIFIED` for the conditional Wave 81 claims, plus one separately
labelled verifier-derived `DERIVED` strengthening.

This clean-room package independently reconstructs the labelled norm-16
reduction without importing the discovery checker. It confirms:

- 1,800 anchored support matrices and five `S8 x S8` label orbits;
- 4,985 deficiency-pair coupling multisets;
- all 4,985 pass the stated per-`X2` local marginal-flow test;
- the six outside pair-moment equations leave 43 rows for `t=0`, seven for
  `t=1`, and none for `t>=2`;
- the corrected Jacobi factors, spectral traces, and four-cycle counts for
  all five support orbits.

The verifier also derives a stricter degree-graphicality filter that rejects
three of the 43 `t=0` rows, leaving `40+7`. That extension is `DERIVED`, not
`VERIFIED`, until a separate verifier reproduces it.

No outside graph is constructed. Conway-99 and novelty remain `UNKNOWN`.

## Replay

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave81-norm16-labeled-design\independent_check.py `
  --verify verification\wave81-norm16-labeled-design\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave81-norm16-labeled-design\test_independent_check.py
```

The verifier uses only the Python standard library and refuses to start
below 15% free physical memory.
