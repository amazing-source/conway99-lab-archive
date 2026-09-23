# Wave 118: calibrated strategy estimate

Timestamp UTC: `2026-07-28T04:16:50Z`

Status: `SUBJECTIVE_RESEARCH_ESTIMATE`, not a theorem or forecast.

Evidence baseline: sealed Wave 96 manifest
`1d1e7d01edfbfcd2871683390b56e16dc36a18cfc899f301f15a0fce3b246a73`.

## Bottom line

The C4-incidence program has a respectable chance of producing another
useful exact theorem, but the current pointwise cap route is a long shot for
a complete proof.  The aggregate Jacobi-theta refinement is the most
promising version because it retains coordinate information without asking
for an exceptionally strong bound on every individual four-cycle.

Even a successful rank-28 or rank-30 exclusion would not by itself resolve
Conway-99.  A full resolution still has to cover every surviving rank and
non-endpoint branch, or replace them with one global argument.

## Method and horizon

These estimates use obstacle decomposition, not a statistical prediction:

1. identify the independent mathematical steps still missing;
2. discount routes whose current relaxations admit large positive controls;
3. distinguish a publishable intermediate theorem from a row exclusion and
   from the full conjecture;
4. give ranges under three research-productivity scenarios.

The probability horizon is **six calendar months or about 90 focused
researcher-days**, with parallel proof search, exact computation, and an
independent verifier.  Percentages are not mutually exclusive.

| Outcome within the horizon | Conservative | Central | Liberal |
|---|---:|---:|---:|
| Useful verified theorem beyond Wave 96 | 30% | 55% | 75% |
| Pointwise cap `<=25` for norm-16/18 extensions | 3% | 10% | 25% |
| Pointwise cap `<=24` through norm 20 | 2% | 7% | 18% |
| Nontrivial aggregate Jacobi/C4 incidence theorem | 15% | 35% | 60% |
| Jacobi/C4 argument excludes rank 28 or rank 30 | 4% | 15% | 35% |
| Any current C4 variant excludes at least one hard rank row | 6% | 20% | 40% |
| Current C4/Jacobi strategy alone fully resolves Conway-99 | 0.2% | 1% | 5% |

A "useful theorem" means a new independently verified exact restriction:
for example, a nontrivial extension-multiplicity bound, a proof-producing
aggregate incidence inequality, a stronger norm-20 design theorem, or a
rigorous Jacobi-form reduction.  It does not mean that Conway-99 is solved.

## Scenario assumptions and conditional timing

### Liberal scenario

Assumptions:

- the rational-characteristic Jacobi transformation closes in a modest
  finite-dimensional space;
- enough aggregate coefficients have a positivity or semidefinite
  interpretation;
- exact LP/SDP dual certificates are small enough to verify;
- the true target lies close to the necessary cap;
- no new branch explosion appears after rank 28 or rank 30 is removed.

Conditional time if the route succeeds:

| Milestone | Liberal time |
|---|---:|
| Useful theorem | 2-10 focused days |
| Rank-28 or rank-30 exclusion | 2-8 weeks |
| Full Conway-99 resolution by a cascade of the same ideas | 3-12 months |

### Central scenario

Assumptions:

- the Jacobi/coset representation can be constructed, but requires several
  iterations of basis building and certificate design;
- pointwise caps are false or inaccessible, while aggregate bounds give
  gradual improvements;
- at least one additional independent method is needed after a row
  exclusion.

Conditional time if the route succeeds:

| Milestone | Central time |
|---|---:|
| Useful theorem | 2-6 weeks |
| Rank-28 or rank-30 exclusion | 2-6 months |
| Full Conway-99 resolution | 1-3 years |

### Conservative scenario

Assumptions:

- the marked Jacobi series needs the full discriminant-form/Weil
  representation and loses scalar positivity;
- local extension caps are genuinely larger than 25 and 24;
- exact flag or SDP systems grow faster than proof certificates can be
  checked;
- eliminating one rank reveals structurally different surviving rows.

Conditional time if a solution is nevertheless found:

| Milestone | Conservative time |
|---|---:|
| Useful theorem | 2-4 months |
| Rank-28 or rank-30 exclusion | 6-24 months |
| Full Conway-99 resolution | 3-10+ years |

Under the conservative assumptions, the most likely outcome is that this
strategy never resolves the conjecture by itself.  The displayed time is
conditional on eventual success, not an expected completion date.

## Why the pointwise caps are difficult

- The fixed-C4 type partition still admits
  `6,148,477,125,000` norm-16 selections before global graph constraints.
- The common projector and lattice minimum leave a 40-dimensional residual
  sphere.  Its relaxation admits an 80-point cross-polytope, well above the
  required cap 25.
- A cap must therefore use arithmetic lattice-coset information or
  simultaneous graph compatibility, not only distance, dimension, or local
  degree moments.
- The norm-20 cap covers an additional shell and more support geometries,
  so its smaller target 24 is at least as demanding pointwise.

## Why the Jacobi route remains credible

- Every induced C4 has the same four-coordinate projector Gram matrix.
- The desired shell statistic is an exact coefficient of the aggregate
  four-variable marked theta/Jacobi series.
- Aggregation may exploit cancellation and modular relations even when one
  cycle has many extensions; a pointwise cap is unnecessarily strong.
- The norm-20 classification extends the graph dictionary by one theta
  coefficient and gives a second independent target at rank 30.
- The modular spaces are finite-dimensional, so a successful inequality
  can in principle end in an exact rational certificate.

The critical unknown is whether the required marked coefficients lie in a
cone with enough sign control.  Harmonic theta coefficients are generally
signed, and scalar nonnegativity does not automatically survive the
coordinate refinement.

## Recommended allocation

- 60%: construct the aggregate C4 Jacobi/coset transformation and search
  for an exact dual incidence certificate;
- 25%: build a proof-producing local extension or rooted flag-SDP
  relaxation that imports global common-neighbor constraints;
- 15%: strengthen the norm-20 support classification and test whether
  higher theta coefficients provide additional positive observables.

Stop or redirect a lane when it produces a verified feasible witness above
the needed bound.  Preserve such witnesses as null certificates rather
than treating solver nonhits as evidence.

## Limitations

- These probabilities are subjective research judgments, not calibrated
  frequencies, guarantees, deadlines, or model capability claims.
- Mathematical discovery has a heavy-tailed time distribution; "never by
  this route" is a real possibility.
- The estimates assume the current Wave 96 claims survive independent
  verification.
- Literature novelty and priority are not estimated.
- A row exclusion is not a proof of Conway-99.
