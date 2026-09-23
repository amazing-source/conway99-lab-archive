# Wave 43 Proof Agent B: branch-15 two-unfixed-triangle cuts

```yaml
role: proof_b
date_utc: 2026-07-27T15:23:32Z
git_commit: e28f90464d00b98d37672b0b2b23dba15399a6f2
claim_label: DERIVED
scope: complete mate-anchor coordinate-triangle-pair prism cuts in refined endpoint branch 15, conditional on n3=4158
inputs:
  - attempts/wave37-proof-producing-endpoint/branch-15.opb.gz
  - attempts/wave42-endpoint-certificate/branch-15-seventh-triangle-delta.opb.gz
  - attempts/wave42-endpoint-certificate/branch-15-combined-propagation-certificate.json
method: exhaustive rooted-label reconstruction, all-pairs/all-matchings enumeration, exact OPB export, generalized-unit closure, and bounded two-polarity probes
command: see attempts/wave43-branch15-two-triangle/run-report.yaml
outputs:
  - attempts/wave43-branch15-two-triangle/branch-15-two-coordinate-triangle-result.json
  - attempts/wave43-branch15-two-triangle/branch-15-two-coordinate-triangle-delta.opb.gz
  - attempts/wave43-branch15-two-triangle/branch-15-two-coordinate-triangle-active-delta.opb.gz
  - attempts/wave43-branch15-two-triangle/branch-15-two-coordinate-triangle-closure.json
  - attempts/wave43-branch15-two-triangle/branch-15-two-coordinate-triangle-probes.json
limitations: independent verification pending; branch 15 remains UNKNOWN; endpoint coverage remains 0/33
```

## Derived family

I reconstructed all 924 coordinate-anchored potential triangles. The Wave 42
closure fixes 7 controllers true and 157 false, leaving 760 unfixed. Exhausting
all 288,420 unordered pairs and all six matchings leaves exactly 40,800
compatible visits and 40,800 distinct width-four prism cuts.

The enumeration yields an exact structural classification. A compatible
matching exists only for vertex-disjoint triangles whose coordinate anchors
are paired neighbors in the rooted scaffold, and the matching must pair those
anchors. There are 20,400 such triangle pairs, each with the two possible
residual matchings. Every cut forbids the conjunction of the two triangle
controllers and the two residual cross edges. There is no completed-graph
automorphism assumption.

The new family has zero exact raw-row overlap with the Wave 37 formula plus the
Wave 42 delta. Under the Wave 42 closure, 6,460 raw rows are satisfied and
34,340 distinct active width-four rows remain.

## Exact continuation result

All 34,340 active rows have slack three, so generalized-unit closure remains
exactly 830 assignments, including 174 primary graph edges. No new assignment
or contradiction appears.

I then replayed both polarities of the 32 unfixed triangle controllers with
highest active-cut incidence through the complete frozen formula and both
deltas. All 64 probes were noncontradictory. They produced zero candidate
implications, zero doubly failed variables, and zero Wave 43-sourced
derivations. There is therefore no implication requiring independent replay.

## Evidence boundary

This is a replayable stronger reduction, not a branch closure. It omits prisms
involving a triangle without a coordinate anchor. A noncontradictory
propagation fixed point is not a SAT witness, and propagation closure is not
promoted as an UNSAT proof. No target solver terminal, complete graph,
endpoint exclusion, strict upper-bound improvement, or Conway-99 solution was
obtained. Branch 15 and `n3=4158` remain `UNKNOWN`; checked endpoint coverage
is still `0/33`.

The clean-room verifier protocol is
`attempts/wave43-branch15-two-triangle/verifier-protocol.md`.

