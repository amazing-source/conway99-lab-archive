---
role: construction
date_utc: 2026-07-27T20:03:04Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: CANDIDATE
scope: bounded exact rational cut loop over all verified Wave45, Wave47, and Wave49 moment families
inputs:
  - attempts/wave53-exact-cut-loop/input-freeze.sha256
method: exact rational witness replay, exhaustive 32-family matrix evaluation, primitive integer negative directions, lower-deck cut linearization, and exact active-set reconstruction
command: .\.venv\Scripts\python.exe -B attempts\wave53-exact-cut-loop\exact_cut_loop.py --compute
outputs:
  - attempts/wave53-exact-cut-loop/exact-result.json
  - attempts/wave53-exact-cut-loop/package-manifest.sha256
limitations:
  - discovery cannot verify itself
  - bounded three-cut run only
  - rational aggregate witnesses are not integer counts or graphs
  - endpoint and strict upper-bound status remain UNKNOWN
---

# Wave53 exact cut-loop discovery report

The run began from the independently verified Wave51 support-136 rational
witness. It evaluated 32 moment matrices at each of four exact rational
witnesses: three Wave45, eight Wave47, and twenty-one Wave49 families.

All 128 matrices were exactly indefinite. A primitive integer direction with
negative exact rational quadratic was recorded for every matrix. The
trace-scaled exact selection rule added Wave49 root-family cuts `220`, `62`,
and `221`. Every cut rejected its source witness exactly, and every augmented
LP through 177 cuts had an exact rational successor satisfying all 170
Wave44 equations, cumulative cuts, bounds, and nonnegativity conditions.

Support sizes progressed `136 -> 132 -> 136 -> 138`. All 32 matrices at the
terminal witness remain indefinite, so the run supplies machinery and three
new valid cuts but no full-PSD point or infeasibility certificate.

An unsealed fourth-cut experiment produced a floating infeasibility status.
Its proposed Farkas ray had a `7.431e-10` residual and failed exact
reconstruction, so it was rejected and retained only as a failed route.

Outcome: the final 177-cut rational relaxation is **CANDIDATE exactly
feasible**, conditional on independent replay of this discovery package.
Full PSD feasibility, integrality, graph construction, endpoint `n3=4158`, a
strict upper bound, Conway-99, and novelty remain **UNKNOWN**.
