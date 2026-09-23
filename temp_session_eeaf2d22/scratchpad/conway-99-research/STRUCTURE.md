# Checked structural baseline

This file collects consequences of the frozen target. `DERIVED` means the
argument is reproduced in this project; it does not imply novelty.

## Global counts (`DERIVED`)

Any Conway 99-graph has:

- spectrum `14^1, 3^54, (-4)^44`;
- 693 edges;
- 231 triangles, with the edges partitioned among them;
- seven triangles through every vertex;
- 4,158 nonedges;
- 2,079 four-cycles; and
- 84 four-cycles through every vertex.

The clique number is exactly three: triangles exist, while a `K_4` would put
each of its edges in two triangles. Hoffman's ratio bound gives independence
number at most 22 and therefore chromatic number at least five.

The complement would be `srg(99,84,71,72)`. The Laplacian spectrum is
`0^1, 11^54, 18^44`, so the matrix-tree theorem forces

```text
spanning_trees = 11^54 * 18^44 / 99.
```

## Forced `N3` and two-vertex percolation (`CITED` + `DERIVED`)

Every putative Conway graph contains an induced `N3`: two disjoint triangles
joined by exactly two independent cross-edges. Makhnev proved that no target
graph satisfies the condition that two triangles joined by at least two
cross-edges always have exactly three; `lambda=1` makes those cross-edges a
matching, so failure of the condition forces `N3`.

Reimbayev's six-vertex identities then give

```text
n3 = 0 (mod 3),
induced_C6_count = 209,286 + n3.
```

Wave 6 first sharpened the target-specific count to `n3>=24`. Wave 7 excludes
the next two multiples of three, Waves 8--13 exclude equality at 30, 33, 36,
39, 42, and 45, Wave 15 excludes equality at 48, Wave 16 excludes equality at
51, Wave 17 excludes equality at 54, Wave 18 independently excludes equality
at 57, and Wave 19 excludes equality at 60. Wave 20 then replaces the
equality frontier with a global Schur-projector argument, and Wave 23 excludes
its first surviving endpoint. The currently strongest internally verified
project bound is

```text
n3 >= 708,
induced_C6_count >= 209,994.
```

Wave 21 independently exhausts the published six-vertex and Hamiltonian
seven-vertex affine count systems. Relative to the then-current Wave 20
bound, those necessary conditions retained every multiple of three from 705
through 4,158 and therefore supplied no improvement.

For the proof, form a graph `J` on the 693 graph edges, joining two when they
are opposite in a four-cycle. It is 12-regular, so has 4,158 edges. Its
triangles are exactly induced triangular prisms. The subgraph `H` of
nontriangular `J` edges is triangle-free and its edges correspond bijectively
to induced `N3` copies. At every `H` vertex the degree lies in
`{0,4,6,8,10,12}`. Nonemptiness uses the target-specific forced `N3` theorem;
minimum degree, Mantel's bound, and `n3 = 0 (mod 3)` reduce the sub-24 cases
to 18 and 21 edges, and separate local arguments exclude both. The Wave 6
proof and adversarial audit are in
`agents/2026-07-22-wave6-opposite-edge-graph.md` and
`verification/2026-07-22-n3-count-bound-audit.md`.

For the Wave 7 strengthening, form a graph `L` on the 231 graph-triangles,
joining two when they are the sides of an induced `N3`. If `p(T)` is the
number of prism partners of triangle `T` and `q(T)=12-p(T)`, exact cross-edge
counts give

```text
d_L(T)=3q(T),
sum_T q(T)=2n3/3.
```

Lou and Murin's 2014 MIT PRIMES report already gives the equivalent fixed-
triangle partner equations and excludes `q=1` in its variables
`(alpha,beta,gamma)=(a1,a2,a3)`. Wave 7 independently rederived this profile
and combined it with the later opposite-edge graph framework; the project
does not claim novelty for the partner identities or the `q`-gap.

The local two-matching structure makes the `N3`s with fixed side `T` a
2-regular subgraph of triangle-free `H`, so `q(T)` is zero or at least two.
For `n3=24` and 27 this forces respectively eight and nine active triangles,
all with `q=2`. Their `L`-complements are a perfect matching and a 2-regular
graph. For each graph vertex `u`, the active triangles containing `u` form an
independent set `S_u` in `L`, and every actual graph edge satisfies

```text
d_H(uv)=e_L(S_u,S_v).
```

Exact point-incidence enumeration bounds the support of `H` by six when
`n3=24`, and by nine or eight in the only surviving 27-edge cases. These
contradict the required support sizes. Two materially different standard-
library checkers reproduce the finite reduction. The proof and independent
audit are in `agents/2026-07-22-wave7-triangle-side-incidence.md` and
`verification/2026-07-22-n3-side-incidence-audit.md`.

Wave 8 treats `n3=30`. The same arithmetic forces ten active triangles, all
with `q=2`; their `L`-complement `K` is cubic. For an original graph vertex
`u`, a uniform fixed-side count gives

```text
sum_{v: uv in E(G)} d_H(uv) = 4 |S_u|.
```

Point cliques `S_u` consume disjoint `K`-edges. A size-four point is a
saturated `K4` component and forces singleton points, contradicting the fixed-
point identity. Without a size-four point, singletons are again impossible,
and the incidence/edge budget forces fifteen size-two points consuming every
`K`-edge. A cubic graph on ten vertices has a vertex with two nonadjacent
neighbors `j,k`; the corresponding original vertices share an active graph-
triangle but have exactly the one crossing `L`-edge `jk`. The support identity
would give forbidden `H`-degree one. This excludes `n3=30` without classifying
cubic graphs. An independent slow audit also exhausts all 21 cubic types and
674,880 point-clique families. The proof and audit are in
`agents/2026-07-22-wave8-n3-equality.md` and
`verification/2026-07-22-n3-equality-audit.md`.

Wave 9 treats `n3=33`. The active-`q` arithmetic leaves only a mixed profile
`(2^8,3^2)` on ten triangles and an all-`q=2` profile on eleven. A labeled
crossing graph between possibly overlapping point sets shows that an active
singleton point would give incident `H`-degree zero or two; the global allowed
degree set eliminates two, while the fixed-point identity eliminates zero.
This immediately rules out the mixed profile.

In the eleven-triangle case the complement `K` is 4-regular. Disjoint
point-clique edge consumption leaves only size profiles
`(x2,x3)=(12,3),(15,1)`. Every size-three point forces a saturated `K5`
component. Three such points need fifteen vertices; one leaves
`K6` minus a perfect matching, where the three consumed neighbors of any
vertex would have to be a clique but never can be. This excludes `n3=33`
without assuming connectedness or a completed-graph automorphism. The proof,
compact checker, and adversarial audit are in
`agents/2026-07-22-wave9-n3-33-equality.md`,
`verification/n3-33-equality/verify.py`, and
`verification/2026-07-22-n3-33-equality-audit.md`.

Wave 10 treats `n3=36`. The active arithmetic gives `(2^12)`, `(2^9,3^2)`,
and `(2^6,3^4)`. The singleton lemma eliminates both mixed profiles because
their `q=3` triangles have `K`-degree one or zero. In the all-`q=2` case,
`K` is 5-regular on twelve active triangles and the only local point types are
`222`, `223`, `224`, and `233`.

Three point sets cannot pairwise meet at three distinct active triangles:
their original vertices would form a second graph-triangle on each edge. This
common-point rule, together with the local crossing alternatives, eliminates
size-four points and both possible modes of size-three incidence. In the
all-size-two branch, the consumed edges form a cubic graph `F`, while
`K-E(F)` is forced to be `4C3`; symmetry gives `F=2K3,3` and `K=2K6`.
Within either component the nine original point objects induce
`L(K3,3)=srg(9,4,1,2)`. Every internal pair has already saturated its required
`lambda=1` or `mu=2` common-neighbor count, whereas the fixed-point identity
forces each opposite point to be adjacent to two of them. This contradiction
excludes `n3=36` without a completed-graph automorphism assumption.

The proof, compact checker, independent 216-support census, and adversarial
audit are in `agents/2026-07-22-wave10-n3-36-equality.md`,
`verification/n3-36-equality/verify.py`,
`verification/n3-36-equality/n3-36-support.json`, and
`verification/2026-07-22-n3-36-equality-audit.md`. An initially proposed
closed-`K5` shortcut failed review and is not used in the repaired proof.

Wave 11 treats `n3=39`. The active arithmetic leaves four profiles. Singleton
forcing eliminates the three mixed profiles, while the all-`q=2` profile has
thirteen active triangles and a 6-regular complement `K`. Every active point
set is a clique in `K`; linearity and the common-point rule show that a point
of size `s` needs `2s` distinct representatives outside itself, so `s<=4`.

A size-four point has eight external petals in nine available places. At
least three occurrences are `224`; two such occurrences provide four distinct
endpoints adjacent in `K` to all four root vertices, forcing root degree at
least seven. With only sizes two and three left, let `F` be the point-clique
edges and `U=K-E(F)`. If `t_i` size-three points pass through active triangle
`i`, then

```text
d_F(i)=3+t_i and d_U(i)=3-t_i.
```

At a `233` occurrence, the size-two endpoint has four singleton-crossing
neighbors. The common-point rule prevents any of their edges from lying in
`F`, contradicting `d_U<=3`. A size-three point cannot be all `333` by the
same external-capacity argument; hence it has a `223` occurrence. Its five
forced `U`-edges propagate `223` to the other two root occurrences, whose four
distinct endpoints then force `U`-degree four at the original root, although
its available degree is two. Finally, an all-size-two point family would have
even total incidence, contradicting `13*3=39`.

The derivation and all checkers explicitly require that `K` is the simple
complement of `L` on distinct active triangles. An earlier exposition omitted
that bridge and failed audit. The repaired compact checker, independent
8,907-record replay, and public audit are in
`agents/2026-07-22-wave11-n3-39-equality.md`,
`verification/n3-39-equality/`, and
`verification/2026-07-22-n3-39-equality-audit.md`.

Wave 12 treats `n3=42`. Exact partitioning of `sum q(T)=28` gives six raw
active profiles. The inherited no-singleton premise first leaves
`(2^14)` and `(2^11,3^2)`. A triangle of forced point sets around any active
`K`-vertex of degree three excludes the mixed profile, so the sole case has
fourteen active triangles, `q=2` everywhere, and a 7-regular `K`.

Expansion again bounds active point size by four. Eight petals around a
size-four point occupy ten external labels, forcing at least six singleton
external sides and hence `K`-degree at least nine at every root label. With
sizes two and three left, put `t_i` for the number of size-three points through
label `i`, let `F` be the point-clique edges, and set `U=K-E(F)`. Then

```text
d_F(i)=3+t_i,  d_U(i)=4-t_i.
```

For a size-three point `{i,j,k}`, singleton petals and capacity leave only
`(t_i,t_j,t_k)=(2,2,2)` or a permutation of `(2,3,3)`. The latter forces five
distinct full `2`-by-`2` crossings, contributing 20 to a fixed-point sum equal
to 12. If a size-three point remained in the former mode, the intersection
graph of size-three points would be cubic and triangle-free. Incidence bounds
reduce it to `K3,3`; its nine edge labels would inject into only five `t=0`
labels because `L(K3,3)` has no open twins. Thus every active point has size
two.

The 42 point incidences are therefore the 21 edges of a simple cubic
triangle-free graph `F` on fourteen labels. Every valid `K` contains `F` and
every pair of `F`-neighbors of one label. The fixed-point identity makes the
positive-support graph on `E(F)` a 2-factor. Testing support rectangles only
against those mandatory `K`-edges is a relaxation, while the forced active
adjacency graph must obey the SRG common-neighbor upper caps one and two.

An independently decoded GENREG catalog supplies the 110 connected types;
direct order-six and order-eight censuses supply the two disconnected types.
They match the independent 112-record graph6 catalog bijectively. Only four
types survive the mandatory-degree filter, and independently generated and
replayed rejection trees find no support factor satisfying the caps. This
conditionally excludes `n3=42`; it assumes no completed-graph automorphism and
does not resolve Conway-99. The proof, support certificate, and final audit are
in `agents/2026-07-22-wave12-n3-42-proof-a.md`,
`verification/n3-42-equality/`, and
`verification/2026-07-22-wave12-integration-audit.md`.

Wave 13 treats `n3=45`. Exact partitioning of `sum q(T)=30` gives nine raw
active profiles. The inherited no-singleton and degree-three obstructions
leave only

```text
r=14: q-profile (2^12,3^2),
r=15: q-profile (2^15).
```

In the mixed case, active points have size at most three. A size-three point
containing a `q=3` label has no admissible local mode. An ordinary size-three
point can have only mode `222` or `233`; fixed-crossing capacity removes
`233`, while `222` would make the intersection graph cubic and triangle-free.
It reduces to `K3,3`, whose line graph has distinct open neighborhoods, forcing
an impossible injection of nine labels into three. If all points instead have
size two, either special label needs at least five `K`-neighbors although its
capacity is four. Thus the mixed profile is impossible.

For the all-`q=2` order-fifteen profile, flower enumeration removes point sizes
five and four. Let `t_i` count size-three points through label `i`. Exact
crossing and fixed-point capacities leave four local types:

```text
111, 122, 222, 223.
```

Type `223` would induce a one-regular graph on three labels and is impossible.
For type `111`, the six co-point endpoints saturate every root label in `K`;
the remaining labels cannot supply the required fixed support. Hence only
types `122` and `222` remain. A size-two point then has positive crossing
degree four, while a size-three point already consumes eight or twelve units,
so every vertex of the edge-auxiliary graph `H` has degree zero or four. But
`|E(H)|=n3=45`, and the handshake sum `90` is not divisible by four. This
conditionally excludes `n3=45`, forcing `n3>=48` and
`induced_C6_count>=209334`.

Two independent semantic audits reconstruct this argument without assuming a
completed-graph automorphism, connectedness, or transitivity. The separate
active-local SAT scan is not part of the proof and its 17 negative rows remain
`UNSAT_UNVERIFIED`; its initial self-validation bundle failed audit and was
repaired and re-audited without erasing the failure. See
`agents/2026-07-22-wave13-n3-45-proof-a.md`,
`verification/2026-07-22-wave13-n3-45-audit.md`,
`verification/2026-07-22-wave13-n3-45-audit-b.md`, and
`verification/2026-07-22-wave13-computation-repair-audit.md`. The result is a
conditional necessary bound only. Conway-99 and novelty remain `UNKNOWN`.

Wave 14 treats the unresolved equality case `n3=48`. Partitioning
`sum q(T)=32` gives twelve raw active profiles; the inherited minimum
point-clique degree and degree-three obstruction leave

```text
r=14: q-profile (2^10,3^4),
r=15: q-profile (2^13,3^2),
r=16: q-profile (2^16).
```

In the order-fourteen case, local crossing capacity reduces size-three points
to two modes; their intersection graph and incidence budget conflict, and the
all-size-two alternative overfills a special label. In the order-fifteen
case, size-three points cannot meet either special label, while a remaining
special--ordinary size-two point has fixed support sum ten although every
term is divisible by four. Both mixed profiles are therefore excluded.

For `r=16`, expansion and flower obstructions leave only point sizes two and
three. Exact local enumeration gives ten aligned size-three modes; fixed
support eliminates the two modes with no full meeting crossing. A six-edge
crossing is then impossible, so every graph-edge vertex of `H` has degree
zero or four. If `mathcal P` is the active point family and `R` joins point
objects whose actual graph edge has `H`-degree four, then

```text
d_R(P)=|P| in {2,3},
sum_(P in mathcal P)|P|=48,
|E(R)|=24,
```

and every one of the 48 edges of the 6-regular graph `L` has exact twofold
coverage by the full `K2,2` rectangles carried by `R`.

This finite residual is consistent at the active/local/support level. The
archived all-size-two object has point graph `2Q3`, support `6C4`, a simple
4-regular triangle-free `H`, and passes the declared common-neighbor upper
caps. It omits the other 75 original vertices, inactive triangles, degree-14
completion, and the missing SRG equalities, so it is a countermodel only to an
overstrong relaxation claim. A separate computation has raw status
`1 SAT_CANDIDATE`, `7 UNSAT_UNVERIFIED`, `1 BUDGET_UNKNOWN`, and
`2 TIMEOUT_UNKNOWN`; none of its negative rows is proof evidence. The
reduction and independent audits are in
`agents/2026-07-22-wave14-n3-48-proof-a.md`,
`verification/2026-07-22-wave14-n3-48-proof-audit.md`, and
`verification/2026-07-22-wave14-n3-48-computation-audit.md`. Thus Wave 14
does not improve the verified `n3>=48` bound. The equality exclusion, target,
and novelty remain `UNKNOWN` at this checkpoint.

Wave 15 excludes the Wave 14 `n3=48` residual with a global induced-subgraph
obstruction. Let

```text
X = {u in V(G) : S_u is nonempty}.
```

The sixteen active triangle labels have point degree three, so
`sum_u |S_u|=48`. Every nonempty point has size at least two; hence
`|X|<=24`. Each active triangle through `u` supplies its other two vertices as
distinct neighbors of `u` in `X`. Distinct triangles through `u` cannot share
another vertex because every graph edge lies in exactly one triangle. Thus a
point of size at least three already gives six induced neighbors.

If `|S_u|=2`, the Wave 14 support graph has two distinct actual graph-edge
neighbors at `S_u`. Neither is one of the four triangle neighbors. If such a
support edge met `S_u` in an active label, deleting the shared label would
leave one crossing row and at most two columns. The audited two-sided `0/2`
crossing law makes its `H`-degree zero (and in any event below four), whereas
a support edge has `H`-degree four. Therefore the two support neighbors are
new, and every vertex of `G[X]` has induced degree at least six.

The target spectrum is `14^1,3^54,(-4)^44`. For `m=|X|`, decomposing the
characteristic vector of `X` into its all-ones and orthogonal parts gives

```text
2e(X) <= 14m^2/99 + 3(m-m^2/99)
       = 3m + m^2/9.
```

But minimum degree six gives `2e(X)>=6m`, so `m>=27`, contradicting
`m<=24`. A separate exact count of the first two moments of outside degrees
reaches the same contradiction by Cauchy--Schwarz. Consequently `n3=48` is
impossible; the divisibility `3|n3` and Reimbayev identity give

```text
n3 >= 51,
induced_C6_count >= 209337.
```

Two discovery lanes and two independent audits reproduce the result. The
explicit Wave 14 all-size-two object remains a valid countermodel to its
stated active/local/support relaxation, but its lift to the full SRG equations
is refuted. See `agents/2026-07-23-wave15-global-lift.md`,
`agents/2026-07-23-wave15-algebraic.md`,
`verification/2026-07-23-wave15-global-lift-audit.md`, and
`verification/2026-07-23-wave15-algebraic-audit.md`. This is a conditional
necessary bound only; Conway-99 and novelty remain `UNKNOWN`.

Wave 16 applies the same global obstruction directly at `n3=51`, without a
Wave 14 point-size classification. Here

```text
sum_T q(T)=34,
q(T)>=2,
d_K(T)=r-1-3q(T).
```

