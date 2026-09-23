# Wave 10 `n3=36` equality-exclusion audit

Verdict: `PUBLISH` for the conditional exclusion of `n3=36` and the resulting
necessary bound `n3>=39`. Target result: `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T03:42:00Z
git_commit: d8ee17669cfd6efdc42b7595d2ae56e9b10161d1
claim_label: VERIFIED
scope: conditional exclusion of n3=36 for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  agents/2026-07-22-wave7-triangle-side-incidence.md: 7b4693420eae7e6f13ce0d66c786424c18863a1b1c350da83097f8e982ebe324
  agents/2026-07-22-wave8-n3-equality.md: 010fe1e2a9752ac18067b44c9e6cf1114e2d1651364c49a574adbe22fe5461f3
  agents/2026-07-22-wave9-n3-33-equality.md: b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555
  agents/2026-07-22-wave10-n3-36-equality.md: 9a1e2ad7cac5e26f9fe4117c8ced2390ca15a4dfda7b1e67faa02b8e90ba507e
  agents/2026-07-22-wave10-status-search.md: 2d22350758916125f9c696a7e5d44c9e2ff4d8841b3f2fbad8a84d8e7f542d0f
  verification/n3-36-equality/verify.py: 3ec131b44a25db344f164f946dd2631fcd16af0a0bc664c1efa6ed2ccb4f498a
  verification/n3-36-equality/audit_support.py: 89a244f78626b90a73bf3b90e25aed9a3b3f229b0680478bb2a88a88f1f7b27b
  verification/n3-36-equality/verify_support.py: e33a1face50be872fb9366c9e4be4271caf360869c8811ffb6e0a92deb3da831
  verification/n3-36-equality/n3-36-support.json: 5f645d5438c9c144c9afb58affec2d783e60f8533d96ffb4f5bfabb3228363e6
  verification/test_n3_36_equality.py: 0c97b857de76c9d62d6847eded70e00dd590d1349516d3db6deee5d3186a5706
  verification/test_n3_36_support.py: f1b185f5a6b84cf7919daf51a0b3b20f943c7214411177ec147e89c353af6117
  verification/2026-07-22-wave10-clean-clone.md: a55d77f74ccd0c9cffb1931084c3139e5b59862ad2f624ec5335a47d665e7094
method: independent proof reconstruction, adversarial repair of a failed shortcut, compact exact checker, two-strategy exhaustive support census, mutation tests, current-status audit, and detached clean-source replay
command: |
  .venv/Scripts/python verification/n3-36-equality/verify.py
  .venv/Scripts/python -m unittest verification.test_n3_36_equality -v
  .venv/Scripts/python verification/n3-36-equality/verify_support.py --certificate verification/n3-36-equality/n3-36-support.json
  .venv/Scripts/python -m unittest verification.test_n3_36_support -v
outputs:
  verdict: PUBLISH
  technical_commit: 2194c2b68ebd5c34491d64f15d30f1a3597baa74
  support_commit: 6da2cb997ad091459b4d934675621671fe2ede42
  conditional_global_n3_lower_bound: 39
  conditional_induced_C6_lower_bound: 209325
  focused_tests: 16_passed
  full_code_tests: 48_passed
  full_verification_tests: 62_passed
  integer_resource_profiles: 14
  labeled_point_families: 100
  abstract_support_masks: 216
  support_mask_sha256: 6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a
  rook_saturation_violations_per_mask: 18
  final_support_survivors: 0
limitations: all conclusions are conditional on the Wave 6-9 graph-theoretic premises and target-specific N3 occurrence; the checkers accompany rather than replace the human reduction; no Conway-99 construction or nonexistence proof is claimed
```

## Adversarial history and repaired objection

The verifier did not accept the first submitted proof. That draft asserted
that one `223` occurrence of a size-three point forced a closed `K5` gadget.
The assertion had a real gap: another occurrence could use the unique external
`K`-neighbor, so the original two endpoints were not automatically repeated.

