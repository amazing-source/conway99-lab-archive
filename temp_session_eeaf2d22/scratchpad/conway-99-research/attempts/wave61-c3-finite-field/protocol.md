# Wave 61 finite-field cross-incidence protocol

Frozen at `2026-07-27T21:23:25Z`, before inspection of the Wave 60 component
census or implementation.

## Conditional target

Assume the prism-free `n3=4158`, `kappa=3` fixed-triangle lane.  The
36-vertex graph `X` has three twelve-vertex connected components, each meeting
each fixed-triangle fibre in four vertices.  Let `B` be a hypothetical
`36 x 60` binary `X/Y` incidence matrix and let

```text
G = B B^T
  = 12I-A_X+2J-blockdiag(J12,J12,J12)-A_X^2.
```

Every column of `B` has two ones in each of the three graph fibres and,
by the verified Wave 36 component balance, two ones in each of the three
components.

## Questions

1. Independently reconstruct all 18 fibre-preserving normalized `m=4`
   component types from the sealed Wave 60 census.
2. Visit all `C(18+3-1,3)=1140` unordered triples with repetition and rebuild
   the corresponding 36-by-36 integral Gram target.
3. Over `F_2`, verify:
   - the three fibre indicators and three component indicators span a
     five-dimensional subspace of `ker(B^T)`;
   - `rank(B)<=31`;
   - `G` is alternating;
   - the exact `rank_F2(G)` histogram.
4. Test exact rank and radical consequences over useful odd primes, with
   chronology checks against the Wave 36/Wave 58 rational theorem.
5. Go beyond rank: derive every valid quadratic or cubic parity identity for
   weight-two intersections with the six fibre/component parts; analyze the 21
   permitted component-pattern types; and test whether the three fixed pair
   inventories can be coupled modulo small primes.
6. Classify the alternating-form/Witt requirement for a factorization
   `G=B B^T` over `F_2`, while distinguishing unrestricted bilinear
   factorization from the required 60 binary columns.
7. Construct exhaustive small countermodels for any tempting overstrong
   lemma.  Preserve failed obstructions and identify the exact missing
   invariant if the lane remains feasible.

## Independence and completeness

- Wave 36, Wave 58, and the Wave 60 component census are SHA-frozen in
  `input-freeze.sha256` before inspection.
- No Wave 60 code is imported.
- The 1,140-triple census is complete only for unordered triples with
  repetition of the 18 normalized component types.  It is not an
  isomorphism census and assumes no completed-graph automorphism.
- Coordinate normalization within the three four-point pieces is not treated
  as a graph symmetry.
- An unrestricted finite-field Gram factor is not a binary weight-pattern
  factor and does not construct `B`.
- A modular solver nonhit or process status is not a certificate.

## Status wall

The discovery begins `UNKNOWN`.  It may emit an exact modular obstruction, or
a rigorous reduction/filter with positive countercontrols.  It may not
promote its own findings to `VERIFIED`.

No simultaneous integer `B`, compatible `A_Y`, endpoint graph, endpoint
exclusion, general `n3` upper-bound improvement, or Conway-99 resolution is
claimed without a complete independently checkable certificate.

## Resource guard

All computations use exact small matrices and bounded enumerations.  The
checker refuses to start below 20 percent free physical memory, stricter than
the user's 15 percent floor.
