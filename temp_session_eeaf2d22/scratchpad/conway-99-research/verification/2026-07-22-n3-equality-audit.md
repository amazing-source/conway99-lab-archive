# Wave 8 `n3=30` equality-exclusion audit

Verdict: `PUBLISH` for the conditional exclusion of `n3=30` and the resulting
necessary bound `n3>=33`. Target result: `UNKNOWN`.

The Wave 7 input hash below is the frozen pre-attribution version present at
technical commit `b2a31846...`. A later prose-only correction credits
Lou--Murin 2014 for the upstream partner profile and `q`-gap; see the Wave 8
status report.

```yaml
role: verifier
date_utc: 2026-07-23T01:36:12Z
git_commit: b2a31846d243a76b9e516f85304e21137e3fe874
claim_label: VERIFIED
scope: conditional exclusion of n3=30 for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 2225d7f26f8719d24bceca0c4ef6d8b829332a80793762769d282f176e75b651
  wave8_draft_at_verification:
    path: agents/2026-07-22-wave8-n3-equality.md
    sha256: b612eb0a47514b20c11539cd5cc54cecaa2a5489e1eb47bd0be79db308e8ca70
    note: the final report adds only the later Lou-Murin attribution correction
  final_wave8_report:
    path: agents/2026-07-22-wave8-n3-equality.md
    sha256: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave8-status-search.md: 31511fd902d2887823174374c8a058c22452bb81950f49a25834e69efcc460ed
  verification/n3-equality/verify.py: 17b306d0e7d198d5c30e068a9c4e7b490ff01dfc91758416b9e67ed641007bf6
  verification/test_n3_equality.py: 8f6a7c6772733386ccb71810c24c996b2ef1739588846a622d670bffa44ad313
  verification/n3-equality/audit_exhaustive.py: ec463642e2efa5a0b4f25673de1f78e2ef5b5af8bc698791e22c8743d43c1750
  verification/n3-equality/n3-30-audit.json: 0a33add151177432243a8d318fe107371430d9c39200d4bf5e0c11dd9c6f4cd7
  verification/2026-07-22-wave8-clean-clone.md: 38ba54a0af5a251e0e5e1c3b5d0b6a9212dac2e06cebc02a1cee1ebc0c532719
method: independent proof reconstruction, adversarial multiplicity and overlap audit, exact arithmetic checker, solver-free exhaustive secondary audit, and frozen-commit clean-source replay
command: |
  python verification/n3-equality/verify.py
  python -m unittest verification.test_n3_equality -v
  python verification/n3-equality/audit_exhaustive.py --check verification/n3-equality/n3-30-audit.json
outputs:
  verdict: PUBLISH
  primary_checker_commit: b2a31846d243a76b9e516f85304e21137e3fe874
  exhaustive_audit_commit: 164857e29d2720e3e285b0e20c6895ce7404764e
  conditional_global_n3_lower_bound: 33
  conditional_induced_C6_lower_bound: 209319
  focused_tests: 8_passed
  full_code_tests: 48_passed
  full_verification_tests: 35_passed
  normalized_labeled_cubic_graphs: 133105
  cubic_isomorphism_types: 21
  point_clique_families: 674880
  exact_two_cover_solutions: 0
limitations: all conclusions are conditional on the Wave 6/7 graph-theoretic premises and target-specific N3 occurrence; the primary checker is an arithmetic regression companion; no Conway-99 construction or nonexistence proof is claimed
```

## Independent proof reconstruction

The verifier reconstructed the proof without using the discovery agent's
Petersen-graph detour. The following potential failure modes were checked
explicitly.

### Active-triangle multiplicity

At `n3=30`, the handshake sum is `sum q=20`. The gap `q=0` or `q>=2` and the
degree inequality `3q(T)<=r-1` force exactly ten active triangles, all with
`q=2`. Hence the active `L` is 6-regular and its complement `K` is a simple
cubic graph on ten vertices.

For each fixed unordered pair of vertices in a graph-triangle, the Wave 7
ordered-pair construction is a bijection onto twelve disjoint partners using
cross-edges at both vertices. The ten prism partners use all three pairs,
leaving two `N3`s for each side-vertex pair. Each vertex lies in two pairs,
so it occurs as a cross-edge endpoint four times for that fixed side.

Summing over `S_u` gives

```text
sum_{v: uv in E(G)} d_H(uv) = 4 |S_u|.
```

No factor of two is missing: an `N3` has exactly one cross-edge incident with
`u`, and exactly one of its two disjoint side triangles contains `u`. The
identity also handles `S_u` empty, when both sides vanish.