Exact partitioning gives sixteen raw active profiles. Every active label lies
in three non-singleton linear points, so `d_K>=3`; the independently audited
degree-three obstruction strengthens this to `d_K>=4`. Exactly four profiles
remain:

```text
r=14: q=2^8 3^6,
r=15: q=2^11 3^4,
r=16: q=2^14 3^2,
r=17: q=2^17.
```

For the indexed active original-vertex set

```text
X={u:S_u is nonempty},
sum_{u in X}|S_u|=3r.
```

No active point is a singleton, so `|X|<=floor(3r/2)<=25`. A point of size
at least three already supplies six distinct active-triangle neighbors. For a
size-two point `P={i,j}`, the complete two-sided crossing classification is
endpoint-local:

```text
P and Q meet:                  d_H(uv)=0,
P and Q are disjoint:          d_H(uv) is 0 or 4.
```

The fixed-point sum is `2(q(i)+q(j))`. Thus a `(2,2)` point has exactly two
positive nonmeeting neighbors, a mixed `(2,3)` point is impossible modulo
four, and a `(3,3)` point has exactly three positive nonmeeting neighbors.
All positive terms are distinct actual graph neighbors in `X`, not support
multiplicities. Consequently every vertex of `G[X]` has induced degree at
least six.

The Wave 15 spectral inequality requires every nonempty induced set of
minimum degree six to have order at least 27, contradicting `|X|<=25`.
Therefore `n3=51` is impossible. Divisibility by three and the exact cycle
identity give

```text
n3 >= 54,
induced_C6_count >= 209340.
```

The independent audit explicitly tests that the proof does not assume a
point-size-at-most-three bound, a global `H`-degree `{0,4}` law, or the Wave 14
support-graph identity. A separate computation verifies a seven-branch
active-local archive and one positive relaxation object but is not used in
the exclusion; its one raw UNSAT return has no proof trace. See
`agents/2026-07-23-wave16-n3-51-structural.md` and
`verification/2026-07-23-wave16-n3-51-structural-audit.md`. This remains a
conditional necessary bound; Conway-99 and novelty are `UNKNOWN`.

Wave 17 applies the same framework at `n3=54`, where

```text
sum_T q(T)=36.
```

The exact `d_K>=4` filter leaves six profiles. Five have `r<=17`, hence
`|X|<=25`, while the endpoint-local crossing arithmetic still gives
`delta(G[X])>=6`; the spectral subset bound excludes them. The last profile is

```text
r=18, q=2^18, |X|=27.
```

Equality forces every active point to have size two, `G[X]` to be 6-regular,
and the cut to be equitable with quotient `[[6,8],[3,11]]`. Let `F` be the
simple cubic triangle-free graph on the 18 active labels whose 27 edges are
the active points. The remaining two neighbors of each point form a simple
2-factor `R` on `E(F)`. If `N` is the vertex-edge incidence matrix of `F`,
then

```text
G[X] = line(F) union R,
N A_R N^T = 2 A_L.
```

No nonadjacent pair of `F` has codegree exactly two. Hence each component is
`K3,3` or has girth at least five. Component sizes reduce to `(18)`, `(6,12)`,
or `(6,6,6)`; an exact binary parity argument excludes `3K3,3`. The two
remaining families contain exactly 455 connected cubic girth-at-least-five
graphs of order 18 and two disjoint unions of `K3,3` with a connected such
graph of order 12, according to the official House of Graphs catalogs.

For a fixed `F`, a compatible support variable joins two disjoint `F`-edges
whose endpoint rectangle avoids every forced `K`-pair. Reducing point-degree
two and rectangle-coverage zero-or-two modulo two gives a `180`-row binary
system. Among the 455 connected cases, 443 kernels are trivial. The remaining
12 have nullities `1^4,2^5,4^2,18`; exhaustive enumeration of all 262,204
vectors in those nontrivial kernels finds no vector with integer degree two at
all 27 points. In each mixed case, the nine `K3,3` point-edges force 18 cross
edges and therefore nine internal order-12 edges, but only one or zero such
candidates exist.

An independent implementation fetched and hash-validated both official
catalogs, reconstructed all 457 cases, reproduced every certificate field,
and passed 17 hostile tests. This exact obstruction excludes `n3=54`.
Divisibility by three and the induced-cycle identity give

```text
n3 >= 57,
induced_C6_count >= 209343.
```

The raw SAT scout also returned `UNSAT` on all 457 fixed-`F` cases, but it
produced no checked proof traces and is non-evidentiary. Catalog completeness
and one representative per isomorphism class remain external official
premises. See `agents/2026-07-23-wave17-n3-54-structural.md`,
`verification/2026-07-23-wave17-n3-54-structural-audit.md`,
`agents/2026-07-23-wave17-n3-54-census.md`, and
`verification/2026-07-23-wave17-n3-54-census-audit.md`. This is a conditional
necessary bound, not a target resolution or novelty determination; both
Conway-99 and novelty remain `UNKNOWN`.

Wave 18 analyzes `n3=57` directly, without importing the Wave 17 exclusion.
Here

```text
sum_T q(T)=38.
```

The exact `d_K>=4` filter gives nine profiles with `14<=r<=19`. Endpoint-local
crossing arithmetic again yields `delta(G[X])>=6`, while non-singleton indexed
points give `|X|<=floor(3r/2)`. The spectral subset bound requires `|X|>=27`,
so every profile with `r<=17` is impossible.

For `r=18`, equality forces 27 size-two points and exact 6-regularity of
`G[X]`. The surviving profiles are `q=2^16 3^2` and `q=2^17 4`. The former
would separate the two odd labels from the sixteen even labels in a simple
cubic point graph, which cannot give either odd label degree three. In the
latter, every point incident with the unique `q=4` label is of type `(2,4)`
and has induced degree at least seven, contradicting 6-regularity.

For `r=19`, the only profile is `q=2^19` and `27<=|X|<=28`. At 27 vertices,
the exact point-size profiles are `2^26 5`, `2^25 3 4`, and `2^24 3^3`;
meeting-neighbor counts or the fixed-point sum exclude all three. At 28
vertices, the sole profile `2^27 3` forces the size-three point to have at
least nine active neighbors. The even degree sum is therefore at least 172,
whereas

```text
2e(G[X]) <= 3(28)+28^2/9 = 1540/9
```

permits at most 170. Thus conditional `n3=57` is impossible. A materially
independent checker reconstructs the profiles, overlap-deleted crossings,
point-size partitions, and exact rational bounds, passing 14 tests and
detecting 24 hostile mutations. Combining this exclusion with Wave 17 yields

```text
n3 >= 60,
induced_C6_count >= 209346.
```

See `agents/2026-07-23-wave18-n3-57-structural.md` and
`verification/2026-07-23-wave18-n3-57-structural-audit.md`. This is a
conditional necessary bound over authenticated audited framework premises,
not a target resolution, formal-kernel proof, or novelty determination;
Conway-99 and novelty remain `UNKNOWN`.

The Wave 18 literature lanes independently checked the exact endpoint numbers,
the standard Rayleigh ingredient, current sources, and two close 2022/2026
status leads. No exact published `n3=57` exclusion, `n3>=60`, or `209346`
endpoint was found; those focused nonhits do not establish novelty. Baker's May
2026 conference abstract describes a related induced-subgraph paradigm but
states no exact theorem or proof. Ishihara's 2022 Theorem 28 claims
nonexistence, but its equation (88) assumes every second-layer residual vertex
has two first-layer residual neighbors. Root-label reconstruction instead gives
degrees `1^20,2^51` and the corrected double count

```text
10(10)+11(2)=122=2(71)-20,
```

not 142. Thus that displayed proof is `REFUTED`, while both target outcomes
remain `UNKNOWN`. See `agents/2026-07-23-wave18-status-search.md` and
`verification/2026-07-23-wave18-status-audit.md`.

Wave 19 treats `n3=60`, so `sum_T q(T)=40`. The `m=27` equality profile
forces 21 size-two and six size-three indexed points. The positive-meeting
graph on the six size-three points is either a triangular prism or `K3,3`;
exact twofold witness multiplicity excludes both after making the grid-label
injectivity step explicit.

At `m=30`, every active point has size two. Writing the 30 points as the edges
of a triangle-free cubic graph `F` on 20 active labels gives

```text
D = L(F) union R union Z,
N A_R N^T = 2 A_L,
|Z| <= 3,
B = 12I - D - D^2 + 2J = C C^T.
```

Here each local `L` row is a remote induced six-cycle, the choices are
symmetric, `R` is the resulting point 2-factor, and `Z` contains the remaining
allowed point edges. Exact enumeration of all official connected cubic
order-20 records and all disconnected component types leaves only two Petersen
components. Its 120 `L/R` models form one orbit with stabilizer 240. Exhausting
all `1+165+C(165,2)+C(165,3)=748826` labeled `Z` placements leaves 16 PSD Gram
orbits. Fifteen coefficient systems are inconsistent. For the sole residual

```text
Z = {(0,23),(1,22),(2,17)},
```

an integer Farkas functional has target `-6` and nonnegative score on every one
of the 232 possible nonzero binary outside columns. Hence no nonnegative column
multiplicities can realize `B`, excluding conditional `n3=60` and yielding

```text
n3 >= 63,
induced_C6_count >= 209349.
```

A materially independent verifier authenticates the canonical-LF release,
reconstructs every connected and disconnected disposition, re-enumerates all
`Z` placements and Gram systems, checks hostile mutations, and replays the
submitted checker. See `agents/2026-07-23-wave19-alternate-frontier.md` and
`verification/n3-60-closure/2026-07-23T161951Z-final-audit.md`. Official House
of Graphs catalog completeness and nonisomorphism are explicit external
premises. This remains a conditional necessary bound; Conway-99 and novelty
remain `UNKNOWN`.

Wave 20 uses only the target parameters and the full set of 231 graph
triangles. Let `N` be the `99`-by-`231` vertex-triangle incidence matrix and
let `Gamma` join intersecting triangles. Then

```text
N N^T = A + 7I,
N^T N = 3I + Gamma,
spec(Gamma) = 18^1, 7^54, 0^44, (-3)^132.
```

For

```text
C = Gamma^2 - 5Gamma - 18I,
```

the diagonal and intersecting entries vanish, while a disjoint pair entry is
its number `r` of cross-edges, in `{0,1,2,3}`. If `a_r(T)` counts disjoint
triangles with `r` cross-edges to a fixed triangle and
`q(T)=12-a_3(T)`, exact zeroth, first, and second moments give

```text
(a0,a1,a2,a3) = (20+q, 180-3q, 3q, 12-q),
2n3 = 3 sum_T q(T),
3 divides n3.
```

The orthogonal projector onto the 44-dimensional zero eigenspace of `Gamma`
is

```text
E = (3I + J - Gamma - C)/21.
```

Thus the integral matrix `M=21E` is positive semidefinite, has rank 44,
satisfies `M^2=21M`, has diagonal 4, and has off-diagonal entries
`0,1,-1,-2`. Put

```text
W = M o M,
A4 = M W M.
```

Schur positivity makes `W` and `A4` positive semidefinite. Since
`W=M (mod 2)`, one has `A4=M (mod 2)`, and every row is nonzero. Writing
`D=(W-M)/2`, the matrix `D mod 2` is symmetric with zero diagonal, so its
quadratic form is alternating. It follows that every diagonal of `A4` is
divisible by four. A zero diagonal in a positive-semidefinite matrix would
force the corresponding row to vanish, so all 231 diagonals are at least
four. Finally,

```text
tr(A4) = 84(n3-693) >= 4*231 = 924.
```

Hence `n3-693>=11`; divisibility by three forces

```text
n3 >= 705,
induced_C6_count >= 209991.
```

A blind verifier independently reconstructed the combinatorial entries,
projector scaling, Schur trace, mod-two and mod-four arguments, and endpoint;
its 16 tests and the submitted 18 tests pass with byte-identical regenerated
JSON. See `agents/2026-07-23-wave20-global-schur.md` and
`verification/2026-07-23-wave20-global-schur-audit.md`. The frozen
`failed-routes.md` introduction retains the intermediate endpoint 699, while
the later section and every operative artifact use 705; the correction and
failed harness invocations are retained in `orchestrator-notes.md`.

An independent status auditor froze the claim without opening the proof,
verified the cited triangle-graph spectrum and induced-six-cycle identity, and
found no accepted target resolution or exact published `705/209991` endpoint
through 2026-07-23. Generic Schur/Krein positivity is prior art, and
non-discovery cannot certify novelty. The argument is a conditional necessary
bound rather than a construction, nonexistence proof, or formal-kernel proof;
Conway-99 and novelty remain `UNKNOWN`.

## First surviving endpoint refinements (`VERIFIED_INCONCLUSIVE`)

At the first surviving value `n3=705`, the integral Schur lift from Wave 20

```text
W = M o M,
A4 = M W M
```

has trace 1,008. Representing `M` as the Gram matrix of norm-four vectors in
dimension 44 and contracting the associated quadratic tensors gives, for
every triangle `T`,

```text
A4[T,T] >= (99/43)*(q(T)-2)^2.
```

Every diagonal is already known to be a positive multiple of four. Since the
other 230 diagonals contribute at least 920, a selected diagonal is at most
88, and therefore

```text
q(T) <= 8.
```

The exact trace-square arithmetic also yields

```text
tr(A4^2) = 441*t,
t = 4 (mod 8),
t >= 60,
tr(A4^2) >= 26,460.
```

These restrictions do not close the endpoint. Keeping `q=1`, the exact scalar
relaxation has 22,113 aggregate profiles; one survivor has 223 rows with
`q=2` and eight with `q=3`. A separate rank-44 two-moment spectrum also
survives. Neither object is asserted to be a compatible matrix or graph.

The parallel lattice reduction puts

```text
U = im(M),
L = U intersect Z^231,
h = [L : 21L*].
```

The independently audited identities include

```text
E Z^231 = L*,
M Z^231 = 21L*,
h = 21^44/det(L).
```

The lattice `L` is even with minimum at least four. On `L`, the operator
`B=A4/21` is integral, self-adjoint, positive definite, and congruent to the
identity modulo two. For an integral basis matrix `X` of `L`, the even
positive-definite Gram matrix `Q=X^T W X` satisfies

```text
det(B) = h*det(Q).
```

At `n3=705`, `tr(B)=48` and exact AM--GM gives `det(B)<=45`. The discovery
submission obtained the weaker necessary list `{1,3,7,9}`. The verifier
separately proved that an even integral Gram matrix of rank 44 and odd
determinant has determinant one modulo four. Together with the standard
rank-44 even-unimodular signature obstruction, this sharpens the full endpoint
condition to

```text
n3=705  ==>  h in {1,9}.
```

At the Wave 21 checkpoint the index `h` was not determined, so those lanes
gave no improvement over `n3>=705`. Wave 23 later excludes the whole endpoint
by a stronger argument. Full derivations and exact replays are in
`agents/2026-07-23-wave21-local-diagonal.md`,
`verification/wave21-local-diagonal/2026-07-23T185252Z-audit.md`,
`agents/2026-07-23-wave21-lattice-extension.md`, and
`verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md`.

## Six-/seven-vertex affine count envelope (`VERIFIED_INCONCLUSIVE`)

The Wave 21 lane independently enumerates every locally admissible graph under
the pairwise conditions inherited from `srg(n,k,1,2)`. Canonicalization under
all vertex permutations gives exactly

```text
order 4:                  9 classes
order 5:                 21 classes
order 6:                 62 classes
order 7, Hamiltonian:    19 classes
```

Reconstructing every vertex-deletion deck uniquely aligns these classes with
the indices in Reimbayev's six-vertex and Hamiltonian seven-vertex tables.
The aligned `N3` is exactly two vertex-disjoint triangles joined by two
independent cross-edges, so the source parameter `n3` is the project parameter.
No automorphism of a putative target is assumed.

The printed five-to-six deletion equations in arXiv:2508.03377v2 have one
defect. Sixty-one `N_j` columns have coefficient sum six, but the `N23` column
has sum five. Substitution of the source's own affine formulas gives

```text
20 equations:                 residual 0
printed m7(n-5) equation:     residual n23
n23 at the Conway parameters: 1,496,880 + 4*n3
```

Trying the missing deletion card in each of the 21 possible `M_i` rows shows
that only `M7` yields an actual locally admissible six-vertex deck. The narrow
correction is therefore

```text
printed m7(n-5) right-hand side + n23.
```

The raw equation is retained as `REFUTED_AS_PRINTED`; the correction is a
separately named and independently checked path. After that correction all 62
deletion columns sum to six, all source indices align bijectively, and all 21
deck identities have zero residual.

At `n=99,k=14`, exact rational specialization of all 62 six-vertex formulas
gives simultaneous integrality and nonnegativity exactly when

```text
n3 = 0 (mod 3),
0 <= n3 <= 4158.
```

Writing the free Hamiltonian seven-vertex count as `h11`, all 19 displayed
counts are simultaneously integral and nonnegative exactly when

```text
h11 = 0 (mod 4),
ceil_to_multiple_of_4(2*n3) <= h11 <= 4*n3.
```

The universal choice `h11=4*n3` works for every six-vertex-feasible value.
Consequently, the then-current Wave 20 bound left

```text
n3 = 705,708,...,4158:        1,152 values
n3=705, h11=1412,1416,...,2820: 353 values
```

This is a complete exhaustion of the encoded formulas, not of global graphs.
The seven-vertex source enumerates Hamiltonian types rather than all induced
seven-vertex types, and a feasible count vector is not an adjacency matrix.
The discovery suite passes 16 tests, the separately written verifier passes
19, and all three exact JSON outputs replay byte-identically. See
`agents/2026-07-23-wave21-six-vertex-lp.md`,
`verification/wave21-six-vertex-lp/2026-07-23T174137Z-audit.md`, and
`verification/wave21-six-vertex-lp/2026-07-23T175223Z-orchestrator-replay.md`.
The source-first status record
`verification/wave21-six-vertex-lp/status/2026-07-23T182843Z-source-status-audit.md`
confirms that official v1 and the still-current v2 both omit the term and
records that no formal or corrected publication was located. That bounded
non-discovery is not a novelty certificate. The count result supplies no
stronger bound or target resolution.

## Complete aggregate order-seven deck (`VERIFIED_INCONCLUSIVE`)

Wave 22 enumerates all `2^21` labeled graphs on seven vertices, retains the
394,020 that satisfy the inherited local common-neighbor upper bounds, and
canonicalizes them into 208 isomorphism classes. Deleting every possible
vertex produces the complete integer matrix

```text
D: 62 six-vertex types x 208 seven-vertex types.
```

Its exact row ranks over `F_2,F_3,F_5,F_7,F_11` are respectively
`48,57,61,61,62`. At the historical endpoint
`n3=705,h11=2820`, a frozen nonnegative integer vector has total
`binom(99,7)`, support size 105, satisfies all 62 equations

```text
D*x = 93*(n1,...,n62),
```

and assigns all 19 pinned Hamiltonian classes their displayed published
counts. The discovery and independent implementations separately reconstruct
the complete order-six/order-seven censuses, deletion cards, Hamiltonian
classes, source alignment, and exact arithmetic.

