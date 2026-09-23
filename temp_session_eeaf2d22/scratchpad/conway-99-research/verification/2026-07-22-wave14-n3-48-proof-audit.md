# Wave 14 `n3=48` proof-A adversarial audit

Verdict: **PASS for the scoped `DERIVED` reduction.**  The proof correctly
reduces a putative `n3=48` Conway graph to the stated finite residual.  It
does **not** exclude `n3=48`; that exclusion remains `UNKNOWN`.

The explicit all-size-two object independently passes as a countermodel to
the stated active-layer relaxation.  It is not a Conway graph, a partial
99-vertex completion, or evidence for target existence.

```yaml
role: verifier
date_utc: 2026-07-23T09:29:41Z
git_commit: 4e354b80101b24cd9ef0861e9f65f948b912621f
claim_label: DERIVED
audit_verdict: PASS
scope: adversarial verification of the Wave 14 proof-A conditional reduction at n3=48 and of its explicit all-size-two active-relaxation countermodel
inputs:
  agents/2026-07-22-wave14-n3-48-proof-a.md: f0a7d7b5638415cff7d5ad4ef176542de9aa89a2b46a03347f90a2133f18999c
  attempts/wave14-proof-a/profile_modes.py: 929b95b14e648ba7cf6dad0bd00192f6ffc74c9a77e36c797147f6f2ed4f7b9f
  attempts/wave14-proof-a/all2_census.py: f817fb68dc1b34d980f4ae1793a4cd56c70681adf7a6fe28fc1e1a6161f9c40b
  attempts/wave14-proof-a/cubic-trianglefree-16.g6: 2df2ebc03d5135f7959f6aa66aba84d44efa5d1dc977d8184c2e1dffcce9569d
  attempts/wave14-proof-a/all2-census.json: 21f80192a82fc8e32e587ae32ea5540c78759cb224726789ff808f14baf76cf2
  attempts/wave14-proof-a/all2-index12.json: 728d2483a33d35e417980b977e553f6a0018e4eda2b64294d83e26fc30c88ccd
  attempts/wave14-proof-a/build_all2_countermodel.py: 182d6317de0957f266716169225d56ee07d7c6284ca6c79fbef07913ec8c386d
  attempts/wave14-proof-a/all2-active-countermodel.json: 5d06ae777fb0ca4450951708bba3ffc85d1f617be1d19c2be210f43df82b8952
  attempts/wave14-proof-a/verify_all2_countermodel.py: 6f386ff8ca66f17c15b144600261d660baac603fcec43b541966ed6eb19648ee
  attempts/wave14-proof-a/test_wave14_proof_a.py: 8aa6c9a8b2b77221ac4e27a6f38bc175e6feca7c46803b61d4011a75b53c09a5
  verification/n3-48-proof/preinspection-freeze.md: aa21f20b0e2f176c2d7f8c35126e627a4deb22dfb690ee164f2c3f44fffa1f99
  verification/n3-48-proof/independent_reconstruction.py: 554233011c8ef7e511928e6c3a20e85870073a9720e97078bcf61d7e0d01ee05
  verification/n3-48-proof/audit_countermodel.py: 62e6b5ed33a6244b8248642f67bfee230f695a5dd4bd99b7e60012349fdf9675
method: independent preinspection reconstruction, line-by-line proof audit, exact arithmetic replay, direct semantic reconstruction of the countermodel, literal N3 matching checks, and hostile mutations
command: |
  python -B verification/n3-48-proof/independent_reconstruction.py
  python -B attempts/wave14-proof-a/profile_modes.py
  python -B attempts/wave14-proof-a/verify_all2_countermodel.py attempts/wave14-proof-a/all2-active-countermodel.json
  python -B -m unittest -v attempts/wave14-proof-a/test_wave14_proof_a.py
  python -B verification/n3-48-proof/audit_countermodel.py attempts/wave14-proof-a/all2-active-countermodel.json
outputs:
  raw_sum_q_profiles: 12
  profiles_after_inherited_filters: 3
  mixed_r14_exclusion: PASS_DERIVED
  mixed_r15_exclusion: PASS_DERIVED
  surviving_profile: "r=16, q=(2^16), K simple 9-regular"
  surviving_point_sizes: [2, 3]
  surviving_aligned_size3_modes: 8
  residual_H_degrees: [0, 4]
  all_size_two_countermodel: PASS_CANDIDATE_RELAXATION_ONLY
  conditional_n3_48_exclusion: UNKNOWN
  conway_99: UNKNOWN
limitations: conditional on the inherited Wave 6-12 semantic framework; no Wave 13 or Wave 14 computation path was inspected; the eight modes are necessary local modes rather than a global realization; the countermodel omits 75 original vertices and all inactive-triangle and completion data
```

