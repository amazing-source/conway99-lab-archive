# Wave 80: characteristic-seven overlattice code

Status: `DERIVED` discovery, awaiting independent verification.

Conditional on Waves 66 and 71, the marked 99-vector frame defines an
injective evaluation code
\[
C=\{(\langle y,v_i\rangle\bmod7)_i:y\in L^*/7L^*\}.
\]
It is always a \([99,44]_7\) code, and its hull is exactly
\(\operatorname{row}_{\mathbf F_7}(S)\).  At the difficult rank-28 row,
the quotient by the 28-dimensional hull is the non-split orthogonal space
\(O^-(16,7)\).

The package also proves the conditional small-support theorem
\[
d(C^\perp)\ge6.
\]
The proof checks every sign pattern through support four and all 1,024
labelled five-vertex graphs, including all outside-neighborhood patterns.

Wave 71's forced norm-\(14,16,18\) vectors become balanced codewords of
weights \(14,16,18\) with self-dots \(0,4,1\).  The non-split quotient
allows all three, and the strength-five MacWilliams moments retain strict
slack.  Thus this is a sharper finite-field reformulation, not a
contradiction: rank 28 and Conway-99 remain `UNKNOWN`.

## Reproduce

```powershell
python exact_check.py
python -m unittest -v test_exact_check.py
```

## Files

- `protocol.md`: frozen imports, code definition, and status rules.
- `derivation.md`: exact lattice-to-code proof and orthogonal decomposition.
- `exact_check.py`: deterministic finite-field and five-support exhaustion.
- `exact-results.json`: machine-readable output.
- `test_exact_check.py`: regression and hostile-control tests.
- `hostile-controls.md`: quotient, scale, sign, and status guards.
- `failed-routes.md`: retained null routes and continuation targets.
- `input-freeze.sha256`: imported package hashes.
- `run-report.yaml`: reproducibility metadata.
