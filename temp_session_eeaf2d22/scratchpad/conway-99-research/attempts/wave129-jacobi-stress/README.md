# Wave129: higher-cutoff level-7 Jacobi stress

Status: **CANDIDATE / SEALED**. Conway-99 remains **UNKNOWN**.

This continuation preserves the sealed Wave127 package and applies its exact
affine-face method sequentially at cutoffs 18, 20, and 28. Every floating
status is diagnostic only. A cutoff is reported feasible only after a rational
239-variable vector is checked against every original exact row; infeasibility
requires an exact Farkas certificate.

## Results

| Cutoff | Exact outcome | Original rows | Tight inequalities |
| --- | --- | --- | --- |
| 18 | exact rational feasible | 366 equalities, 846 inequalities | 381 |
| 20 | exact rational feasible | 386 equalities, 1,000 inequalities | 396 |
| 28 | unknown | 454 equalities, 1,686 inequalities | not applicable |

At cutoffs 18 and 20, `verify_candidate.py` reconstructed the complete exact
constraint system from the cached exact columns and substituted the 239
rational coordinates into every unreduced row. It found no failed equality or
inequality.

At cutoff 28, the numerical reduced LP reported an apparent feasible point,
but that status is not a certificate. Exact reduction left 139 independent
equalities, 510 distinct inequalities, and a 100-dimensional affine solution
space. The bounded active-face recovery exhausted 1,549 recursive trace nodes
and six initial threshold attempts without finding an exact rational point.
No exact Farkas certificate was produced. Therefore this run establishes
neither feasibility nor infeasibility at cutoff 28.

## Reproduction

From the repository root:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave127-independent-jacobi-certificate/verify_candidate.py `
  --cutoff 20 `
  --candidate attempts/wave129-jacobi-stress/exact-candidate-cutoff20.json `
  --columns-cache attempts/wave129-jacobi-stress/columns-cutoff20.pkl `
  --write attempts/wave129-jacobi-stress/verification-cutoff20.json
```

The analogous cutoff-18 command changes all three occurrences of `20` to
`18`. The attempted cutoff-28 recovery and its full trace are retained in
`exact-candidate-cutoff28.json`.

## What this does not show

These are finite necessary-condition relaxations. They do not construct a
strongly regular graph, construct a lattice, prove that a rank-28 case is
realizable, exclude rank 28, or resolve Conway-99. Discovery has not promoted
its own work to `VERIFIED`; an independent verifier is still required.
