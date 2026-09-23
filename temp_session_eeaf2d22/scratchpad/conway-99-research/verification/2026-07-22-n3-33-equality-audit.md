# Wave 9 `n3=33` equality-exclusion audit

Verdict: `PUBLISH` for the conditional exclusion of `n3=33` and the resulting
necessary bound `n3>=36`. Target result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T02:36:20Z
git_commit: 3d47bb260a71c5c2606347d8bb53e3ad766236e8
claim_label: VERIFIED
scope: conditional exclusion of n3=33 for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  agents/2026-07-22-wave8-n3-equality.md: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave9-n3-33-equality.md: b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555
  agents/2026-07-22-wave9-status-search.md: add0d9d2afc335b7de9f9f6d5ffab72d66af97a568141cc8e885725984dc6b05
  verification/n3-33-equality/verify.py: fdac28fb0daf7a9af09dd490d878a3c848b187d64a8716e0bdabe2ce36d2aea8
  verification/test_n3_33_equality.py: 8e2adceda27399d948844820f48718c3588ada9e16987af13a5bda411e5a113f
  verification/n3-33-equality/audit_exhaustive.py: 6f22d93c5575fea96dd459a1425fddb268408959e3c6f5e1ef21449f6de8ee1f
  verification/n3-33-equality/verify_exhaustive.py: 31d0c9158d471e16c85922c4647e5081ba4510b430eb1228250084b50bb4bb73
  verification/n3-33-equality/n3-33-census-manifest.json: 92cf3e612a44ab24be5e191bd8ffdb59f5f6dae5335e7ce917ef5ab73c083b9e
  verification/test_n3_33_census.py: 8160eb197cc5eae4f38daf49247fe32432181589a888182719280655e4a64608
  house_of_graphs_quartic_catalog: 05ee6bb0c2b40d63d5c44efc8e89ed1c0a381a170d81a3d052749c8edf6b14fd
  verification/2026-07-22-wave9-clean-clone.md: 94e9ebed2f7e26703ff9071ff344b71353035edce3b3656f21704b618ac0a5ec
method: independent proof reconstruction, adversarial overlap and actual-edge audit, compact exact checker, two-implementation exhaustive quartic census, mutation tests, and frozen-commit clean-source replay
command: |
  python verification/n3-33-equality/verify.py
  python -m unittest verification.test_n3_33_equality -v
  python verification/n3-33-equality/audit_exhaustive.py --catalog <11_4_3.g6.gz> --certificate <scratch.json> --git-commit 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
  python verification/n3-33-equality/verify_exhaustive.py --catalog <11_4_3.g6.gz> --certificate <scratch.json> --output <replay.json>
outputs:
  verdict: PUBLISH
  technical_commit: 3d47bb260a71c5c2606347d8bb53e3ad766236e8
  exhaustive_commit: 19f27d1ede9cdb0b4110540f52eeb3ad9c94cc94
  conditional_global_n3_lower_bound: 36
  conditional_induced_C6_lower_bound: 209322
  focused_tests: 10_passed
  census_integrity_tests: 1_passed
  full_code_tests: 48_passed
  full_verification_tests: 46_passed
  quartic_isomorphism_types: 266
  point_clique_families: 610
  exhaustive_survivors: 0
