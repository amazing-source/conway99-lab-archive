# Wave 12 independent audit of the `n3=42` all-size-two support case

Verdict: **VERIFIER PASS** for the remaining all-size-two branch, conditional
on the previously audited Wave 6--12 reduction. The official GENREG archive
decodes to 110 connected types and is in bijection with the 110 connected
records of the independent 112-record graph6 catalog. The other two graph6
records are exactly `K3,3 + Q3` and `K3,3 + M8`. An independently written
proof-producing search rejects all four types that survive the mandatory
`K`-degree filter, and a second set-based program checks every forcing and
leaf of the compact rejection certificate.

This closes only the conditional all-size-two `n3=42` branch. Combining it
with the separately audited size-three exclusion is an orchestrator decision.
No `srg(99,14,1,2)` existence or nonexistence claim follows here, and the
Conway-99 target remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T06:52:18Z
git_commit: 4d561fb8b5e0b335d430c2ac93962cbf0ae40184
claim_label: VERIFIED
scope: conditional all-size-two n3=42 active-support relaxation for a putative srg(99,14,1,2)
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  agents/2026-07-22-wave12-n3-42-proof-a.md: 971e0809376d5bb40967ddd297eca627e0b125df908e30817a95cfa67d5b6f4a
  verification/2026-07-22-wave12-n3-42-premise-audit.md: abc6be22f73735e2e46c3c59cbb3b15665b9b639db4b263b59a3c50515ba13a2
  attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6: 24bfd4964cc4e86554f721ff0f988c5e0bb8fc992b6113f142f09737d3ac90fd
  verification/n3-42-equality/14_3_4.scd: 6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0
method: independent shortcode and graph6 decoders; custom exact isomorphism backtracking; independent order-6/order-8 cubic triangle-free census; direct reconstruction of mandatory K and fixed-point supports; proof-tree support-factor search; structurally separate certificate replay; cap weakening and five adversarial certificate mutations
command: |
  Invoke-WebRequest -Uri 'https://www.mathe2.uni-bayreuth.de/markus/REGGRAPHS/SCD/14_3_4.scd' -OutFile 'verification\n3-42-equality\14_3_4.scd'
  .venv\Scripts\python verification\n3-42-equality\build_support_certificate.py --scd verification\n3-42-equality\14_3_4.scd --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 --output verification\n3-42-equality\n3-42-support-certificate.json
  .venv\Scripts\python verification\n3-42-equality\verify_support_certificate.py --certificate verification\n3-42-equality\n3-42-support-certificate.json --scd verification\n3-42-equality\14_3_4.scd --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 --mutations
outputs:
  verification/n3-42-equality/build_support_certificate.py: f9c31766827a8be098d000a7b1cda8b1cc1fb2f8d20e981357f1316b9dc6917a
  verification/n3-42-equality/verify_support_certificate.py: 2c3a1a2375c148bdfc3149b521c13910c5b1d6b2d79a049fedec1a7d495def48
  verification/n3-42-equality/n3-42-support-certificate.json: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
  official_connected_types: 110
  independently_classified_disconnected_types: 2
  mandatory_degree_survivors: [0, 6, 14, 17]
  support_cap_survivors: 0
  conditional_all_size_two_branch: EXCLUDED
  target_result: UNKNOWN
