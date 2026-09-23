# Wave 60 clean-verifier seal protocol

Frozen: 2026-07-27

## Separation

The verifier first listed and SHA-256 hashed the complete discovery directory
and the relevant public inputs.  Those bytes were written to
`preinspection-freeze.sha256` before any discovery derivation,
implementation, test, or result was opened.  The independent verifier then
reconstructed the finite problem from the mathematical specification and
does not import a discovery module.

The discovery implementation was inspected only after the independent
reconstruction passed.  Discovery tests were replayed as a secondary source
audit, never as verification of their own claims.

## Independently reconstructed scope

1. Enumerate the `3 * 3 * 24 = 216` coordinate-normalized component graphs.
2. Check connectedness, cubicity, triangle-freeness, and every sector-aware
   common-neighbour cap directly.
3. Canonicalize accepted components under the complete `S4 x S4 x S4`
   action inside the fixed fibres, with no fibre permutation.
4. Act on the 1,140 unordered triples using only one simultaneous `S3`
   permutation of the fixed triangle and all component fibres.
5. Build the exact 36-by-36 integer target Gram matrix for every triple and
   row-reduce it independently over `F2`.
6. Derive the six local pair categories, enumerate all 21 row/column-sum-two
   component/fibre patterns, and count candidate columns for all triples.
7. Directly enumerate and check all 20,928 aligned type-4 candidate columns,
   including fibre/component profiles, mixed cuts, and every positive Gram
   pair.
8. Derive the within-component pair sums, row sums, and aligned pattern-ledger
   equations without using a SAT or local-search artifact.

## Hostile controls

- A triangle-producing edge injection must fail component admission.
- A `600/600/600` fibre profile must fail the formal-pattern filter.
- A local pair with zero target Gram entry must fail candidate admission.
- Toggling one target diagonal entry must be detected as non-alternating over
  `F2`.
- Independent fibre permutations on different components are forbidden.  The
  verifier emits a concrete triple whose unsafe independent image is outside
  its legitimate simultaneous-fibre orbit.

## Search-status policy

The bounded SAT artifact contains no model or checked proof.  The local-search
artifacts contain no best-state matrix or assignment.  Their numerical
telemetry is therefore not promoted.  Both remain
`UNKNOWN_NON_EVIDENTIARY`; a positive-error heuristic run is not an
infeasibility certificate.

## Commands

```powershell
.\.venv\Scripts\python.exe -B verification\wave60-c3-incidence-design\test_independent_verify.py
.\.venv\Scripts\python.exe -B verification\wave60-c3-incidence-design\independent_verify.py
.\.venv\Scripts\python.exe -B attempts\wave60-c3-incidence-design\test_exact_check.py
```

## Promotion boundary

`VERIFIED` applies only to the finite classification, safe coordinate
quotient, rank histogram, candidate-support counts, and marginal reduction.
No 36-by-60 incidence design, UNSAT certificate, compatible `Y`, endpoint
contradiction, or Conway-99 solution is verified.  The endpoint remains
`UNKNOWN`.