This witness is not a graph: it does not impose consistency between
overlapping seven-subsets and supplies no adjacency matrix. Its role is to
show that the complete aggregate deletion relaxation alone does not exclude
the old endpoint. See
`agents/2026-07-23-wave22-full-seven-deck.md` and
`verification/wave22-full-seven-deck/2026-07-23T191133Z-audit.md`.

## Projector-index endpoint exclusion (`VERIFIED`)

Wave 23 returns to the rank-44 projector lattice. At `n3=705`, write the
integral positive self-adjoint endomorphism as

```text
B = I+2C,
rank(B)=44,
tr(B)=48,
tr(C)=2.
```

For an integral matrix, `tr(C^2)=tr(C) (mod 2)`. Positive-form
self-adjointness makes the eigenvalues of `C` real, so `tr(C^2)` is a
positive even integer. Hence

```text
tr(B^2) >= 60.
```

The 44 positive eigenvalues of `B` therefore have sum 48 and square sum at
least 60. A complete compactness/KKT argument puts any determinant maximizer
on square sum 60 with exactly two eigenvalue values. The independent checker
uses exact dyadic radical intervals for all 38 positive multiplicities and
proves

```text
det(B) < 13.
```

Since `det(B)` is a positive integer congruent to one modulo four,
`det(B)` is in `{1,5,9}`. The verified factorization
`det(B)=h det(Q)`, the rank-44 even-Gram congruence, and the
even-unimodular signature obstruction leave only `h=1`; but
`h=1` would make `G/21` an even positive-definite unimodular form of
signature 44, which is impossible. Thus the endpoint is excluded:

```text
n3 != 705,
n3 >= 708,
induced_C6_count >= 209994.
```

A second proof lane, isolated from this derivation, obtains the looser but
sufficient exact cap `det(B)<43` directly from Newton and Maclaurin:

```text
e2 <= 1122,
det(B)^(1/22) <= 1122/binom(44,2) = 51/43,
51^22 < 43^23.
```

Together with the scaled-dual determinant congruence this also leaves no
index. A separately written verifier reconstructs the proof and passes 17
hostile tests. Its first audit also caught an ancillary discovery-ledger
error: `(9,3,27)` violates the retained `det(B)=1 (mod 4)` condition. The bad
control is preserved and refuted, `(9,1,9)` is the corrected
single-relaxation witness, and a second frozen addendum verifies that the
mathematical result is unchanged.

The primary proof and blind audit are
`agents/2026-07-23-wave23-index-pranks.md` and
`verification/wave23-index-pranks/2026-07-23T192952Z-audit.md`; the isolated
cross-check, audit, and correction record are
`agents/2026-07-23-wave23-endpoint-crosscheck.md`,
`verification/wave23-endpoint-crosscheck/2026-07-23T195158Z-audit.md`, and
`verification/wave23-endpoint-crosscheck/2026-07-23T200645Z-correction-audit.md`.

Both arguments are conditional necessary bounds. Neither constructs a graph
or proves that no target graph exists. A source-separated audit of 24 frozen
query and citation paths found that its inspected current sources still treat
the target as open and located neither the exact `708/209994` endpoint nor
the complete method. This is bounded non-discovery, not proof of openness or
novelty; both target existence and novelty remain `UNKNOWN`. See
`verification/wave23-literature-audit/2026-07-23-wave23-literature-audit.md`.

## Orbit-refined order-seven extensions (`VERIFIED_INCONCLUSIVE`)

A parallel Wave 23 lane strengthens the aggregate seven-vertex deck by
distinguishing every vertex and pair orbit inside each six-vertex card. Over
all 208 locally admissible seven-vertex classes, the exact integer system has

```text
deletion rows:               62
vertex-orbit rows:          207
edge-pair-orbit rows:       180
nonedge-pair-orbit rows:    263
total:                      712
```

The independent verifier checks every canonicalizing isomorphism and confirms
that these coefficients merely partition distinguished vertices and pairs;
they impose no automorphism on the putative 99-vertex target. A separately
rebuilt lower-order gate forces the counts through order five, and the source
order-six vector passes all 171 orbit-refined `5->6` rows.

At the now-excluded historical endpoint `n3=705`, the matrix `A` has rational
rank 207. A frozen nonzero integer vector `delta` spans its checked kernel,
and adjoining only the pinned `H11` coordinate raises the rank to 208. The
exact family

```text
x(z) = base + (z-353) delta,
z = 353,...,705,
h11 = 4z
```

satisfies every row. Its endpoint minimum counts are two and zero, so every
coordinate remains nonnegative throughout the interval. The other 18
Hamiltonian formulas are post-hoc comparisons, not solver inputs, and all
match.

Thus this complete encoded necessary relaxation is feasible for all 353
allowed values. It does not impose overlap consistency, provide an adjacency
matrix, or contradict the stronger lattice exclusion. The current bound
remains `n3>=708`, and target existence remains `UNKNOWN`. See
`agents/2026-07-23-wave23-weighted-extensions.md` and
`verification/wave23-weighted-extensions/2026-07-23T202156Z-audit.md`.

## Next-endpoint lattice boundary (`VERIFIED_INCONCLUSIVE`)

At the first surviving endpoint `n3=708`, the same rank-44 endomorphism has

```text
B = I+2C,
tr(B)=60,
tr(C)=8.
```

Because `C` is integral and self-adjoint for a positive Gram form, its
nonzero eigenvalues are real and their product is a nonzero integer. If their
number is `r`, AM--GM and Cauchy give

```text
tr(C^2) >= r,
tr(C^2) >= 64/r,
tr(C^2) >= 8,
tr(B^2) >= 108.
```

For every real `x>-1/2`, `x!=0`, an exact calculus argument proves

```text
log(1+2x)
  <= x log(3) - (log(3)-2/3) log|x|.
```

Summing over the nonzero eigenvalues and using their integral
pseudodeterminant yields

```text
det(B) <= 3^8 = 6561.
```

The factorization `det(B)=h det(Q)`, the floor `det(Q)>=5`, and the
scaled-dual conditions reduce the endpoint to exactly

```text
h in {9,21,49,81,189,441,729,1029}.
```

The harmonic local identities separately imply `q(T)<=11` and permit at most
one triangle with `q(T)=11`. A scalar profile with 221 values equal to two
and ten equal to three still survives.

Most importantly, the remaining abstract lattice conditions are genuinely
feasible. With `E8` the even unimodular rank-eight Gram matrix and
`A2=[[2,-1],[-1,2]]`, define

```text
S = E8^5 direct_sum A2^2,
Q = (E8^-1)^5 direct_sum A2^2,
G = 21 S^-1,
B = S Q.
```

Exact 44-by-44 arithmetic gives

```text
det(S)=h=9,
det(Q)=9,
det(B)=81,
tr(B)=60,
S G=21I,
G B=21Q,
B=I (mod 2),
minimum(G)>=14.
```

This is a hostile control against overclaiming the lattice route. It is not a
primitive sublattice of `Z^231`, a 231-row projector-frame realization, a
matrix with proved `W=M o M` origin, or a graph. Thus `n3=708` remains open
inside the project, and a further contradiction must use one of those omitted
structural bridges. See
`agents/2026-07-23-wave24-n3-708-index-boundary.md` and
`verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md`.

A proof-separated source audit found no exact match for `n3=708`,
`det(B)<=3^8`, the ordered eight-value index list, or the complete logarithmic
argument in its frozen searches. It records Knill's general
pseudodeterminant work and Bacher--Venkov's rational-idempotent lattice
construction as conceptual prior art, not exact target matches. This is
bounded non-discovery; novelty and priority remain `UNKNOWN`. See
`verification/wave24-literature-audit/2026-07-23-wave24-literature-audit.md`.

The combined detached Waves 21-24 publication replay is
`verification/2026-07-23-wave24-clean-clone.md`. It records 278 passing tests,
15 byte-identical regenerated files, seven exact manifests, metadata and
unpublished-history privacy checks, a clean tracked tree, and Git object
integrity at integration commit
`4111abeea284d218af31cfb7d37ec8a697400998`.

## Strict first-endpoint arithmetic (`VERIFIED_INCONCLUSIVE`)

Wave 25 excludes the only equality case in the Wave 24 trace-square bound.
If `tr(C^2)=8`, equality in the rank and Cauchy estimates gives

```text
C^2=C,
spectrum(C)={1^8,0^36}.
```

Because `C` is integral, its image and kernel split `Z^44` in a unimodular
adapted basis. Self-adjointness for the positive Gram matrix `G` makes that
split orthogonal. On the hypothetical equality case's rank-36 kernel block,

```text
Q0=G0/21,
S0=21G0^(-1)=Q0^(-1).
```

Both `Q0` and `S0` are even integral positive-definite forms, so `Q0` would
be even unimodular of rank 36. This contradicts the standard theorem that
the signature of an even unimodular lattice is divisible by eight. The
restriction to this equality-case kernel block is essential: globally
`SQ=B`, not `I`, and the identity `S=Q^(-1)` is false.

Trace parity and the excluded equality case now give

```text
tr(C^2) >= 10,
tr(B^2) >= 116,
det(B) < 6561.
```

The congruence `det(B)=1 (mod 4)` first gives `det(B)<=6557`. Exhausting the
323 exact factor pairs allowed by `det(B)=h det(Q)`, the scaled-dual index
conditions, and `det(Q)=1 (mod 4)` sharpens the combined necessary cap to

```text
det(B) <= 6525,
```

uniquely maximized at `(h,det(Q))=(9,725)`. The surviving index set remains

```text
{9,21,49,81,189,441,729,1029}.
```

This stricter arithmetic still does not exclude the endpoint. The exact
Wave 24 `E8^5 direct_sum A2^2` package has `h=9`, `det(B)=81`, and
`tr(C^2)=32`, so it survives all Wave 25 arithmetic. Wave 26 below later
excludes its required projector-frame and Schur-square origins while
preserving the abstract matrices. Thus the project bound remains `n3>=708`,
while Conway-99 existence remains `UNKNOWN`. See
`agents/2026-07-23-wave25-n3-708-strictness.md` and
`verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md`.

The proof-separated Wave 25 source audit froze 30 queries before proof
inspection and inspected ten primary or authoritative sources. It found no
exact match for this Conway-99 synthesis, while recording established prior
art for rational-idempotent lattices, rational orthogonal graph lattices, and
the even-unimodular rank theorem. This is bounded non-discovery only; novelty
and priority remain `UNKNOWN`. See
`verification/wave25-literature-audit/2026-07-23-wave25-literature-audit.md`.

The detached Wave 25 publication replay is
`verification/2026-07-23-wave25-clean-clone.md`. It records 39 passing tests,
two byte-identical regenerated JSON files, two exact manifests, 129 verified
status path/hash pairs, scoped link and line-ending checks, zero exact-blob
privacy findings in the release tree and the four-commit unpublished range,
a clean tracked tree, and Git object integrity at integration commit
`156756d4ef98dc7233e29a7f8c9feeb143548197`.

## Explicit `A2` survivor-origin obstruction (`VERIFIED_INCONCLUSIVE`)

Wave 26 uses the realization data omitted by the Wave 24 hostile control.
Suppose the scaled-dual form `S` of an actual 231-row projector frame has an
orthogonal `A2` summand. In a basis displaying that summand,

```text
M=Y S Y^T,
Y^T Y=21 S^(-1),
M_ii=4,
M_ij in {0,1,-1,-2}.
```

The `A2` block of the second identity has energy 42. Since `A2` has six
oriented roots of norm two and no vector of norm four, exactly 21 rows meet
that block in a root. Rows sharing one oriented root have norm-two residuals;
the off-diagonal alphabet and positivity give a fibre cap of three. The total
capacity is therefore only

```text
6*3=18<21.
```

The independent frame verifier reconstructs the contragredient basis change,
the exact root enumeration, the opposite-root edge case, and active `+2` and
missing-frame hostile controls. See
`agents/2026-07-23-wave26-a2-frame-obstruction.md` and
`verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md`.

A separate cubic/Schur argument does not use the off-diagonal fibre cap. The
same frame block places seven rows on each of the three unoriented root lines,
so their three signed imbalances are odd. The exact cubic Gram form has
eigenvalues `6,9,9`, giving

```text
tr(A2 Q_AA)>=18.
```

Ordered-tensor orthogonality shows that complement and mixed blocks cannot
decrease this compression. For either displayed `A2` block of the explicit
Wave 24 package,

```text
Q_AA=A2,
tr(A2 Q_AA)=tr(A2^2)=10,
```

which is impossible. The independent verifier checks ordered and normalized
symmetric-tensor conventions, cross blocks, basis covariance, row
orientation, and a dropped-frame control. It also proves that `M1=0` is
unnecessary for the numeric floor. See
`agents/2026-07-23-wave26-a2-cubic-obstruction.md` and
`verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md`.

These arguments refute the projector-frame and full Schur-square origins of
one explicit abstract survivor. They do not refute its coordinate-lattice
identities, classify all even `h=9` forms, exclude `n3=708`, or resolve
Conway-99. The proposed global cap `det(B)<=3645` remains `UNKNOWN`.

The proof-separated Wave 26 source audit attempted 28 frozen queries and
inspected 15 primary or authoritative sources. General tight-frame,
lattice-eutaxy, spherical-design, SRG-embedding, and Hadamard-Gram machinery
is established prior art, while generic `A2` root data is compatible with
tightness and strong eutaxy. No direct or near-direct match for the
parameter-specific 231-row exclusion was found. This is bounded
non-discovery only; novelty and priority remain `UNKNOWN`. See
`verification/wave26-literature-audit/audit-report.md`.

The detached Wave 26 publication replay is
`verification/2026-07-23-wave26-clean-clone.md`. It records 65 passing tests,
four byte-identical regenerated JSON files, three exact manifests, 151
verified status path/hash pairs, link and line-ending checks, zero exact-blob
privacy findings in the integration tree and three-commit unpublished range,
a clean tracked tree, and Git object integrity at integration commit
`4f1f3be35e712789dcba10fda5ec8d2bc569bc17`.

## A2-summand-free control and orthogonal ADE screen (`VERIFIED_INCONCLUSIVE`)

Wave 27 first supplies a different exact hostile control after Wave 26
excluded the old Wave 24 package's required projector/Schur origins:

```text
S = E8^4 orthogonal_sum E6^2,
Q = (E8^(-1))^4 orthogonal_sum Q6^2,
G = 21 S^(-1),
B = S Q,
C = (B-I)/2.
```

The full integral package satisfies

```text
rank(S)=44,
det(S)=det(Q)=9,
det(B)=81,
tr(B)=60,
tr(C)=8,
tr(C^2)=32,
B=I (mod 2),
G B=21Q.
```

Complete exact root enumeration gives component sizes

```text
240,240,240,240,72,72.
```

An orthogonal `A2` direct summand would contribute a complete connected
six-root component, so none is present, even after an integral basis change.
This is a direct-summand statement only. Each `E6` component contains
embedded `A2` root subsystems, and the positive control deliberately retains
one so the two notions cannot be conflated. The package remains an abstract
arithmetic/lattice candidate: it supplies no 231-row frame, projector,
Schur-square tensor, or graph. See the
[construction report](agents/2026-07-23-wave27-a2free-construction.md) and
[independent audit](verification/wave27-a2free-construction/2026-07-24T001657Z-audit.md).

A separate local optimization is unrestricted within its stated algebraic
class. For the frozen `E6` Cartan form,

```text
Q symmetric, even integral, positive definite
E6 Q=I (mod 2)
  implies
tr(E6 Q)>=14.
```

The displayed `Q6` attains 14. This algebraic minimum is not the
projector-frame cubic minimum. Its verifier records one nonfatal prose
omission: the discovery report needs
`tr(C^2)=tr(C) (mod 2)` when passing from the excluded value two to the next
admissible trace-square value. The theorem and equality witness are
unchanged. See the
[trace report](agents/2026-07-23-wave27-h9-classification.md) and
[independent audit](verification/wave27-h9-classification/2026-07-24T002029Z-audit.md).

The full frame/Schur origin supplies more structure. For an orthogonal
integral summand `R`, the projected rows obey

```text
sum_i z_i z_i^T=21R^(-1),
sum_i z_i=0.
```

Repeated coordinates of the symmetric cubic tensor consequently lie in an
explicit affine parity lattice. Exact rational affine-CVP enumeration gives
empty closed balls through energy 18 for `E6` and through energy 60 for
`A6`. The zero-sum identity makes the actual cubic energy divisible by six,
so the safe floors are

```text
orthogonal E6 cubic energy >=24,
orthogonal A6 cubic energy >=66.
```

The complementary positive compression has trace at least its rank. Hence a
rank-six component has local trace at most `60-38=22`, contradicting the
`E6` floor, while the `A6` floor already exceeds the full trace 60. Arbitrary
cross-block entries in `Q` are allowed. These theorems require an orthogonal
summand; an embedded nonorthogonal root subsystem is outside their scope.
In particular, the algebraic trace-14 `E6` block is a valid hostile control
for the weaker arithmetic problem and is rejected only after the cubic
origin is imposed.

The frozen core ADE census first tests the necessary integrality of
`21R^(-1)`. Among all irreducible simply-laced Cartan forms through rank 44,
only

```text
A2, A6, A20, E6, E8
```

pass. The Wave 26 `A2` theorem and the Wave 27 `A6`/`E6` tensor theorems
leave exactly

```text
h=21, A20 orthogonal_sum E8^3
```

among the 17 full rank-44 ADE decompositions. This was the sole survivor of
the frozen **core** screen, not a claimed realization.

A later, separately frozen orchestrator addendum factors the path Cartan
matrix as

```text
A_n=e_1e_1^T+e_ne_n^T
    +sum_(i=1)^(n-1)(e_i-e_(i+1))(e_i-e_(i+1))^T.
```

For every even integral positive-definite `Q`,

```text
tr(A_n Q)>=2(n+1).
```

At `n=20`, the local floor 42 plus the rank-24 complement floor 24 gives
`66>60`, excluding an orthogonal `A20` summand. Thus the core
`A20 orthogonal_sum E8^3` survivor is removed only by this later addendum.
The independent audit preserves that chronology and verifies both packages
separately. See the
[core tensor report](agents/2026-07-23-wave27-general-root-tensor.md),
[later A20 addendum](agents/2026-07-24-wave27-a20-trace-addendum.md), and
[independent combined audit](verification/wave27-general-root-tensor/2026-07-24T010548Z-audit.md).

Combining the component results gives the conditional statement

```text
full n3=708 projector/Schur endpoint identities
and S is a full orthogonal ADE root lattice
  implies
no n3=708 endpoint package.
```

This does not classify general even rank-44 scaled-dual lattices. Such a
lattice may be glued, non-root, or otherwise not an orthogonal ADE sum, so
the endpoint and all unrestricted `h` rows remain `UNKNOWN`. The project
bound is still `n3>=708`; Conway-99 existence remains `UNKNOWN`.

