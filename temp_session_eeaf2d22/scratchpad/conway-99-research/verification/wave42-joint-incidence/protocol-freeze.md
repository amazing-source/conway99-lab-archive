# Wave 42 canonical joint-incidence verifier: precomparison protocol

Frozen before opening `attempts/wave42-joint-incidence/**` or its agent report.

## Input and scope

The sole mathematical data input is the independently verified Wave 41 result
`verification/wave41-allquotient-lifts/independent-results.json` at the hash in
`input-freeze.sha256`.  The selected record is the canonical first witness with
`rank_F7(3I-A_core)=32`, equivalently the triangle block has rank 33.  Its lift
mask must be 51739.

Everything checked here is conditional on all of the following:

1. a hypothetical `srg(99,14,1,2)` exists;
2. `n3=4158`;
3. `r3=12`;
4. every edge has local type `2+2+2`;
5. the canonical Wave 41 mask-51739 triangle block occurs.

No conclusion will be promoted to existence of a 60-column completion, an
outside graph, endpoint exclusion, a strict upper bound, a graph, a
counterexample, a solution, or a novelty/priority claim.

## Independent reconstruction

The verifier will use only Python's standard library and will not import
discovery code.  It will:

1. reconstruct the 36-vertex core from the frozen Wave 41 edge list;
2. reconstruct the 39-vertex triangle block and check its rank over `F_7` is
   33;
3. derive the required Gram matrix `Q=B B^T` from the SRG common-neighbour
   equations, not from any Wave 42 discovery output;
4. verify that the core components have orders 12 and 24 and meet each of the
   three 12-vertex fibres in 4 and 8 vertices;
5. prove the Cauchy equality that every hypothetical outside column contains
   exactly 2 vertices of the 12-component and 4 of the 24-component;
6. enumerate the 60 nonmatching pairs in each fibre and check that every
   hypothetical completion uses each pair exactly once;
7. derive the six component-pattern multiplicities
   `4,4,4,16,16,16`;
8. exhaust all `60^3=216000` six-sets through these filters:
   positive Gram support, component equality, and local SRG
   common-neighbour feasibility;
9. verify a separately generated positive two-fibre concurrence certificate;
10. derive the conditional outside-column overlap distribution and every
    forced numerical consequence for a hypothetical outside graph `H`.

Expected numerical targets supplied for adversarial checking are:

- six-set census `216000 -> 118718 -> 49736 -> 45032`;
- column overlaps `0/1/2 = 458/1004/308`;
- outside edges by overlap `0/1/2 = 96/144/0`;
- 32 triangles and 181 four-cycles in a hypothetical `H`.

These expected values are targets, not trusted evidence.  The verifier must
derive them from the frozen Wave 41 input.

## Independence and comparison boundary

Implementation, hostile tests, a positive two-fibre certificate, and the
precomparison result will be hashed before any discovery artifact is opened.
Only then may a separate comparison routine read discovery output.  A match
can verify this scoped reduction; it cannot verify a full completion.

