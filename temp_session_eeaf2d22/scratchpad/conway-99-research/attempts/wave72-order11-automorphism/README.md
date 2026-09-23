# Wave 72: order-11 automorphism fixed-point theorem

Status: `DERIVED`; independent verification pending.

This package proves a conditional structural theorem for a hypothetical
`srg(99,14,1,2)`:

> Every automorphism of order 11 is fixed-point-free.

The proof does not assume vertex transitivity.  It studies the graph induced
by the fixed vertices, uses the prime-orbit decomposition, and eliminates
every positive fixed-set size by exact integer arithmetic.

Combined **conditionally** with Wave 69's independently pending exhaustive
exclusion of a semiregular order-11 quotient, the theorem would imply:

1. a target graph has no automorphism of order 11; and
2. a target graph is not vertex-transitive.

Those corollaries remain conditional on independent verification of both
packages.  They do not establish nonexistence of an asymmetric target, so the
unrestricted Conway-99 problem remains `UNKNOWN`.

## Reproduce

```powershell
.\.venv\Scripts\python.exe attempts\wave72-order11-automorphism\exact_check.py --verify
.\.venv\Scripts\python.exe -m unittest discover -s attempts\wave72-order11-automorphism -p "test_*.py" -v
```

## Files

- `protocol.md`: frozen scope and status boundary.
- `derivation.md`: complete human derivation and conditional corollaries.
- `exact_check.py`: deterministic enumeration of all fixed-degree models.
- `exact-results.json`: sealed exact output.
- `test_exact_check.py`: hostile edge-case tests.
- `failed-routes.md`: scope limits and deliberately unused shortcuts.
- `run-report.yaml`: protocol-compliant discovery report.
- `input-freeze.sha256`: hashes of frozen project inputs.
- `package-manifest.sha256`: hashes of all substantive package files.
