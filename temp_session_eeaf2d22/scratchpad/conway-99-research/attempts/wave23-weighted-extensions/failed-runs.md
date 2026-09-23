# Wave 23 retained run failures

## Missing discovery dependency in the system interpreter

The first discovery command used the system `python`, which has no SciPy:

```text
ModuleNotFoundError: No module named 'scipy'
```

No mathematical inference was made.  Later discovery commands explicitly used
the repository virtual environment.  The exact checker still uses the system
interpreter and only the Python standard library.

## Dependency locator hang

An attempt to locate bundled workspace dependencies did not return and was
aborted after approximately 2474 seconds.  It produced no model, solver result,
or mathematical evidence.  It was not retried.

## False infeasibility from destructive row scaling

The first LP divided each equality row by

```text
max(maximum absolute matrix coefficient, absolute right-hand side).
```

Because the right-hand sides are induced-subgraph counts as large as billions,
this shrank coefficients of the count variables to roughly `1e-10`.  HiGHS
then reported both the 712-row orbit system and its 186-row coarse aggregation
as infeasible.  That status was not accepted as a certificate.

A direct Farkas-ray search returned only the zero vector, exposing the
contradiction between the two numerical diagnostics.  Reparameterizing
`q_J=x_J/binom(99,7)` kept the integer coefficient matrix unchanged and scaled
only the right-hand side.  In that well-scaled model, both systems were
feasible to residual below `1.3e-14`.

The final artifact does not rely on either numerical verdict: two rounded
solutions satisfy every equation exactly, and their exact integer difference
certifies the full affine family.

## Inadmissible interpolation helper

The initial helper for Hamiltonian affine formulas evaluated the source table
at `h11=0`.  That point violates `h11>=2*n3`, so the source evaluator correctly
raised on a negative `H_16` count.  The helper now interpolates at the two
adjacent admissible points `h11=1412` and `h11=1416`.  A hostile regression
test covers this route.