The `git_commit` above was read from `.git/HEAD` and its ref file without
running Git.  The shared-workspace ref moved during this audit; it is only
the full hash observed when this report was frozen.

## 1. Independence protocol

Before opening the submitted report or any `attempts/wave14-proof-a` file, I
reconstructed the arithmetic and local framework from the frozen Wave 6-12
reports.  That reconstruction is recorded in
`verification/n3-48-proof/preinspection-freeze.md`.

The freeze found the twelve profiles, the inherited degree filters, the
`r=16` all-`q=2` reduction, the size-two/three point reduction, and the
all-size-two support/coverage identities.  It deliberately left the two
mixed-profile exclusions and the claimed countermodel unresolved.  It also
flagged that the cyclic `U`-capacity inequalities alone leave nine sorted
`t`-triples.  The submission correctly resolves that apparent discrepancy:
the claimed eight modes are aligned `(t_i,a_i)` modes after recording empty
meeting crossings and excluding two zero-full-crossing modes.  There is no
count mismatch.

No Wave 13 path and no Wave 14 computation-lane path was read.  None is
needed for the deductions checked here.

## 2. Claim-by-claim verdict

| Claim | Verdict | Audit result |
|---|---|---|
| Twelve `sum q=32` profiles | PASS | Independent enumeration reproduces `1+1+4+3+2+1=12` profiles for `r=11,...,16`. |
| Inherited degree filters | PASS | Three non-singleton point cliques give `d_K>=3`; the audited degree-three lemma removes the last `r=13` row. |
| Mixed `r=14` profile | PASS / DERIVED | Point sizes reduce to two/three; size-three points are eliminated; the remaining cubic point graph overfills a special label of `K`-degree four. |
| Mixed `r=15` profile | PASS / DERIVED | Point sizes reduce to two/three; no size-three point meets a special label; a special-ordinary size-two point has fixed sum ten but every incident term is `0 mod 4`. |
| `r=16` profile | PASS | `q=(2^16)` and `K=overline L` is simple 9-regular. |
| Point sizes two/three | PASS | Expansion gives size at most five; the size-five and size-four flower cases contradict degree/crossing capacity. |
| Ten aligned local modes, then eight | PASS | Independent enumeration gives 32 labeled states and ten permutation types; the `111` and empty-`112` modes are correctly excluded. |
| All residual `H`-degrees are zero/four | PASS | A six-crossing contradicts the fixed sum twelve once every size-three point has a full meeting crossing. |
| Support and coverage residual | PASS | `d_R(P)=|P|`, `|E(R)|=24`, and every one of 48 `L`-edges has exactly two cross-edge rectangles. |
| Explicit all-size-two object | PASS / CANDIDATE relaxation | Independent reconstruction verifies every stated finite active-layer condition and five hostile mutations fail. |
| Exclusion of `n3=48` | UNKNOWN | No exclusion is proved or claimed. |
| Conway-99 | UNKNOWN | No 99-vertex construction or nonexistence proof is present. |

## 3. Profile arithmetic and inherited filters

