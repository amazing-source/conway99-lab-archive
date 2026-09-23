# Wave 12 computational lane: the \(n_3=42\) equality frontier

```yaml
role: construction
date_utc: 2026-07-23T06:30:28Z
git_commit: eef36d7bbcc14b3a031c56ee096e098580d6847a
claim_label: CANDIDATE
scope: >
  Independent reconstruction of the n3=42 active profiles; exhaustive
  rooted-local checks for point size four and the mixed order-13 profile; a
  restricted all-size-two active-local SAT diagnostic; and a conditional
  four-type support/common-neighbor census. This is not a 99-vertex search.
inputs:
  AGENTS.md: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  STATUS.yaml: c73aa7bb7b48abf0c7827e61a99609b2eee8cd4cc49cfd12dda0a8753a9835b5
  STRUCTURE.md: 96818ac7a0674efb8daebb7ca70327f60d3b217be1fa79064aaaa8dea49fdd6f
  agents/2026-07-22-wave9-n3-33-equality.md: b2fe46cce67440d1a730d6f56b48a512952624d79afa9835ffc772c050c94555
  agents/2026-07-22-wave10-n3-36-equality.md: 9a1e2ad7cac5e26f9fe4117c8ced2390ca15a4dfda7b1e67faa02b8e90ba507e
  agents/2026-07-22-wave11-n3-39-equality.md: 0119df513027d9f895eabc9746ac6efd4f5a779366638603b5dc0dfa81b80e82
  verification/2026-07-22-n3-39-equality-audit.md: 159b1746b715984749f3efc790c56be5b2624e889901412ad0bcf8e2cc9497b9
  requirements-search.txt: 262f4a1a62fab79ee790da44b9f923b14ed77bafe6e9a6732846953ee9c622ce
method: >
  Re-derived the active-q partition and K degrees without importing prior
  checker formulas; enumerated all 3^8 rooted size-four petal words and both
  degree-three-star continuations; generated and independently validated a
  restricted PySAT/CaDiCaL model; generated an isomorphism catalog with nauty
  2.9.1; then used a standard-library include/exclude factor search with
  monotone lambda/mu cap pruning.
command: |
  python code/wave12_n3_42_active.py --certificate attempts/wave12-computation/n3-42-size2-active-local-candidate.json
  python code/wave12_n3_42_size2_scout.py --compare attempts/wave12-computation/n3-42-size2-active-local-candidate.json
  python code/wave12_n3_42_size2_caps.py --catalog attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6
  python code/test_wave12_n3_42.py -v
  geng -q -td3D3 14 21:21
outputs:
  code/wave12_n3_42_active.py: 9d0b63a0fc74031de52987028595e3daeeb62ead7f57eac05e40672e5932bde2
  code/wave12_n3_42_size2_scout.py: ac0737c8c898196fc8607e38e2718a7d9a9ed8557af8199b447250b01ceb6996
  code/wave12_n3_42_size2_caps.py: 3de29e1e32b555aec9bd4a5dbbba8ea24d2ca3deebc32c4d77c66c3db5b33011
  code/test_wave12_n3_42.py: 5aa8d112b903b4e7c62fe6bca7f5908aaac7fedc3e026781a88e5e4625dd7e21
  attempts/wave12-computation/n3-42-size2-active-local-candidate.json: 1fdba37dbe6015b0788b0a545b970ae3e506d906bbfc191e5183902d3a7a8210
  attempts/wave12-computation/n3-42-cubic-trianglefree-14.g6: 24bfd4964cc4e86554f721ff0f988c5e0bb8fc992b6113f142f09737d3ac90fd
  raw_active_profiles: 6
  profiles_after_no_singleton_premise: 2
  mixed_order13_local_survivors: 0
  restricted_active_local_candidate: SAT
  conditional_all_size_two_full_cap_survivors: 0
  target_result: UNKNOWN
limitations: >
  Every conclusion is conditional on the Wave 7-11 active-point premises.
  The all-size-two cap census is restricted to that point-size branch. Its
  112-record graph6 catalog has nauty completeness as an external premise;
  no second generator or UNSAT proof trace is archived here. The construction
  agent therefore does not promote the zero-survivor census to VERIFIED.
  The SAT diagnostic is not a graph completion. No automorphism of a completed
  Conway graph is assumed, no 99x99 adjacency matrix is produced, and the
  target remains UNKNOWN.
```