The proof-separated Wave 27 literature audit executed 56 frozen or separately
frozen service-query pairs and inspected 303 records through 2026-07-24. It
found standard component tables and `A_n` Cartan data as conceptual precedent,
but no direct match for the trace-14 optimization, scale-21 cubic
obstructions, A20 use, or exact rank-44 comparison. One frozen interpretation
defect was corrected in a separately retained protocol correction, and failed
zbMATH requests remain failures rather than zero-result evidence. Novelty and
priority remain `UNKNOWN`. See the
[Wave 27 literature audit](verification/wave27-literature-audit/audit.md).
The
[Wave 27 correction ledger](verification/2026-07-24-wave27-orchestrator-corrections.md)
preserves the E6 exposition bridge, the literature-protocol correction, and
the later A20-addendum chronology without rewriting their frozen inputs.

The detached
[Wave 27 clean-source replay](verification/2026-07-24-wave27-clean-clone.md)
records 116 passing tests, seven byte-identical JSON regenerations, all 51
entries of six manifests, 211 status path/hash pairs, scoped link and
line-ending gates, exact-blob privacy checks of the release tree and
seven-commit unpublished range, clean status, and strict Git object
verification at integration commit
`4a2f65d20f8fa403a3a245815799070cf126173f`.

## Wave 28 general-lattice controls

At `n3=708`, write

```text
G=X^T X,
S=21G^(-1),
M=XSX^T,
W=M o M,
Q=X^T W X,
B=SQ=I+2C.
```

Wave 28 keeps this full endpoint package frozen while dropping every
root-lattice, orthogonal-decomposition, strong-modularity, and automorphism
assumption from its generic reductions.

For

```text
h=det(S) in {9,21,49,81,189,441,729,1029},
```

the discriminant group has elementary 3- and 7-primary parts and exact level
`3`, `7`, or `21`. The exact Milgram calculation leaves twelve formal finite
quadratic modules. A primitive root has divisibility one but need not split:
its orthogonal complement has determinant `2h`, and the primitive
root-closure is governed by root-preserving isotropic glue against a rootless
complement. The exact projector moments leave 46 one-root coordinate
patterns, reduced to 32 by the cubic-energy bound. These are necessary count
patterns, not frame realizations.

The frozen discovery sentence excluding cyclic order-21 invariant factors is
false. The correct statement is:

```text
no p-primary cyclic factor has order p^2 or higher;
invariant factors divide 21 and may have order 21.
```

The independent
[glue audit](verification/wave28-glue-discriminant/audit.md) verifies the
corrected primary decomposition and every downstream finite calculation. It
excludes no determinant row.

The theta lane proves the exact generic level, character, Poisson/Weil, Sturm,
and modularity-veto statements and constructs the bare control

```text
S0=K12 orthogonal_sum LAMBDA(F),
det(S0)=729,
min(S0)=4,
r_S0(2)=0,
r_S0(4)=147636,
min(21S0^(-1))=28.
```

The rooted lattice `E6^6 orthogonal_sum E8` has the same finite discriminant
quadratic module and Weil representation but 672 roots. Hence these bare
lattice/theta data do not determine the root coefficient. The complete
fraction-free enumeration of the 32-dimensional component visits 15,053,011
closed-ellipsoid nodes. See the
[theta audit](verification/wave28-theta-modular/audit.md). Neither comparison
object includes the marked 231-vector frame.

Finally, a simultaneous two-neighbor transformation of the Wave 27 paired
forms produces two exact abstract controls. The preferred control has 568
roots of rank 43 and components

```text
A1^4 orthogonal_sum A5 orthogonal_sum D5 orthogonal_sum D8
  orthogonal_sum E7^3,
```

while the retained initial control has 568 roots of full rank 44. Their
complete matrices, roots, closures, and glue indices pass independent exact
reconstruction. See the
[neighbor audit](verification/wave28-simultaneous-neighbor/2026-07-24-wave28-simultaneous-neighbor-audit.md).

These controls establish sharp boundary information:

```text
bare scaled-dual lattice data do not force roots;
general neighbors need not retain an orthogonal ADE decomposition;
full projector/Schur endpoint compatibility remains UNKNOWN.
```

No Wave 28 object supplies all of `X,M,W,Q,B`. Thus no `h` row, `n3=708`,
or Conway-99 outcome is excluded. The bound remains `n3>=708`, with at least
209,994 induced six-cycles. Corrections and failed routes are collected in
the
[Wave 28 correction ledger](verification/2026-07-24-wave28-orchestrator-corrections.md).
The detached
[clean-clone replay](verification/2026-07-24-wave28-clean-clone.md) verifies
all 88 tests, five byte-identical regenerations, 46 manifest entries, central
metadata, links, exact Git-blob privacy, clean status, and strict object
integrity at integration commit
`4c4d2cb8dec14c7834984d47a7e5b29991891e60`.

## Wave 29 exclusion of the rootless `S0` endpoint origin

Wave 29 tests whether the Wave 28 bare control

```text
S0=K12 orthogonal_sum LAMBDA(F)
```

can carry the full frozen `n3=708` projector/Schur package. Because both
integral summands have minimum four, every norm-four frame row lies wholly in
one summand. The tight-frame trace gives the exact split

```text
K12 rows:       63
LAMBDA(F) rows: 168.
```

After permuting rows, `X`, `M`, `W`, `Q`, and `B` split into matching blocks.
The endpoint determinant bound gives `det(Q)=5`. Evenness rules out a
rank-12 unimodular `Q_K`, so

```text
det(Q_K)=5, det(Q_L)=1,
det(B_K)=3645, det(B_L)=1.
```

The projector row alphabet and cubic trace identity make both block traces
positive multiples of six. Exact AM--GM leaves only

```text
tr(B_K)=24, tr(B_L)=36.
```

Thus the integral, `G_K`-self-adjoint matrix
`C_K=(B_K-I_12)/2` has trace six. It is not assumed positive semidefinite;
only `B_K=I+2C_K` is positive, so each `C_K` eigenvalue is greater than
`-1/2`. Integral characteristic coefficients make the nonzero
characteristic pseudodeterminant an integer of absolute value at least one.
The full-domain logarithmic inequality then gives

```text
det(B_K)<=3^6=729,
```

contradicting `det(B_K)=3645`.

The
[independent audit](verification/wave29-s0-frame-exclusion/audit.md)
reconstructs the proof with 27 hostile tests and a byte-identical result. The
[source audit](verification/wave29-s0-literature-audit/audit.md) logs 81
queries and finds no exact combined precedent, without asserting novelty.
Corrections and packaging chronology are retained in the
[Wave 29 correction ledger](verification/2026-07-24-wave29-orchestrator-corrections.md).

The detached
[clean-clone replay](verification/2026-07-24-wave29-clean-clone.md) verifies
all 45 tests, two byte-identical regenerations, 19 manifest entries, central
metadata, repository-wide links, exact Git-blob privacy, clean status, and
strict object integrity at integration commit
`ae8fd70baaeb35302f957653e20ad710e5e77281`.

This excludes one exact `S0` endpoint origin only. Other determinant-729
lattices, the full `h=729` row, `n3=708`, Conway-99, and novelty remain
`UNKNOWN`.

## Wave 30 decomposable rootless `h=729` boundary and bare survivor

Wave 30 considers every endpoint form `S` satisfying

```text
rank(S)=44,
det(S)=729,
S even, integral, positive definite, rootless,
S nontrivially integrally orthogonally decomposable,
```

together with the full frozen `n3=708` projector/Schur identities. The
decomposition is required to be integral and unimodular; a merely rational
orthogonal split is insufficient.

Every frame row has `S`-norm four. Since each nonzero integral component in a
rootless summand has norm at least four, a row cannot have two nonzero
components. Consequently the rows are block supported, and `X`, `M`, `W`,
`Q`, `B`, and `C=(B-I)/2` split over the same integral blocks.

For a block `J`, the tight-frame identity gives

```text
4*n_J=21*rank(J),
```

so every original block rank is divisible by four. Since `det(Q)=5`, exactly
one `Q` block has determinant five; the others are even unimodular and have
rank divisible by eight. Combining the exceptional ranks

```text
4,12,20,28,36
```

with the possible `3`-adic determinant exponents

```text
2,4,6
```

gives a complete fifteen-type aggregate census. Grouping several
even-unimodular complement blocks loses no type.

The complete frame-row alphabet has thirteen solutions. Its cubic sum makes
every positive block trace a multiple of six. Exact integer AM--GM and the
blockwise logarithmic bound

```text
det(B_J)<=3^tr(C_J)
```

eliminate the strict cases. Equality makes `C_J` an integral self-adjoint
idempotent. Its integral image and kernel split orthogonally, and the
corresponding nonzero `Q` restrictions are even unimodular; their ranks must
therefore be divisible by eight. This excludes the four remaining forbidden
equality cases.

Fourteen of the fifteen aggregate types are impossible. The sole surviving
necessary type is

```text
S=A20 orthogonal_sum U24,

rank(A20)=20, det(A20)=729,
rank(U24)=24, det(U24)=1,
rows=(105,126),
det(Q_A),det(Q_U)=(5,1),
det(B_A),det(B_U)=(3645,1),
tr(B_A),tr(B_U)=(36,24),
B_U=I24.
```

`A20` is a local block label, not the ADE root lattice `A_20`. Exact tensor
arithmetic leaves 62 possible aggregate row profiles on the survivor. These
are necessary counts, not symmetric Gram matrices, frames, or endpoint
realizations.

An independent construction lane reaches an exact rootless rank-20 lattice
`T20` through five explicit 2-neighbors from
`K12 orthogonal_sum E8`:

```text
root counts: 240 -> 112 -> 48 -> 20 -> 6 -> 0
rank(T20)=20
det(T20)=729
min(T20)=4
norm-four vectors=5076
exact level=3
Gram SHA-256:
1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6
```

Both `3*T20^(-1)` and `21*T20^(-1)` are even integral. Therefore

```text
S44=T20 orthogonal_sum LAMBDA24,
G44=21*S44^(-1)
```

is an exact rootless even integral rank-44 determinant-729 bare `S/G`
package. This realizes the survivor's rank and determinant shape only.
Nothing proves that the generic `A20` is `T20`, and the construction supplies
no compatible `Q`, `B`, 105/126 frame, `X`, `M`, `W`, or Schur-square
certificate.

The first general discovery revision froze a transient Wave 29 audit hash,
so its submitted suite ran zero tests and its generator failed before output.
That failure and publication veto remain at commits `091d0a4...` and
`0bc6dc9...`. The provenance-only repair at `a7be6b8...` changes no theorem
content. The
[fresh re-verifier](verification/wave30-general-h729/reverification-audit.md)
passes the repaired 20-test replay, reproduces the original failure, and
passes the unchanged 32-test historical independent verifier in its frozen
snapshot. The [construction verifier](verification/wave30-h729-construction/audit.md)
passes 24 independent hostile tests. Full chronology is in the
[Wave 30 correction ledger](verification/2026-07-24-wave30-orchestrator-corrections.md).

The bounded [Wave 30 literature audit](verification/wave30-literature-audit/audit.md)
found no exact match for either signature in 96 logged queries, without
establishing novelty. The surviving decomposable type, rooted and integrally
indecomposable `h=729` forms, the entire determinant row, `n3=708`,
Conway-99, and novelty remain `UNKNOWN`.

## Wave 31 actual-incidence sign-commutant obstruction

Wave 31 returns from the free matrix/Schur realization to the actual
vertex-triangle incidence semantics of a putative `srg(99,14,1,2)`. Let
`N` be its `99 x 231` vertex-triangle incidence matrix and `Gamma` the
triangle-intersection adjacency matrix. Exact counting gives

```text
N*N^T=7I+A,
N^T*N=3I+Gamma.
```

The endpoint projector is the rank-44 projector `E=M/21` onto
`ker(Gamma)`, with constant diagonal `4/21`. For `u` in `im(E)`,

```text
||Nu||^2=3||u||^2,
(7I+A)Nu=3Nu.
```

Thus `N` maps `im(E)` bijectively, with squared scale three, onto the
44-dimensional graph eigenspace

```text
V=ker(A+4I).
```

Suppose the rootless even integral endpoint form `S` had a nontrivial
integral orthogonal decomposition. After the corresponding unimodular basis
change, the frame remains integral. Each row has `S`-norm four, while every
nonzero component in any lattice block has norm at least four. Hence every
row is supported on exactly one block. Cross-block `S`-products vanish, so
`M` and `E` become coordinate-block diagonal across a nonempty proper
triangle subset `I`.

Let `b=|I|` and let `D=diag(s)` have sign `+1` on `I` and `-1` on its
complement. Coordinate-block diagonality is equivalent to

```text
D*E=E*D.
```

The symmetric vertex operator

```text
K=N*D*N^T
```

therefore preserves `V`; symmetry also preserves `V` orthogonal complement.
It commutes with the exact spectral projector

```text
P_-4=(27I-9A+J)/63.
```

With `d=Ns`, expansion gives

```text
3(KA-AK)=d*1^T-1*d^T.
```

For adjacent vertices `x,y`, the strongly regular parameter `lambda=1`
provides a unique common neighbor `z`, and `{x,y,z}` is one of the graph
triangles indexing `D`. Writing `K=diag(d)+Z`, a complete partition of all
99 local summands shows that the same triangle sign is the only surviving
contribution to both `(ZA)_xy` and `(AZ)_xy`. Hence

```text
(ZA-AZ)_xy=0,
(KA-AK)_xy=d_x-d_y.
```

The exact commutator identity now gives

```text
3(d_x-d_y)=d_x-d_y,
```

so `d_x=d_y`. The target graph is connected because `mu=2` gives a
length-two path between every nonadjacent pair, so `d` is constant.

Summing signed triangle incidences in two ways yields

```text
99d=3(2b-231),
```

and hence `33 | b`. The discovery proof combines this with the block
tight-frame relation `4b=21r` and checks all proper ranks. The independent
verifier found a shorter route: the principal coordinate block `E_I` is
itself a projector and

```text
rank(E_I)=trace(E_I)=4b/21.
```

Therefore `21 | b`. Since `lcm(21,33)=231`, every nonempty proper block is
impossible.

The [primary verifier](verification/wave31-sign-commutant/audit.md) passes
21 independent tests and the frozen 15-test submitted replay. The
[secondary skeptic](verification/wave31-sign-commutant-skeptic/audit.md)
independently checks the integral basis transport, all local summands,
multiblock/complement cases, and deleted-premise controls. The conclusion
applies across endpoint determinant rows because `h=729` is absent from the
argument. It does not exclude any whole determinant row: rooted and
rootless integrally indecomposable forms remain untreated.

## Wave 31 exact T20 finite geometry

The parallel construction lane enumerates the complete norm-four shell of
the displayed Wave 30 lattice `T20`:

```text
norm-four vectors: 5076
antipodal lines:   2538
line-list SHA-256:
25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e
```

All `3,219,453` unordered distinct-line pairs have inner product in
`{0,+/-1,+/-2}`. The absolute-two graph has 242,649 edges. The exact
105-line second-moment formulation has 2,538 Boolean variables, 210 moment
equations, and an odd-cardinality equation. Its coefficient and augmented
GF(2) ranks are both 210, so parity does not obstruct it.

An exact rational box witness has 33 unit weights, 210 strictly fractional
weights, 2,295 zero weights, total weight 105, and satisfies all 210 moments.
It is not a Boolean frame. The named 105-line near-frame has residual score
121. A complete exact scan of all 105-by-2,433 one-exchanges and all
5,460-by-2,958,528 two-exchange pair combinations finds no repair. The
independent verifier uses an injective base-257 code on this bounded domain
and separately replays the submitted modulo-`2^64` filter.

Only that named radius-two neighborhood is excluded. Supports at distance at
least three and all other supports remain `UNKNOWN`. The cap-one-coordinate
domain is separately excluded, and the conditional `B_U=I` identities force
`A4_U=M_U`, transferring all 84 excess diagonal units to the T20 block.
No orientation, compatible `Q_A/B_A/A4_A`, coupled endpoint, or graph is
supplied.

The [independent finite audit](verification/wave31-t20-frame/audit.md)
passes 11 tests after the discovery suite's 10 tests. Its finite conclusions
remain valid, but the sign-commutant theorem independently excludes every
rootless decomposable actual endpoint that could use this block.

The bounded [Wave 31 literature audit](verification/wave31-literature-audit/audit.md)
found no exact prior result in 80 logged queries and 14 retained metadata
records, without establishing novelty. The exact correction and scope
chronology is retained in the
[Wave 31 correction ledger](verification/2026-07-24-wave31-orchestrator-corrections.md).
Rooted and rootless integrally indecomposable endpoints, `n3=708`,
Conway-99, and novelty remain `UNKNOWN`.

## Wave 32 rooted Fano support and indecomposable motif reductions

Wave 32 attacks the two exhaustive endpoint branches that remain after
Wave 31, for every determinant value

```text
h in {9,21,49,81,189,441,729,1029}.
```

In the rooted branch, let `r` be a norm-two vector, `y=XSr`, and let `N`
be actual vertex-triangle incidence. Primitivity makes `X^T` onto, so
`y` lies in `M Z^231`. The exact identity

```text
NM=(9I-3A)N+J
```

therefore makes `z=Ny` constant modulo three. The two nonzero residue
classes contradict the exact sum and norm, leaving

```text
z=3k,  Ak=-4k,  sum(k)=0,  ||k||^2=14.
```

The integral `-4` eigenvector equations force seven `+1` and seven `-1`
entries and no other nonzero amplitudes. The `lambda=1`, `mu=2`
common-neighbor equations then force the induced signed support, up to
relabeling, to be the bipartite complement of the Fano incidence graph.
Consequently every root has the necessary triangle-image pattern

```text
y: (+1)^21, 0^189, (-1)^21.
```

This refines the earlier root-pattern sieve:

```text
46 moment patterns -> 32 tensor patterns -> 16 matrix-only patterns
                   -> 1 actual-incidence pattern.
```

The clean-room [rooted verifier](verification/wave32-rooted-vector/audit.md)
passes 19 tests without importing or executing discovery code. It independently
reconstructs the primitive-image bridge, modular transport, support saturation,
outside census, tensor and fourth-moment contractions, and adversarial
premise deletions. A discovery-v1 residual-degree error is retained and
corrected in
[the rooted correction ledger](attempts/wave32-rooted-vector/correction-ledger.md).
The partial 99-vertex control is not an extension certificate, and the unique
pattern is not excluded.

For the rootless branch, primitivity makes the 231 frame rows generate
`Z^44`. Under minimum four, an integral orthogonal decomposition is therefore
equivalent to disconnected nonzero support of `M`. The Wave 31
actual-incidence theorem forces that support graph to be connected, so every
surviving rootless actual-incidence endpoint is integrally indecomposable.
This implication is unavailable for a matrix-only realization.

Independently, three frame rows with pair products

```text
{-2,-2,-1}
```

have positive-definite Gram matrix but sum to a norm-two vector. This is the
unique switched three-row motif over the endpoint entry alphabet with that
property. Rootlessness therefore requires

```text
tr(A_-1 A_-2^2)=0,
```

where the trace is exactly twice the unordered motif count. The exact
unordered pair census

```text
M=+1,0,-1,-2: 2546,22161,708,1150
```

does not force this mixed trace. The clean-room
[indecomposable verifier](verification/wave32-indecomposable/audit.md)
passes 19 tests, including full-size hostile controls, while leaving the
actual-incidence motif-forcing step `UNKNOWN`.

