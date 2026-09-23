# Independent verification protocol

The verifier was asked to work clean-room from the parameter definition and
the frozen prior certificates, without trusting the discovery prose.

Checks:

1. reconstruct cross degrees and all four apex-apex exclusions;
2. recover the lane sizes and inclusion-exclusion multiplicities;
3. test all four fringe support failures explicitly;
4. separate completion uniqueness from completion existence;
5. audit the marked-cycle/Wagner incidence in both directions;
6. reproduce the defect arithmetic and endpoint integer rounding;
7. inspect every vertex degree in the local shell countermodel; and
8. enforce the distinction between a shell obstruction and a full graph.

The verifier can veto promotion but cannot repair a discovery claim silently.
No computation was allowed below the host memory floor.