### Point resources and actual edges

The sets `S_u` are cliques in `K`. Their consumed `K`-edge sets are disjoint,
because two graph-triangles cannot share two original vertices. Thus the ten
active triangles give thirty point incidences and at most fifteen consumed
edges.

The singleton argument ranges over all graph neighbors, including vertices
whose active set is empty. With no size-four point, every crossing from a
singleton is at most three and therefore must have `H`-degree zero. This
contradicts its fixed-point sum four. The remaining integer equations have
the unique solution `x2=15,x3=0`, so every edge of `K` is consumed.

The final pair is an actual graph edge, not merely a candidate support pair:
the two original points both lie in the active graph-triangle indexed by `i`.
For `S_u={i,j}` and `S_v={i,k}` with `jk` outside `K`, the only crossing
`L`-edge is `jk`. The overlap at `i` is not counted twice, giving
`d_H(uv)=1`, outside the Wave 6 allowed set.

### Disconnected and size-four cases

The proof never assumes that `K` is connected. If every cubic neighborhood
were a clique, every component would be `K4`, impossible on ten vertices.

A size-four point itself forms a saturated `K4` component and forces eight
distinct singleton points in its four graph-triangles. Edge-disjointness
forbids a second size-four point on the same component, while a second `K4`
component would leave two vertices and cannot occur in a cubic graph. Each
forced singleton has crossing zero with the size-four point and at most three
with every other point, again contradicting its fixed-point sum.

The verifier therefore returned `PUBLISH` on the human proof.

## Checker scope and mutation tests

The compact standard-library checker exactly recomputes:

- the unique ten-entry active-`q` sequence;
- ten prism partners, two `N3`s per side-vertex pair, and four per side vertex;
- the point-size integer solution `(x1,x2,x3)=(0,15,0)`;
- the cubic component-order alternatives `(4,6)` and `(10)`;
- the fact that no positive allowed `H`-degree can occur on an internal
  active-triangle edge;
- the overlapping-set crossing value one; and
- the global and twelve branch-local strengthened bounds.

Eight focused tests cover successful replay and malformed inputs. All 48 code
tests and all 35 verification tests pass. The checker does not encode the
entire graph-theoretic proof: the endpoint bijection, disjoint edge
consumption, singleton implication, and size-four saturation are human
lemmas. Its printed conclusion is valid only with the recorded derivation.

## Independent exhaustive secondary audit

The optional slow checker uses only the Python standard library and is
materially different from the short proof. It generated all labeled simple
cubic graphs with harmless normalization `N_K(0)={1,2,3}`, quotiented them by
an exact adjacency-preserving isomorphism search, and recovered

```text
133,105 normalized labeled graphs,
21 isomorphism types = 19 connected + 2 disconnected.
```

The automorphism checksum for every class is `43,200/|Aut(K)|`. Across the 21
types it enumerated all 674,880 point-clique families, permitted unused
`K`-edges, enforced disjoint intersection resources and the common-point
rule, and added distinct singleton fillers. The staged totals were

```text
internal and fixed-side valid families:       20,624
families with at least 11 support candidates:    267
exact-two covers of all 30 L-edges:                 0
surviving patterns/types:                          0 / 0.
```

The 267 last candidates occur in five cubic types with counts
`237,18,4,4,4`. None satisfies even the weakest remaining global requirement
that every `L`-edge receive exactly two selected cross graph-edges. Later
matching, `H`-simplicity, triangle-freeness, and graph-degree-capacity layers
therefore have no survivors.

Exact certificate replay took 280.6 seconds under Python 3.13.14 and returned

```text
certificate_replay PASS
script_sha256 ec463642e2efa5a0b4f25673de1f78e2ef5b5af8bc698791e22c8743d43c1750
certificate_sha256 0a33add151177432243a8d318fe107371430d9c39200d4bf5e0c11dd9c6f4cd7
PASS n3=30 abstract incidence exclusion
```

The script is archived verbatim from the independent scratch lane, so its
opening provenance comment still describes that origin. This slow audit is
secondary confirmation, not a prerequisite for the classification-free
human proof.

## Publication boundary

The verified result is the conditional necessary bound

```text
n3 >= 33,
induced_C6_count >= 209,319.
```

It neither constructs `srg(99,14,1,2)` nor proves that none exists. Universal
`N3` occurrence retains its upstream `DERIVED`/cited boundary, and Conway-99
remains `UNKNOWN`.
