---
role: literature
date_utc: 2026-07-23T17:06:12Z
git_commit: "NOT_CAPTURED_NO_GIT (task explicitly prohibited Git)"
claim_label: UNKNOWN
scope: "Independent literature/status audit through 2026-07-23 for the conditional claim that every putative srg(99,14,1,2) has n3 >= 705, where N3 is two disjoint triangles joined by exactly two independent cross-edges, hence has at least 209991 induced 6-cycles."
inputs:
  - path: verification/global-schur/2026-07-23T162526Z-status-preinspection-freeze.md
    sha256: e8a356a8947d6825c1415c837db099989848681c8affc9cc2cfbfb82141460e0
  - path: agents/2026-07-23-wave20-global-schur.md
    sha256_frozen_only_not_opened: 64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632
method: "Source-first exact-phrase, formula, topology, spectral, Schur/Hadamard/Krein, author/title, and current-resolution searches; inspection of the hypotheses and relevant pages of primary papers; raw-byte hashing of retrieved sources; arXiv, Crossref, and OpenAlex discovery checks."
command: "Exact queries, URLs, retrieval metadata, response hashes, and a reproducible hashing command are in the companion source/query ledger."
outputs:
  - path: verification/global-schur/2026-07-23T170612Z-status-literature-audit.md
    sha256: "see companion status-hashes.sha256 after freeze"
  - path: verification/global-schur/2026-07-23T170612Z-status-source-query-ledger.json
    sha256: "see companion status-hashes.sha256 after freeze"
  - path: verification/global-schur/2026-07-23T170612Z-status-hashes.sha256
    sha256: "not self-listed"
limitations: "A literature search cannot establish novelty or mathematical truth. Indexing can lag; inaccessible manuscripts, talks, private correspondence, and non-indexed sources may exist. The discovery report was deliberately not read, and this audit does not check or certify its proof."
---

# Independent Wave 20 literature/status audit

## Bottom line

**NO RESOLUTION FOUND.** As of the cutoff above, this audit found no accepted
construction or nonexistence proof for `srg(99,14,1,2)`, no primary source for
the exact inequality `n3 >= 705`, no primary source for the equivalent
`C6 >= 209991` endpoint, and no located source evaluating the same
Schur/Hadamard spectral-projector inequality on the 231-vertex triangle graph.

That is a search result, not a proof of openness or novelty. The correct labels
remain:

| Item | Audit label | Finding |
|---|---:|---|
| Existence/nonexistence of `srg(99,14,1,2)` | `UNKNOWN` | No accepted resolution found; current primary and maintained sources still treat the target as unresolved. |
| Identity `C6 = 209286 + n3` for the target | `CITED` + arithmetic `DERIVED` | Reimbayev proves the general `n12` identity for `srg(n,k,1,2)`; substitution gives the target constant. |
| Definition of `N3` in the audited formulation | `CITED` | Reimbayev's current six-vertex source figure has two disjoint triangles and exactly two vertex-disjoint cross-edges. |
| Positive lower bound `n3 >= 705` | `UNKNOWN` | No matching or stronger published bound was located. Non-discovery is not novelty. |
| Triangle-graph spectrum `18^1, 7^54, 0^44, (-3)^132` | `CITED` | Petro--Phillips derive it conditionally for the putative target. |
| Exact Schur/Hadamard projector specialization | `UNKNOWN` | Generic Schur/Krein machinery is standard prior art, but no exact target specialization or equivalent endpoint was located. |
| Candidate proof correctness | **not assessed** | Separation boundary: the frozen discovery report was not opened. |

## Frozen statement and separation boundary

The only candidate-facing material read was
`verification/global-schur/2026-07-23T162526Z-status-preinspection-freeze.md`,
whose raw SHA-256 is recorded above. The discovery report
`agents/2026-07-23-wave20-global-schur.md` was excluded from inspection. Its
hash was copied from the freeze record and was not recomputed here.

The statement audited was therefore fixed as follows:

- `G` is a putative simple strongly regular graph with parameters
  `(v,k,lambda,mu)=(99,14,1,2)`.
