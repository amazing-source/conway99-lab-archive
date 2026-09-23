# Wave 66 verifier failed routes and retained boundary

## Discovery scalar replay is not independence

The discovery checker contains correct scalar arithmetic but does not encode
the quotient-lattice saturation proof or the low-norm graph arguments.  It
was not imported or used as verification.  A structurally separate checker
reconstructs those deductions and uses discovery JSON only after the
independent artifact is built.

## The imported lower endpoint was misstated

For the package's unqualified hypothetical-graph scope, the prior universal
theorem is `r>=27`; the prior `r>=28` theorem is conditional on `n3=4158`.
This cannot be treated as a universal imported interval.  The correction
does not change Wave 66's surviving rows because Milgram independently
forces `r` even, thereby removing `r=27`.

## One Wave 2 dependency is overstated

The dual-minimum proof uses the binary-kernel minimum weight and independence
of a weight-eight support.  It does not use the separately verified fact that
every graph vertex meets such a support in zero or two points.  Discovery's
hostile-control statement that dropping any of the three facts invalidates
the proof is therefore too strong.

## “All 17 rows survive” is not the final status

All 17 endpoint rows enter the discovery Milgram table, but only the eight
even rows `28,30,...,42` survive.  The main table and survivor count are
correct; the contradictory limitation sentence is not.

## Smith data alone does not prove existence

The group

```text
Z/9 direct_sum (Z/7)^(44-r)
```

and its Milgram-compatible sign are necessary data only.  No even
rank-44 lattice realizing a surviving row, no 99-vector tight frame, and no
graph is constructed here.

## Blichfeldt does not reach the verified floor

The dual-minimum bound and Blichfeldt give only `r>=18`.  The `r=18` row
passes the exact inequality, so geometry of numbers at this strength is
strictly weaker than the imported universal `r>=27`.

## Norm fourteen remains

The proof excludes integral primitive `-4` eigenvectors of squared norms
8, 10, and 12.  Squared norm 14 is not excluded.  Even excluding norm 14
would still require a stronger lattice density or classification theorem to
produce a graph contradiction.

Conway-99 and novelty remain `UNKNOWN`.
