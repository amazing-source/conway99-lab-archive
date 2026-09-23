# Wave193 global low-target verifier

This package independently verifies the conditional circuit theorem

```text
117Q>=177C,
Q>=6291
```

in the prism-free rank-11 endpoint model.

The verifier reconstructs:

- the complete raw-assignment split by source and exact multiplicity;
- the type-one exact-two residual in both affine branches;
- old exact-three unused-label flow and the orbit-closed new residual slack
  `SR`;
- one privacy-free low leaf target per selected-type-three label and the
  low-capacity slack `SL`; and
- the exact nonnegative identity for `Q0-59C/39`.

The independent mathematical result was frozen before the Wave193 source
package was opened.  The final verdict is `VERIFIED_WITH_SCOPE`.

No graph, code, cover, endpoint, or Conway-99 solution is claimed.

## Replay

```powershell
.\.venv\Scripts\python.exe -B verification\wave193-global-low-target-verifier\independent_check.py --verify-math verification\wave193-global-low-target-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave193-global-low-target-verifier\independent_check.py --verify verification\wave193-global-low-target-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave193-global-low-target-verifier\test_independent_check.py
```
