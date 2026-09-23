# Wave 174: no weight-three dual words at the endpoint

Status: `VERIFIED_WITH_SCOPE`.

At the prism-free endpoint, the centered ternary block code has dual
distance at least four:

```text
B1=B2=B3=0.
```

The proof converts a hypothetical weight-three dependency into a ternary
line-sum coloring of the partial quadrangle.  Exact cell counts,
interlacing, and a common-neighbor convexity identity force a unique
`36/27/36` coloring.  Its nine triple-center points then split into three
triangles, each perfectly matched to an original triangle, producing a
forbidden triangular prism.

No graph search, code search, SAT, MILP, or automorphism assumption is used.
An independent clean-room verifier found the omitted degenerate `c=18`
quotient case, supplied the exact `-1152` spectral exclusion now included
in the proof, and verified the repaired theorem.  The conclusion is scoped:
the endpoint and Conway-99 remain `UNKNOWN`.

Run:

```powershell
.\.venv\Scripts\python.exe -B attempts\wave174-no-weight3-dual\exact_check.py --verify attempts\wave174-no-weight3-dual\exact-results.json
.\.venv\Scripts\python.exe -B -m unittest -v attempts\wave174-no-weight3-dual\test_exact_check.py
```