limitations: the reduction to this finite domain is inherited rather than re-proved in full here; GENREG and nauty completeness remain external generator claims rather than proof traces, although their catalogs were independently decoded and cross-matched bijectively; no K completion, 99-vertex graph, automorphism assumption, or unrestricted graph search is used; the GENREG archive page does not state a redistribution license
```

## Reconstruction of the finite domain

In the inherited all-size-two branch there are fourteen active triangle
labels, each contained in three active point sets. The `42` incidences
therefore give `21` point objects of size two. Regard each point object as an
edge of a graph `F` on the active labels. Linearity makes `F` simple, the
three incidences at each label make `F` cubic, and the common-point rule
forbids a triangle of `F`.

For two point objects `{x,a}` and `{x,b}` meeting at `x`, deleting the common
labeled copy leaves a `1`-by-`1` crossing. Its row and column must have degree
zero or two, so the crossing is empty in `L`. Complementarity forces `ab` to
be in `K`. Each `F`-edge is already in `K` because a point set is a `K`
clique. Consequently every valid `K` contains

```text
M = E(F) union {ab : a and b are distinct F-neighbours of one label}.
```

The active `K` is 7-regular. Hence `max_degree(M)>7` is an immediate and
sound rejection.

For an active point object `u` of size two, both labels have `q=2`, so the
fixed-point identity is

```text
sum_{v: uv in E(G)} d_H(uv) = 2(2+2) = 8.
```

An overlapping active point has a singleton crossing and contributes zero.
An inactive point also contributes zero. For two disjoint size-two points,
the `2`-by-`2` crossing law makes `d_H` either zero or four. Thus every point
object has exactly two positive support partners. A positive support requires
all four endpoint cross-pairs to lie in `L`.

The verifier deliberately tests this only against `M`, not against a chosen
7-regular completion `K`. It therefore admits a support whenever the four
cross-pairs avoid `M`. This is a relaxation: completing `K` can only remove
support opportunities.

Let `R` be the selected support graph on the 21 `F`-edges. The fixed-point
identity says that `R` is 2-regular. The graph

```text
A = line_graph(F) union R
```

is a forced subgraph of the putative SRG on the corresponding active original
vertices. Therefore:

- if a pair is adjacent in `A`, it has at most `lambda=1` common neighbour
  already visible in `A`;
- every pair has at most two common neighbours already visible in `A`, since
  an actual adjacent pair has one and an actual nonadjacent pair has two.

The second rule is valid even when a pair not joined in `A` might later be an
unknown zero-support graph edge. Declaring it adjacent would tighten its cap
from two to one. Adding omitted active edges or inactive vertices can only add
common neighbours, never repair a cap violation.

## Independent catalog completeness check

The [official regular-graphs table](https://www.mathe2.uni-bayreuth.de/markus/reggraphs.html)
lists 110 connected cubic graphs on fourteen vertices with girth at least
four and links the exact
[`14_3_4.scd` archive](https://www.mathe2.uni-bayreuth.de/markus/REGGRAPHS/SCD/14_3_4.scd).
The [GENREG manual](https://www.mathe2.uni-bayreuth.de/markus/manual/genreg.html)
specifies that each graph stores the upper endpoint of every edge in vertex
order, and each later record replaces a common initial segment by its prefix
length.

The independent decoder obtained:

```text
archive bytes:              871
archive SHA-256:            6f3e9cf2b7e0d85c5df59c1638ab9d2f
                             ddbfc9905c49b35da01cc892f847e9a0
