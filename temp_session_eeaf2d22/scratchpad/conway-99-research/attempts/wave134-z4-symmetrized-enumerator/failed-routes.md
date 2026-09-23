# Failed and bounded routes

## Invalidated provisional searches

All three searches below used a preseal undercount with 26 primal and eight
dual composition orbits. The corrected complete tables have 42 and 22
orbits. These runs document failure modes only and make no claim about the
corrected system.

## Full exact rational solve

The hostile-corrected system contained 1,119 primal orbits, 1,118 allowed
dual rows, and 157 forced-zero dual rows. Z3 exact rational arithmetic
reached a 300-second hard wall with no result. Peak observed working set was
about 3.3 GiB. Classification:
`INVALIDATED_PRESEAL_UNDERCOUNTED_MODEL`.

## Floating-point support discovery

The transform was row-scaled and passed to HiGHS through SciPy. HiGHS warned
that 978,080 coefficients were below its matrix threshold and then returned
`Solve error`; no numerical support was emitted. Classification:
`INVALIDATED_PRESEAL_UNDERCOUNTED_MODEL`.

Floating-point output would not have been evidence even if returned; it was
intended only to propose a support for exact reconstruction.

## Incremental exact face

An exact incremental model retained all 157 zero rows but initially added
only the eight graph-forced dual lower rows. Its first rational feasibility
solve reached the 180-second hard wall before producing a point.
Classification: `INVALIDATED_PRESEAL_UNDERCOUNTED_MODEL`.

## Corrected pre-publication mistakes

Four pre-verification defects were found and corrected:

1. `q_u+q_v` and `q_u-q_v` were initially conflated with their doubles.
   They are distinct dual words; only doubled plus/minus coincide modulo
   four.
2. The primal torsion code is `R+<1>`, so weight seven remains possible as
   the complement of an `R` word of weight 92. The dual torsion code is
   `Rperp` and still has minimum weight eight.
3. Mixed odd/even coefficients on supports of size at most three were
   missing. The corrected tables enumerate every nonzero primal coefficient
   pattern and every even-sum dual coefficient pattern through size three.
4. The dual residue shell `nodd=92` was initially allowed. Since
   `Res(Cperp)=D intersect j^perp`, complementing any nonzero even residue
   word stays in `D`; `d(D)>=8` forces even residue weights at most 90.
   Four orbits moved from allowed to forced zero.

No output from either incorrect provisional model is retained as evidence.