The corrected [literature package](verification/wave32-literature-audit/audit.md)
and [independent source audit](verification/wave32-literature-audit-independent/audit.md)
preserve 68 exact queries in 17 batches, 15 metadata records with explicit
14-plus-one chronology, eight direct inspection events, three access
failures, and no raw source payload. Petro--Phillips's conditional
triangle-intersection spectrum is prior art. No exact resolution of either
surviving endpoint was found in the searched sources, which is not a novelty
or openness certificate.

Thus the rooted Fano-support reduction, actual-incidence rootless
indecomposability, and rootless motif exclusion are `VERIFIED` only in their
stated necessary scopes. Root exclusion, actual-incidence motif forcing,
both surviving endpoints, `n3=708`, Conway-99, and novelty remain `UNKNOWN`.
The full repair and scope chronology is retained in the
[Wave 32 orchestrator ledger](verification/2026-07-24-wave32-orchestrator-corrections.md).

## Wave 33 finite rooted extension and rootless contraction wall

Wave 33 continues from the two independently verified Wave 32 endpoints.
Nothing in this section assumes an automorphism outside the already-forced
relabeling of the signed Fano support.

### Rooted three-cell structure

Let `S` be the signed 14-vertex support, `O` the 70 vertices with one
neighbor in each sign class, and `Q` the 15 vertices with no support
neighbor.  Summing target common-neighbor counts over `S` gives

```text
o in O: 2*lambda+12*mu = 8+2 deg_O(o),
q in Q: 14*mu          = 2 deg_O(q).
```

At `lambda=1, mu=2`, this forces

```text
       S  O  Q
S      4 10  0
O      2  9  3
Q      0 14  0.
```

In particular, `Q` is independent.  If `B` is the `70 x 15` O-Q incidence,
then

```text
B 1=3 1,
B^T 1=14 1,
B^T B=12I+2J.
```

No two rows of `B` can repeat: two O vertices with the same three Q
neighbors would have at least three common neighbors, exceeding both
`lambda` and `mu`.  Thus the rows are a simple `2-(15,3,2)` design.

Let `A_S` be the fixed signed-support adjacency and `F` the fixed
support-to-O incidence.  Naming the induced O adjacency `D`, the full
adjacency has block form

```text
    [ A_S  F  0 ]
A = [ F^T  D  B ].
    [  0  B^T 0 ]
```

The target identity is equivalent, block for block, to

```text
A_S^2+F F^T             =12I-A_S+2J,
A_S F+F D               =2J-F,
F B                     =2J,
F^T F+D^2+B B^T         =12I-D+2J,
D B                     =2J-B,
B^T B                   =12I+2J.
```

Necessity follows by multiplication.  Conversely, binary `B`, symmetric
binary zero-diagonal `D`, and all six equations reassemble
`A^2=12I-A+2J`; the diagonal and off-diagonal entries then give the target
degree and common-neighbor counts.  This is a necessary-and-sufficient
finite criterion for the **graph extension**.  It does not by itself
enforce the endpoint projector, lattice, tensor, or Schur conditions.

The equations split `R^70` into exact invariant spaces and force

```text
spec(D)=
9^1, (-1)^14,
(-1-sqrt(2))^6, (-1+sqrt(2))^6,
3^27, (-4)^16.
```

Consequently any solution has

```text
edges(D)=315,
triangles(D)=56,
C4(D)=294,
det(D)=2^32 3^29.
```

The independent
[rooted comparison audit](verification/wave33-rooted-extension/comparison-audit.md)
passes 33 tests and finds no material defect.  It verifies the criterion,
spectrum, cycles, determinant, and hostile two-`PG(3,2)` design without
importing or executing discovery code.  It does not supply or exclude a
binary solution.

### Restricted rooted construction evidence

The [construction audit](verification/wave33-rooted-construction/audit.md)
checks one explicit O-Q certificate.  It has exact
`2-(15,3,2)` row/column/pair data but support-point count histogram

```text
1^5, 2^200, 3^5,
```

so exactly ten entries of `FB=2J` fail and the squared defect is ten.  The
O-O layer is unsupplied.  An empty O-O layer appears only as a verifier
hostile control.

A separate zero-objective MILP encodes all `70!` assignments of this one
fixed simple design to the 70 labeled O vertices.  It does not cover other
nonisomorphic designs.  The 25-second run returned a time limit with no
primal and never entered the O-O phase.  This has no mathematical status.
The original local frozen-context verifier recorded 37/37 and independently
regenerated the hostile certificate.  Chronology v2 replays 36 unchanged
verifier cases and separately passes the portable source half of the sole
omitted composite test.  The verifier also supplied strict duplicate-key and
scope gates absent from the discovery checker.  Once this Wave 33 section
changed the mutable `STRUCTURE.md`, direct live-root replay correctly failed
the original input hash.  The separate
[chronology audit](verification/wave33-rooted-construction-chronology/audit.md)
authenticates the exact eight historical inputs in an isolated temporary
root, replays the unchanged `14+36=50` portable construction cases, and
passes 20 outer tamper, path, environment-isolation, status, and no-write
tests.  The portable source half of the sole omitted composite verifier test
passes separately.  The solver-environment half, which depends on ignored
local files, is `NOT_REPLAYED_NONBLOCKING`; v2 opens zero such files and
observes zero environment hashes.  The unchanged comparison CLI is therefore
`NOT_RUN_BY_DESIGN`.  The outer and embedded counts are distinct evidence
layers.

### Rootless fused-algebra boundary

Write

```text
C=Gamma^2-5Gamma-18I,
Q[Gamma]=span_Q{I,J,Gamma,C}.
```

The exact multiplication table includes

```text
Gamma^2 =18I+5Gamma+C,
Gamma C =-18I+18J-2Gamma-C,
C^2     =72I+216J-16Gamma-14C.
```

At a formally allowed `q(T)=q(U)=2` `R2` pair, two nonnegative integral
third-triangle tables have the same margins and every bilinear contraction
against this algebra, while their `(R3,R3)` entries are zero and one.
Also

```text
N^T A^k N=(3I+Gamma)(Gamma-4I)^k in Q[Gamma]
```

for every `k>=0`.  Hence the displayed local trade is invisible to
bilinear `Q[Gamma]` and `N^T p(A)N` contractions.  This is the verified
scope; it is not a statement about arbitrary uncontracted, three-leg, or
globally compatible incidence arguments.

Actual target incidence around any `R2` pair independently forces the
outside double-neighbor board

```text
[[1,0,1],
 [0,1,1],
 [1,1,2]].
```

A common `R3` triangle is exactly a triangular transversal of this board.
There are four pair-indexed transversal candidates.  At `n3=708`, this is
`2832` candidates counted with base-pair multiplicity.  Rootlessness
requires all of them to remain open, but neither their global avoidance nor
their forced closure is proved.

The [rootless audit](verification/wave33-rootless-motif/audit.md) passes 48
tests and returns
`PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER`.  The unqualified
discovery headline "all two-leg contractions" is replaced by the exact
local algebraic scope above.

Thus Wave 33 verifies a finite rooted reformulation, conditional spectral
consequences, a scoped formal rootless null-trade control, and exact local
incidence data.  Binary rooted solvability, actual global motif forcing or
avoidance, both endpoints, `n3=708`, Conway-99, and novelty remain
`UNKNOWN`.  The complete chronology is in the
[Wave 33 orchestrator ledger](verification/2026-07-24-wave33-orchestrator-corrections.md).

## Wave 34 rooted reparameterization and rootless overlap bounds

Wave 34 keeps the exact Wave 33 labeled domains and assumes no completed-graph
symmetry.

### Rooted support kernel and residual projector (`VERIFIED`)

Let `P` be the fixed `14 x 70` support-to-O incidence matrix. Exact labeled
minors give

```text
rank(P)=13,
SNF(P)=diag(1^13,0),
dim ker(P)=57.
```

For an admissible O-Q incidence `B`, the fixed Fano-image, centered-B, and
joint-kernel spaces have dimensions

```text
13+14+43=70.
```

This is exactly the earlier `27+43` split because the Fano and B images share
the one-dimensional constant space. On the 43-space the O-O adjacency
restriction satisfies

```text
H^2+H-12I=0
```

with multiplicities `3^27,(-4)^16`. If `E_-4` is its minus-four projector,
then

```text
H=H_R-E_W+3Q_U-7E_-4.
```

Equivalently, for the fixed integral matrix `C_star`,

```text
L=C_star-7BB^T-21H=147E_-4,
PL=0,
B^T L=0,
L^2=147L.
```

Hollow binary recovery forces

```text
diag(L)=30^28,36^42,
tr(L)=2352=147*16,
```

so the integral formulation also forces rank 16. The verifier checked both
directions on every invariant summand. This is an exact reparameterization,
not an existence proof.

For distinct O-vertices, put

```text
g_ij=(P^T P)_ij,
r_ij=(BB^T)_ij,
h_ij=H_ij,
c_ij=(H^2)_ij.
```

The O-O equation gives

```text
g_ij+r_ij+h_ij+c_ij=2.
```

Nonnegativity and binary/design bounds leave exactly nine states:

```text
(0,0,0,2), (0,0,1,1), (0,1,0,1), (0,1,1,0),
(0,2,0,0), (1,0,0,1), (1,0,1,0), (1,1,0,0),
(2,0,0,0).
```

The 21 duplicated-support pairs are forced into `(2,0,0,0)`, so their B
rows are disjoint and they are neither adjacent nor distance-two through O.
The `(1,1,0,0)` relation is 6-regular on 70 vertices and has 210 edges.

A column `b` with `Pb=2*1` is a spanning 2-factor of the fixed bipartite
seven-point/seven-line multigraph. Two independent exact enumerations give

```text
all labeled Pb-only columns:       574,118,037
duplicate-free necessary columns: 448,879,368.
```

The second number removes precisely the half-cycle types containing a
one-cycle. It does not impose compatibility among 15 columns or the
remaining graph/projector equations.

### Complete rooted CNF (`VERIFIED ENCODING ONLY`)

An independently reconstructed CNF encodes every binary, hollow, symmetry,
degree, design, coupling, and common-neighbor equation in the six Wave 33
blocks. It has

```text
1,233,001 variables,
4,323,943 clauses,
89,546,779 raw bytes,
SHA-256 2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3.
```

The ordered `D` variables are tied by explicit hollow/symmetry gates and do
not restrict the labeled domain. Every AND and exact-cardinality gadget is
bidirectional. The verifier regenerated all clauses without importing the
candidate generator. No SAT/UNSAT solve or proof replay exists.

### Rootless triangle-fibre holonomy (`VERIFIED SCOPED`)

For a graph triangle `T={t0,t1,t2}`, the three outside neighbor fibres have
size 12. Each induces `6K2`, and every pair of fibres is joined by a perfect
matching. After transporting labels, the third cross-fibre matching is a
permutation. If `q(T)` is its number of moved labels, then

```text
deg_R3(T)=12-q(T),
deg_R2(T)=3q(T),
q(T) != 1.
```

At `n3=708`,

```text
sum_T q(T)=472,
|E(R3)|=1150.
```

The projector Gram matrix shows that an `R3` edge has at most one common
`R3` neighbor. Hence `R3` contains at most 383 edge-disjoint triangles.
Actual incidence sharpens the common-`R3` codegree caps for

```text
Gamma,R0,R1,R2,R3
```

to

```text
0,5,1,1,1.
```

In particular, each `R2` pair has at most one globally compatible closure,
and

```text
tr(A_R2 A_R3^2)
 =2 * #{unordered R2 pairs whose unique closure is realized}.
```

Rootlessness sets this trace to zero but does not prove that a closure must
occur.

The verifier-owned Stage 1 derivation also gives the necessary global
constraints

```text
sum of R0-centered R3 wedges >= 6860,
#C4(A_R3)                    >= 3041,
tr(A_R3^4)                   >= 67848.
```

These are `DERIVED_SCOPED`. They remain numerically feasible and do not force
the forbidden mixed motif.

The 45-vertex control and the sharp scalar degree profile are partial local
objects, not graph or endpoint certificates. Binary rooted
solvability/exclusion, rootless motif forcing/avoidance, both endpoints,
`n3=708`, Conway-99, and novelty remain `UNKNOWN`. Full scope and correction
details are in the
[Wave 34 structural audit](verification/wave34-rooted-structural/comparison-audit.md),
[rootless audit](verification/wave34-rootless-global/audit.md), and
[orchestrator ledger](verification/2026-07-24-wave34-orchestrator-corrections.md).

## Wave 35 prism-free upper endpoint

Let `P` be the number of induced triangular prisms. Exact opposite-edge
double counting gives

```text
n3 + 3P = 4158.
```

Hence `n3=4158` if and only if `P=0`. The endpoint forces every graph triangle
to have cross-edge profile

```text
(a0,a1,a2,a3)=(32,144,36,0).
```

### Signed projector (`VERIFIED SCOPED`)

For the rank-44 integral projector scaling `M`, put `S=M-4I`. Conditional on
the endpoint,

```text
S^2=13S+68I,
S1=-4*1,
spec(S)=17^44,(-4)^187,
SNF(S)=diag(1^44,4^143,68^44).
```

Equivalently,

```text
C=2S-13I=2M-21I,
C^2=441I.
```

The independent verifier reconstructed these identities, all 40 mixed-Schur
values, the compression slack, and the scalar incidence bounds without
importing discovery code. It found no contradiction. Since `rank(M)=44`,
every 45-by-45 principal block is singular. A 45-set `X` satisfying

```text
max_i sum_{j in X} |S_ij| <= 3
```

would make `4I+S[X]` strictly diagonally dominant and contradict singularity.
The absolute values are essential; an absolute algebraic row-sum condition is
false.

### One-triangle incidence reduction (`DERIVED`)

Fix a triangle `T` and partition the vertices into

```text
T | X | Y = 3 | 36 | 60.
```

The neighbor counts into the three cells are

```text
X vertex: 1,3,10
Y vertex: 0,6,8.
```

Thus `G[X]` is cubic and triangle-free, `G[Y]` is 8-regular, and the `X-Y`
bipartite graph has degrees `(10,6)`. The three 12-point fibres inside `X`
each induce a perfect matching. Every `y in Y` determines a six-point block
meeting every fibre twice. If `B` is their 36-by-60 incidence matrix, `R` is
the three-fibre indicator matrix, and `A_X` is the adjacency matrix of
`G[X]`, then

```text
B B^T = 12I - A_X + 2J - R R^T - A_X^2.
```

This is a finite exact one-triangle feasibility problem. A restricted
pairwise control exists, but no simultaneous 60-block system or
cross-triangle compatibility certificate is known.

### Wave 36 modular endpoint restrictions (`VERIFIED SCOPED`)

The integral reflection has stronger finite-field consequences than the
initial endpoint report recorded.  Put

```text
r3=rank_F3(M)=rank_F3(C),
r7=rank_F7(M)=rank_F7(C).
```

Independent reconstruction proves

```text
r3>=12,
r7>=11,
r3+r7=0 (mod 2).
```

If `d1|...|d231` are the Smith factors of `C`, then

```text
d_i d_(232-i)=441.
```

Consequently the complete Smith form is fixed once `(r3,r7)` is fixed.  The
rank-seven bound comes from the entrywise-cubic identity

```text
C^(o3)=4(I+C) (mod 7).
```

The right side is invertible because `C^2=0 (mod 7)`.  Thus 231 pure
symmetric cubes are independent and

```text
binom(r7+2,3)>=231.
```

The sharper ternary bound uses finite orthogonal geometry.  A symmetric
rank factorization modulo three writes

```text
C=V H V^T.
```

Its 231 factor rows give distinct norm-two projective points, each
orthogonal to exactly 162 of the others.  In either determinant class, the
ambient norm-two projective orthogonality graph is strongly regular.  If it
has parameters `(v,k,lambda,mu)` and positive nonprincipal eigenvalue
`theta`, an induced 231-point, 162-regular subgraph would require

```text
162 <= (231k+(v-231)theta)/v.
```

Exact point counts make the right side smaller than 162 in both determinant
classes through dimension eleven.  At dimension twelve the nonsquare class
still has upper bound 158, while the square class survives with upper bound
`4149/13`.  Hence `r3>=12`, and equality requires the square determinant
class.  These are conditional arithmetic restrictions, not an endpoint
matrix or an upper-bound improvement.

### Wave 36 one-triangle strengthening (`VERIFIED SCOPED`)

Write `H=A_Y` for the 60-vertex graph in the one-triangle partition.  The
three exact block equations are

```text
B B^T       = 12I - A_X + 2J - R R^T - A_X^2,
B H         = 2J - (I+A_X)B,
B^T B + H^2 = 12I - H + 2J.
```

For a column `b` of `B`, the mixed equation forces

```text
d(b)=2*1-(I+A_X)b>=0.
```

Besides requiring the selected vertices to induce a matching, this says
that no unselected `X` vertex has three selected neighbors.  On the frozen
Wave 35 restricted core, this exact cut reduces the individual-block census
from

```text
183980 to 151712.
```

It is still only an individual-column census.

If a connected component of `A_X` contains `m` vertices in each of the
three fibres, every six-point block meets that component in exactly `m/2`
points.  Thus every `m` is even.  The `m=2` component is `K3,3`, which
violates the target common-neighbor rule, leaving exactly

```text
[12], [4,8], [6,6], [4,4,4]
```

as the possible component-size partitions in units of one vertex per
fibre.

Finally, if `c` is the number of components and

```text
chi_X(t)=(t-3)^c t^2 f(t),
```

then any compatible `H` must satisfy

```text
chi_H(t)=(-1)^(34-c)
         (t-8)(t-3)^18(t+4)^(7+c) f(-1-t).
```

In particular `H` is connected, has exactly 32 triangles, and has

```text
C4(H)=171+C4(A_X).
```

No simultaneous 60-column `B`, compatible `H`, or contradiction is known.

### Rooted and one-edge construction reductions (`DERIVED` / `CANDIDATE`)

Fix a root `o`, whose 14 neighbors are seven mate pairs `(a_i,b_i)`. For
every other root-neighbor coordinate `r`, the residual edge

```text
{a_i,r} -- {b_i,r}
```

would close a prism with `{o,a_i,b_i}`. Therefore `P=0` imposes exactly
`7*12=84` negative residual-edge units. Intersecting them with the verified
12-way normalized `N3` cover immediately removes branches

```text
1,2,3,6,7,9,11
```

and leaves exactly

```text
4,5,8,10,12.
```

Around one graph edge, the union of the two endpoint fibre matchings has one
of four cycle partitions:

```text
2+2+2, 2+4, 3+3, 6.
```

For each partition, exhaustive neighborhood enumeration gives 5,500 masks,
of which 5,184 remain as binary variables after exact moment reduction. The
exported local OPB models have 380 equality rows. They omit all edges among
the 72 outside vertices and therefore are necessary relaxations only.

All five rooted branch scouts stopped at conflict budgets. All four local
integer scouts stopped at time limits without incumbents. No result is a
proof or counterexample. The rigorous interval remains

```text
708 <= n3 <= 4158,
```

and both `n3=4158` and Conway-99 remain `UNKNOWN`.

### Wave 38 universal coclique-rank strengthening (`VERIFIED`)

