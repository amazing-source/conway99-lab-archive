# Wave 58 independent cross-incidence verification

Status: `VERIFIED` in the exact conditional scope.

The verifier independently reproduced:

- `rank(B)=35-kappa`, `mult_Y(3)=18`, and
  `mult_Y(-4)=7+kappa` as prior Wave 36 results;
- the three surviving rows `(18,8,1)`, `(18,9,2)`, `(18,10,3)`;
- the universal upper bound `C4(X)<=27`;
- the normalized component censuses `216 -> 50` for `m=4` and
  `162000 -> 34640` for `m=6`;
- the exact local `kappa=3` cycle set
  `{6,8,10,12,14,16,18}`;
- all three separate local/scalar controls; and
- the restricted Wave 40 replay `262144 -> 37378`.

The component counts are coordinate-normalized labelled presentations, not
graph-isomorphism counts.  The displayed `kappa=1` range `0..27` and overall
`kappa=2` range `0..24` are bounds, not exact attainable intervals.  The
Wave 40 support is `{4,5,6,7,8,9,10,11,12,14}`; 13 is absent.

No simultaneous `B`, compatible `A_Y`, graph, or contradiction is produced.
The endpoint and Conway-99 remain `UNKNOWN`.

## Reproduce

```powershell
python -B verification\wave58-cross-incidence-rank\independent_check.py
python -B verification\wave58-cross-incidence-rank\independent_check.py `
  --verify verification\wave58-cross-incidence-rank\independent-results.json
python -B -m unittest discover `
  -s verification\wave58-cross-incidence-rank -p "test_*.py" -v
```

The checker imports no discovery code, uses standard-library exact arithmetic,
verifies all frozen hashes, and refuses to start below 20 percent free
physical memory.

## Files

- `protocol.md`: clean-room scope and promotion rules.
- `preinspection-freeze.sha256`: upstream chronology hashes.
- `discovery-freeze.sha256`: sealed Wave 58 discovery hashes.
- `independent_check.py`: exact clean-room verifier and enumerators.
- `independent-results.json`: machine-readable result.
- `test_independent_check.py`: hostile mutation suite.
- `audit.md`: derivation, wording audit, and evidence boundaries.
- `run-report.yaml`: reproducibility report.
- `package-manifest.sha256`: final checksums.
