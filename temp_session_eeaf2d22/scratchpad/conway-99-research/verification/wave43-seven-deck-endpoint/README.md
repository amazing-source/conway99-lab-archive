# Independent verification: Wave 43 seven-deck endpoint witness

## Verdict

`VERIFIED`, with a strict scope wall: at `n3=4158` and `h11=16632`, the
specified **unrooted order-seven count relaxation** has the published exact
nonnegative integer solution. This is not a construction of a graph, evidence
that the endpoint is realizable, or a proof about Conway-99 existence.

The verifier independently obtained:

- all `156` unlabeled six-vertex graphs and all `1044` unlabeled seven-vertex
  graphs by partitioning the complete labelled universes;
- orbit-size totals `2^15=32768` and `2^21=2097152`;
- `62` and `208` locally admissible classes;
- all `62` six-to-seven deletion equations;
- all `19` Hamiltonian formula classes and exact endpoint values;
- the published `99`-class sparse support, totaling
  `C(99,7)=14887031544`; and
- exactly three seven-classes having a triangular-prism deletion, all with
  coefficient zero.

All 62 deletion residuals and all 19 Hamiltonian/count residuals are zero.
Every coefficient is a nonnegative integer. Six hostile mutations were
rejected.

## Independence

`protocol-freeze.md` and `input-freeze.sha256` were written before discovery
content was inspected. `independent_check.py` imports no discovery or prior
project implementation. It uses only Python's standard library and reads the
public sparse coefficient list from the frozen result JSON as the candidate
to check.

The independent result was then frozen in `independent-freeze.sha256`.
`compare_frozen.py` was run only afterward. It mechanically matched all 13
published fields available for comparison, including the support hash and
the full constraint nonzero count.

## Reproduction

From the repository root:

```powershell
python verification/wave43-seven-deck-endpoint/independent_check.py --output verification/wave43-seven-deck-endpoint/recomputed-result.json
python -m unittest verification/wave43-seven-deck-endpoint/test_independent_check.py -v
python verification/wave43-seven-deck-endpoint/compare_frozen.py
```

Use a separate output path for a fresh run so the pre-comparison frozen result
is not overwritten. The complete census takes about 12 seconds on the
verification host. The checker samples physical memory throughout and aborts
if available memory falls below 15%; the recorded run stayed above 63%.

## Files

- `protocol-freeze.md`: pre-inspection protocol and claim scope.
- `input-freeze.sha256`: opaque discovery input hashes.
- `independent_check.py`: clean-room census and exact checker.
- `independent-result.json`: frozen full verifier output.
- `independent-freeze.sha256`: pre-comparison result hash.
- `compare_frozen.py` / `comparison.json`: post-freeze comparison.
- `test_independent_check.py`: focused positive and hostile tests.
- `2026-07-27T162423Z-audit.md`: human-readable audit.
- `run-report.yaml`: machine-readable run metadata.
- `package-manifest.sha256`: package integrity hashes.

## Scope wall

The solution is a vector of aggregate counts. It does not assign edges among
99 vertices and does not enforce consistency between overlapping seven-vertex
subsets or rooted extensions. Consequently:

- graph construction: `false`;
- endpoint `n3=4158`: `UNKNOWN`;
- strict upper bound below `4158`: `NOT_PROVED`;
- Conway-99: `UNKNOWN`.
