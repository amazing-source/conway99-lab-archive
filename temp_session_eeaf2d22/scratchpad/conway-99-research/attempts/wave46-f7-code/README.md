# Wave 46: characteristic-seven row-code scout

Status: `DERIVED_NULL_RESULT_PENDING_VERIFICATION`.

This package studies the conditional prism-free endpoint `n3=4158` through
the row code over `F7` of the correct matrix

```text
M=21E_0,  order 231,  M^2=21M.
```

It finds no contradiction. The endpoint, a strict upper bound below `4158`,
Conway-99, and novelty all remain `UNKNOWN`.

## Exact outcome

Let `C=row_F7(M)` and `r7=dim(C)`. The verified prior endpoint range supplied
to this discovery lane is

```text
28 <= r7 <= 44.
```

The elementary code consequences are:

- `C` is self-orthogonal and lies in the hyperplane perpendicular to the
  all-one vector;
- the 231 columns are nonzero and projectively distinct, so
  `d(C^perp)>=3`;
- the 231 distinguished projector rows and their six nonzero scalar
  multiples force `A_69>=1386`;
- row sum and self-orthogonality forbid ordinary weights exactly `1,2,4`,
  and do not by themselves forbid any other weight;
- the six known complete weight-enumerator compositions pass all
  degree-zero, degree-one, and degree-two orthogonal-array moments with
  strict slack, even at the smallest possible dimension `r7=28`;
- the exact identity `M^(o3)=M+4I` has inverse `3M+2I` over `F7`, so the
  third Schur power is the full `F7^231`; its resulting floor `r7>=11` is
  weaker than the already verified `r7>=28`.

Most importantly, the machine-readable output contains explicit generic
positive-control codes for every dimension `28,...,44`. They satisfy all of
the ordinary constraints above, including projectivity and
`A_69>=668653683264`. Thus the ordinary weight enumerator alone cannot
contradict this generic constraint set.

Those controls are deliberately not endpoint candidates: they do not match
the six exact endpoint generator compositions. This separates the ordinary
code obstruction from the still-open generator-geometry obstruction.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B `
  attempts\wave46-f7-code\exact_check.py `
  --verify attempts\wave46-f7-code\exact-results.json

.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave46-f7-code -p "test_*.py" -v
```

The checker is deterministic, uses one foreground process, and aborts before
available physical memory falls below 20 percent, leaving margin above the
user's requested 15 percent floor.

## Files

- `derivation.md`: exact mathematics and the separation result;
- `exact_check.py`: independent-of-solver exact arithmetic and construction;
- `exact-results.json`: full projection matrices and hashes for every
  dimension `28,...,44`;
- `test_exact_check.py`: regression, positive, and hostile controls;
- `failed-routes.md`: retained null routes and missing information;
- `verifier-request.md`: frozen independent-verification assignment;
- `run-report.yaml`: AGENTS-schema discovery report;
- `input-freeze.sha256` and `package-manifest.sha256`: evidence hashes.

No content in this package is labelled `VERIFIED`; discovery cannot certify
itself.