Every putative target graph contains a 13-coclique. Choose an edge `xy` and
let `z` be its unique triangle mate. The sets

```text
X=N(x)-{y,z},  Y=N(y)-{x,z}
```

have twelve vertices. Each carries a perfect matching, and the `mu=2`
common-neighbor rule gives a perfect matching between them. Their union is
2-regular; local and cross edges alternate, and every component cycle has
length divisible by four. One alternating color class has twelve vertices.
The `lambda=1` rule makes `z` nonadjacent to all of `X union Y`, so adjoining
`z` gives an independent set of size thirteen.

Let `N` be the vertex-triangle incidence matrix and `M=21E_0` the integral
rank-44 projector on the zero eigenspace of the triangle-intersection graph.
From

```text
N N^T=7I+A,
N^T N=3I+Gamma,
```

spectral transport gives

```text
N M N^T=27I-9A+J.
```

Restricting to the 13-coclique gives

```text
N_I M N_I^T=27I_13+J_13.
```

Its determinant is `27^12*40`, congruent to five modulo seven. Therefore

```text
rank_F7(M)>=13.
```

This is universal conditional on target existence, not merely an endpoint
fact. At `n3=4158`, `C=2M-21I` is congruent to `2M` modulo seven, so the same
rank floor holds for `C`. Combined with even `r3+r7`, the surviving
`r3=12` boundary requires even `r7>=14`. The endpoint arithmetic now leaves
528 rank pairs rather than 629. These are arithmetic survivors, not matrices
or graphs.

The combinatorial coclique construction is credited to Misha Lavrov's public
2025 Mathematics Stack Exchange comment. The combined rank consequence passed
a separate ten-test adversarial reconstruction; novelty remains `UNKNOWN`.

### Wave 38 complete all-prism schema (`VERIFIED CONSTRUCTION SCOPE`)

The rooted scaffold has 96,215 potential triangles:

```text
7 fixed root,
924 coordinate-plus-two-residual,
95,284 residual-only.
```

For every two disjoint potential triangles and each of their six perfect
matchings, the complete schema forbids the simultaneous presence of the nine
prism edges. The `lambda=1` constraints make this positive-edge clause exact:
any unmatched cross edge would give a triangle edge two common neighbors.
An independent exhaustive check of all 64 supergraphs verifies this step.

The residual-only subfamily contains exactly

```text
60*binomial(84,6)=24,388,892,640
```

clauses, so a monolithic static formula is not practical on the current host.
The finite exact alternative is solve--cut--check: decode a candidate,
enumerate every induced prism, add candidate-bound exact cuts to a
source-bound cumulative pool, and repeat. A checked UNSAT result from any
sound partial pool excludes that refined case; a SAT assignment is terminal
only when the full SRG checker and zero-prism oracle both pass.

The 33-case cover and all-prism construction contain no completed-graph
automorphism assumption. Current independently checked proof coverage is
`0/33`; no formula result, graph, endpoint exclusion, or upper-bound
improvement follows.

### Wave 38 fourth-order and local-rank bridge (`VERIFIED`, scoped)

At the endpoint, the signed support matrix `S=M-4I` has

```text
tr(S^4)=3722796.
```

Inclusion-exclusion counts

```text
231*68*(2*68-1)=2120580
```

non-simple closed signed four-walks. Every simple support four-cycle has
eight oriented rooted representations, so

```text
balanced support C4 - unbalanced support C4 = 200277.
```

This exact imbalance is not a contradiction because the two unsigned counts
remain unknown.

Over `F_3`, the seven triangle-factor rows through every original vertex have
one common sum `w`. Centering by `z_T=v_T-w` gives Gram matrix

```text
D=C+J,  rank_F3(D)=r3-1.
```

For the nineteen triangles meeting one base triangle, exact elimination gives

```text
rank_F3(D_local)=rank_F3(P_T-I),
```

where `P_T` is a simple tripartite four-regular graph on `6+6+6` vertices.
A frozen one-triangle control satisfies all audited local caps and has
`rank_F3(P_T-I)=10`, showing that the local axioms alone cannot exclude
`r3=12`. A successful continuation must use simultaneous 60-block `B/H`
compatibility or compatibility among different base triangles. This lane
does not prove `P>=1`. An independent reconstruction passed eleven hostile
tests. Its only wording qualifier is that the seven-row rank-six statement
refers to the centered Gram `D=C+J`; the uncentered Gram has rank seven.

### Wave 39 edge-local characteristic-seven rank (`VERIFIED`)

Fix an arbitrary edge `xy` with unique triangle mate `z`, and let

```text
X=N(x)-{y,z},  Y=N(y)-{x,z}.
```

The `lambda=1` and `mu=2` equations force perfect matchings on `X`, on `Y`,
and between `X` and `Y`. Pulling the cross matching back to `X` leaves the
union of two perfect matchings on twelve vertices. Its alternating cycles
have lengths `2m`; before pullback the corresponding `X union Y` cycles have
lengths `4m`, where the positive parts `m` sum to six. Thus all edge-local
normal forms are indexed by the eleven positive partitions of six.

Let `L={x,y,z} union X union Y`. Modulo seven,

```text
(N M N^T)[L,L] = (J-I-2A)[L,L].
```

Exact elimination on all eleven forms gives

```text
rank_F7((N M N^T)[L,L]) = 25 - 2e,
```

where `e` is the number of even parts. At most three positive even parts can
sum to six, so every such principal block has rank at least nineteen.

The rank transport is equality, not merely an upper comparison. If `v=Mw`
and `Nv=0`, then

```text
0=N^T N v=N^T N M w=3M w=3v.
```

Since three is invertible in `F_7`, `N` is injective on `im(M)`. Applying this
on both sides and using symmetry of `M` proves

```text
rank_F7(M)=rank_F7(N M N^T)>=19.
```

An independent verifier enumerated all 10,395 pulled-back labelled matchings,
reconstructed every normal form, recomputed the ranks, and attacked the
status and rank claims with hostile mutations.

At the prism-free endpoint, parts equal to one are forbidden. The surviving
partitions and local ranks are:

| partition | local rank over `F_7` |
| --- | ---: |
| `2+2+2` | 19 |
| `2+4` | 21 |
| `3+3` | 25 |
| `6` | 23 |

The endpoint arithmetic census therefore has 429 surviving `(r3,r7)` pairs
instead of 528. If `r3=12`, parity forces even `r7>=20`. Moreover, `r7<=20`
forces every edge to have type `2+2+2`; `r7<=22` permits only `2+2+2` and
`2+4`; and `r7<=24` forbids type `3+3`. These are necessary restrictions, not
a global edge-type compatibility theorem.

### Wave 39 proof shard and conditional compatibility lanes

For refined endpoint branch 15, the published units `x24=1` and `x2=1`
generalized-unit propagate through a capacity constraint to `x3591=0`.
Assuming `x187=1` then falsifies a wedge clause. Exact emitted raw and
elaborated kernel proofs, and fresh independent VeriPB 3.0.2 runs accepted
both:

```text
branch15 AND x187=1: UNSAT
branch15 entails x187=0.
```

The `x187=0` polarity shard remains open. Consequently branch 15 is unresolved
and complete endpoint proof coverage remains `0/33`. CakePB supplied no
conclusion.

Conditional on the endpoint and `r3=12`, the cross-base projection lane maps
each 84-triangle vertex star to 72 oriented norm-one vectors in a nonsquare
five-space. It forces at least twelve equal-projection pairs, hence explicit
support-four or support-six factor-row dependencies. Exact quotient controls
of ranks ten and eleven show that a universal local rank-twelve shortcut is
false.

The simultaneous `B/H` lane makes the centered 231 rows distinct projective
isotropic points in a nonsquare eleven-space and derives a self-orthogonal
`[231,11]_3` code with recorded low-weight enumerator constraints. A compatible
`H` would have 96 overlap-zero edges forming 32 edge-disjoint triangles and
144 overlap-one edges partitioned into 36 point-labelled four-edge matchings.
All tested oriented Delsarte transforms are nonnegative, so these restrictions
do not exclude the boundary.

No Wave 39 result forces a prism, closes a full endpoint case, or improves
`n3<=4158`.

### Wave 40 third-fibre completion and universal rank 25 (`VERIFIED`)

Keep the Wave 39 notation for an arbitrary edge `xy`, its triangle mate `z`,
the twelve-point fibres `X,Y`, and the 27-point set

```text
L={x,y,z} union X union Y.
```

The third fibre `Z=N(z)-{x,y}` also has twelve vertices and is disjoint from
`L`. For every `u in X`, the nonadjacent pair `u,z` has common neighbor `x`
and exactly one further common neighbor in `Z`. Conversely, every vertex of
`Z` has exactly one neighbor in `X`. Thus `X-Z` is a perfect matching. The
same argument makes `Y-Z` a perfect matching. Relabeling `Z` by the `X-Z`
matching leaves an arbitrary permutation `f:X->Y`.

Let

```text
K=N M N^T=J-I-2A  over F_7,
S=K[L,L],
U_f=K[L,Z].
```

If the columns of `H` form a basis of `ker(S)`, then every symmetric
completion with an arbitrary lower-right block `W` satisfies

```text
rank([[S,U_f],[U_f^T,W]]) >= rank(S)+2 rank(H^T U_f).       (1)
```

To see this, choose a basis in which the symmetric matrix `S` is congruent
to `diag(D,0)` with `D` invertible, eliminate the `D` rows and columns, and
obtain a remaining block of the form

```text
[[0,C],[C^T,R]],  C=H^T U_f.
```

Its rank is at least `2 rank(C)`, independently of `R`.

For a partition `pi` of six, let `e(pi)` be its number of even parts. The
Wave 39 calculation gives `rank(S)=25-2e(pi)`. A discovery implementation
and a clean-room verifier independently enumerated the projective syndrome
subspaces of the 144 possible third-fibre columns and used exact bipartite
matching to cover every one of the `12!` permutations. Both obtain

```text
min_f rank(H^T U_f)=e(pi)
```

for all eleven partitions. Substitution in (1) gives a 39-point principal
rank of at least 25 for every edge type. Since

```text
rank_F7(K)=rank_F7(M),
```

every hypothetical Conway graph satisfies

```text
rank_F7(M)>=25.
```

In the hardest `2+2+2` case, `rank(S)=19`, `dim ker(S)=8`, and syndrome
subspaces of dimensions zero, one, and two support matchings of size at most
zero, four, and eight. Exactly 32 of the 25,744 enumerated three-spaces
support a perfect matching, so the argument is tight at its stated local
boundary. The earlier conditional `r7>=22` argument is independently
verified but numerically superseded by the universal theorem.

At `n3=4158`, the verified modular arithmetic census now has 330 surviving
`(r3,r7)` pairs instead of 429. If `r3=12`, parity forces even `r7>=26`.
The endpoint remains unexcluded.

### Wave 40 global edge-type complex and 39-block Laplacian (`VERIFIED_SCOPED`)

At the prism-free endpoint, the 4,158 edges of the opposite-edge graph `J`
map bijectively to the 4,158 edges of the induced-`N3` triangle relation
graph `L`. For each graph edge, each component of its Wave 39 local cycle
system is treated as a face. Every edge of `L` lies on exactly two faces.

If `(a,b,c,d)` counts the types `(222,24,33,6)`, the exact face identities
are

```text
F4=3a+b,  F6=2c,  F8=b,  F12=d,
4F4+6F6+8F8+12F12=8316=2|E(L)|.
```

After splitting triangle-vertices with disconnected links, the result is a
disjoint union of closed combinatorial surfaces. If `Hc` is the total number
of link components, then

```text
chi=Hc-4158+(3a+2b+2c+d).
```

For all edges of type `222`, this is a 2,079-face quadrangulation with
`-1848<=chi<=-693`; negative Euler characteristic is not contradictory.

Around one all-`222` base triangle, contracting the six matching edges in
each fibre gives a four-regular tripartite quotient `P_T` on `6+6+6`
vertices. A complete normalized census of 4,050 forms gives

```text
rank_F3(P_T-I): 11  12  13   14    15    16
forms:           8   1 400   46  2616   979.
```

Under the joint assumptions `r3=12` and all edges type `222`, every triangle
must use one of the eight rank-11 boundary forms. Those forms survive.

Let `A_X` be the cubic graph induced by the 36 neighbors outside a fixed
base triangle. Exact Schur elimination gives

```text
rank_F7(K[T union N(T)])=1+rank_F7(3I-A_X).
```

The contracted quotient omits eighteen endpoint-pairing bits and therefore
does not determine this rank. For one rank-11 quotient, a complete `2^18`
lift census has 37,378 triangle-free lifts, with 39-block ranks
`33^264,34^7348,35^29766`. This is a verified census for that one quotient,
not a universal rank-33 floor. Global compatibility among different base
triangles, or a bound on the seven-primary Laplacian nullity for every
admissible core, remains missing.

### Wave 41 full-matching equality and universal rank 26 (`VERIFIED`)

Restore the perfect matching in the third fibre of the Wave 40 39-point
edge block. After normalizing the first matching and two cross matchings,
the cubic-core Laplacian has blocks

```text
[ 3I-P  -I    -I  ]
[ -I    3I-Q -F  ]
[ -I    -F^T 3I-R].
```

Eliminating `3I-P`, whose inverse over `F_7` is `3I+P`, gives the symmetric
24-point block

```text
H = [ P+Q        F+3I+P  ]
    [ F^T+3I+P   P+R     ].
```

For the four all-odd alternating partitions, `P+Q` is invertible and rank
25 would force a Schur identity whose diagonal support admits no perfect
matching, except for one `3+3` permutation whose forced target is not a
zero-one matching.

For a partition with `e` even parts, put `A=P+Q`, let `N` span `ker(A)`,
put `B=F+3I+P`, and let `W` span `ker(N^T B)`. The Wave 40 boundary is
`rank(N^T B)=e`. Exact singular Schur elimination proves that equality in
the rank-25 bound is equivalent to

```text
W^T R W = W^T(B^T A^- B-P)W.
```

A discovery implementation and a clean-room verifier independently cover
all seven even-part types:

```text
minimum-projection permutations: 164928
distinct right kernels:               52
distinct equality targets:        164278
grouped matching evaluations:      540540
rank-25 survivors:                       0.
```

Together with the four all-odd exclusions, this covers all eleven positive
partitions of six. Every hypothetical target therefore satisfies

```text
rank_F7(M)>=26.
```

This is a universal necessary condition and does not assume `n3=4158` or a
graph automorphism. At the prism-free endpoint it removes `r7=25`, leaving
314 arithmetic `(r3,r7)` pairs. It does not exclude the endpoint or improve
the general upper bound on `n3`.

The same analysis identifies a universal obstruction to simply adding local
block ranks. For every graph vertex `v`,

```text
(J-I-2A)(A+4I)e_v=0 mod 7.
```

For each base triangle, its three vertex-star vectors are independent,
supported inside the corresponding 39-point block, and annihilated by all
outside columns. An exact two-triangle individual-column relaxation has
minimum kernel-signature span one and hence supplies only rank 35.

Under the narrower joint hypotheses `n3=4158`, `r3=12`, and every edge of
type `222`, all eight boundary quotients form one strict fibre-coloured
isomorphism class. Each has 37,378 triangle-free lifts with 39-block ranks
`33^264,34^7348,35^29766`. Thus this branch has even `r7>=34`. The sixty
outside vertices and global overlap equations remain the unresolved wall.

### Wave 42 rank-26 equality and universal rank 27 (`VERIFIED`)

Keep the Wave 41 notation and write the exact symmetric decomposition as

```text
rank(K39)=rank(S)+2 rank(F)+rank(D),
```

where `D=Z^T W_R Z-T` is the residual on the right kernel of `F`. For a
partition with `e` even parts,

```text
rank(S)=25-2e,  rank(F)>=e.
```

Wave 41 excluded rank 25. Hence

```text
rank(K39)=26  iff  rank(F)=e and rank(D)=1.
```

For all seven even-part types, an independent clean-room implementation
regenerates every minimum-`F` permutation and all labelled third-fibre
matchings:

```text
minimum-F permutations:              164928
distinct right kernels:                  52
labelled permutation/matching pairs: 1714426560
rank-at-most-one residuals:                   0.
```

For the four all-odd types, `e=0`. A complete pivot/mate CSP covers

```text
4 * 12! * 10395 = 19916886528000
```

labelled pairs and has zero compatible leaves. A nonzero symmetric rank-one
matrix over `F_7` has a nonzero diagonal pivot, so the pivot identities cover
every rank-one possibility. The verifier includes rank-zero, rank-one,
rank-two, zero-diagonal, hostile-mutation, and reduced-universe controls.

All eleven local types therefore satisfy

```text
rank_F7(K39)>=27.
```

Principal-block monotonicity and the verified rank transport imply the
universal theorem

```text
rank_F7(M)>=27.
```

No endpoint or automorphism hypothesis enters this theorem. At `n3=4158`,
the constraints `12<=r3<=44`, `27<=r7<=44`, and `r3+r7` even leave 297
arithmetic pairs. If `r3=12`, then `r7` is even and at least 28.

### Wave 42 canonical joint-incidence reduction (`VERIFIED_SCOPED`)

Assume jointly `n3=4158`, `r3=12`, every edge has type `222`, and the
canonical rank-33 lift mask is `51739`. Its 36-vertex core has components of
orders 12 and 24, meeting each of the three twelve-point fibres in `4+8`
vertices.

For the 36-by-60 outside incidence matrix `B`, the forced Gram identity is

```text
BB^T=12I-A_X+2J-RR^T-A_X^2.
```

The small-component intersection sizes have sum 120 and squared sum 240.
Cauchy has the same lower bound `120^2/60=240`, so every outside column uses
exactly two small-component and four large-component vertices. Every column
also selects one nonmatching pair from each fibre, and every one of the
sixty such pairs per fibre is used exactly once. The component patterns occur
with multiplicities

```text
4 each:  (2,0,0), (0,2,0), (0,0,2)
16 each: (1,1,0), (1,0,1), (0,1,1).
```

Exhaustive, unrestricted filtering gives

```text
all pair triples:                    216000
forced Gram support:                 118718
component equality:                   49736
pointwise mixed-equation feasibility: 45032.
```

Two distinct 60-entry certificates realize the complete two-fibre
concurrence target. Thus no contradiction exists at that projection level.
If a full `B` exists, its unordered column-pair overlaps are
`458/1004/308` at sizes `0/1/2`. A compatible simple eight-regular outside
graph `H` must use `96/144/0` such pairs as edges and have 32 triangles and
181 four-cycles. A full `B` and compatible `H` remain unknown.

### Wave 42 branch-15 seventh-triangle delta (`VERIFIED_SCOPED`)

The frozen refined branch-15 OPB directly contains the unit `x2=1`.
Under the rooted labelling, `x2` joins residual labels `(0,2)` and `(0,4)`;
together with coordinate label 0, represented by full vertex 1, these give
the full zero-based graph triangle `[1,15,17]`.

At the prism-free endpoint, forbidding every prism based at this triangle
adds

```text
64932 = 132 width-3 + 64800 width-5
```

exact negative clauses. A clean-room replay of the source OPB closure forces
830 variables, including 174 primary edges, and simplifies the new family to