limitations: all conclusions are conditional on the Wave 6-8 graph-theoretic premises and target-specific N3 occurrence; connected quartic-catalog completeness relies on the attributed House of Graphs/Meringer source; no Conway-99 construction or nonexistence proof is claimed
```

## Independent proof reconstruction

The verifier returned `VALID` after reconstructing the proof and explicitly
attacking the following failure modes.

### Active profiles

At `n3=33`, the handshake sum is `sum q=22`. Combining the gap
`q=0 or q>=2` with `3q(T)<=r-1` leaves exactly

```text
r=10: (q(T))=(2^8,3^2),
r=11: (q(T))=(2^11).
```

No other partition of 22 satisfies all degree inequalities.

In the mixed case, each `q=3` triangle is universal in active `L` and isolated
in its complement `K`. Every original point on it therefore has singleton
active set. This is inconsistent with the crossing lemma below. Independently,
the residual eight `K`-vertices form a cubic graph, so singleton crossings are
at most four; allowed positive `H`-degree is then exactly four and cannot sum
to the required fixed-point value six.

### Labeled crossing graph and overlap

For an actual graph edge `e=uv`, the verifier formed a bipartite crossing
graph on labeled copies of `S_u` and `S_v`. This avoids silently treating
possibly overlapping point sets as disjoint. A crossing `L`-edge has a unique
orientation because its endpoint graph-triangles are disjoint.

The sets overlap in at most the unique graph-triangle containing edge `uv`.
If present, both labeled copies of that triangle are isolated, since every
triangle in either point set intersects it. At any other left triangle `T`,
the crossing degree equals the degree of graph-edge `uv` in the fixed-side
graph `H_T`, hence is zero or two. The right side has the same property.

Thus a singleton `S_u` gives `d_H(uv)` zero or two for every graph neighbor
`v`. The global Wave 6 degree set

```text
{0,4,6,8,10,12}
```

excludes two. All incident degrees would be zero, contradicting the positive
fixed-point sum `2q(T)`. The argument handles the shared-triangle overlap,
does not double any crossing, and assumes neither connectedness nor a graph
automorphism.

### Point resources and the forced `K5`

In the all-`q=2` profile, `K` is 4-regular on eleven vertices. The three
non-singleton point cliques through every active triangle consume disjoint
incident `K`-edges. Degree four forces sizes two or three and at most one
size-three point through each active triangle. The exact global equations

```text
2x2+3x3=33,
x2+3x3<=22
```

have only `(x2,x3)=(12,3)` and `(15,1)`.

For a size-three point `{i,j,k}`, the other two points on active triangle `i`
have sets `{i,a}` and `{i,b}`. The verifier checked that all three pairs are
actual graph edges because the original points share graph-triangle `i`.
Their possible crossings have sizes at most two, two, and one. The allowed
degree set forces every crossing to vanish, which forces all five missing
edges among `j,k,a,b`. Hence `{i,j,k,a,b}` is a saturated `K5` component.

Three vertex-disjoint size-three points require three distinct `K5`
components: two disjoint triples cannot lie in the same five-vertex component.
This eliminates `(12,3)` without assuming that the original `K` was connected.

### Residual complement matching

For `(x2,x3)=(15,1)`, removing the forced `K5` leaves a 4-regular graph on six
vertices, exactly `K6` minus a structural perfect matching `M`. At every
residual vertex, the three incident edges consumed by its three size-two
points must lead to a `K`-clique: a nonedge among two consumed neighbors would
give the actual internal graph edge a forbidden crossing degree one.

The four neighbors of a vertex in `K6-M` contain the two other nonedges of
`M`. Deleting any one neighbor leaves one full nonedge pair, so the three
consumed neighbors can never form a clique. The audit explicitly distinguished
the structural missing matching from any locally unused `K`-edges.

The verifier therefore returned `PUBLISH` on the conditional human proof.

## Compact checker and mutation boundary

The standard-library checker independently recomputes:

- both active-`q` sequences;
- the fixed-side endpoint totals four and six;
- the impossibility of summing bounded mixed-profile degrees to six;
- every simple singleton crossing graph through the maximum point-clique
  order;
- the two point-size integer solutions;
- all 32 local completions around a size-three point, with only `K5`
  surviving;
- all 15 perfect matchings on six vertices and all 360 labeled residual local
  choices, with zero surviving; and
- the global count, induced-six-cycle count, and twelve branch-local bounds.

Ten focused tests cover successful replay and malformed inputs. All 48 code
tests and all 46 verification tests pass. The checker does not encode the
upstream graph-theoretic derivation, and its printed conclusion is valid only
with the recorded Wave 6-9 proofs.

## Independent exhaustive quartic census

The optional secondary audit is materially different from the compact proof.
It takes the complete House of Graphs list of 265 connected 4-regular graphs
on eleven vertices, attributed there to Meringer's `genreg`, and adds the
unique disconnected type

```text
K5 disjoint union (K6 minus a perfect matching).
```

The uniqueness of the disconnected type is elementary: a 4-regular component
has at least five vertices, so the only partition of eleven is `5+6`; the two
components are necessarily `K5` and the complement of a perfect matching on
six vertices. An independent individualize/refine canonicalizer found 266
distinct codes and preserved each under two nontrivial relabelings. The
catalog itself is not redistributed; its compressed and decompressed hashes,
source URLs, counts, and deterministic canonical-code digest are retained in
the manifest.

After singleton elimination and the incidence/edge budget, the census checks
the three global resource profiles

```text
A: (x2,x3,x4,x5)=(12,3,0,0),
B: (x2,x3,x4,x5)=(13,1,1,0),
C: (x2,x3,x4,x5)=(15,1,0,0).
```

The primary exact `f`-factor enumeration found

```text
profile families A/B/C = 15/0/595,
types carrying A/B/C  = 11/0/119,
total families        = 610.
```

A separate binary incident-edge recursion reproduced the exact family digest
`3b48bc37...e6bc0` and per-type digest `c357c675...2e56f`. Every family has
between 23 and 33 forced actual graph edges inside active graph-triangles with
forbidden crossing degree. Aggregated across the census, degree one occurs
14,488 times and degree two occurs 3,840 times. Thus every family is rejected
before any global `H` support selection is needed.

The independent verifier also checks the compressed/raw catalog hashes, both
implementation hashes, all certificate witnesses, canonical and per-type
digests, and rejects four in-memory mutations: a dropped family record, an
altered witness degree, an altered family digest, and an altered per-type
count. Clean-source regeneration took under ten seconds for the two census
programs under Python 3.13.14 and returned zero survivors.

## Publication boundary

The verified result is the conditional necessary bound

```text
n3 >= 36,
induced_C6_count >= 209,322.
```

It neither constructs `srg(99,14,1,2)` nor proves that none exists. Universal
`N3` occurrence retains its upstream `DERIVED`/cited boundary, and Conway-99
remains `UNKNOWN`. No literature novelty claim follows from this project
verification.
