# Wave 188 clean-room verification

Verdict: `VERIFIED_WITH_SCOPE`.

The frozen Wave 188 theorem is correct under the verified prism-free rank-11
endpoint assumptions:

```text
nonedge-realizing projective dual words of weights 4..9 >= 8316
all projective dual words of weights 4..9              >= 9009
B_4+B_5+B_6+B_7+B_8+B_9                              >= 18018
```

The verifier does not import or execute the discovery checker. It independently
enumerates the 438 feasible coefficient-frequency profiles, reconstructs the
canonical relation words over `F_3`, checks support-level capacities and all
cross-family collision cases, and recomputes the private-label inequality.

This counts actual dual words, including the canonical weight-eight
noncircuit. It does not prove a larger circuit count, contradict a complete
weight enumerator, exclude rank 11, construct or exclude the endpoint graph,
or resolve Conway 99.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  verification\wave188-affine-star-word-amplification-verifier\independent_check.py `
  --verify `
  verification\wave188-affine-star-word-amplification-verifier\independent-results.json

.\.venv\Scripts\python.exe -B -m unittest -v `
  verification\wave188-affine-star-word-amplification-verifier\test_independent_check.py
```
