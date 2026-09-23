# Wave 51: Seidel modular representation and Smith form

Status: **CANDIDATE — not independently verified**.

This package studies the integral Seidel matrix of a hypothetical
`srg(99,14,1,2)` as an alternative to rooted moment-matrix searches.

The main exact candidate result is a complete conditional Smith normal form.
If
\[
r=\operatorname{rank}_{\mathbf F_7}(S),
\]
then
\[
\operatorname{SNF}(S)=
\operatorname{diag}(1^r,7^{99-2r},49^{r-1},490).
\]
The associated symmetric-square representation gives \(r\ge14\).

This does not resolve the endpoint: the independently verified interval is
\(28\le r\le44\), and all 17 integer ranks in that interval survive every
check in this package. The value here is an exact lattice classification and
a precise record of why the first association-scheme dimension argument
collapses to weaker known information.

## Reproduce

From this directory:

```powershell
python exact_check.py --verify
python -m unittest -v test_exact_check.py
```

Both commands use standard-library exact integer and finite-field arithmetic.
The checker refuses to start on Windows if less than 15% of physical memory is
available.

## Files

- `protocol.md`: frozen question, inputs, and restrictions.
- `derivation.md`: mathematical argument.
- `exact_check.py`: deterministic exact checker.
- `exact-results.json`: canonical generated artifact.
- `test_exact_check.py`: focused regression tests.
- `failed-routes.md`: why this lane does not yet exclude the endpoint.
- `input-freeze.sha256`: byte hashes of imported evidence.
- `run-report.yaml`: discovery run metadata.
- `package-manifest.sha256`: package integrity hashes.