At `n3=48`,

```text
sum q = 2n3/3 = 32,
q>=2,
3q<=r-1,
d_K=r-1-3q.
```

Independent nondecreasing partitioning gives exactly:

```text
r=11: (2,3^10)
r=12: (2^4,3^8)
r=13: (2^10,4^3), (2^9,3^2,4^2),
      (2^8,3^4,4), (2^7,3^6)
r=14: (2^12,4^2), (2^11,3^2,4), (2^10,3^4)
r=15: (2^14,4), (2^13,3^2)
r=16: (2^16).
```

Every active label lies in three distinct non-singleton point cliques, whose
incident clique edges are disjoint.  Hence `d_K>=3`.  The previously audited
degree-three obstruction applies with the required quantifiers: all three
points through a degree-three label are forced size two; the three further
singleton crossings produce a forbidden Berge triangle of point sets.

The surviving rows are exactly:

```text
r=14: q=(2^10,3^4), dK=(7^10,4^4)
r=15: q=(2^13,3^2), dK=(8^13,5^2)
r=16: q=(2^16),     dK=(9^16).
```

No graph-realizability or automorphism assumption enters this enumeration.

## 4. The two mixed-profile exclusions

### `r=14`

Flower expansion gives `2s<=14-s`, so a point has size at most four.  A
size-four point has eight pairwise-disjoint nonempty petals in ten external
labels, hence at least six singleton petals.  Each singleton endpoint is
`K`-adjacent to all four roots.  This gives every root at least
`3+6=9` `K`-neighbors, exceeding even the ordinary degree seven.

With point sizes two/three, let `t_i` count size-three points through `i` and
put `U=K-E(F)`.  The degree identities

```text
d_U(i)=4-t_i  (ordinary),
d_U(i)=1-t_i  (special)
```

are correct.  If a size-three point contains a special root `x`, then
`t_x=1` and `d_U(x)=0`.  The absence of singleton petals at the other roots
forces both of their `t`-values to three; the two singleton petals at `x`
then demand two distinct `U`-neighbors where only one is available.

For an all-ordinary size-three point, the cyclic forced-neighbor inequalities
and external capacity leave `(2,2,2)` and `(2,3,3)`.  The latter forces five
distinct full meeting crossings.  These are actual graph edges because the
two point objects share the relevant active graph-triangle.  Their
contribution `5*4=20` exceeds the fixed-point sum twelve.

In the remaining `(2,2,2)` case, the graph on size-three point objects is
simple cubic and triangle-free.  Its `e` edge labels are ordinary; the third
size-two point at each edge requires a distinct ordinary `t=0` endpoint.
Thus `e<=3(10-e)`, so `e<=7`.  A nonempty simple cubic triangle-free graph
has at least six vertices and nine edges, a contradiction.

Finally, if all points have size two, they form a simple cubic triangle-free
graph `F`.  At a special label `x`, a path `x-a-y` forces `xy in K`.
Applying this to both other neighbors of `a` gives five distinct
`K`-neighbors of `x`, contradicting `d_K(x)=4`.  All distinctness assertions
follow from cubicity and triangle-freeness; no hidden connectedness is used.

### `r=15`

Expansion gives size at most five.  A size-five point has ten singleton
petals in exactly ten outside labels.  A size-four point has at least five
singleton petals; if exactly five, the other three petals each have two
external labels, and a base root has at least `3+5+2=10` `K`-neighbors.
Thus only sizes two/three remain.

Here

```text
d_U(i)=5-t_i  (ordinary),
d_U(i)=2-t_i  (special).
```

The cyclic forced-neighbor inequalities have no state for a size-three point
with two special roots.  With one special root, the other roots must both
have `t=3`.  Their four distinct size-three co-points must have full meeting
crossings, contributing sixteen to a fixed sum of fourteen.  The conclusion
that no size-three point contains a special label is therefore sound.