The repaired proof removes the shortcut. If `C={i,j,k}` has a `223` occurrence
at `i` with endpoints `a,b`, local crossing constraints make
`{i,j,k,a,b}` a `K5`. Any `233` occurrence at `j` would need two new endpoints
anticomplete to `i,k`, but only its unique external neighbor qualifies. Thus
`j` is also `223`. Its two endpoints must lie in `{a,b,x}`. Reusing `a` or `b`
would make three point sets pairwise meet at three distinct active triangles,
forbidden by the common-point rule; only `x` remains for two distinct
endpoints. This closes the gap in a stronger way and leaves the failed draft
visible in the research record.

## Active profiles and local crossing audit

At `n3=36`, `sum q=24`. Exact enumeration under `q>=2` and
`3q(T)<=r-1` gives only

```text
r=10: (2^6,3^4),
r=11: (2^9,3^2),
r=12: (2^12).
```

The corresponding `K`-degrees are respectively `3/0`, `4/1`, and `5`.
Three non-singleton point cliques need three distinct incident `K`-edges, so
each `q=3` triangle in the mixed profiles forces three or two singleton
points. The Wave 9 labeled crossing lemma excludes them.

In the all-`q=2` profile, degree five leaves exactly local types `222`, `223`,
`224`, and `233`. The verifier explicitly formed the labeled bipartite
crossing graphs after removing the possible common active triangle. Their
degrees are zero or two on both sides, giving empty `2`-`2`, `2`-`3`, and
`2`-`4` crossings and either empty or full `K2,2` for `3`-`3`.

The common-point rule is a known regular-clique-assembly lemma, cited in the
status audit, and it also has a one-line target proof from `lambda=1`: three
pairwise intersections at distinct graph-triangles would make a second
triangle on each of three graph edges. Its hypotheses match the active point
sets exactly.

## The `K6` and rook-saturation lemma

A local `K6` in a 5-regular twelve-vertex `K` is a component, so
`K=K6 disjoint-union K6`. Complete `L`-crossing between the components has
local degrees equal to the opposite point-set sizes. A positive crossing is
therefore possible only for two size-two points. Any larger point would have
fixed-point sum zero instead of a positive value, so all points are size two.

Consumed point edges inside either `K6` form a cubic graph `F` on six
vertices. A triangle of `F` violates the common-point rule. Since `F` has nine
edges, Mantel equality gives `F=K3,3`; the compact checker independently
enumerates all seventy labeled cubic graphs and finds exactly ten
triangle-free labeled copies, all `K3,3`.

The nine corresponding original vertices induce exactly `L(K3,3)`:

- incident `F`-edges have the third edge at their common endpoint as their
  unique internal common neighbor;
- disjoint `F`-edges have the two cross-corner edges as two internal common
  neighbors, so `lambda=1` also proves that the pair is nonadjacent.

Thus every pair has saturated `lambda=1` or `mu=2`, and an outside vertex may
meet the rook graph at most once. The fixed-point sum instead forces each
size-two point to have two positive neighbors in the opposite rook. This is a
direct contradiction and eliminates every `K6` component.

The verifier specifically challenged whether extra edges could exist among
disjoint `F`-edge points. Their two forced common neighbors would violate
`lambda=1` if such an edge existed, so the induced-rook claim is sound.

## Sizes four and three

Type `224` forces a `K6` by the empty-crossing alternatives. A type `233`
occurrence either forces the same `K6` or is split, with its two external
size-three pairs anticomplete in `K`.

After the repaired `223` contradiction above, every occurrence of a
size-three point would be split `233`. The verifier reconstructed the simple
cubic graph `R` whose vertices are size-three points and whose edges are their
active-triangle occurrences. At an edge `i`, its unique size-two mate `m` is
`K`-adjacent to all four members of `N_(L(R))(i)`.