## Evidence boundary

This lane has three different evidentiary levels:

| result | scope | construction-lane status |
|---|---|---|
| six active profiles, singleton filter, size-four flowers, mixed-star closure | finite arithmetic/local implications from the frozen premises | exact derivation and standard-library replay, awaiting verifier |
| 14-triangle all-size-two local object | deliberately weakened active-local subproblem | explicit `CANDIDATE`; a diagnostic counterexample to an overstrong local exclusion |
| zero all-size-two supports after active common-neighbor caps | 112 nauty types, then exact standard-library search | `CANDIDATE`; catalog completeness and code still need independent verification |

None of these rows establishes existence or nonexistence of
`srg(99,14,1,2)`.

## Six raw profiles, not five

At \(n_3=42\), the handshake identity gives

\[
\sum_T q(T)=\frac{2n_3}{3}=28.
\]

Independently enumerating nondecreasing parts \(q\geq2\) subject to
\(3q(T)\leq r-1\), where \(r\) is the number of active triangles, gives six
profiles:

| \(r\) | \(q\)-profile | \(K\)-degree profile | forced singleton incidences |
|---:|---|---|---:|
| 14 | \(2^{14}\) | \(7^{14}\) | 0 |
| 13 | \(2^{11}3^2\) | \(6^{11}3^2\) | 0 |
| 13 | \(2^{12}4\) | \(6^{12}0\) | 3 |
| 12 | \(2^8 3^4\) | \(5^8 2^4\) | 4 |
| 11 | \(2^5 3^6\) | \(4^5 1^6\) | 12 |
| 10 | \(2^2 3^8\) | \(3^2 0^8\) | 24 |

The \(r=13\), \(2^{12}4\) profile is easy to miss; it is the sixth raw
profile. Three non-singleton point cliques through an active triangle require
three distinct incident \(K\)-edges. Conditional on the already audited
no-singleton lemma, the last four rows shown with positive singleton lower
bound are impossible. The two zero rows remain at this stage.

## Exact size-four rooted-flower check

The Wave 11 expansion argument is unchanged in form. If an active point
\(P\) has size \(s\), the two other point sets at each of its occurrences
supply \(2s\) distinct representatives outside \(P\). Hence

\[
2s\leq r-s.
\]

For both \(r=13\) and \(r=14\), every active point has size at most four.
Suppose \(|P|=4\). Its eight other point sets have pairwise-disjoint external
parts. The checker exhausts all \(3^8=6561\) ordered petal-size words over
\(\{2,3,4\}\).

A size-two petal has singleton external side, so its \(L\)-crossing with
\(P-\{i\}\) is empty. Complementarity makes its endpoint \(K\)-adjacent to all
four members of \(P\). Together with the internal \(K_4\), every member of
\(P\) therefore has \(K\)-degree at least

\[
3+\#\{\text{size-two petals}\}.
\]

The exact censuses are:

| active order | capacity-feasible words | size-two petals | root degree lower bound | survivors |
|---:|---:|---|---|---:|
| 13 | 9 | \(7^8,8^1\) | \(10^8,11^1\) | 0 |
| 14 | 45 | \(6^{28},7^{16},8^1\) | \(9^{28},10^{16},11^1\) | 0 |

The available \(K\)-degrees are at most six in the mixed order-13 profile and
exactly seven in the order-14 profile. Thus size four is excluded in both
surviving active profiles.

## Exact two-assignment obstruction in the mixed profile

Consider a \(q=3\) triangle \(b\) in the \(r=13\),
\(2^{11}3^2\) profile. It has \(K\)-degree three. Its three non-singleton
point cliques must therefore be exactly

\[
\{b,x\},\quad\{b,y\},\quad\{b,z\},
\]

