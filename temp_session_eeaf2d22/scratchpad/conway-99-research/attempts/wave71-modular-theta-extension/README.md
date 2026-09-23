# Wave 71: level-7 neighbor and modular-theta boundary

Status: **DERIVED — discovery, independent verification required**.

Conditional on the Wave 66 lattice package, the 99 marked vectors determine
the order-nine discriminant class exactly.  Its order-three subgroup is
isotropic, yielding an index-three even neighbor \(L\) with
\[
L^*/L\cong(\mathbf Z/7)^q.
\]
The scaled dual \(K=\sqrt7L^*\) is even of exact level seven,
\[
\det K=7^{44-q},\qquad \min K\ge14.
\]

Skoruppa's primary-source mod-7 theta theorem then reduces the problem to
exact level-one modular-form arithmetic.  All eight determinant rows survive
the mandatory theta gap, but the calculation proves:

- for \(q\le14\), \(\min K\le28\);
- for \(q=16\), \(\min K\le18\);
- in the \(q=16\) row, the numbers of integral \(-4\)-eigenvectors of squared
  coordinate norms 14, 16, and 18 obey
  \[
  N_{14}+N_{16}+N_{18}\equiv2\pmod{14}.
  \]

Exact support analysis pins these forced vectors to three finite structures:
a complement-of-Fano \(7+7\) support with an external
\(2\)-\((15,3,2)\) design; a 4-regular bipartite \(8+8\) support; or a
restricted \(9+9\) signed support.

None is excluded here.  This is a precise new-to-project no-go boundary, not
a Conway-99 solution.  Conway status and novelty remain `UNKNOWN`.

## Reproduce

From the repository root:

```powershell
.\.venv\Scripts\python.exe attempts\wave71-modular-theta-extension\exact_check.py --verify
.\.venv\Scripts\python.exe -m unittest -v attempts\wave71-modular-theta-extension\test_exact_check.py
```

The checker uses exact standard-library arithmetic and refuses to run below
15% free physical memory.

## Files

- `protocol.md`: frozen conditional hypothesis and imported theorem.
- `literature-freeze.md`: primary-source citation and bounded search record.
- `derivation.md`: complete neighbor, theta, and support derivation.
- `exact_check.py`: deterministic \(\mathbf F_7\) and profile checker.
- `exact-results.json`: canonical machine-readable output.
- `test_exact_check.py`: focused regression suite.
- `hostile-controls.md`: normalization and status controls.
- `failed-routes.md`: retained null routes and exact remaining boundary.
- `input-freeze.sha256`: hashes of imported Wave 66 artifacts.
- `run-report.yaml`: AGENTS.md discovery run report.
- `package-manifest.sha256`: sealed package hashes.
