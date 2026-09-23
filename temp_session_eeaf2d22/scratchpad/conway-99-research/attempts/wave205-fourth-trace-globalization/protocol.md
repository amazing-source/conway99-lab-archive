# Wave 205 fourth-trace globalization protocol

## Frozen branch

Assume only the still-open conditional branch

```text
G is srg(99,14,1,2)
n3=4158, equivalently the induced triangular-prism count P=0
rank_F3(D)=11
```

Let the verified centered realization have 231 projectively distinct
singular columns `z_T` in a nondegenerate 11-space over `F_3`. For each graph
vertex `x`, let `P_x` be the verified orthogonal projector onto the
six-dimensional span of its seven triangle columns. Freeze

```text
g_xy=tr(P_x P_y)
h_xy=tr(P_x P_y P_x P_y).
```

Wave 204 verifies that for graph edges, `h_xy=1` exactly for outer type
`4+2` and is zero for types `6`, `3+3`, and `2+2+2`.

## Required lanes

### Proof A: nonedge classification

Derive `h_xy` for a nonadjacent graph pair from actual SRG common-neighbor
geometry and the centered 231-column Gram matrix. The preferred endpoint is
one of:

1. a complete finite classification of the possible nonedge cross-Gram
   modules with an exact checker and full premise ledger;
2. a graph-parameter-only formula for `h_xy`; or
3. a rigorously proved obstruction showing why the existing verified data do
   not determine `h_xy`, together with an exact target-shaped relaxed
   countercontrol.

Do not infer a true column relation from a Gram-kernel word.

### Proof B: global moment/module identity

Study the full `99 by 99` matrix `H=(h_xy)`. Seek exact contraction, row-sum,
rank, module, characteristic-polynomial, or association-algebra identities
forced by the actual point-triangle incidence matrix and

```text
sum_x P_x=0.
```

Any claimed rank bound must use the correct ambient tensor space. In
particular, do not place `wedge^2(P_x)` in a 55-dimensional vector space
without accounting for its operator coordinates.

### Literature/hostile construction

Audit primary sources for finite-field fusion-frame fourth moments,
projector designs, orthogonal/polar association schemes, and trace-tensor
rank bounds with exact hypothesis comparison. Independently search for exact
controls that satisfy progressively stronger endpoint premises while
separating fourth-trace behavior. Every failed target premise must be listed.

## Candidate inflection points

A Wave 205 inflection point is reached if independent verification establishes
at least one of:

- a complete nonedge `h_xy` classification;
- a new full-matrix identity or incompatible rank/moment bound;
- an endpoint or rank-11 exclusion;
- a construction-level compatibility blueprint substantially stronger than
  pairwise data;
- a well-sealed obstruction proving that the proposed fourth-order route
  cannot advance without a newly named graph-specific invariant.

A bounded nonhit, solver status, relaxed control, or unverified derivation is
not an inflection point by itself.

## Fixed status boundary

```text
Conway-99:                 UNKNOWN
rank-11 endpoint:          UNKNOWN
n3=4158 endpoint:          UNKNOWN
rigorous n3 interval:      708<=n3<=4158
conditional Q bound:       Q>=7059
Q>=7060:                   NOT PROVED
automorphism assumption:   NONE
```

## Frozen inputs

```text
git commit
e6ac24b5728ae8f2dc13b5a6ee0f50e965843b71

verification/wave171-pq-centered-code/verification-report.md
sha256 1f2ba5ed92ba6bb1ccc05cd753a8e359f208c3ddc7ca85766f26f8869346414f

verification/wave176-star-projector-circuits/audit.md
sha256 f58577409f39e98b06bfbe206221d3d278f0c473bcf5057afc381094d5e65d05

agents/2026-07-29-wave191-global-star-module-proof-b.md
sha256 afe7d35627ec14a9599b427bcca0751e86a3f32b71fb7baf4d91e9e2e335f75f

verification/wave203-two-center-incidence-verifier/audit.md
sha256 382d8553457557fe2ecbe0fd1733ecb06b01f5c60be879e65cab56c078edc3d7

verification/wave204-global-compatibility-verifier/package-manifest.sha256
sha256 48cd018c7f7cebe7f2bc93a6dbd9440422f8dc843bc6c0fa96b29968e440f9c2

verification/2026-07-29-wave204-orchestrator.md
sha256 7760a4c5a4b6a501262bbb3b061828725cd23c6837fd724fada84d94a3124edd
```

## Separation and evidence rules

- Discovery agents may label results only `DERIVED`, `CANDIDATE`, `REFUTED`,
  or `UNKNOWN`.
- Exact computational claims require deterministic source, tests,
  machine-readable results, input hashes, and a package manifest.
- A fresh verifier must freeze its protocol and independent implementation
  before opening Wave 205 discovery packages.
- The verifier may veto or narrow a claim but may not silently repair it.
- Original target status changes only after a complete independently checked
  graph certificate or nonexistence proof.
