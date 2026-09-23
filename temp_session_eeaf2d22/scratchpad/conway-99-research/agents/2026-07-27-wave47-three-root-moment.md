# Wave 47 three-root flag-moment discovery

## Assignment

Move the endpoint search into the next overlap-sensitive moment space that
still closes in order-seven variables: three pointwise-labelled roots and
order-five flags with two free vertices.  Cover every locally admissible root
pattern without target-graph symmetry, calibrate exact coefficients on real
graphs, and test the immutable Wave45-v1 witnesses.

## Candidate finding

`CANDIDATE`; independent verification is required.

All eight labelled root patterns were enumerated.  Their matrix orders are
`64,56,56,42,56,42,42,20` for root masks `000` through `111`; their exact
ordered-root multiplicities at `(99,14,1,2)` are
`590436,99792,99792,16632,99792,16632,16632,1386`.

Every product coefficient counts labelled root embeddings and ordered pairs
of unordered free pairs directly.  Union orders are exactly five, six, and
seven.  There is no automorphism division.

The Petersen and Clebsch controls match their direct Gram matrices exactly in
all eight families.  The direct matrices are sums of integer outer products.

The two stored Wave43/44 witnesses and fifteen immutable Wave45-v1 witnesses
are exactly indefinite in all eight families.  Numerical eigenspaces were
used only to propose integer directions; every promoted direction has a
strictly negative quadratic value under ordinary exact integer arithmetic.
The ledger contains 2,664 source directions and 2,657 distinct primitive
linear PSD cuts.

## Handoff

The verifier-facing artifact is
`attempts/wave47-three-root-moment/compact-handoff.json`, SHA-256
`8b74110bc6ae983e288d448cd1a963f81521f178e8280bbbf5864274a1639a47`.
Its canonical internal payload digest is
`e6d1991c20c8c30c4e393a081cf3fa3c4264b6ee5dacae279d5b6ab726766867`.
It retains one deterministic representative exact cut per source plus hashes
for the complete 50.8 MB reconstruction.

The complete raw cut ledger is intentionally outside the compact manifest.
It is reproducible from the frozen inputs and has SHA-256
`d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e`.

Seven discovery tests pass.  Full-run memory checkpoints stayed between
53.05% and 54.53% free.  The reconstruction now uses a conservative 20%
continuation guard.

## Status wall

- exact coefficient/cut construction: discovery-side `CANDIDATE`;
- independent verification: pending;
- all 17 immutable witnesses: exactly refuted by discovery;
- complete PSD-constrained integer search: not performed;
- endpoint `n3=4158`: `UNKNOWN`;
- strict upper bound below `4158`: `NOT_PROVED`;
- graph construction: none;
- external novelty: `UNKNOWN`.
