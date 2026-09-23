# Wave 12 final integration audit

Verdict: **PASS**.  Conditional on the already verified Wave 6--11
active-triangle framework, the proof-side reduction and the independently
certified all-size-two support census together exclude `n3=42`.  Combining
this exclusion with the prior conditional bound `n3>=42` and `3 | n3` gives

```text
n3 >= 45,
induced_C6_count = 209286+n3 >= 209331.
```

This is a conditional project claim, not a proof that
`srg(99,14,1,2)` exists or does not exist.  Conway-99 remains `UNKNOWN`, and
the novelty of the strengthened bound remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T06:57:47Z
git_commit: 4d561fb8b5e0b335d430c2ac93962cbf0ae40184
claim_label: VERIFIED
scope: conditional exclusion of n3=42 and consequent n3/induced-C6 bounds for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave12-n3-42-proof-a.md: 971e0809376d5bb40967ddd297eca627e0b125df908e30817a95cfa67d5b6f4a
  verification/2026-07-22-wave12-n3-42-premise-audit.md: abc6be22f73735e2e46c3c59cbb3b15665b9b639db4b263b59a3c50515ba13a2
  verification/n3-42-equality/verify_reduction.py: 8aeec3c8f6f53eb14a8a5da49651c0c2b58cf2e118ecd51157c87af13ee6bf72
  verification/test_n3_42_reduction.py: a99a979ccf083670f4feaddddbc415c78e2506d3522bac180ef079fe94cb9b3a
  agents/2026-07-22-wave12-n3-42-computational.md: 38cf3fb303c464ad2d6021e3cd969437aa9b354da5ad2028ad644f0bd8c1534b
  code/wave12_n3_42_size2_caps.py: 3de29e1e32b555aec9bd4a5dbbba8ea24d2ca3deebc32c4d77c66c3db5b33011
  attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6: 24bfd4964cc4e86554f721ff0f988c5e0bb8fc992b6113f142f09737d3ac90fd
  verification/2026-07-22-n3-42-support-audit.md: 82dd4605fff60802768f837f95c8db5d24b5aac2fc93256c4bfcac2220ee1e5e
  verification/n3-42-equality/build_support_certificate.py: f9c31766827a8be098d000a7b1cda8b1cc1fb2f8d20e981357f1316b9dc6917a
  verification/n3-42-equality/verify_support_certificate.py: 2c3a1a2375c148bdfc3149b521c13910c5b1d6b2d79a049fedec1a7d495def48
  verification/n3-42-equality/n3-42-support-certificate.json: 8115b5f34568a463952afc399bc22db927121f3f1aa28cfc33ae191ea93dc68a
  verification/n3-42-equality/14_3_4.scd: 6f3e9cf2b7e0d85c5df59c1638ab9d2fddbfc9905c49b35da01cc892f847e9a0
  agents/2026-07-22-wave12-status-search.md: b3118d19d2c5b74af6cb8a48667f1b674e6a1b3df12a1a94ca46f64e1fcef7e6
method: independent reconstruction of every proof bridge; hostile review of the mandatory-K and common-neighbour relaxations; direct replay of the construction and proof-side programs; byte-identical support-certificate regeneration; independent set-based certificate replay; official/archive cross-isomorphism audit; disconnected-case census; and mutation testing
command: |
  .venv\Scripts\python code\wave12_n3_42_active.py --certificate attempts\wave12-computation\n3-42-size2-active-local-candidate.json
  .venv\Scripts\python code\wave12_n3_42_size2_scout.py --compare attempts\wave12-computation\n3-42-size2-active-local-candidate.json
  .venv\Scripts\python code\wave12_n3_42_size2_caps.py --catalog attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6
  .venv\Scripts\python verification\n3-42-equality\verify_reduction.py
  .venv\Scripts\python -m unittest verification.test_n3_42_reduction -v
  .venv\Scripts\python verification\n3-42-equality\build_support_certificate.py --scd verification\n3-42-equality\14_3_4.scd --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 --output <scratch-certificate.json>
  .venv\Scripts\python verification\n3-42-equality\verify_support_certificate.py --certificate verification\n3-42-equality\n3-42-support-certificate.json --scd verification\n3-42-equality\14_3_4.scd --graph6 attempts\wave12-computation\n3-42-cubic-trianglefree-14.g6 --mutations
