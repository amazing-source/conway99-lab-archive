# Wave130: exact cddlib Jacobi feasibility through q^28

Status: **CANDIDATE / SEALED**. Conway-99 remains **UNKNOWN**.

## Exact result

The rank-28, discriminant-16, level-7 index-10/index-70 Jacobi
necessary-condition relaxation is exactly rational feasible through Fourier
cutoff 28.

The cutoff-28 certificate contains 239 rational module coordinates. Direct
substitution into the unreduced model gives:

- 454 of 454 exact equalities satisfied;
- 1,686 of 1,686 exact inequalities satisfied;
- zero failed rows; and
- 506 tight inequalities.

The candidate SHA-256 is
`05ad8cf461cc7c79f85300d45492f1f30e3c1030a3c1943a9da3984d5add39a3`.

A second replay regenerated the Jacobi columns without the cache and returned
`VERIFIED_EXACT_RATIONAL_FEASIBLE` with the same row counts. Under the
repository separation rule, this discovery package nevertheless remains
`CANDIDATE` until a different verifier agent audits the sealed files.

## Chronology

| Cutoff | Method | Exact outcome | Original replay |
| --- | --- | --- | --- |
| 10 | direct cdd.gmp phase-I feasibility | rational feasible | 282 equalities, 320 inequalities |
| 22 | incremental exact repair from the Wave129 q^20 point | rational feasible | 408 equalities, 1,160 inequalities |
| 24 | incremental exact repair from q^22 | rational feasible | 426 equalities, 1,328 inequalities |
| 28 | incremental exact repair from q^24 | rational feasible | 454 equalities, 1,686 inequalities |

The q^22, q^24, and q^28 equality systems all have exact rank 139, leaving
100 affine variables. At q^28, positive-proportional row deduplication leaves
510 inequalities. The final cddlib solve needed only 145 of them because every
returned rational point was replayed against all 510 and violated rows were
added exactly. Five iterations took 392.34 seconds wall time and 279.52
seconds process CPU in the recorded run.

The earlier full q^18 margin and phase-I trials were capped after making no
terminal progress. Their logs are retained. Those caps prove nothing. The
later incremental route bypassed the degeneracy by using exact feasible
lower-cutoff points as affine origins.

## Correction of the numerical boundary

Wave126 reported a floating-point infeasibility diagnostic at q^28 and
explicitly labeled it non-theorem numerical evidence. Wave127 and Wave129
already refuted analogous lower-cutoff numerical failures. The exact q^28
primal certificate now refutes the Wave126 q^28 numerical diagnosis itself:
one rational vector satisfies every row of that finite relaxation.

This correction does not refute a theorem or settle the graph problem. It
shows that floating solver failure on this badly scaled, highly degenerate
polyhedron was not a valid rank exclusion.

## Exact formulation

The equality rows are eliminated over the rationals. If `x = p + D t`, each
remaining inequality has the form

```text
b_i + a_i t >= 0.
```

Rows are multiplied by positive rational scalars to obtain primitive integer
coefficients, so feasibility is unchanged. `cdd.gmp` then solves exact
zero-objective feasibility subproblems. Each rational point is checked against
every omitted reduced row; the most negative rows are added and the process
repeats. Publication occurs only after reconstruction of all 239 coordinates
and exact replay against every original row.

For an infeasible subsystem, `exact_cdd_lp.py` also implements the exact
common-margin LP

```text
maximize s subject to b_i + a_i t - s >= 0.
```

A negative exact optimum would expose rational dual multipliers forming a
Farkas certificate. No such certificate was needed or found here because the
q^28 system is exactly feasible.

## Reproduction

From the repository root, independently regenerate and replay the q^28
certificate:

```powershell
.\.venv\Scripts\python.exe -B `
  attempts/wave127-independent-jacobi-certificate/verify_candidate.py `
  --cutoff 28 `
  --candidate attempts/wave130-cdd-exact-lp/result-cutoff28-warm.json `
  --write attempts/wave130-cdd-exact-lp/verification-cutoff28-regenerated.json
```

Run the focused exact-cdd tests:

```powershell
$env:PYTHONPATH='attempts/wave130-cdd-exact-lp'
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts/wave130-cdd-exact-lp `
  -p test_exact_cdd_lp.py -v
```

## Finite-relaxation-only wall

This package does **not** construct a strongly regular graph, construct a
lattice, realize rank 28, exclude rank 28, establish an all-cutoff modular
object with every required integrality condition, or resolve Conway-99.
Finite feasibility is a null result for this particular exclusion strategy:
the imposed necessary conditions do not contradict rank 28 through q^28.