```text
33778 = 91 width-3 + 580 width-4 + 33107 width-5.
```

The full normalized raw and active clause streams exactly match discovery.
There is no active unit or empty clause. This is a stronger formula for one
refined endpoint branch, not a SAT or UNSAT result; endpoint proof coverage
remains `0/33`.

### Wave 43 conditional endpoint rank 28 (`VERIFIED`)

At `n3=4158`, the absence of induced triangular prisms leaves exactly the
four edge-local partitions `222`, `24`, `33`, and `6`. Retain the Wave 42
formula

```text
rank_F7(K39) = (25-2e) + 2 rank(F) + rank(D),  rank(F)>=e.
```

Local rank 27 can occur only through

```text
rank(F)=e,   rank(D)=2,
```

or

```text
rank(F)=e+1, rank(D)=0.
```

Complete exact enumeration excludes both mechanisms for `222`, `24`, and
`6`. For `33`, where `F=0`, every symmetric rank-two residual has an
invertible principal `2 x 2` minor; the complete principal-pivot/mate CSP has
zero leaves. Independent reconstruction agrees on all 36 compared counts and
streams and accepts planted type-`6` rank-zero and type-`33` rank-two
controls. Hence every endpoint local block has rank at least 28, and
principal-block monotonicity gives

```text
n3=4158  ==>  rank_F7(M)>=28.
```

Using `n3+3P=4158`, where `P` is the induced triangular-prism count, the
contrapositive refinement is

```text
rank_F7(M)=27  ==>  P>=1  ==>  n3<=4155.
```

This does not give a strict general upper bound because the endpoint remains
compatible with `28<=rank_F7(M)<=44`. The endpoint arithmetic census is 281
pairs with `12<=r3<=44`, `28<=r7<=44`, and `r3+r7` even.

### Wave 43 all-rank-33 lift reduction (`VERIFIED_SCOPED`)

Under `n3=4158`, `r3=12`, and all edges type `222`, every one of the 264
canonical triangle-free rank-33 lifts has:

```text
component sizes:       12 + 24
fibre balances:        (4,4,4) + (8,8,8)
forced Gram rank:      33
rational kernel:       two fibre differences + one component contrast.
```

Cauchy equality forces every outside six-set to use two vertices from the
small component and one nonmatching pair from each fibre. The five numerical
support/component/mixed candidate censuses occur with multiplicities

```text
(118718,49736,45032): 48
(131908,54560,49328): 48
(132196,54736,49520): 24
(132250,54560,49328): 48
(132402,54648,49424): 96.
```

These are numerical classes, not asserted isomorphism classes. Every lift
survives, and no simultaneous 60-column `B` or compatible outside graph `H`
is known.

### Wave 43 branch-15 two-triangle cuts (`VERIFIED_SCOPED`)

At the frozen Wave 42 closure, the 924 coordinate-anchored triangle candidates
split as `7` true, `157` false, and `760` unfixed. Exhausting all 288,420
unordered pairs and 1,556,994 compatible matching visits gives 40,800
distinct width-four prism clauses. None duplicates a Wave 37 or Wave 42 raw
row. Closure satisfies 6,460 and leaves 34,340 active clauses, all with slack
three. Sixty-four selected polarity probes yield no contradiction or new
implication. This is a complete result for the named clause family only.

### Waves 43--44 order-seven count-space controls (`VERIFIED_SCOPED`)

The unrooted order-seven system has 208 locally admissible graph types, 62
six-to-seven deletion rows, 19 Hamiltonian rows, and the integer variable
`y=h11/4`. At `n3=4158`, `y=4158`, an exact nonnegative 99-support solution
satisfies every row and totals

```text
binom(99,7)=14887031544.
```

All three seven-vertex types containing an induced triangular prism have
count zero. This is a count vector, not a graph.

Wave 44 adds seven vertex-root rows, 36 ordered-edge-root signature rows, and
46 ordered-nonedge-root rows. For an ordered edge, the remaining 97 vertices
have adjacency categories `(1,12,12,72)`; for an ordered nonedge they have
categories `(2,12,12,71)`. Thus the right-hand side for signature
`(a,b,c,d)` is respectively

```text
99*14*C(1,a)C(12,b)C(12,c)C(72,d)
```

or

```text
99*84*C(2,a)C(12,b)C(12,c)C(71,d).
```

The full 170-row system has coefficient rank 93 over each of
`F_101,F_103,F_107`. Although the unrooted witness fails all three new rooted
families, a different exact 91-support integer witness at `y=4158` satisfies
all 170 rows. A floating-point MILP report of infeasibility is therefore
refuted. Aggregate rooted counts still forget which overlapping subsets must
be realized simultaneously; positive-semidefinite flag moments or explicit
cross-block compatibility are the next missing layer.

### Wave 45 rooted flag moments (`VERIFIED_SCOPED`)

For each labelled root embedding, let `z` be the vector of induced
four-vertex rooted-flag counts. Every graph supplies the Gram matrix

```text
M_flag = sum z z^T,
```

so every integer vector `c` obeys `c^T M_flag c>=0`. Retaining the complete
overlap of two flags yields exact matrices of sizes `17`, `16`, and `19` for
a vertex, ordered edge, and ordered nonedge root. Their entries use unrooted
induced counts through orders seven, six, and six respectively.

A clean-room enumeration matches all 484 class-matrix records and 16,660
nonzero ordered coefficients. The Petersen and Clebsch controls agree by
direct outer products. The vertex-root matrix has six exact negative
directions on each of the Wave 43 and Wave 44 aggregate witnesses, refuting
those two count vectors. The pair-root matrices are PSD of rank one on both
because lower-order counts are already fixed.

The immutable v1 continuation contains 17 reconstructed cuts and 15 exact
intermediate witnesses. Each witness satisfies the original 170 rows and all
prior cuts; each new cut rejects its source. The following solver call timed
out, so this is a verified finite obstruction sequence, not an endpoint
exclusion or a strict upper bound.

Each of the two central diagonal nonedges of the four-cycle in any `N3`
2-percolates the whole graph. The seed first infects the other two vertices of
the four-cycle and then the two remaining triangle vertices. The closure classification of
Ibrahim--LaFayette--McCall leaves only a proper `srg(9,4,1,2)` closure, but the
unique `K3 square K3` contains no induced `N3`. Therefore

```text
m(G,2) = 2.
```

For normalized triangles `{x,u,v}`, `{a,b,c}` with cross-edges `xa,ub`, the
only outside two-neighbor profiles, with multiplicity, are

```text
xa:1, ub:1, xc:1, uc:1, va:1, vb:1, vc:2.
```

The singleton profile is `(9,9,8,9,9,8)`, and 33 outside vertices see none of
the six. From seed `{x,b}`, synchronous percolation wave 1 is exactly `{u,a}`
and wave 2 is exactly `{v,c,P_xa,P_ub}`. Later waves may contain additional
vertices beyond the remaining six pair-profile vertices.

Fixing one labeled `N3` is an existentially safe search normalization: a
putative graph has an occurrence that can be globally relabeled. This does not
claim that occurrences form one automorphism orbit. The complete derivation
and source boundaries are in `agents/2026-07-22-wave3-prior-art.md`; the
single-unit implementation and branch-interaction guards are independently
checked in `verification/2026-07-22-n3-normalization-audit.md`.

## Rooted counts (`DERIVED`)

For a root `x`, write `N1=N(x)` and `N2=V-(N1 union {x})`. The induced graph
on `N1` is `7 K_2`, and `N2` is the 12-regular 84-vertex residual graph from
[CONJECTURE.md](CONJECTURE.md). It has:

- 504 internal edges;
- 84 triangles with one vertex in `N1` and two in `N2`;
- 140 triangles entirely inside `N2`; and
- five fully residual triangles through each residual vertex.

For residual labels `p,q`, let `t=|p intersection q|`, which is 0 or 1. Their
required number of common residual neighbors is:

| label relation | residual edge? | common residual neighbors |
|---|---:|---:|
| `t=1` | yes | 0 |
| `t=1` | no | 1 |
| `t=0` | yes | 1 |
| `t=0` | no | 2 |

## Triangle-intersection graph (`DERIVED`, literature-aligned)

Create a graph `T` whose 231 vertices are the triangles of the putative graph,
joining two when they share a vertex. If `N` is the 99-by-231 vertex-triangle
incidence matrix, then

```text
N N^T = A + 7 I,
N^T N = 3 I + adjacency(T).
```

It follows that `T` is 18-regular with forced spectrum

```text
18^1, 7^54, 0^44, (-3)^132.
```

This viewpoint agrees with Petro and Phillips' clique-graph treatment. It is
another exact formulation, not currently a construction.

## Automorphism restrictions (`CITED`, not independently recomputed)

The strongest combined published restrictions in the current audit imply

```text
Aut(G) is one of: trivial, C2, C3.
```

An order-three action would be fixed-point-free. This summary combines results
of Wilbrink, Behbahani--Lam, Crnkovic--Maksimovic, and Cesarz--Woldar; see
[SOURCES.bib](SOURCES.bib) and the dated literature report under `agents/`.

The full project never assumes one of these groups. The automorphism group of
the rooted *uncompleted scaffold* is `C2 wreath S7`; using it to select one
representative from equivalent rooted labelings is safe. Requiring any of it
to survive as an automorphism of the completed graph is not safe.

## Exact residual pair table (`DERIVED`)

The 84 residual labels have 924 intersecting unordered pairs and 2,562
disjoint unordered pairs. The block equations force this complete table:

| labels | residual edge? | common residual neighbors | pair count |
|---|---:|---:|---:|
| intersect | yes | 0 | 84 |
| intersect | no | 1 | 840 |
| disjoint | yes | 1 | 420 |
| disjoint | no | 2 | 2,142 |

Thus each residual vertex has two intersecting-label neighbors, ten
disjoint-label neighbors, 20 intersecting-label nonneighbors, and 51
disjoint-label nonneighbors.

The 84 intersecting-label edges form a 2-regular graph with no triangles. The
420 disjoint-label edges split among 140 edge-disjoint residual triangles. For
every residual vertex `u`, its induced neighborhood is

```text
5 K_2 disjoint-union 2 K_1.
```

The two isolated neighbors are precisely its intersecting-label neighbors.

There are 1,071 four-cycles wholly inside the residual graph, and every
residual vertex lies in 51 of them. This follows because only the 2,142
disjoint-label nonedges have two residual common neighbors; each residual
four-cycle is counted by its two diagonals.

## Seven forced multiple-of-four cycle systems (`DERIVED`)

For a root-neighbor coordinate `a`, let `F_a` be the 12 residual labels that
contain it. For each of the seven matched coordinate pairs `a,mate(a)`, the
partition

```text
F_a, F_mate(a), remaining labels
```

is equitable with quotient matrix

```text
[1 1 10]
[1 1 10]
[2 2  8].
```

Both fiber-induced graphs and the bipartite graph between the two fibers are
perfect matchings. The induced graph on their 24 vertices is a 2-factor. Its
cycles alternate same-side and cross edges, and a closed cycle uses an even
number of cross edges. Every component length is therefore divisible by four.

The possible cycle-length multisets are exactly the 11 partitions of 24 into
multiples of four. This is a pruning condition with no completed-graph symmetry
assumption. Its novelty in the literature has not been established.

These 11 multisets are only coarse cycle types. They are not 11 orbits of the
full 24-vertex configuration under the scaffold stabilizer, so fixing one
24-vertex representative per multiset would be an unsafe symmetry reduction.
The separate 11-branch split in `attempts/2026-07-22-eleven-branch-cover.md`
fixes a matching inside one 12-vertex fiber and is not this rejected shortcut.

## Residual spectrum (`DERIVED`)

Let `B` be the residual adjacency matrix and `C` the fixed endpoint-incidence
matrix. Since

```text
C C^T = 11 I + J - M,
```

`B` acts on `im(C^T)` with eigenvalues `12^1, (-2)^6, 0^7`. On `ker(C)`, the
block equation gives `B^2+B-12I=0`. Dimension and trace then force

```text
spectrum(B) = 12^1, 3^40, 0^7, (-2)^6, (-4)^30.
```

In particular, a putative residual graph is connected.

## Endpoint-fiber incidence (`VERIFIED`)

For a root-neighbor coordinate `a`, let `F_a` be the 12 residual labels
containing `a`, and let `W_a` be the 60 labels containing neither `a` nor its
mate. The map

```text
w -> N_B(w) intersection F_a
```

is a bijection from `W_a` to the 60 nonedges of the perfect matching
`B[F_a]`. Thus `B[F_a,W_a]` is the vertex-edge incidence graph of
`K_12-6K_2`.

Coupling the corresponding bijections for `a` and its mate gives a 12-by-12
nonnegative integer matrix `R` with entry sum 240. Consequently

```text
sum binom(R[u,v],2) >= 96.
```

Each counted pair defines a residual four-cycle separated by that root-matched
coordinate pair. This supplies at least 96 distinct such cycles per root group,
but cycles may be counted for multiple groups, so it is not a contradiction.

Wave 3 sharpens the count. For each root group there is an integer
`0<=z_g<=24` such that the exact number of separated cycles is

```text
S_g = 96 + z_g.
```

Thus the seven groups give at most 840 separation incidences, and at least 231
of the 1,071 residual four-cycles are not separated by any group. The same
block algebra yields a matching-plus-2-regular packaging of selected residual
edges and the exact number of residual four-cycles through each relation type:

```text
(Q,D) = (1,0),(1,1),(0,0),(0,1),(0,2)
cycles =   10,   11,    8,    9,   10.
```

See `agents/2026-07-22-wave2-structural.md` for the endpoint bijection and
`agents/2026-07-22-wave3-fiber-coupling.md` for the independently checked
coupling identities and scope warnings.

## Conditional alpha-22 design reduction (`VERIFIED`)

If a putative graph has an independent set of size 22, its other 77 vertices
define a simple `2-(22,4,2)` design with point-block incidence matrix `N` and
an outside adjacency matrix `D` satisfying

```text
NN^T = 12I+2J,
ND = -N+2J.
```

Writing `G=N^T N` and `X=4D+16I-G`, the remaining SRG equation is exactly

```text
X^2=28X.
```

Equivalently, for symmetric hollow Boolean `D` satisfying the linear
incidence equation, it is enough to impose

```text
D+4I >= 0,
33I-11D+J >= 0.
```

A compatible `X` would be 28 times a rank-33 projector. The design's
intersection-one graph consists of 22 edge-disjoint perfect matchings, while
its disjoint-block edges form 77 triples of pairwise-disjoint blocks, a linear
`77_3` configuration.

The repository includes an exact cyclic `2-(22,4,2)` certificate with block
intersection histogram `1155/1540/231`; this shows the design equations alone
are consistent. No compatible `D` is known, and this one design does not cover
the alpha-22 case. See `agents/2026-07-22-wave3-coclique-design.md`.

## Modular and integral constraints (`VERIFIED`)

Conditional on existence, the full adjacency matrix has

```text
rank_F2(A) = 54,
rank_F3(A) = 45,
SNF(A) = diag(1^45, 3^9, 6, 12^43, 84).
```

The residual adjacency matrix has exact modular Jordan forms

```text
over F2: 1^40 + J_3(0)^6 + 0^26,       rank 52;
over F3: 1^6 + 2^30 + J_2(0)^7 + 0^34, rank 43.
```

Its top nonzero determinantal divisor is

```text
Delta_77(B) = 2^49 * 3^34.
```

This determines 25 nontrivial 2-primary torsion factors with total valuation
49 and 34 factors equal to `Z/3`; it does not determine the individual
2-primary exponents.

Over `F2`, `im(A)` is an even LCD `[99,54]` code and `ker(A)` is its LCD
`[99,45]` dual. Both have minimum weight at least eight. A weight-eight dual
word must support an independent eight-set, with every vertex meeting that set
in zero or two points. Over `F3`, `im(A)` is an LCD `[99,45]` code.

Full derivations and the independently checked boundaries are in
`agents/2026-07-22-wave2-algebra-codes.md` and
`verification/2026-07-22-wave2-audit.md`.

## Waves 60--63: component, finite-field, invariant-SDP, and cone boundary

All statements in this section are conditional on the prism-free endpoint
`n3=4158`.

### Three-component incidence design (`VERIFIED SCOPED`)

For the `[4,4,4]` component partition of the fixed-triangle graph `X`, exact
coordinate normalization gives

```text
216 presentations -> 50 accepted -> 18 fibre-preserving types.
```

The 1,140 unordered triples with repetition reduce to 275 orbits under safe
simultaneous coordinate relabelling. This is not an assumed automorphism of a
completed graph. Each triple has 15,936--27,200 individually allowed
six-set columns. The exact `F2` target-rank histogram is

```text
rank:     14   16   18   20   22   24
triples:  67  415  412  185   51   10.
```

No triple is excluded. For the aligned type-4 triple, two independent
enumerations give 20,928 candidate columns and all 21 component/fibre
patterns.

### Finite-field boundary (`VERIFIED WITH CORRECTION`)

Every candidate column meets each of three fibres and each of three
components twice. Over `F2`, the six partition indicators span a
five-dimensional subspace of `ker(B^T)`, so `rank(B)<=31`. Since every row
has weight ten, `BB^T` is alternating and has even rank at most 30.

All 1,140 targets survive:

- the 198 within-component pair-coordinate span;
- the complete 630 pair-coordinate span;
- the 21-pattern parity-moment system;
- the quadratic/Witt screens over `F2`; and
- the stated odd-prime screens for `p=3,5,7,11`.

The full 630-coordinate generator-rank histogram is

```text
rank:     438  442  446  450  454  458  462
triples:   56  189  333  327  171   54   10.
```

The identity

```text
sum_{k not in {i,j}} T_ijk = 4 G_ij
```

and its displayed scalar totals are verified. The discovery phrase “all
consequences determined by `G`” was too broad: no nonnegative integral tensor
`T` was constructed or excluded.

### One-root invariant SDP (`VERIFIED SCOPED`)

The 84 signed edges of `K7` form a six-class commutative scaffold scheme with
valencies

```text
1,2,1,20,20,40
```

and primitive multiplicities

```text
1,6,7,14,21,35.
```

Scaffold symmetry is used only to average universally positive-semidefinite
matrices. No target automorphism is assumed. The endpoint relation counts
depend on an integer `0<=y<=42`. Every such value survives the exact
projector SDP. A degree-24 Schur family checks 1,949 nontrivial averaged
matrices and 23,388 exact scalar blocks, with zero negative blocks. Including
the deliberately omitted tautological matrix changes the counts but supplies
no negative block.

### Rational pair cone (`VERIFIED SCOPED`)

A fixed stress set of 74 component triples contains all 56 minimum-support
lanes, the unique maximum-support lane, all 18 diagonal lanes, and the first
representative of every full-pair rank stratum, with eight overlaps removed.
For every lane there is an exact nonnegative rational vector on allowed
six-sets satisfying all 630 pair equations. Every coefficient also satisfies
`x_s<=1`, and the support sizes 438--462 match the full-pair binary generator
ranks.

These are fractional points, not zero-one designs. No integer `36 x 60`
incidence matrix, compatible `A_Y`, endpoint graph, or endpoint exclusion is
known. The rigorous interval remains

