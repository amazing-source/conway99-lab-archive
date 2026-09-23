# Wave 66: spherical-code and even-lattice shift

Status: **CANDIDATE — independent verification required**.

This package moves a hypothetical `srg(99,14,1,2)` out of the rooted
pair-coordinate space and into a real equiangular-line system and an exact
44-dimensional even lattice.

The candidate theorem is:

\[
\det M=9\cdot7^{44-r},\qquad
M^*/M\cong\mathbf Z/9\oplus(\mathbf Z/7)^{44-r},\qquad
\min(M^*)\ge2,
\]

where \(r=\operatorname{rank}_{\mathbf F_7}(2A-J+I)\).  Moreover
\(63M^*\subseteq M\), and Milgram's formula forces \(r\) to be even and at
most 42.

The route starts with the primitive-idempotent spherical embedding in
dimension 44.  A constant-coordinate lift gives 99 real equiangular lines in
dimension 45 with angle \(1/7\).  Centering their integral Gram vectors and
halving the difference pairing produces \(M\).

This is a stronger exact reformulation, not a resolution.  Eight currently
allowed even ranks \(28,30,\ldots,42\) survive, no lattice or graph is
constructed, and Conway-99 remains `UNKNOWN`.  Novelty is `UNKNOWN`.

## Reproduce

From the repository root:

```powershell
.\.venv\Scripts\python.exe attempts\wave66-spherical-code-shift\exact_check.py --verify
.\.venv\Scripts\python.exe -m unittest -v attempts\wave66-spherical-code-shift\test_exact_check.py
```

The checker uses exact standard-library arithmetic and refuses to run below
15% free physical memory.

## Files

- `protocol.md`: frozen hypothesis, imports, and separation rules.
- `derivation.md`: complete mathematical derivation.
- `exact_check.py`: deterministic exact arithmetic checker.
- `exact-results.json`: canonical output.
- `test_exact_check.py`: focused and hostile regression tests.
- `failed-routes.md`: nonworking shortcuts and the remaining boundary.
- `input-freeze.sha256`: hashes of imported evidence.
- `run-report.yaml`: AGENTS.md run report.
- `package-manifest.sha256`: package hashes.