and \(N_K(b)=\{x,y,z\}\). The three singleton-by-singleton crossings at
\(b\) are empty in \(L\), so \(xyz\) is a triangle in \(K\). None of
\(xy,xz,yz\) may have a point owner: for example, an owner of \(xy\)
together with \(\{b,x\}\) and \(\{b,y\}\) forms the forbidden three-point
Berge triangle.

Now inspect the point \(\{b,x\}\) at its occurrence \(x\). The other two
point sets through \(x\) have nonempty, disjoint external parts. Their
crossings with the singleton side \(\{b\}\) are empty, so every external
member must lie in

\[
N_K(b)-\{x\}=\{y,z\}.
\]

There are exactly two ordered assignments:

```text
({y},{z}) and ({z},{y}).
```

Both make \(xy\) and \(xz\) point-clique edges, contradicting the owner veto
above. The standard-library routine emits both records and zero survivors.
Subject to independent proof review, this reduces the unrestricted active
frontier to

```text
r=14, q=(2^14), K 7-regular, point sizes in {2,3}.
```

## Retained counterexample to an overstrong local claim

The pinned search environment contains `python-sat==1.9.dev7`. A 5,579-clause,
2,198-variable CaDiCaL 1.9.5 instance restricted every active point to size
two. In this restriction the point hypergraph is a cubic triangle-free graph
\(F\) on 14 active triangles. The SAT clauses require:

1. \(F\subseteq K\);
2. \(K\) is 7-regular; and
3. the three \(F\)-neighbors of every active triangle form a clique in \(K\),
   exactly the singleton-crossing law at that triangle.

The result is `SAT`. The archived object has 21 point pairs, 49 \(K\)-edges,
and the exact 42-edge complement \(L\). A second exact-cardinality instance
finds a 21-cycle of disjoint point pairs whose crossing is a full \(K_{2,2}\)
in \(L\). Each active point consequently has two available contributions of
four, matching the numerical fixed-point right side \(4|S|=8\).

The object is intentionally retained because it refutes the tempting claim
that active incidence, common-point, complement, regularity, and local
crossing constraints alone exclude the equality case. Its semantic canonical
digest is

```text
1f9b1ddf93b1c9a187ac06711fb6377d817fca785a9695f3b13c3584f11fb3a3.
```

The pretty-printed file SHA-256 is the different, byte-level digest shown in
the run header.

This object is not a partial SRG certificate. If the line-graph adjacencies
and the chosen support opportunities are treated as forced active
adjacencies, the resulting 6-regular graph on the 21 active original points
has:

```text
34 adjacent-pair lambda-cap violations,
20 universal two-common-neighbor-cap violations
  (13 pairs have 3 active common neighbors and 7 have 4).
```

The validator computes these failures rather than hiding them.

## Adding the fixed-point support and SRG caps

The all-size-two restriction permits a much smaller exact representation.
The 21 active original points are the edges of the cubic graph \(F\).
Their active-triangle adjacencies form the line graph \(L(F)\).

For an active original point \(u\), \(|S_u|=2\) and both active triangles
have \(q=2\), so the fixed-point identity requires

\[
\sum_{v\sim u} d_H(uv)=8.
\]

An overlapping active point and an empty active point contribute zero. For
two disjoint size-two point sets, the zero-or-two crossing law permits a
positive contribution only when their entire \(2\)-by-\(2\) crossing lies
in \(L\), in which case the contribution is four. Hence the positive-support
edges form a 2-regular graph \(R\) on \(E(F)\).

Let \(M\) contain:

- every edge of \(F\); and
- every pair of \(F\)-neighbors of a vertex.

Every valid \(K\) contains \(M\). Thus \(\Delta(M)>7\) immediately rejects
\(F\). A possible edge of \(R\) joins disjoint \(F\)-edges and requires all
four endpoint cross-pairs to avoid \(K\). The census tests this only against
\(M\), giving a relaxation: completing \(K\) can only delete support
opportunities.

Finally put

\[
A=L(F)\cup R.
\]

These are forced adjacencies among the 21 active original points. Therefore:

- an adjacent pair in \(A\) has at most one common neighbor in \(A\); and
- every pair has at most two common neighbors in \(A\).

