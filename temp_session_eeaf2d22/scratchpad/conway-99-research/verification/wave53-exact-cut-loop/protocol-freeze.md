# Wave 53 exact-cut-loop independent verification protocol

Frozen at 2026-07-27T20:24:00Z before opening, importing, or executing any
Wave 53 discovery source.

## Role and status boundary

Role: verifier.  The target is the finite exact-arithmetic claim made by
`attempts/wave53-exact-cut-loop/**`, not the Conway-99 conjecture and not graph
existence/nonexistence.  This verification cannot promote any endpoint claim.
The strongest possible outcome is `VERIFIED` for the stated finite relaxation.

## Clean-room order

1. Hash and inventory the declared source data and reports.  Do not inspect,
   import, or execute `attempts/wave53-exact-cut-loop/exact_cut_loop.py` or its
   tests yet.
2. Recover the mathematical schema only from frozen JSON/data artifacts and
   previously independently verified Wave 45/47/49/51 packages.  Treat those
   packages as inputs to be rechecked, not as trusted conclusions.
3. Implement a new checker using only Python's standard-library integer and
   `fractions.Fraction` arithmetic.  No discovery-module imports, floating
   point feasibility decisions, NumPy, SciPy, or solver exit codes are allowed
   in the exact claim path.
4. Freeze the independent checker and its first result by SHA-256 before
   reading or running Wave 53 discovery code.
5. Only then compare against the discovery result/source and perform
   adversarial mapping, parsing, normalization, and coverage audits.

## Exact checks required

- Reconstruct the Wave 51 base system: the complete 174-cut rational witness,
  all equalities, all cumulative cut inequalities, and every nonnegative
  variable bound.
- Reconstruct every available Wave 45, Wave 47, and Wave 49 moment family and
  evaluate each matrix entry exactly at each claimed witness.
- For Wave 49 roots `220`, `62`, and `221`, independently normalize the claimed
  separating directions to primitive integer vectors, reconstruct the
  corresponding rank-one linear cuts, prove exact rejection of the source
  witness, and detect duplicate or sign-misnormalized cuts.
- Substitute each rational witness into the full relaxation.  Require all 170
  claimed equations to equal zero, all cumulative cuts and variable bounds to
  be nonnegative in their declared orientation, and independently count
  supports as `136, 132, 136, 138`.
- For the 32 declared moment matrices at each of four witnesses, prove
  indefiniteness exactly: exhibit one vector with a strictly negative exact
  quadratic form and one with a strictly positive exact quadratic form for
  each matrix, for 128 matrix/witness checks total.
- Add the three accepted primitive Wave 49 cuts to the 174-cut base and verify
  exact feasibility of the resulting 177-cut relaxation.
- Examine the excluded fourth dense Wave 45 candidate.  Its reported
  `7.431e-10` numerical residual is not an exact Farkas certificate.  Determine
  its exact residual when a rational representation is available; otherwise
  classify it as numerical-only and unusable for infeasibility.

## Adversarial checks

- Cut selection must be derived from exact rejection, not list position,
  floating tolerances, or a solver status.
- Primitive normalization divides by the gcd of all integer coefficients and
  fixes a deterministic sign; duplicates are detected after normalization.
- Variable/monomial ordering is reconstructed by names and exponent tuples,
  never by unchecked array position.
- Matrix-family coverage is compared as a set of stable family/root/block keys;
  missing and duplicate keys fail verification.
- Rational parsing accepts integers and explicit numerator/denominator forms
  only, rejects zero denominators and non-finite/decimal approximations on exact
  paths, and canonicalizes through `Fraction`.
- Numerical values may be diagnostics only.  Exact signs, equality, rejection,
  feasibility, rank-one cut coefficients, and Farkas conclusions use integers
  or `Fraction`.

## Manifest and resource checks

- Recompute every declared input-freeze and package-manifest entry, reject
  path traversal, duplicate paths, malformed hashes, absent files, and
  self-referential package-manifest entries.
- Record the current git commit and dirty-worktree boundary.  Do not edit
  discovery artifacts or unrelated WIP.
- Measure physical RAM immediately before and after the verification run.
  Require free physical memory to remain at least 15 percent.

## Acceptance

`VERIFIED` requires every exact check above plus passing independent tests and
manifest checks.  Any schema ambiguity, missing family, approximate-only sign,
hash mismatch, or resource-boundary failure downgrades the affected claim to
`UNKNOWN` or `REFUTED`.  Feasibility of the 177-cut relaxation is evidence only
that these cuts do not close the endpoint.
