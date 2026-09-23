# Wave192 equality-face verifier

This package independently verifies the conditional strict circuit bound

```text
Q>=6238,
```

where `Q` counts projective short circuits cross-realizing graph nonedges in
the prism-free rank-11 endpoint model.

The verifier reconstructs the complete equality face of the verified
Wave191 bound `Q>=6237`, checks the strict residual capacity
`2Z<=3Y`, proves canonical `tau`-pair saturation, and excludes:

- `m=0` by the unused affine checkerboard-axis word; and
- every `m>0` branch by a nonprivate `3+6` leaf word.

The independent equality reconstruction and both branch contradictions were
frozen before the Wave192 source package was opened.  The final verdict is
`VERIFIED_WITH_SCOPE`; the equality face `Q=6237` is `REFUTED`.

No graph, code, cover, endpoint, or Conway-99 solution is claimed.

## Replay

```powershell
.\.venv\Scripts\python.exe -B verification\wave192-equality-face-verifier\independent_check.py --verify-math verification\wave192-equality-face-verifier\independent-math-result.json
.\.venv\Scripts\python.exe -B verification\wave192-equality-face-verifier\independent_check.py --verify verification\wave192-equality-face-verifier\independent-results.json
.\.venv\Scripts\python.exe -B -m unittest -v verification\wave192-equality-face-verifier\test_independent_check.py
```