outputs:
  proof_side_n3_42_frontier: "21 size-two point sets forming a simple cubic triangle-free F on 14 labels"
  official_connected_types: 110
  independently_classified_disconnected_types: 2
  mandatory_degree_survivors: [0, 6, 14, 17]
  relaxed_support_cap_survivors: 0
  conditional_n3_42: EXCLUDED
  conditional_n3_lower_bound: 45
  conditional_induced_C6_lower_bound: 209331
  target_result: UNKNOWN
  novelty_status: UNKNOWN
limitations: conditional on the inherited Wave 6--11 graph-theoretic premises and target-specific forced-N3 consequence; GENREG and nauty completeness are external generator claims, though their independent catalogs were decoded and cross-matched bijectively; no 99-vertex completion or automorphism is assumed; absence of a checked prior-art hit does not establish novelty; the official shortcode binary has no stated redistribution license and should not be committed without a permission or third-party-license determination
```

## Logical bridge from `n3=42`

The proof-side argument was reconstructed without using the support census.
At `n3=42`,

```text
sum q(T)=28,  q(T)>=2,  3q(T)<=r-1.
```

Exact partitioning gives six raw profiles.  Three non-singleton point cliques
through each active label require `K`-degree at least three, leaving only

```text
r=14: q=(2^14),       d_K=(7^14);
r=13: q=(2^11,3^2),  d_K=(6^11,3^2).
```

The degree-three profile is impossible.  At a degree-three label `x`, its
three point sets must be `{x,a}`, `{x,b}`, and `{x,c}`.  Singleton-side
crossings then force `{a,b}`, `{a,c}`, and `{b,c}` as point sets.  Those three
sets meet pairwise at three different labels, contradicting the inherited
common-point rule.  Thus only `r=14`, `q=(2^14)`, with `K` 7-regular remains.

Expansion gives point size at most four.  A size-four point has eight
pairwise-disjoint petals in ten external labels, so at least six petals have
singleton external side.  Each of their six distinct endpoints is
`K`-adjacent to all four root labels.  Every root label would have at least
`3+6=9` neighbours in the 7-regular `K`, excluding size four.

Let `t_i` count size-three points through label `i`, let `F` be the union of
point-clique edges, and put `U=K-E(F)`.  Then

```text
d_F(i)=3+t_i,  d_U(i)=4-t_i.
```

For a size-three point `{i,j,k}`, singleton petals and external-label
capacity give

```text
4-t_i >= (3-t_j)+(3-t_k)  cyclically,
t_i+t_j+t_k <= 8.
```

The only possibilities are `(2,2,2)` and permutations of `(2,3,3)`.
In the latter case the two `t=3` labels are saturated in `U`.  The five
size-three co-points through the three root labels must consequently have
full `2`-by-`2` `L`-crossings with the root point.  They are five distinct
actual graph neighbours, each contributing four to a fixed-point sum equal
to twelve, an immediate contradiction.

If a size-three point remained, its size-three intersection graph would be a
nonempty simple cubic triangle-free graph `R`.  If `e=|E(R)|`, the forced
size-two third point at each edge label consumes an incidence at a `t=0`
label, giving `e<=3(14-e)` and hence `e<=10`.  Therefore `R` has order four
or six; triangle-freeness leaves only `K3,3`.  Its nine edge labels would
have to map into five `t=0` labels.  Equality of two images would give equal
open neighbourhoods in `L(K3,3)`, but the `3`-by-`3` rook graph has no open
twins.  The required map is injective, a contradiction.  Every active point
set therefore has size two.

The resulting 42 incidences are 21 edges of a simple cubic triangle-free
graph `F` on fourteen labels.  This is the exact point at which the
proof-side checker stops; it does not silently assume the support exclusion.
Its integrated `n3>=45` output is guarded by an explicit external-support
premise, and deleting that premise is rejected by the focused tests.

## Soundness of the finite relaxation

Every `F`-edge lies in `K`.  If `{x,a}` and `{x,b}` are two incident
`F`-edges, their remaining `1`-by-`1` crossing is empty in `L`, so `ab` lies
in `K`.  Hence every valid completion contains

```text
M = E(F) union {ab : a,b are distinct F-neighbours of one label}.
```

Rejecting `Delta(M)>7` is therefore necessary, not heuristic.

For each size-two point object, the fixed-point identity has value eight.
An overlapping point contributes zero; a disjoint size-two point contributes
zero or four.  Thus the positive-support graph on the 21 point objects is
exactly 2-regular.  A positive support needs a full `2`-by-`2` `L` rectangle.
The search admits every disjoint pair whose rectangle avoids only `M`.
Because `M` is merely a subset of the final `K`, this enlarges the support
domain: adding the missing `K`-edges can only delete opportunities.  A zero
survivor result in this enlarged domain is therefore a sound exclusion.

For a selected support factor `R`, the graph

```text
A = line_graph(F) union R
```

is a forced subgraph of the putative SRG on the active original vertices.
An edge of `A` may have at most one common neighbour already in `A`; every
pair may have at most two.  The latter cap is safe even for a pair whose
actual adjacency is not yet known: making it adjacent would tighten the SRG
cap from `mu=2` to `lambda=1`.  Omitted active edges and inactive vertices
can only add common neighbours.  Common-neighbour violations are consequently
monotone and cannot be repaired by a later completion.

These observations rule out the two main possible false-UNSAT mechanisms:
the mandatory-`K` approximation makes the search larger, not smaller, and
the universal two-common-neighbour cap does not assume that an unknown pair
is a nonedge.

## Catalog and certificate audit

The [official University of Bayreuth table](https://www.mathe2.uni-bayreuth.de/markus/reggraphs.html)
states that there are 110 connected cubic graphs on fourteen vertices with
girth at least four.  Its linked shortcode archive was fetched independently
in memory and had exactly 871 bytes and SHA-256
`6f3e9cf2...f847e9a0`, matching the audited file.  The
[GENREG manual](https://www.mathe2.uni-bayreuth.de/markus/manual/genreg.html)
agrees with both independent shortcode decoders.

The 110 decoded connected graphs match bijectively, by an exact custom
isomorphism backtracker, the 110 connected records in the 112-record graph6
catalog.  A disconnected cubic triangle-free graph of order fourteen must
split as `6+8`.  Direct small-order enumeration gives one order-six type
(`K3,3`) and two order-eight types (`Q3` and `M8`), producing exactly the two
remaining catalog records.  Thus no connected or disconnected `F` type is
lost in the cross-catalog bridge.

The maximum mandatory-degree histogram over the 112 types is

```text
6: 1 type,  7: 3 types,  8: 15 types,  9: 93 types.
```

Only indices `0,6,14,17` survive.  Their relaxed support domains and
independent proof-tree results are:

| index | supports | proof-tree nodes | cap leaves | surviving factors |
|---:|---:|---:|---:|---:|
| 0 | 108 | 15 | 8 | 0 |
| 6 | 35 | 3 | 2 | 0 |
| 14 | 35 | 3 | 2 | 0 |
| 17 | 108 | 15 | 8 | 0 |

The certificate replayer does not import the builder.  It reconstructs all
graphs and support opportunities with set-valued data, checks every forced
move, visits both children of every branch, and recomputes every terminal
witness.  The certificate regenerated byte-for-byte at SHA-256
`8115b5f3...93dc68a`.  Five hostile mutations were rejected: an out-of-range
branch, reversed cap forcing, reversed degree forcing, a corrupted cap
witness, and a false survivor.

The weaker lambda-only model has a retained near-survivor `R=3C7` at index
6.  The universal cap rejects it because point objects `(0,4)` already have
three active common neighbours.  This confirms that the search can construct
a support factor and that the final rejection genuinely uses the valid
`mu<=2` consequence rather than an accidental degree failure.

## Final status and publication boundary

No earlier gap was found in the bridge from a putative `n3=42` graph to the
four finite support cases, and no gap was found in their exhaustive rejection.
It is safe to record the scoped conditional exclusion and the consequent
bounds as `VERIFIED`.

The prior-art audit found no checked source for the exact exclusion or bound,
but a negative search does not establish novelty.  The correct external
status is still `novelty: UNKNOWN`, and the target remains `UNKNOWN`.

The official `14_3_4.scd` page and manual do not state a redistribution
license.  This does not affect the mathematical replay, but the binary should
not be committed to the public repository without permission or an explicit
third-party-license determination.  A public replay can instead publish the
official URL, expected byte length and SHA-256, decoder, derived certificate,
and download command.
