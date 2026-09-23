# Independent audit of the opposite-edge graph and `N3` bound

Verdict: `PASS` for the conditional global bound `n3 >= 24`, the local branch
table, the exact six-vertex boundary profile, and the mate-edge propagation
lemma. Conway-99 remains `UNKNOWN`.

```yaml
role: verifier
date_utc: 2026-07-23T00:08:58Z
git_commit: a066170e452f31efe1e00610b8159a66b825b01f
claim_label: VERIFIED
scope: J/H auxiliary-edge proof, global and branch-local N3 counts, normalized N3 boundary profile, and mate-edge propagation
inputs:
  agents/2026-07-22-wave6-opposite-edge-graph.md: 4197c40e1b43d72d5a2ad9a6203099ffed2e1dbf4f0b3c07186aaad54cae4fa2
  verification/n3-joint-cover/n3-joint-cover.json: 58c4994ff0eef9c5e1702840f791d1400c3da71b445e3c217e3704c5e70de172
  verification/n3-count-bound/verify.py: ecf06150285ce450e8ce6bc5c3a3004078acdb2abb6188b1f58f4bf9dd10d946
  verification/test_n3_count_bound.py: be1b231643a9a48ce421227e730d6ecfa2733279eb2545cb3c00fffe336a1b8d
method: independent SRG derivation, adversarial orientation and multiplicity audit, exact certificate replay, exhaustive perfect-matching enumeration, extremal degree-sequence filtering, and local graph search
command: |
  .venv/Scripts/python verification/n3-joint-cover/verify.py verification/n3-joint-cover/n3-joint-cover.json
  .venv/Scripts/python verification/n3-count-bound/verify.py
outputs:
  global_n3_lower_bound: 24
  global_induced_C6_lower_bound: 209310
  branch_n3_lower_bounds: [24, 33, 42, 48, 48, 24, 42, 48, 33, 48, 42, 48]
  exact_checker: PASS
limitations: H is nonempty only by the target-specific cited-and-derived N3 occurrence; cycle signatures are coarse; no graph or nonexistence proof was produced
```

## Core verdict

The verifier independently reconstructed the graph `J` on the 693 graph
edges, with adjacency for opposite edges of a four-cycle. It confirmed that
`J` is simple and 12-regular, hence has 4,158 edges.

The switching audit of three pairwise-opposite graph edges leaves a triangular
prism or `K3,3`; `mu=2` excludes the latter. For one `J` edge, its two side
triangles determine a unique possible third prism edge. The audit corrected a
wording issue in the discovery draft:

- the two original four-cycle diagonals are absent by `lambda=1`;
- the four remaining unwanted cross-edges are absent because each would give
  a third common neighbor to one of those nonedges, violating `mu=2`.

With that correction, a nontriangular `J` edge corresponds bijectively to one
unlabeled induced `N3`; no orientation or factor-of-two ambiguity remains.
Thus `H`, the subgraph of nontriangular `J` edges, is triangle-free,

```text
|E(H)| = n3,
4,158 = 3 * triangular_prisms + n3.
```

The two local perfect matchings at any graph edge give

```text
d_H(e) = 12 - 2t,
d_H(e) in {0,4,6,8,10,12}.
```

## Source boundary and extremal check

Nonemptiness of `H` is not a parameter-only consequence. The 3-by-3 rook
graph `srg(9,4,1,2)` is a countercontrol: its analogous `J` is a union of six
triangles and its `H` is empty. The proof therefore explicitly depends on the
established target-specific result that every putative Conway graph contains
an `N3`.

For a nonisolated `H` vertex of degree `d`, its independent neighborhood and
minimum nonzero degree four give `|E(H)| >= 4d`. Divisibility by three leaves
18 and 21 below 24. The independent extremal derivation reproduced the
contradictions for a 4-regular triangle-free graph on nine vertices and the
degree sequence `(6,4^9)` on ten vertices.

The standard-library checker exhausts every degree sequence below 24 that
survives handshake, Mantel, allowed-degree, divisibility, and local-neighborhood
bounds. Only the 18-edge `4^9` case remains; enumeration of all
`4^4 * binom(6,2)` forced local models leaves zero survivors. Therefore

```text
n3 >= 24,
induced_C6_count >= 209,310.
```

These abstract `H` constraints alone cannot raise 24: `K4,6` is a
triangle-free 24-edge graph with allowed nonzero degrees. Any stronger target
bound must use more of the origin of `H` inside `J`.

## Branch and boundary checks

The verified 12-branch certificate was replayed. Independent reconstruction
gave mate-edge counts

```text
4,2,1,0,0,3,1,0,2,0,1,0
```

and local `N3` lower bounds

```text
24,33,42,48,48,24,42,48,33,48,42,48.
```

All 10,395 perfect matchings were also enumerated. The distribution by
nonmate matching edges is

```text
{0:1, 2:30, 3:160, 4:900, 5:3264, 6:6040}.
```

The recorded alternating-cycle signatures are correct but coarse: branches
3/7 and 5/10 share signatures, so the signatures do not classify the orbits.

An independent common-neighbor deficit table for the normalized six-set
reproduced exactly eight two-neighbor boundary vertices, singleton counts
`(9,9,8,9,9,8)`, and 33 vertices with no neighbor in the six-set. Percolation
wave 1 and wave 2 are exact as recorded. Publication deliberately makes no
exact wave-3 cardinality claim: other outside vertices may qualify through
the two pair-profile vertices already infected in wave 2.

Finally, the verifier reproduced the 22 specified nonedges for each mate edge
and checked that the blocks for distinct mate edges are disjoint. This lemma
is published as an explicit consequence of existing incidence equations, not
as an additional independent cut or as a complete propagation closure.
