# Wave 49 five-root moment clean-room verification

Status: `VERIFIED_SCOPED`.

This package independently reconstructs the exact finite five-root,
one-free-vertex moment calculation. It does not import or execute either
Wave49 discovery script.

## Verified

- labelled locally admissible graph counts:
  `683 / 13,174 / 394,020` at orders `5 / 6 / 7`;
- complete permutation-orbit counts: `21 / 62 / 208`, with exact canonical
  stream hashes;
- all 21 canonical root masks and attachment dimensions;
- all 683 labelled-root order-six and order-seven coefficient tensors;
- raw per-class totals of `720` same-free contributions at order six and
  `5,040` ordered-distinct contributions at order seven, with no
  automorphism divisor;
- all 2,520 canonical-root by `S5` attachment bijections and 680,400
  class-tensor congruence checks;
- the complete discovery coefficient document, exactly, including canonical
  payload SHA-256
  `940ed2820a3501e1b5017a5a3dafce55789ce189a754ef94af01954f28a79511`;
- all 42 Petersen/Clebsch direct integer outer-product matrices and
  coefficient expansions;
- all 17 support hashes and exact order-five/order-six lower decks;
- all 357 witness matrices and all 357 supplied integer negative directions.

Every supplied direction was reevaluated by exact integer arithmetic and has
the claimed strictly negative quadratic value. The independent precomparison
run also found its own exact negative integer direction for every matrix.

Root permutations are coordinate relabellings. They are not automorphisms of
an unknown target graph and are never used to divide counts.

## Reproduce

```powershell
.\.venv\Scripts\python.exe `
  verification\wave49-five-root-moment\independent_check.py `
  --validate verification\wave49-five-root-moment\independent-result.json

.\.venv\Scripts\python.exe `
  verification\wave49-five-root-moment\comparison_check.py `
  --validate verification\wave49-five-root-moment\comparison.json

.\.venv\Scripts\python.exe -m unittest `
  verification\wave49-five-root-moment\test_independent_check.py -v
```

The full reconstruction commands are recorded in `run-report.yaml`.

## Evidence boundary

The numerical combined-SDP artifact is hash-recorded only. Its status,
floating duals, residuals, and eigenvalue margins are not evidence.

The 357 exact negative directions reject the 17 supplied aggregate count
witnesses. They do not exhaust the full PSD-constrained count region.
Endpoint `n3=4158`, branch closure, a strict upper bound, graph construction,
novelty, and Conway-99 remain `UNKNOWN` or `NOT_PROVED`.

At comparison time the discovery directory contained no package manifest.
The verifier therefore binds the compared discovery artifacts by their exact
hashes in `comparison.json` and seals its own complete package manifest.