Vertex `m` cannot be type `222`: its other two endpoints must be the same-side
pair among those four, and one of the associated size-three point sets then
forms a forbidden three-intersection configuration with `{i,m}` and one of
the new size-two points. Hence mates pair the type-`233` edges of `R`.

For a matched disjoint pair `i=uv,m=xy`, equality of their open line-graph
neighborhoods forces all four cross-edges between `{u,v}` and `{x,y}`. But
then an edge at `u` and an edge at `v` meet at `x`, contradicting the split
condition at `uv`. The compact checker enumerates the sixteen endpoint
subsets and finds one open-twin configuration, the full `K4`, with zero
split-compatible survivors.

## All-size-two reduction

With only size-two points, their consumed edges form a spanning cubic graph
`F`, and `U=K-E(F)` is a 2-factor. At every vertex `i`, the three `F`-neighbors
are pairwise joined in `K` by the local `222` rule. Their pair edges cannot be
consumed without violating the common-point rule, so they form a triangle
component of `U`. Every vertex lies in such a neighborhood, giving `U=4C3`.

If one triangle maps by `F` to another, symmetry and cubicity force the full
`K3,3`; the four triangles pair off. Therefore `F=2K3,3` and `K=2K6`, already
excluded. The compact checker enumerates all three fixed-point-free pairings
of the four triangle groups and obtains component orders `(6,6)` every time.

The verifier found no hidden connectedness assumption: disconnected `K` is
explicitly allowed and is precisely the terminal configuration rejected by
the rook lemma. No automorphism of the completed 99-vertex graph is imposed.

## Independent finite support census

As a materially different check, the computational lane retained the terminal
all-size-two `2K6` domain instead of immediately applying the human rook
argument. There are fourteen global resource profiles before local pruning,
and the terminal domain has `10^2=100` labeled `K3,3` point families in one
orbit.

For one labeled family, a positive support is a 2-regular bipartite graph on
the two nine-point rook sets. The primary program decomposes it into two
permutation matchings and pairs exact coverage signatures. It examined
230,112 eligible first permutations and accepted 3,456 ordered complementary
decompositions, deduplicating to 216 masks.

The independent program does not import the primary implementation. It fixes
the first matching and recursively constructs the second from residual cell
coverage. It recovers the same 216 masks and digest

```text
6659fe1972cbacc6980a9792557714730572817b43224b5f1fac24bb0c4ca61a.
```

Every mask satisfies exact-two `L`-cell coverage, matching, fixed-point sums,
degree capacity, `H` simplicity, 4-regularity, connectedness, and
triangle-freeness. Each one makes every row and column source point an extra
common neighbor of a pair in the opposite induced rook, giving eighteen
saturation violations and zero final survivors. Five in-memory mutations are
rejected, including a dropped mask, altered digest, false restored survivor,
altered rook `mu` count, and target-status inflation.

## Tests, clean replay, and status boundary

The pinned environment passes all 48 code tests and 62 verification tests.
A fresh `--no-local` clone detached at
`d8ee17669cfd6efdc42b7595d2ae56e9b10161d1` regenerated the support domain,
replayed both the scratch and committed certificates independently, and
remained clean. An ambient Python run missing `python-sat` produced two import
errors before the pinned replay; that environment mismatch is retained in the
clean report rather than hidden.

The verified conditional consequences are

```text
n3 >= 39,
induced_C6_count >= 209325,
branch bounds = 39,39,42,48,48,39,42,48,39,48,42,48.
```

The precise literature search found no checked occurrence of this equality
exclusion, but negative search cannot establish novelty. The fixed-triangle
profile, `n3` congruence, hexagon formula, common-point lemma, and rook-graph
identification are explicitly attributed prior art. The result remains a
conditional internally checked project derivation pending qualified external
review. It neither constructs `srg(99,14,1,2)` nor proves nonexistence; the
target remains `UNKNOWN`.
