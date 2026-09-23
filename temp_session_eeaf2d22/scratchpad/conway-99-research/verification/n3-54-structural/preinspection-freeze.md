# Wave 17 `n3=54` structural audit: preinspection freeze

```yaml
role: verifier
date_utc: 2026-07-23T12:09:53Z
git_commit: 1eb7c18
claim_label: UNKNOWN
scope: independent adversarial audit of the frozen Wave 17 conditional n3=54 structural residual
inputs:
  expected_submission: agents/2026-07-23-wave17-n3-54-structural.md
  expected_submission_sha256: ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18
method: precommitted reconstruction, mutation, and hostile edge-case plan written before inspection of the submitted report or implementation
command: none
outputs:
  verification/n3-54-structural/preinspection-freeze.md: SELF_HASH_AFTER_WRITE
limitations: this freeze records no verdict and imports no discovery implementation detail
```

## Inspection boundary

This file was written before opening either
`agents/2026-07-23-wave17-n3-54-structural.md` or any file under
`attempts/wave17-n3-54-structural/`.  Only the audit assignment was known:
the submission is expected to discuss a 23-to-6 active-profile reduction,
an active-set minimum-degree/equality case, a cubic point graph, incidence
identities, component and parity arguments, binary rank bounds, surface
links, and moment calculations.

No submitted checker, enumeration order, proof prose, or intermediate value
has been read.  The provisional status of the conditional `n3=54` case,
Conway-99, and novelty is `UNKNOWN`.

## Claims that require independent reconstruction

1. Starting only from explicitly cited and hash-bound audited premises,
   enumerate every nondecreasing active `q`-profile at `n3=54`, including
   all profiles containing `q=4`; confirm the claimed raw and residual
   counts without importing a discovery enumerator.
2. Re-derive the active-set size upper bound and the internal minimum-degree
   lower bound.  Audit every map from labels, points, graph vertices, and
   support incidences to distinct actual neighbors.  A multiplicity,
   repeated support edge, or quotient point must not be counted twice.
3. If the argument reaches equality in a spectral/Rayleigh bound, prove each
   equality condition and the resulting equitable cut.  Merely attaining a
   numerical bound is insufficient.
4. Reconstruct the claimed graph `F` from indexed active point sets and prove
   it is simple, cubic, and triangle-free.  Check that these properties do
   not silently assume a Wave 14 global `H`-degree law, a point-size upper
   bound, connectedness, transitivity, or an automorphism.
5. Verify the exact scope of
   `G[X] = line(F) union R` and of
   `N A_R N^T = 2 A_L`.  Determine whether these are full matrix identities,
   identities only off the diagonal, or identities restricted to
   independent edges.  Test diagonal, adjacent-edge, and independent-edge
   entries separately.
6. Independently derive any no-codegree-two statement and component
   classification.  Search for small counterexamples and disconnected
   exceptions before accepting a classification.
7. Reconstruct the human `3 K_(3,3)` parity contradiction with explicit
   vertex and edge indexing.  Check every parity transfer, component
   permutation, and implicit orientation choice.
8. Recompute all claimed `F_2` ranks, nullities, and dimension bounds using
   an implementation independent of the submission.  Test rank claims
   against row/column convention changes and disconnected components.
9. Audit the conversion to hexagonal surface links, especially manifold
   hypotheses, repeated faces or edges, componentwise Euler characteristic,
   and the claimed nonorientability obstruction.
10. Re-derive outside-vertex and triangle moment identities directly from
    the SRG parameters.  Confirm their domain, integrality, and equality
    cases, and test whether they add a genuine contradiction.

## Precommitted hostile mutations

- Delete every `q=4` profile before filtering.
- Permit an active point of size four or a singleton point.
- Merge two nominal support neighbors or two triangle neighbors.
- Count a meeting-point neighbor again as an independent support neighbor.
- Replace equality in Rayleigh by inequality while retaining equitability.
- Add a loop, parallel edge, triangle, or disconnected component to `F`.
- Apply the incidence-matrix identity on diagonal or adjacent-edge entries
  when only independent-edge entries are justified.
- Introduce a pair of vertices with codegree two and test whether the claimed
  component classification still follows.
- Flip one edge or one component in the `3 K_(3,3)` parity system.
- Transpose an incidence matrix or change the binary-rank field.
- Make a surface link disconnected, repeated, or orientable.
- Inflate a raw `UNSAT`, timeout, budget exhaustion, or absence of a
  candidate into nonexistence evidence.
- Promote `n3=54`, Conway-99, or novelty without an independently checked
  complete implication.

## Acceptance criteria

A scoped claim can become `VERIFIED` only if the human implication is
complete, every imported premise is current and hash-bound, all finite
enumerations reproduce independently, likely mutations are rejected, and
the discovery computation is not used as its own verifier.  Raw SAT
`UNSAT`, timeout, and budget statuses are non-evidentiary without checked
proof certificates.  Any repair must be recorded rather than made silently.
