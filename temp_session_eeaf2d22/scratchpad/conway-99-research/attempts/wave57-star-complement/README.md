# Wave57: star complements around an endpoint triangle

## Outcome

`DERIVED_INCONCLUSIVE`.

Under the conditional Wave35 endpoint `n3=4158`, an arbitrary fixed triangle
forces a 39-vertex supported spectral sector.  This gives

```
18 <= mult_Y(3) <= 20,
 8 <= mult_Y(-4) <= 13.
```

Exactly 18 multiplicity pairs remain.  Fourth moments reduce the four-cycle
parameter to `0 <= C4(X) <= 89`, with a sharper lower bound for each pair.
Every one of the 18 rows has an exact algebraic-integer scalar control matching
the first four residual spectral moments.  Those controls are not certified
graph spectra and do not construct `G[Y]`.

The endpoint is **not excluded**, no endpoint graph is constructed, and
Conway-99 remains `UNKNOWN`.

## Strongest deductions

- The quotient matrix on `(T,X,Y)` has eigenvalues `14,3,-4`.
- For each of `lambda=3,-4`, a two-dimensional eigenspace is supported
  entirely on `U=T union X`.
- The principal projector blocks on `Y` have ranks
  `60-mult_Y(-4)` and `60-mult_Y(3)`.
- A `3`-star set must hit `U` in at least `mult_Y(-4)-6`, namely 2 to 7
  vertices.  A `-4`-star set must hit `U` in at least
  `mult_Y(3)-16`, namely 2 to 4 vertices.
- The smaller exact target is a 60-vertex, 8-regular graph `G[Y]` with
  32 triangles, the stated rank constraints, and a compatible binary
  star-complement reconstruction.

## Reproduction

From this directory:

```powershell
python exact_check.py
python -m unittest -v test_exact_check.py
```

The checker uses only the Python standard library, verifies the frozen input
hashes, and refuses to run below 15 percent free physical memory.

## Files

- `protocol.md`: frozen assumptions, questions, sources, and status boundary.
- `derivation.md`: complete mathematical derivation.
- `exact_check.py`: deterministic exact checker and control verifier.
- `exact-results.json`: machine-readable ledger.
- `test_exact_check.py`: regression tests and negative status control.
- `failed-routes.md`: retained non-obstructions and next exact target.
- `input-freeze.sha256`: discovery and independent-verification inputs.
- `run-report.yaml`: reproducibility report.
