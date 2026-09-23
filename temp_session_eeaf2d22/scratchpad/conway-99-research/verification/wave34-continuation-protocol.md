# Wave 34 continuation protocol freeze

Date frozen: 2026-07-24T19:45:20Z

Public base commit:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

Public draft PR:
`https://github.com/YesterdaysLemon/conway-99-research/pull/1`

Project status at freeze:

```text
Conway-99 existence/nonexistence:                 UNKNOWN
n3=708:                                           UNKNOWN
rooted graph-extension criterion:                 VERIFIED scoped
rooted binary criterion solution or exclusion:    UNKNOWN
rooted full endpoint:                              UNKNOWN
rootless formal contraction null trade:           VERIFIED scoped
rootless actual-incidence motif forcing/avoidance: UNKNOWN
rootless indecomposable endpoint:                  UNKNOWN
strongest conditional bound:                      n3>=708
```

## Frozen inputs

| input | SHA-256 |
|---|---|
| `AGENTS.md` | `4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3` |
| `CONJECTURE.md` | `7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58` |
| `STATUS.yaml` | `feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864` |
| `verification/2026-07-24-wave33-clean-clone.md` | `d83e18052114affaed873ddaa7bdc6a26c63afc6432345e1027aeef5bd66d052` |
| `verification/wave33-rooted-extension/comparison-results.json` | `2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd` |
| `verification/wave33-rooted-extension/comparison-audit.md` | `fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a` |
| `verification/wave33-rootless-motif/comparison-results.json` | `8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872` |
| `verification/wave33-rootless-motif/audit.md` | `a761d48419664b3db8605ca2a7dd203c2a1ce6ccd1e96d1ac2c028b1c5209bc9` |
| `verification/wave33-rooted-construction-chronology/chronology-results.json` | `b2f0b872221a3fd9f41d6a88637be21034b70e8c8129fe57617115548b425957` |
| `verification/wave33-rooted-construction-chronology/audit.md` | `1346992e11db72c4c94018293d3827214e2ee79e074490b8f905028e20fa30f1` |

## Target R-S: rooted structural attack

Conditional on the exact Wave 33 rooted premises, use the fixed labeled
14-vertex signed Fano support and its fixed support-to-O incidence. The
remaining graph variables are a symmetric hollow binary O-O adjacency
matrix and a binary O-Q incidence matrix. Attack the complete six-block
criterion for `A^2=12I-A+2J`.

The target is one of:

1. a complete binary solution, emitted as a full 99-vertex machine-readable
   adjacency certificate;
2. a complete checkable exclusion of all binary solutions; or
3. a new exact structural reduction that strictly shrinks the unrestricted
   labeled domain and records every surviving degree of freedom.

No automorphism, orbit representative, transitivity, Cayley, circulant,
outside-vertex symmetry, or fixed O-Q design may be assumed. A theorem about
one selected simple `2-(15,3,2)` design is restricted evidence only.

Promising but nonbinding directions include exact kernel/SNF analysis of the
linear blocks, parity or modular consequences, forced intersection
distributions, and consistency between `DB=2J-B` and the nonlinear O-O
block. Any division, rank claim, or without-loss-of-generality step must be
audited.

## Target R-C: rooted exact encoding and certificate track

Independently encode the same unrestricted labeled binary criterion. The
encoding must include every binary, symmetry, zero-diagonal, row/column,
design, coupling, and nonlinear common-neighbour equation required by the
six blocks.

A positive result must emit the complete 99-vertex graph and pass a small
independent exact checker. A negative result requires a proof-producing
complete-domain certificate and an independently checked mapping from the
criterion to the certified formula. A solver exit code, timeout, heuristic
nonhit, incomplete enumeration, or search over one design is no evidence of
nonexistence.

Before running a large search, record variable and clause/constraint counts,
the exact domain, solver/version/proof format, and the planned independent
checker. Unsafe symmetry breaking is prohibited.

## Target I: rootless actual-incidence attack

Assume the exact frozen target, actual vertex-triangle incidence, the
rootless integrally indecomposable endpoint, and

```text
tr(A_-1 A_-2^2)=0.
```

Attack one of:

1. derive from actual incidence and the full projector/Schur package that
   `tr(A_-1 A_-2^2)>0`;
2. derive another complete contradiction; or
3. construct a complete valid rootless endpoint.

The Wave 33 formal local null trade proves that the audited bilinear
`Q[Gamma]` and `N^T p(A)N` contractions alone cannot force the motif.
Therefore any positivity proof must use genuinely additional information:
uncontracted labels, three-leg incidence, global overlap consistency,
projector/Schur compatibility, or another precisely named premise.

The actual R2 board has four pair-indexed transversal candidates. Counting
these with multiplicity is not enough; the track must control closure and
overlap in an actual global object. Partial 99-vertex controls, low moments,
or formal local tables remain scoped evidence.

## Initial discovery separation

Three initial tracks run from this protocol and the frozen public inputs:

- rooted structural proof;
- rooted complete-domain encoding/construction; and
- rootless actual-incidence proof.

Each track uses GPT-5.6/Sol at maximum reasoning, as requested. Until its
initial report and artifacts are saved, a track must not inspect another
Wave 34 track's files or messages. The shared Wave 33 inputs are permitted.

Each initial report must state:

1. exact claim and domain;
2. assumptions and imported results;
3. numbered lemmas or exact witness;
4. commands, dependencies, versions, seeds, and runtime;
5. complete versus restricted coverage;
6. failed routes;
7. strongest self-objection;
8. machine-readable outputs and SHA-256 hashes;
9. limitations and unresolved obligations; and
10. the strongest conclusion actually justified.

Discovery tracks may use only `DERIVED`, `CANDIDATE`, finite evidence,
`REFUTED`, or `UNKNOWN`. They cannot promote their own work to `VERIFIED`.

## Verification and publication wall

The orchestrator alone controls Git and public state. A substantive candidate
must be frozen before comparison and reconstructed by a verifier that did not
author it. Repairs retain the failed version and receive a fresh verification
pass.

No result changes `n3=708`, Conway-99, endpoint, or novelty status unless the
applicable exact-statement, complete-domain, independent-verification,
clean-clone, and current-literature gates all pass. Absence of a found object
is not nonexistence evidence without a complete checked certificate.