```text
708 <= n3 <= 4158.
```

## Waves 64--65: rooted transition design and hypergraph algebra

All statements here are conditional on the prism-free endpoint `n3=4158`.
Fix a root. Its 14 neighbors form seven mate pairs, and the 84 residual
vertices are canonically the edges of

```text
H=K14-7K2=K_{2,2,2,2,2,2,2}.
```

Residual edges between intersecting `H`-labels form a perfect matching on the
twelve labels through each base point. After excluding the six
prism-forbidden pairs, each base point has exactly 6,040 possible transition
matchings, drawn from 60 allowed transitions. Globally there are 840
transition variables.

Every other selected residual edge joins disjoint labels and lies in a unique
residual triangle. Thus those 420 edges form 140 blocks, each a three-edge
matching of `H`, and every `H`-edge lies in five blocks. The 35,560 candidate
blocks have exact five-type census

```text
(0,0,3): 6720,  (0,1,2): 20160,  (0,2,1): 6720,
(0,3,0): 280,   (1,0,2): 1680.
```

For each root mate pair, the selected-block occupancy is forced to

```text
(n0,n1,n2)=(32,96,12).
```

An explicit 140-block witness satisfies the block-only master. The stronger
linear transition/block master remains rationally feasible under the exact
scaffold-invariant assignment

```text
z_(0,0,3)=1/120, z_(0,1,2)=1/240, t=1/10.
```

This checks every one of the 1,176 endpoint-profile rows and proves that this
linear relaxation has no Farkas contradiction.

For binary variables, put `Q_pq=|label(p) intersect label(q)|`. The exact
remaining residual condition is

```text
sum_{r != p,q} x_pr*x_qr = 2-Q_pq-x_pq.
```

Together with the rooted scaffold and pair simplicity, these quadratic rows
complete the strongly regular graph equations. They do not separately enforce
global prism-freeness away from the root.

For the algebraic orientation, write `B=T+D`, where `T` is the transition
2-factor and `D` is the point graph of the selected block hypergraph. With
84-by-140 incidence matrix `Z` and block graph `R=Z^T Z-3I`,

```text
D+5I=ZZ^T,
lambda_min(R)>=-3,
mult_R(-3)>=56,
c4(R)=1260+c4(D),
1260<=c4(R)<=2331.
```

The target spectral projectors give

```text
64/5<=tr(T E3)<=16,
5376<=tr(B^3 T)<=5712,
tr(B^4 T)+3tr(B^3 T)=52416.
```

All 258 scaffold-averaged PSD lanes survive. A separately checked local
control satisfies the unlabelled hypergraph and local-graph conditions but
has target-moment errors

```text
degree 4: +5496, degree 5: -12020, degree 6: +239772.
```

The first missing invariant is therefore the entrywise, noncommutative
placement of `Z` and `T` relative to the fixed line graph `Q`, not another
scalar or one-root averaged moment.

```text
transition/design and hypergraph finite claims: VERIFIED SCOPED
integral strong witness:                       UNKNOWN
full residual codegree compatibility:          UNKNOWN
strict upper bound below 4158:                 NOT PROVED
Conway-99 / novelty:                           UNKNOWN
```

## Waves 130 and 132--134: Jacobi, code-enumerator, and topology shifts

Three independent changes of mathematical language sharpen the current
boundary without resolving the graph.

The Jacobi-form lane translates rank constraints into a finite system of
linear equations and inequalities for Fourier coefficients. At cutoff 28,
an exact rational point satisfies all 454 equations and 1,686 inequalities.
Thus this finite approximation is consistent and cannot exclude rank 28.

The binary-code lane studies the row space of the hypothetical adjacency
matrix over the field with two elements. Keeping intersections with the 99
distinguished neighborhood rows forces the three highest possible image
weights to vanish:

```text
A94=A96=A98=0.
```

This refutes the first ordinary weight-enumerator point, but a stronger
rational split-enumerator point survives. Integrality and realization by an
actual code remain open.

For a graph triangle, the twelve outside neighbors attached to each of its
three vertices form three fibres. Pairwise perfect matchings between these
fibres compose to a permutation `h_T`. Its fixed points are exactly induced
triangular prisms based at the triangle. At the prism-free endpoint every
`h_T` is therefore a derangement, and the exact global sign identity is

```text
product_T sign(h_T)=(-1)^(chi+E-F).
```

Both signs occur in exact local controls. A connected, nonorientable abstract
surface with the endpoint aggregate counts realizes the parity data, so
parity by itself cannot exclude the endpoint. A successful continuation must
couple the edge-twist/orientability data back to point-level graph equations.

The quaternary lane keeps the adjacency rows over `Z/4Z`, rather than reducing
all overlap counts modulo two. Smith normal form forces

```text
C=row_Z4(A): 4^54 2^1,
Cperp:       4^44 2^1.
```

Translation by the common order-two word `2*1` exchanges the numbers of zero
and two symbols. Complete coefficient patterns on at most three graph rows
force 84 symmetrized compositions and 8,557,760 distinct words; the analogous
dual closed-row patterns force 44 compositions and 4,126,784 words. The
corrected sparse MacWilliams system has

```text
1119 primal orbits,
1114 allowed dual orbits,
161 forbidden dual orbits.
```

The exact transform and forced tables are verified, but the corrected
rational and integral feasibility problems have not been run. They remain
`UNKNOWN`, so no quaternary code or graph is claimed.

```text
cutoff-28 finite Jacobi relaxation:             VERIFIED FEASIBLE
distinguished rational split-enumerator:        VERIFIED FEASIBLE
endpoint aggregate holonomy parity obstruction: REFUTED
quaternary transform and forced tables:          VERIFIED
corrected quaternary rational/integral system:   UNKNOWN NOT RUN
rank 28 / prism-free endpoint / Conway-99:       UNKNOWN
rigorous interval:                               708 <= n3 <= 4158
```

## Waves 135--142: quadratic forms, graph codes, and interlace data

### Tightened quaternary face (`VERIFIED UNKNOWN WALL`)

Wave 135 reconstructs the corrected 1,119-variable `Z/4Z` scalar model
exactly.  The forbidden dual rows have equality rank 143 and nullity 976.
Normalization and the code-size rows raise the affine rank to 145.  The
previously omitted primal torsion-shell equation

```text
sum_(primal states with b=0) coefficient = 2^54
```

is independent and raises the rank to 146, leaving affine dimension 973.
The analogous dual torsion sum is redundant.  Exact rational row generation
ends `UNKNOWN_WALL` in both the unshifted and torsion-tightened runs.  No
nonzero Farkas vector, rational primal, integral enumerator, code, or graph is
present.

### Binary Arf and signed Krawtchouk branches (`VERIFIED FORMAL`)

For `R=im_F2(A)`, define

```text
q(x)=wt(x)/2 mod 2.
```

The restriction of `q` to `R` is nondegenerate, so its Gauss sum is

```text
G_R=epsilon*2^27, epsilon in {+1,-1}.
```

For a `t`-set `T`, exact graph algebra gives

```text
q(A 1_T)=t+e(T) mod 2
```

and hence

```text
M_t=sum_(w even)(-1)^(w/2)K_t(w)A_w=G_R*S_t,
S_t=sum_(|T|=t)(-1)^(t+e(T)).
```

Independent reconstruction gives

```text
S0=1, S1=-99, S2=3465, S3=-56595,
S4=462924, S5=-1821204.
```

Both Arf signs have exact rational formal witnesses through `S5`, including
all ordinary MacWilliams rows, the four distinguished split systems, and all
approved absolute shadow bounds.  These witnesses are not integral
enumerators or codes.

Over the two-adic completion, the even hyperplane has negative Arf sign and
the rank-54 `3`-eigenspace lattice gives the bridge

```text
epsilon_R=(2/det U).
```

Opposite-sign local controls have the same recorded rank, spectrum, Smith
factors, and coarse discriminant group, but different full discriminant
forms.  They are not integral zero-one SRG adjacency matrices.  Thus the
coarse data do not determine the target sign; entrywise and odd-primary
compatibility remain open.

### Bivariate graph-code enumerator (`VERIFIED`)

Define

```text
B[i,j]=#{x in F2^99 : wt(x)=i and wt(Ax)=j}.
```

The exact marginals and symmetries are

```text
sum_j B[i,j]=binom(99,i),
sum_i B[i,j]=2^45 A_j,
B[i,j]=0 for odd j,
B[i,j]=B[99-i,j].
```

The symplectic self-duality of `{(x,Ax)}` gives

```text
B[i,j]=2^-99 sum_(a,b) K_i(b)K_j(a)B[a,b].
```

Output parity and this transform generate `D8`.  Exact Burnside traces give
an invariant dimension of 1,275 in the 5,000 output-even states, hence
equality rank 3,725.  Input complementation leaves 2,500 working variables
and transform rank 1,225.

The exact rows through input weight three are

```text
B[0,*]: 0^1
B[1,*]: 14^99
B[2,*]: 24^4158, 26^693
B[3,*]: 30^70686, 32^41580, 34^36036, 36^8547.
```

Replaying all 62 six-vertex count formulas gives the new target equation

```text
sum_(j even)(-1)^(j/2)B[6,j]
  = 2024484 + (512/3)n3.
```

Every `N3` has outside profile `0^33,1^52,2^8`, so its image has weight 56
and

```text
B[6,56]>=n3.
```

Nonnegativity alone gives only `n3<=6,553,737`.  The bounded floating
row-generation scout has large inactive transform residuals and remains
`UNKNOWN_NUMERICAL`; it is neither a primal nor a dual certificate.

### Interlace/isotropic lift (`PARTIAL PASS WITH VETO`)

The size-refined interlace specialization has exact six-set rows

```text
I60 = 45,845,415 + (4/3)n3
I62 = 470,213,205 - 3n3
I64 = 503,184,528 + (4/3)n3
I66 = 101,286,108 + (1/3)n3
```

and kernel-size moment

```text
sum 2^nullity = 16,459,961,595 + 32n3.
```

All 3,968 diagonal-toggle cells of the isotropic model were independently
replayed.  Its strongest decreasing cell gives only
`n3<=7,609,140`, which is weaker than the established 4,158 cap.  The
interlace data require a support-intersection refinement beyond the
bivariate `B[i,j]` table; no target-specific elimination back to a stronger
`B` inequality is known.

The discovery top-complement claim for sizes 86--91 is vetoed.  The frozen
target evidence proves `d(im A)>=8`, while minimum 14 belongs only to an
unrealized rational formal witness.  The corrected target-forced band is
therefore sizes 92--99.  All local interlace identities above remain valid.

```text
strict upper bound below 4158: NOT PROVED
binary/quaternary/code realization: UNKNOWN
Conway-99 / external novelty: UNKNOWN
```

## Waves 143--146: exact `S6` projection and rooted deck coupling

### Binary `S6` projection (`VERIFIED WITH SCOPE CORRECTION`)

Wave 143 substitutes

```text
S6 = 2024484 + (512/3)n3
```

into the ordinary and distinguished binary enumerator systems.  Exact
rational witnesses survive at `n3=708` and `n3=4158` for both Arf signs.
The weak shadow projection gives only

```text
0 <= n3 <= 838878579/128.
```

An exact `109 x 142` Hermite-normal-form calculation has rank 109 and
nullity 33.  Projecting that equality lattice yields `n3=0 mod 3`, already
known from the graph count identities.

The rational witnesses live in a stronger formal slice with image minimum
14 and dual minimum 15.  A target adjacency matrix proves only
`d(im A),d(ker A)>=8`.  The verifier therefore vetoes every target
implication that uses the stronger zeros.  The HNF calculation is weaker
again: it omits those dual zeros and all inequalities.  Integral
nonnegative feasibility and graph realization remain unknown.

### Exact six-set outside profiles (`VERIFIED NULL BOUNDARY`)

For a six-set `S` with induced class `H`, Wave 144 introduces

```text
z_P = #{x outside S : N(x) intersect S = P}
```

for all 64 subsets `P` of `S`.  The total, six degree rows, fifteen
pair-common-neighbor rows, and output parity exactly enumerate 368 attainable
`(H,wt(A1_S))` cells across all 62 classes.  Four classes have a unique
output weight:

```text
class 1 -> 66, class 3 -> 56,
class 5 -> 46, class 14 -> 36.
```

An explicit 65-cell nonnegative integer aggregate at `n3=4158` satisfies all
62 class marginals, the Wave 141 reciprocity moments through degree three,
and the signed `S6` row.  Clean-room replay verifies all 66 stored local
profiles.  The witness does not assign the same outside vertices to
overlapping six-sets, so it is not a graph.

### Corrected additive-`GF(4)` boundary (`VERIFIED VETO`)

Wave 145 audits the Wave 139 lower-bound merge.  Five raw families collide
and must be summed, giving

```text
(84,0,15): 198
(73,0,26): 8316
(66,0,33): 149688
(62,0,37): 55440
(60,0,39): 462.
```

Using `max` undercounted every one of these states.  The pure-`Y` zeros at
weights 8, 10, and 12 are also unsupported; only
`{2,4,6,94,96,98}` are justified.  The Rains shadow transform is
independently calibrated on all 1,099 simple graphs through order five.
Corrected full feasibility was not solved and remains `UNKNOWN`.

### One-root six-to-seven lift (`EXACT RATIONAL NULL BOUNDARY`)

Wave 146 first requires each positive `z_P` cell to form a locally
admissible induced seven-vertex graph with its outside root.  This is
equivalent to

```text
#{v in P : uv in E(H)} <= 1 if u in P,
#{v in P : uv in E(H)} <= 2 if u not in P,
```

together with the residual pair-capacity rows inside `S`.  It removes 25
weight cells across 16 classes.

Rooted patterns are grouped only under `Aut(H)`.  If `X_(H,w,P)` is their
aggregate count and `Y_K` counts the 208 order-seven classes, exact double
counting gives 944 rows

```text
sum_w sum_(P in orbit P0) X_(H,w,P)
  = sum_K m(K;H,P0) Y_K.
```

The selected Wave 144 profiles violate the two-row identity
`R_(38,8)=2R_(37,12)` by `3,076,026,288`.  This refutes that witness only.
Freeing every local profile still refutes the fixed 65-cell aggregate table,
but the full 343-cell endpoint relaxation has an exact rational witness:

```text
variables:             13,973
equalities:             8,981
integer nonzeros:     110,269
positive coordinates:   2,998
maximum denominator:         4
h11:                     16,632.
```

All equations replay exactly.  The variables remain aggregate: two rooted
seven-set views need not agree on their eight-vertex union.  Consequently
the next genuine compatibility level is a two-root/order-eight model.

### Two-root order-eight flag space (`VERIFIED FINITE MODEL`)

Wave 147 constructs the next level without running a numerical endpoint SDP.
The root is an ordered edge or ordered nonedge, and each flag adds three
unordered free vertices.  Exact canonicalization gives flag bases

```text
ordered-edge root:      66
ordered-nonedge root:   87.
```

Products of two such flags have unions of orders five through eight.  The
complete locally admissible class streams have sizes

```text
order 5: 21, order 6: 62, order 7: 208, order 8: 916.
```

For every class `H` the package records the integer embedding matrix
`C_H^sigma`.  Across both root families this is 2,414 matrices with 272,054
nonzero upper-triangular entries.  The moment expansion is

```text
M_sigma = sum_(h=5)^8 sum_(H in H_h) x_H C_H^sigma >= 0.
```

All 208 ordinary deletion rows

```text
92*x_H7 = sum_K d(H7,K8)x_K8
```

are included.  In each root family an explicit matrix entry has coefficient
`4*n3` and triangular-prism coefficient zero, so the space can address the
upper-bound objective directly rather than only through an aggregate
surrogate.

The `3 x 3` rook graph, `srg(9,4,1,2)`, supplies an exact positive control:
both moment matrices are explicit sums of 36 integer outer products.  The
verifier independently rebuilds 24 representative class matrices and the
complete `N3`/prism matrices, while checking the full artifact's hashes,
record counts, deletion layer, and class streams; it does not recompute all
272,054 stored coefficients independently.  The current package does not add
the stronger marked degree/common-neighbor extension rows, run an endpoint
SDP, or extract a rational dual.  It is an exact finite route to the next
bound attempt, not a bound itself.

## Wave 204: global compatibility and fourth-order star pairs

Wave 204 tested whether the surviving `b=0` face could be closed by local
slot holonomy or by higher projector moments.

The honest flag transition is on triangle blocks:

```text
S -> T,  g(S->T)=z_T-z_S.
```

It is the literal coboundary `dz`, so it telescopes on true block cycles.
Wave 203 does not identify the incoming and outgoing block at an intermediate
center and supplies only partial five-slot maps. Exact relaxed rank-11 `A6`
controls and ambiguous total `S_5` extensions therefore refute center-walk
chaining and determined monodromy from those local premises.

A separate exact relaxed 99-center certificate realizes all frozen
degree/complement, Hilton--Milner, fiber, equality-row, and slot-capacity
data with `b=0`. It is not strongly regular and has no ternary columns or
endpoint code, so it refutes only the local-interface force-`b>0` lemma.

The positive theorem is fourth-order. For adjacent endpoint stars, with
outer biadjacency matrix `N`,

```text
P_xP_yP_x|E_x=NN^T,
h_xy=tr(P_xP_yP_xP_y)=tr((NN^T)^2).
```

Over `F_3`, `h_xy` equals one precisely for edge type `4+2` and zero for
types `6`, `3+3`, and `2+2+2`. It is also the exterior-square projector
trace. Pair trace plus intersection dimension does not determine it.

The independent verifier passed 11 source-blind and five post-source hostile
tests, all 32 submitted manifest entries, and all 28 submitted tests.
The optional repeated-direction 99-projector control was source-replayed but
not independently promoted.

The next exact target is to classify nonedge `h_xy` and derive a
graph-specific global identity for the full fourth-trace matrix. No rank-11
or prism-free endpoint exclusion, `Q>=7060`, strict improvement of
`708<=n3<=4158`, graph, or Conway-99 resolution follows.

## Wave 205: fourth-trace globalization inflection

Wave 205 derives the exact nonedge cross-Gram profiles and exhausts the
normalized `t=6,7` frontier.  Full-rank local controls show that projectivity
does not force `t>=7` and that fixed `t=7` does not determine the fourth
trace.  These are 28-vertex two-center controls, not global graphs.

The global lane proves

```text
H=U K_D U^T,
rank_F3(U)=99,
```

and identifies the missing graph-specific data as the crossing kernel on
`row(U)`, the Hadamard localizers `Q o (D S_x D)`, or the vectors `w_TU`.
Correct tensor coordinate spaces are all larger than 99, and a scoped
control refutes the generic implication `sum_x P_x=0 => H1=0`.

The hostile lane adds a relaxed 99-projector/231-column incidence coupling
whose nonedge fourth traces vary while all edge fourth traces agree.  It
fails projective distinctness and the target `lambda/mu` laws.

A fresh verifier froze nine tests before source exposure and passed eight
more independent post-source tests.  Verdict: `PASS_SCOPED_INFLECTION`.
Actual endpoint nonedge traces, rank 11, `n3=4158`, and Conway-99 remain
`UNKNOWN`.