decoded connected records:  110
```

Every record was rechecked for order 14, cubicity, connectedness, and absence
of triangles. A separate graph6 decoder checked the repository catalog's 112
records. A custom exact isomorphism backtracker, with no nauty or NetworkX
call, found one and only one graph6 match for each shortcode record. The 110
matched indices are distinct and equal the set of connected graph6 indices.

The disconnected part was not inferred from nauty's count. A direct labeled
cubic triangle-free enumeration at orders six and eight gave:

```text
order 6:   10 labeled graphs, 1 isomorphism type
order 8: 3360 labeled graphs, 2 isomorphism types
```

A disconnected cubic triangle-free graph on fourteen vertices must have
component orders `6+8`: every component has even order and a triangle-free
cubic component has at least six vertices. The unique order-six type is
`K3,3`; the two order-eight types are the bipartite cube `Q3` and the
nonbipartite Wagner graph `M8`. Their disjoint unions match exactly:

| graph6 index | graph6 | independent type |
|---:|---|---|
| 0 | `M???FB_w?wBOD_B_?` | `K3,3 + Q3` |
| 17 | `M??CE?wM@oW_P_@o?` | `K3,3 + M8` |

Thus the independent official connected catalog plus the independently
classified disconnected cases is in exact bijection with all 112 records
used by the construction lane.

## Exact support rejection

The histogram of the maximum mandatory `M`-degree over all 112 types is:

```text
max degree 6:  1 type
max degree 7:  3 types
max degree 8: 15 types
max degree 9: 93 types
```

Only four types survive `Delta(M)<=7`. The independent model and compact
proof trees give:

| index | graph6 | `|M|` | relaxed supports | tree nodes | cap leaves | factors surviving |
|---:|---|---:|---:|---:|---:|---:|
| 0 | `M???FB_w?wBOD_B_?` | 39 | 108 | 15 | 8 | 0 |
| 6 | `M???FBOiAgDOD_B_?` | 49 | 35 | 3 | 2 | 0 |
| 14 | `M??CEB_[@oB_B_@o?` | 49 | 35 | 3 | 2 | 0 |
| 17 | `M??CE?wM@oW_P_@o?` | 43 | 108 | 15 | 8 | 0 |

Each proof-tree node contains a sequence of individually checkable
implications and then either a two-way branch or a local contradiction. The
only implications are:

1. exclude every remaining support at a vertex that already has degree two;
2. select every remaining support when all are needed to reach degree two;
3. exclude a support if adding it already violates a common-neighbour cap.

The third rule is monotone: later selected supports only add adjacencies and
common neighbours, and changing a violating nonadjacent pair to adjacent
tightens rather than relaxes the permitted count. Leaves exhibit either an
unreachable support degree or an explicit pair, adjacency status, list of
common neighbours, and cap.

The second checker does not import the builder. It re-derives the graphs and
supports with sets, replays every implication, checks both children of every
branch, and recomputes each leaf witness. It accepted all four trees and
counted zero survivors. Five in-memory mutations were all rejected: an
out-of-range branch, a reversed cap exclusion, a reversed degree forcing, a
corrupted common-neighbour witness, and a false survivor leaf.

A second generation to a scratch path was byte-identical to the archived
certificate:

```text
records are deterministic: true
archived SHA-256: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
scratch SHA-256:  8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
```

## Hostile check of the `mu` cap

The universal two-common-neighbour cap is essential rather than decorative.
With that cap disabled, index 6 has the following support factor, which
satisfies support degree two and every adjacent-pair `lambda<=1` cap:

```text
(0,16,7,10,13,4,20)
(1,17,6,11,12,5,18)
(2,15,8,9,14,3,19)
```

Thus the weakened support graph is `3 C7`. Under the full rule, the
nonadjacent active-point pair `(0,4)` already has the three common neighbours
`{1,3,20}`. This violates the universal upper bound two. If an omitted graph
edge later joined `(0,4)`, the pair would instead be adjacent and its allowed
count would fall to one, so unknown adjacency cannot rescue the witness.

This explicit near-survivor is retained in the certificate. It demonstrates
both that the search is capable of constructing a factor and that the
`mu<=2` use is exactly the SRG cap needed for the exclusion.

## External-source and publication boundary

The GENREG archive was downloaded from Markus Meringer's official University
of Bayreuth page and is bound above by URL, byte length, and SHA-256. The site
asks publications using GENREG to cite Meringer's 1999 paper, but neither the
archive page nor the manual states a redistribution license for the `.scd`
file. Therefore this audit does **not** assert that the third-party binary is
covered by the repository's license.

For a public integration, the conservative option is to publish the URL,
expected SHA-256, decoder, derived certificate, and exact replay command while
requiring the user to download the 871-byte archive from its official host.
If the binary itself is committed, it should be accompanied by an explicit
third-party notice or permission determination. This licensing caveat does
not affect the mathematical replay performed here, but it does affect what
should be redistributed in the public Git repository.