- `n3` counts induced six-vertex subgraphs consisting of two disjoint
  triangles joined by exactly two independent cross-edges.
- The conditional candidate endpoint is `n3 >= 705`.
- Through the cited cycle identity, the numerical consequence is at least
  `209991` induced 6-cycles.

No automorphism, transitivity, or other symmetry hypothesis was added.

## Exact established ingredients

### Six-vertex identity and arithmetic

Reimbayev's 2024 paper states, for the studied family
`srg(n,k,1,2)`,

```text
n12 = (1/12) n k (k-2) (2k^2 - 21k + 53) + n3,
```

where `n12` is the number of type-12 induced subgraphs, identified there as
hexagons. The paper's theorem uses only the trivial inequality `n3 >= 0`.
The 2025 six-vertex paper repeats the identity and explicitly retains `n3` as
a free/unknown parameter.

For `(n,k)=(99,14)`,

```text
(1/12)(99)(14)(12)(2*14^2 - 21*14 + 53)
= (99)(14)(151)
= 209286.
```

Hence `n12 = 209286 + n3`, and the audited candidate endpoint would imply
`n12 >= 209286 + 705 = 209991`. This audit confirms the citation and
arithmetic only; it does not confirm `n3 >= 705`.

The current arXiv source bundle for Reimbayev's six-vertex paper was inspected
because text extraction does not encode the graph drawing. Its `N3` image
matches the frozen topology: two vertex-disjoint triangles with two
vertex-disjoint cross-edges and no third cross-edge.

### The 231-vertex triangle graph

For a putative target, `lambda=1` makes every edge lie in a unique triangle.
There are `99*14/2 = 693` edges, hence `693/3 = 231` triangles. Petro and
Phillips conditionally derive the spectrum of the resulting 3-clique
intersection graph as

```text
18^1, 7^54, 0^44, (-3)^132.
```

Their paper establishes this spectral input, but searches of the paper and its
May 2026 thesis expansion found no `n3`, Schur-product, Hadamard-projector, or
primitive-idempotent evaluation producing the audited bound. The thesis's
different local `tau,rho` nonnegative-integer system is explicitly reported to
have solutions for every feasible `srg(n,k,1,mu)` parameter set tested with
`k <= 50,000,000`; it does not eliminate the target.

## Closest current literature

1. **Reimbayev (2024; current journal PDF and arXiv v1).** Establishes the
   exact induced-hexagon identity and only the baseline `n3 >= 0` bound.

2. **Reimbayev (arXiv v2, 2025-11-03).** Classifies the possible induced
   six-vertex types in the `lambda=1, mu=2` family and parameterizes their
   counts by the still-free variable `n3`. This is the closest exact
   combinatorial source and contains no positive lower bound for `n3`.

3. **Petro--Phillips (Discrete Mathematics 349(3), 114862, 2026; arXiv
   2502.17845v1).** Establishes the conditional 3-clique-graph spectrum.
   It does not contain the audited Schur/Hadamard step or endpoint.

4. **Phillips thesis (arXiv 2605.22867v1, 2026-05-19).** Expands the
   clique-graph framework and tests a separate local linear/integrality
   system. It reports that system does not restrict existence and contains
   no occurrence of `n3` or `Schur`.

5. **Keramatipour (arXiv 2604.23037v2, 2026-04-28).** Reports that the
   presented SAT encodings do not handle the target in reasonable time and
   calls for better strategies; it provides neither a construction nor an
   UNSAT certificate.

6. **Cesarz--Woldar (Algebraic Combinatorics 8 (2025), 379--398).**
   Explicitly calls existence an elusive open problem and proves restricted
   automorphism-group results. Those hypotheses do not apply to an arbitrary
   target graph and do not yield the audited bound.

7. **Baker, Cumberland Conference abstract (May 2026).** Announces upper
   and lower bounds for disjoint copies of a general induced subgraph `H`,
   depending on its neighborhood size, with evenly distributed boundary
   edges in equality cases, and mentions the Conway problem. Exact-title,
   author, and arXiv searches found no manuscript or slides. The abstract
   contains no exact `N3`, `705`, `209991`, projector, or resolution claim,
   so applicability cannot be inferred.