Each special label consequently lies in three size-two points.  Linearity
allows at most one special-special point, so a special-ordinary size-two
point exists.  Its fixed-point sum is ten.  For each **actual graph
neighbor**, the other active point has size zero, two, or three.  After
deleting a possible overlap, the two-sided `0/2` crossing rule makes every
term zero or four.  Their sum cannot be ten.  This argument does not apply
the crossing rule to arbitrary nonedges.

## 5. The `r=16` point and local-mode reductions

Now `L` is 6-regular and its simple complement `K` is 9-regular.  Expansion
gives point size at most five.

- A size-five point has at least nine singleton petals.  Together with its
  internal `K4`, every root already exceeds degree nine.
- A size-four point has at least four singleton petals.  The cases with at
  least five are overfull at a petal base.  With exactly four, external
  capacity is exact and there is one size-three petal at each root.  Every
  root is saturated.  The external pair of any such petal is therefore
  `L`-adjacent to all three other roots, producing a `K_(2,3)` crossing.
  Its row degree three violates the actual-edge two-sided `0/2` law.

Thus every active point has size two or three.

For a size-three point `P={1,2,3}`, `t_i` counts size-three points at root
`i`, while `a_i` counts the other size-three co-points at `i` whose meeting
crossing with `P` is empty.  Empty meeting rectangles are in `U`: an
`F`-owner would form a forbidden Berge triangle with the two meeting points.
Consequently

```text
d_U(i)=6-t_i,
6-t_i >= sum_(j!=i)(3-t_j+2a_j),
4 sum_i(t_i-1-a_i) <= 12.
```

The last inequality counts distinct actual co-point neighbors with full
crossing.  Independent enumeration reproduces 32 labeled states and the ten
aligned permutation types in the submitted table.

The two zero-full-crossing modes are correctly excluded:

- In mode `111`, the six singleton endpoints are `K`-adjacent to all three
  roots.  The remaining three root-to-outside `K` incidences distribute as
  `3`, `2+1`, or `1+1+1`.  Applying the crossing restriction only to active
  sets of actual neighbors gives total possible positive contribution at
  most six, below twelve.
- In empty-`112`, five singleton endpoints and the empty co-point's external
  pair saturate all three roots.  Each remaining label has crossing degree
  three into `P` and cannot occur in an actual-neighbor point.  Every actual
  edge at `P` consequently has `H`-degree zero, again contradicting twelve.

Exactly eight aligned necessary local modes remain.  The report correctly
does not claim that every such mode extends to a global point hypergraph.

## 6. `H`-degree, support, and exact coverage

Once the two zero-full modes are gone, every size-three point has at least
one full meeting crossing of `H`-degree four.  A six-crossing can occur only
between disjoint size-three points.  With one existing four-contribution it
would leave a remainder two in the fixed sum twelve; with at least two it
would exceed twelve.  Thus all graph edges have `H`-degree zero or four.

Let `R` join point objects whose actual graph edge has `H`-degree four.
The fixed-point identity gives

```text
d_R(P)=|P|,
sum_P |P|=16*3=48,
|E(R)|=24.
```

Each `R`-edge supplies one full `2 x 2` `L`-rectangle.  Every `L`-edge is an
induced-`N3` side pair and has exactly its two independent cross graph-edges,
so exact coverage is two.  The counts agree:

```text
24 rectangles * 4 L-edges = 48 L-edges * 2 covers = 96.
```

The 24 `R`-edges are the nonisolated vertices of `H`; each has degree four.
The inherited `H` is simple and triangle-free and has 48 edges.  These are
necessary residual constraints, not an exclusion.

## 7. Independent countermodel verification

`verification/n3-48-proof/audit_countermodel.py` parses the frozen JSON
without importing any discovery-lane module and reconstructs all derived
graphs.  It verifies:

```text
F:       16 vertices, 24 edges, simple cubic triangle-free, components 2 Q3
K/L:     complementary simple graphs, degrees 9/6, edges 72/48
points:  24 size-two blocks, label degree three, linear, no Berge triangle
R:       24 edges, point degree two, components 6 C4
coverage: exactly two support rectangles on every one of 48 L-edges
H:       24 vertices, 48 edges, connected simple 4-regular triangle-free
```

For every `L`-edge, the independent verifier additionally constructs its two
three-point side triangles and checks that the two selected cross graph-edges
have four distinct endpoints.  All 48 six-vertex active subgraphs are literal
`N3`s.  This matching check is not a separate assertion in the submitted
validator, but the submission's adjacent-pair common-neighbor cap already
implies it: two cross edges sharing an endpoint would give a side edge its
designated triangle neighbor plus the shared cross endpoint.  The explicit
check removes any dependence on that indirect implication.

The builder re-renders the frozen certificate byte-for-byte with SHA-256
`5d06ae777fb0ca4450951708bba3ffc85d1f617be1d19c2be210f43df82b8952`.
Five mutations were mounted and rejected independently:

```text
q value                 REJECTED
K/L complement          REJECTED
support rectangle       REJECTED
H reconstruction        REJECTED
actual-edge crossing    REJECTED
```

The submitted validator and all ten submitted focused tests also pass.

## 8. Encoded and unencoded premises

The certificate and independent replay encode:

- all sixteen active `q=2` labels and their 24 indexed point objects;
- point simplicity, cubicity, triangle-freeness/common-point rule;
- `K/L` simplicity, complementarity, and exact regular degrees;
- every forced meeting singleton crossing;
- selected actual support edges and their two-sided crossings;
- fixed-point sum eight at every point;
- exact twofold `L`-coverage and independent `N3` cross edges;
- the resulting nonisolated `H`, including simplicity, degree four,
  connectedness, and triangle-freeness; and
- active-subgraph common-neighbor upper caps `lambda<=1`, `mu<=2`.

They do not encode:

- the other 75 original graph vertices or degree-14 completion;
- all 231 graph-triangles, inactive triangles, or prism partners;
- the full 693-vertex opposite-edge graph `J` or isolated part of `H`;
- the missing common-neighbor equalities in the completed 99-vertex graph;
- extension of the active object to an `srg(99,14,1,2)`; or
- any target existence, nonexistence, or novelty claim.

The catalog census is not needed for the positive countermodel.  Its first
run explicitly restricts all active points to size two, tests only mandatory
`K`, depends externally on the 801-record `geng` catalog, and imposes a
100,000-node cutoff.  The recorded `798 UNSAT / 3 CUTOFF` outcome is
non-evidentiary for target nonexistence.  The deeper index-12 run is useful
only as discovery provenance; the detached explicit object carries the
positive relaxation claim.

## 9. Strongest objections and status boundary

1. **Conditional semantic bridge.**  The human proof relies on the inherited
   no-singleton, complementarity, common-point, support, fixed-point, and
   two-sided labeled-crossing lemmas.  This audit checked their use and
   quantifiers but did not rederive all of them from a raw 99-by-99 adjacency
   matrix.
2. **Local modes are not global objects.**  The eight surviving
   size-three modes are a necessary local classification only.
3. **Countermodel scope is narrow.**  Passing the active/support relaxation
   says only that those premises cannot exclude the all-size-two subcase.
   Completion constraints involving inactive triangles or omitted vertices
   may still exclude it.
4. **No negative computation is a certificate.**  Catalog nonhits and node
   cutoffs carry no nonexistence weight.

None of these objections invalidates the scoped reduction.  They enforce its
boundary:

```text
Wave 14 proof-A structural reduction: PASS / DERIVED
all-size-two active countermodel:     PASS / CANDIDATE relaxation
conditional n3=48 exclusion:         UNKNOWN
Conway-99:                            UNKNOWN
novelty:                              UNKNOWN
```