These are only upper bounds. Unknown zero-support adjacencies and inactive
vertices are omitted, so the finite model is a sound relaxation of the full
SRG constraints.

## The 112-type cubic census

Nauty 2.9.1 generated the archived catalog with

```text
geng -q -td3D3 14 21:21
```

The catalog contains 112 distinct graph6 records, including disconnected
graphs. The standard-library consumer rechecks order 14, 21 edges, cubicity,
triangle-freeness, graph6 syntax, and record uniqueness. The generator
provenance available in scratch at run time was:

| artifact | SHA-256 |
|---|---|
| `nauty.tar.gz` | `488fa906d10a372c72d2364c5dee48e0f7307004fbe52c2bce50c52de8cd873e` |
| nauty 2.9.1 `geng.c` | `12bba376483782ae40b132e0b66f42cbbbf3acb6c2468f8c0e33ccdd505fc2d0` |
| locally built `geng` | `a70d25eda4e7b783b541111b0fbd3d46a6f0579436623c331f2afb810423c031` |

The mandatory-\(K\) degree filter rejects 108 records. Four representatives
remain:

| catalog index | graph6 | \(|M|\) | support opportunities | exact full-cap search |
|---:|---|---:|---:|---|
| 0 | `M???FB_w?wBOD_B_?` | 39 | 108 | 43 nodes, 36 cap rejections, 0 survivors |
| 6 | `M???FBOiAgDOD_B_?` | 49 | 35 | 13 nodes, 9 cap rejections, 0 survivors |
| 14 | `M??CEB_[@oB_B_@o?` | 49 | 35 | 4 nodes, 3 cap rejections, 0 survivors |
| 17 | `M??CE?wM@oW_P_@o?` | 43 | 108 | 43 nodes, 36 cap rejections, 0 survivors |

The include/exclude search enforces degree two in \(R\). Whenever an edge is
forced or selected it recomputes active common-neighbor counts; these counts
are monotone under later edge additions, so an upper-cap violation is a safe
prune. The search uses the relaxed compatibility graph defined by \(M\), not a
chosen completion \(K\).

For index 6, an adjacent-cap-only diagnostic survives:

```text
R = 3 C7
cycles:
  0-16-7-10-13-4-20
  1-17-6-11-12-5-18
  2-15-8-9-14-3-19
```

Adding the universal two-common-neighbor cap eliminates it and every other
factor. This is a sharper failure witness than a bare solver status.

Conditional on the nauty catalog being complete and on the correctness of the
small backtracker, the all-size-two branch has no survivor. This lane does not
promote that statement to `VERIFIED`: there is no independently generated
catalog, no checked UNSAT proof, and no independent verifier yet.

## Failed and bounded attempts retained

- A direct labeled joint SAT over \(F,K,R\) with the stronger constraints was
  attempted elsewhere in the Wave 12 coordination. MiniCard and CaDiCaL
  reached a 120-second cutoff without a conclusion. No proof trace was
  produced; this contributes no evidence.
- This lane blocked the first 100 labeled active-local models and found no
  cap-compatible support. That duplicated isomorphic structures and was
  discarded as a completeness route.
- A 20,000-model labeled loop hit its 60-second cutoff before a conclusion.
  It was replaced by the 112-type isomorphism catalog.
- After the initial successful nauty generation, two later exact-line replay
  attempts in the shared, heavily contended WSL instance hit 15- and
  30-second process cutoffs before returning output. The archived catalog and
  its hash are public, but this is another reason the catalog layer remains a
  premise pending clean independent replay.

## Status

The strongest construction-lane conclusion suitable for handoff is:

```text
raw n3=42 active profiles:                 6
after the established no-singleton lemma: 2
size-four local survivors:                0
mixed order-13 local survivors:           0
remaining unrestricted active domain:     r=14, q=(2^14), sizes {2,3}
all-size-two cap census:                   0 survivors, CANDIDATE only
Conway-99 target:                          UNKNOWN
```

The remaining size-three branches in the \(r=14\) domain were not exhaustively
searched here. No bound beyond the already verified \(n_3\geq42\) is claimed.