8. **Shpectorov talk announcement (2026-06-24).** Reports nonexistence work
   for the different parameter set `srg(85,14,3,2)` and describes only a
   *possible similar approach* for `srg(99,14,1,2)`. It is not a target
   resolution.

9. **Brouwer's maintained parameter table.** The row for `(99,14,1,2)` is
   still marked `?`; Brouwer--Van Maldeghem define that mark as “none is
   known.” This is status evidence, not a proof that no unindexed result
   exists.

## Schur/Hadamard/Krein prior-art assessment

The Schur product theorem and Krein/primitive-idempotent positivity in
association schemes are standard. Searches therefore did not treat the use of
entrywise positivity itself as novel. The audit instead searched for the
specific combination of:

- the 231-vertex triangle/clique graph of the putative Conway graph;
- spectrum `18,7,0,-3` with multiplicities `1,54,44,132`;
- a rank-54 or rank-44 spectral projector/primitive idempotent;
- an entrywise square or Schur/Hadamard product;
- the numerical endpoints `705` or `209991`; and
- equivalent descriptions of two disjoint triangles joined by a 2-edge
  matching.

No exact specialization was located. Generic papers on Hadamard series,
modified/generalized Krein parameters, and Euclidean Jordan algebras for
strongly regular graphs concern the three-dimensional adjacency algebra of an
SRG or general parameter inequalities. None of the inspected metadata or
searchable text tied those results to the non-strongly-regular 231-vertex
triangle graph or yielded the audited endpoint.

Accordingly, the method-level prior art is **known**, while the exact
specialization's prior-art and novelty status are **UNKNOWN**.

## Apparent contrary claim: Ishihara (2022)

Ishihara's JSAI technical report contains “Theorem 28,” claiming that
`srg(99,14,1,2)` does not exist. It is not an accepted resolution, and the
decisive double count in equation (88) is invalid.

Fix the report's root `w0`. Its first subconstituent `L1` is a matching on
14 vertices, and each vertex of `L2` has two neighbors (labels) in `L1`.
For `w in L2`, let `H1` be its 12 neighbors inside `L2` and let `H2` be the
remaining 71 vertices. This does cover all of `L2`: any nonneighbor of `w`
shares at most one `L1` label with `w`, so at least one of its two common
neighbors with `w` lies in `L2`, giving a length-two path inside `L2`.
If `a,b` are the two `L1` labels of `w`, then:

- each of `a,b` has 12 neighbors in `L2`;
- besides `w`, exactly one of those neighbors is in `H1`, because the
  neighborhood of `w` is a matching;
- the other ten for each label lie in `H2`, and the two groups are disjoint;
- those 20 vertices have only one common neighbor with `w` in `H1`, since
  their other common neighbor is the shared `L1` label;
- the other 51 vertices of `H2` have both common neighbors with `w` in
  `H1`.

Thus the `H2`-side degrees into `H1` are `1^20, 2^51`, totaling
`20 + 2*51 = 122`, not `2*71 = 142`. Equivalently, on the `H1` side the
degrees are `10^10, 11^2`, also totaling `122`. Equation (88) asserts
`10 s + 11 t = 2 b` and drops exactly this 20-edge correction. The claimed
contradiction therefore does not follow.

This check explains why the technical report does not supersede the later
peer-reviewed and maintained sources that continue to call the target
unresolved.

## Search interpretation and publication gate

The exact query and source ledger records all searched formulations, source
versions, URLs, byte hashes, and access failures. The strongest defensible
status statement is:

> Through 2026-07-23, no accepted target resolution and no published exact or
> stronger `n3 >= 705` / `C6 >= 209991` result was located in the searched
> sources. Exact-prior-art and novelty status remain UNKNOWN.

This report cannot promote the discovery claim to `VERIFIED`, cannot certify
its proof, and should not be cited as evidence of novelty. An independent
proof verifier must still reconstruct every projector identity, trace
calculation, combinatorial interpretation, and equality case without relying
on discovery internals.
