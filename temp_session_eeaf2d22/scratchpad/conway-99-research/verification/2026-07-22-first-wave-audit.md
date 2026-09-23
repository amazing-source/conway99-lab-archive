# First-wave adversarial audit

- Date: 2026-07-22
- Role: independent adversarial verifier
- Scope: structural baseline, rooted SAT prototype, branch coverage, and
  positive certificate validators
- Verdict: `PASS` for this limited scope; Conway-99 existence remains `UNKNOWN`

## Accepted

- The frozen Conway wording, `srg(99,14,1,2)` formulation, and rooted 84-vertex
  block equations are equivalent.
- The residual pair table, local triangle/four-cycle counts, endpoint-fiber
  multiple-of-four lemma, and residual spectrum follow from the block equations.
- The compact one-way-wedge encoding is exact because its local upper bounds
  and the forced global wedge count coincide.
- The single-fiber branch split is safe: an explicit generator-BFS finds 11
  `C2 wreath S6` orbits covering all 10,395 perfect matchings, with sizes
  `3840, 2304, 1440, 720, 640, 960, 160, 120, 180, 30, 1`.
- The Python and PowerShell positive-certificate validators agree on the
  positive fixture and reject tested mutations and malformed inputs.

## Rejected or quarantined

- The 11 possible cycle-length multisets of a 24-vertex endpoint-pair 2-factor
  are coarse types, not scaffold-stabilizer orbits. Fixing one 24-vertex
  representative per multiset is rejected as an unsafe symmetry reduction.
- PySAT's in-process proof traces were incomplete or unstable on the audited
  Windows/Python build. That path was removed. No local UNSAT trace is accepted.
- Solver-returned `UNSAT_UNVERIFIED`, `UNKNOWN`, and bounded-search failures have
  no mathematical evidentiary value.
- No construction or nonexistence certificate for the 99-vertex target exists
  in this wave.

## Independent checks

- 20 code tests passed, including compact/direct small-instance agreement,
  exact branch-orbit traversal, and a bounded-scout integration check.
- 11 verification tests passed, including independent PowerShell validation,
  duplicate/case-varied JSON-key rejection, mutations, and tiny DRUP controls.
- Exhaustive truth evaluation of all 64 primary assignments for the
  `pair_count=2` calibration agreed with both SAT variants.
- `compileall` and `git diff --check` completed without errors.

The audited SHA-256 of `code/sat_model.py` is
`499fa347ab3a65ba21cf3feb2c73a42a36ebf226fb874bca6d696703bc414cf7`.

## Publication gate

This audit authorizes publishing the infrastructure and derived constraints as
exploratory work. It does not authorize a resolution claim. A positive claim
still needs a complete graph passing independent validators; a negative claim
still needs a complete public proof artifact and independent replay.
