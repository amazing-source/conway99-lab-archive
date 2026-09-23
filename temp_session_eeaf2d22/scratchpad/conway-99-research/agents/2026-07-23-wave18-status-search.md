# Wave 18 literature/status audit: proposed `n3=57` exclusion

## Preinspection search-plan freeze

```yaml
role: literature
date_utc_plan_frozen: 2026-07-23T12:41:43Z
git_commit_at_freeze: e78b6f9194d0d7aa2f0e73c4780aa5e042227190
claim_label: UNKNOWN
scope: >
  Current status of Conway's srg(99,14,1,2), and exact prior art for a
  conditional n3>=60 bound, exclusion of n3=57, the consequent induced-C6
  bound 209346, and the particular r=18/r=19 active-point
  spectral/crossing arguments assigned for Wave 18.
inspection_boundary: >
  This plan and the applicability checklist below were written before any
  Wave 18 discovery report was opened. The assigned task text supplied the
  proposed numerical conclusions and the terms r=18/r=19,
  active-point, spectral, and crossing. Earlier public project material
  supplied the frozen target and the convention p6=209286+n3.
```

### Source order

1. Check current primary or maintained sources for an authoritative
   construction or nonexistence proof for `srg(99,14,1,2)`, including
   author/journal/arXiv updates through 2026-07-23.
2. Recheck the primary six-vertex/hexagon-count sources for the definition
   of `n3`, the identity `p6=209286+n3`, and any published lower bound on
   that variable.
3. Search exact numerical statements and notation variants for
   `n3>=60`, `n3>57`, exclusion of `n3=57`, and `p6>=209346`.
4. Search alternate structural language for the proposed `r=18` and
   `r=19` arguments: active labels/points/lines, partner triples,
   multiplicity or profile counts, crossing sets, equitable sets,
   interlacing/Hoffman/expander-mixing bounds, partial quadrangles, and
   local configurations in diamond-free strongly regular graphs.
5. Follow citations and theorem references from any numerical or
   structural near-match and audit the original statement rather than
   relying on snippets or secondary summaries.
6. Only after this freeze and source-first search, inspect the Wave 18
   discovery report solely to compare its exact statement and vocabulary
   against the frozen searches. It will not be treated as literature
   evidence.

### Exact planned query families

```text
"srg(99,14,1,2)"
"SRG(99,14,1,2)" existence OR nonexistence
"Conway 99-graph" proof OR construction OR nonexistence
"Conway's 99-graph" 2026
"Conway-99" resolution
site:arxiv.org "Conway-99"
site:doi.org "99,14,1,2"
"n3 >= 60" graph
"n_3 >= 60" graph
"n3≥60" "strongly regular"
"n_3\geq 60" "strongly regular"
"n3 > 57" graph
"n_3 > 57" graph
"n3=57" "Conway"
"n_3=57" "99,14,1,2"
"exclude n3=57" graph
"209346" hexagons
"209,346" hexagons
"209346" "strongly regular"
"p6=209286+n3"
"209286+n3" graph
"lower bound" hexagons "99,14,1,2"
"six-vertex induced subgraphs" "99,14,1,2"
"active points" "strongly regular graph"
"active point" "partial quadrangle"
"active labels" graph triangles
"active lines" "Conway 99"
"r=18" "Conway 99"
"r=19" "Conway 99"
"r = 18" "srg(99,14,1,2)"
"r = 19" "srg(99,14,1,2)"
"crossing bound" "strongly regular graph"
"crossing edges" "partial quadrangle"
"spectral bound" "active points" graph
"Hoffman bound" "partial quadrangle" subset
"interlacing" "99,14,1,2"
"expander mixing" "99,14,1,2"
"equitable partition" "99,14,1,2"
"regular set" "99,14,1,2"
"intriguing set" "PQ(2,6,2)"
"diamond-free strongly regular" local configuration
"lambda=1 mu=2" active points
"triangle partners" strongly regular graph
"partner triples" "Conway 99"
"point multiplicity" "partial quadrangle" crossing
"degree profile" "Conway 99"
```

Punctuation, Unicode/ASCII inequality, subscript, hyphenation, and variable
variants will also be tried. Citation-graph searches will include the
Conway statement, Wilbrink (1984), Lou--Murin (2014), Reimbayev (2024 and
2025), Cesarz--Woldar (2025), Petro--Phillips (2026), and Keramatipour
(2026).

### Applicability checklist frozen before inspection

Every apparent match must pass all relevant checks:

1. **Ambient object:** Does the theorem concern a finite simple
   `srg(99,14,1,2)` or an exactly equivalent `PQ(2,6,2)` point graph,
   rather than merely another `srg(v,k,1,2)` or a graph of order 99?
2. **Variable identity:** Is its `n3` the same six-vertex induced-subgraph
   variable used in `p6=209286+n3`, with the same labeled/unlabeled and
   induced/non-induced convention?
3. **Logical strength:** Is the result unconditional, conditional on the
   target's existence, or conditional on additional symmetry,
   connectedness, regularity, or a chosen local configuration?
4. **Numerical endpoint:** Does it prove the integer endpoint
   `n3>=60` (and hence exclude 57), rather than `n3>=57`, an average or
   asymptotic bound, or a bound on a differently normalized count?
5. **Hexagon translation:** Does `209346` count induced 6-cycles in the
   same convention? The arithmetic implication must be checked from the
   exact source formula, not inferred from a title or abstract.
6. **Active-set definitions:** Are `r`, active points/labels, crossing
   pairs, and their multiplicities defined exactly as in the proposed
   argument? Coincidental use of `r=18` or `r=19` is not a match.
7. **Spectral hypotheses:** For any subset-size or cut bound, verify the
   matrix, eigenvalues, integrality/rounding, equality conditions, and
   whether the induced graph or ambient graph is being bounded.
8. **Crossing hypotheses:** Verify whether every claimed crossing pair is
   genuinely distinct and forced, and whether hidden assumptions such as
   an automorphism, connected active support, or uniform multiplicities
   enter.
9. **Near-family exclusion:** Explicitly reject results about
   `srg(19,6,1,2)`, `srg(85,14,3,2)`, `PQ(2,10,2)`, generalized
   quadrangles, or other partial-quadrangle families unless an exact
   parameter-preserving implication is proved.
10. **Source quality and date:** Record author, title, publication or
    version date, DOI/URL, access date, exact theorem/page, and whether the
    full text was accessible. Prefer primary manuscripts, journal pages,
    institutional repositories, maintained parameter tables, and author
    repositories.
11. **Status discipline:** A current source calling the problem open is a
    status signal, not proof that no newer resolution exists. A search
    nonhit is `UNKNOWN`, never evidence of novelty or nonexistence.

The target's resolution and the novelty of every proposed Wave 18 statement
remain **`UNKNOWN`** unless an authoritative exact result is located.

## Completed audit

```yaml
role: literature
date_utc: 2026-07-23T12:49:32Z
git_commit: e78b6f9194d0d7aa2f0e73c4780aa5e042227190
claim_label: UNKNOWN
scope: >
  Source-first status and exact-prior-art audit for Conway's
  srg(99,14,1,2), the conditional n3>=60 claim, exclusion of n3=57,
  the induced-C6 endpoint 209346, and the Wave 18 r=18/r=19
  active-point crossing/spectral argument.
inputs:
  - path: agents/2026-07-23-wave18-n3-57-structural.md
    sha256: fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6
    use: >
      Opened only after the search-plan freeze and the initial
      primary-source search; used for exact claim comparison, never as
      literature evidence.
  - path: AGENTS.md
    sha256: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
method: >
  Primary/authoritative source search, citation chasing, exact-string and
  alternate-notation search, followed by theorem-by-theorem applicability
  checks. One apparent resolution was checked directly and its decisive
  counting step was independently falsified.
command: >
  Not applicable: literature search and hand-checkable counting/algebra;
  no solver result or computational certificate is asserted.
outputs:
  - path: agents/2026-07-23-wave18-status-search.md
    sha256: >
      Not embedded because a file cannot contain its own stable digest;
      compute SHA-256 on the completed file at handoff.
limitations: >
  Search nonhits do not prove novelty. Wilbrink's 1984 full text and
  Makhnev's 1988 full text were not reliably extractable in this pass.
  Ben Baker's May 2026 conference abstract was accessible, but no paper,
  slides, or exact theorem statement was located. The mathematical
  correctness of the Wave 18 discovery belongs to the independent
  verifier, not this literature lane.
```

### Bottom line

1. **Conway-99 resolution: `UNKNOWN`.** No authoritative construction or
   valid nonexistence proof was found through the access date
   2026-07-23. A maintained parameter table still marks the parameter set
   with `?`, and primary sources from April 2025 through June 2026 continue
   to describe the existence question as open or as a prospective target.
2. **Exact prior `n3=57` exclusion: `UNKNOWN`.** No exact statement or
   equivalent theorem was found. The November 2025 six-vertex census
   explicitly retains this same `n3` as a free variable.
3. **Exact prior conditional `n3>=60`: `UNKNOWN`.** No exact or
   notation-equivalent published statement was found.
4. **Exact prior induced-hexagon bound `209346`: `UNKNOWN`.** The published
   formula is `p6=209286+n3` for `(n,k)=(99,14)`. Therefore `209346`
   follows arithmetically if `n3>=60` is independently verified, but the
   source itself proves only `n3>=0` and hence `p6>=209286`.
5. **The generic spectral inequality is standard, not a novelty claim.**
   The particular active-set construction, crossing identities, profile
   reductions, and `r=18`/`r=19` endpoint eliminations were not found in
   the searched literature; their novelty therefore remains `UNKNOWN`.
6. **A 2022 proceedings paper is an important false near-match.** Its
   Theorem 28 claims nonexistence of `srg(99,14,1,2)`, but the claim that
   its displayed equation (88) follows from strong regularity is false.
   Thus that paper does not resolve Conway-99. This report gives a short
   local contradiction to the asserted counting premise below.

## 1. Current-status audit

### 1.1 Maintained parameter table

Andries Brouwer's maintained table, [Strongly regular graphs with
51--100 vertices](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html),
lists the row `(99,14,1,2)` with existence marker `?` and spectrum
`3^54, -4^44`. The [table
legend](https://aeb.win.tue.nl/graphs/srg/srgtab.html) explains the
existence column. Accessed 2026-07-23.

This is a strong current-status signal, but a maintained table is not a
proof that a very recent manuscript does not exist.

### 1.2 Recent primary and institutional sources

- Patrick G. Cesarz and Andrew J. Woldar, ["On the automorphism group of
  a putative Conway 99-graph"](https://alco.centre-mersenne.org/articles/10.5802/alco.418/),
  *Algebraic Combinatorics* 8(2) (2025), 379--398,
  [DOI 10.5802/alco.418](https://doi.org/10.5802/alco.418), published
  online 2025-04-24. The abstract and introduction expressly call
  existence an elusive, longstanding open problem. The paper proves
  restrictions on a putative graph's automorphism group, not existence
  or nonexistence. Full text accessible; accessed 2026-07-23.

- Robert R. Petro and Connor M. Phillips, ["On Clique Graphs and Clique
  Regular Graphs"](https://arxiv.org/abs/2502.17845), *Discrete
  Mathematics* 349(3) (2026), article 114862,
  [DOI 10.1016/j.disc.2025.114862](https://doi.org/10.1016/j.disc.2025.114862).
  Example 4, PDF p. 27, calls `(99,14,1,2)` a longstanding existence
  question and conditionally gives the spectrum of its 3-clique graph.
  It does not give an `n3` bound or any Wave 18 active-point argument.
  Full arXiv text accessible; accessed 2026-07-23.

- Connor M. Phillips, ["A Comprehensive Study of Clique Graphs and
  Clique Regular Graphs"](https://arxiv.org/abs/2605.22867), honors
  capstone, May 2026. Chapter 1 says the Conway prize has "yet to be
  claimed" and introduces clique-graph methods as a possible route. It
  contains no exact `n3=57`, `n3>=60`, or `209346` match found by
  full-text search. Full arXiv HTML accessible; accessed 2026-07-23.

- Ali Keramatipour, ["Approaching the Conway-99 problem using SAT
  solvers"](https://arxiv.org/abs/2604.23037), arXiv:2604.23037v2,
  revised 2026-04-28. The abstract says the tested SAT approach cannot
  handle the instance in reasonable time and that better strategies are
  required to find the graph or prove nonexistence. It supplies neither
  a satisfying assignment nor an UNSAT certificate. Full arXiv text
  accessible; accessed 2026-07-23.

- The official program of the [34th Cumberland
  Conference](https://www.auburn.edu/cosam/departments/math/cumberland-conference/home.htm),
  May 16--17, 2026, contains Ben Baker's abstract, ["An Induced
  Subgraph Paradigm for Strongly Regular Graph
  Constructions"](https://www.auburn.edu/cosam/departments/math/cumberland-conference/34th_cumberland_program.pdf),
  program p. 4. It announces upper/lower bounds for disjoint copies of an
  induced subgraph, equality forcing evenly distributed outgoing edges,
  a generalization of Lou--Murin's independence bound, and an application
  to Conway-99. The accessible abstract has no theorem formula,
  `n3`, `57`, `60`, `209346`, `r=18`, `r=19`, active points, or crossing
  identity. Exact-title and author searches located no manuscript or
  slides. This is a genuine methodological near-match whose exact overlap
  is **`UNKNOWN`**, not evidence of either novelty or prior publication.
  Accessed 2026-07-23.

- Hebei Normal University's official announcement for Sergey
  Shpectorov's 2026-06-25 lecture, ["Non-existence of the strongly regular
  graph srg(85,14,3,2)"](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html),
  says the talk will discuss a *possible similar approach* to
  `srg(99,14,1,2)`. The proved/computational target in the announcement is
  `(85,14,3,2)`, not Conway-99. This is a later institutional status
  signal and fails applicability checks 1 and 9 for a Conway resolution.
  Accessed 2026-07-23.

These sources are mutually consistent with the maintained table and with
the absence of an authoritative exact-resolution hit in the final
2026-specific search. The correct conservative label remains
**`UNKNOWN`**, not "proved open."

## 2. Apparent 2022 resolution: direct theorem audit

### 2.1 Source and claim

Hideto Ishihara, ["Theory of the pain of humans
etc."](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_pdf/-char/en),
JSAI Technical Report, Type 2 SIG, 2022 issue AGI-021, article 01,
released 2022-07-14,
[DOI 10.11517/jsaisigtwo.2022.AGI-021_01](https://doi.org/10.11517/jsaisigtwo.2022.AGI-021_01).
The [official issue
page](https://www.jstage.jst.go.jp/browse/jsaisigtwo/2022/AGI-021/_contents/-char/en)
and full PDF were accessible on 2026-07-23.

Theorem 28 on PDF pp. 15--16 asserts that no
`srg(99,14,1,2)` exists. After fixing a vertex `w0`, the proof writes
`L^0_1=N(w0)` and lets `L^0_2` be the 84-vertex residual graph. In a
residual component `H_k`, it fixes `w_k`, lets `H^k_1` be the residual
neighbors of `w_k`, and `H^k_2` the remaining component vertices. Its
decisive premise is:

> every vertex of `H^k_2` is adjacent to exactly two vertices of
> `H^k_1`.

That premise is used to obtain equation (88),
`10 s_k + 11 t_k = 2 b_k`, and the claimed contradiction.

### 2.2 Why equation (88)'s premise is false

The flaw is local and does not assume an automorphism.

1. Since `lambda=1`, `G[N(w0)]` is a perfect matching on 14 vertices.
   Every residual vertex has exactly two neighbors in `N(w0)` because it
   is nonadjacent to `w0` and `mu=2`. Call that unordered pair its
   **root label**.
2. A label cannot be a matched edge: the endpoints of a matched edge
   already have `w0` as their unique common neighbor. Conversely, every
   nonedge `{a,b}` inside `N(w0)` has exactly one residual common
   neighbor, because `a,b` have exactly two common neighbors and one is
   `w0`. There are `C(14,2)-7=84` such nonedges, so the 84 residual
   vertices are in bijection with these labels.
3. Fix the residual vertex `w_k` with label `{a,b}`. Exactly 11 other
   valid labels contain `a`, and exactly 11 contain `b`: exclude the
   matched partner of the endpoint and exclude the label `{a,b}`.
   Hence 22 residual vertices have labels meeting `{a,b}` in exactly one
   point.
4. The vertex `w_k` has only 12 residual neighbors (its other two
   neighbors lie in `N(w0)`). Therefore at least `22-12=10` of those 22
   vertices are residual **nonneighbors** of `w_k`.
5. Let `z` be one such nonneighbor. The pair `w_k,z` already has one
   common neighbor in `N(w0)`, namely the shared label point. Since
   `mu=2`, it has exactly one further common neighbor, and that neighbor
   is residual. Thus `z` lies in the same residual component as `w_k`
   and, after deleting `w_k` and its residual neighbors, lies in
   `H^k_2`. Moreover, `z` has exactly **one**, not two, neighbors in
   `H^k_1`, because a neighbor in `H^k_1` is precisely a residual common
   neighbor of `z` and `w_k`.

So the asserted uniform degree two from `H^k_2` into `H^k_1` is false
for at least ten forced vertices. Equation (88) is therefore not a valid
double count, and the paper's proof does not establish Theorem 28.

The correct labels are:

- "This proof establishes nonexistence": **`REFUTED`**.
- "No `srg(99,14,1,2)` exists": still **`UNKNOWN`**.

The later peer-reviewed 2025 paper and 2026 primary sources continuing to
call the question open are consistent with this direct defect, though the
defect itself is already sufficient to reject the purported proof.

## 3. Exact `n3` and induced-hexagon source audit

### 3.1 Published identity

Reimbay Reimbayev, ["The Lower Bound for Number of Hexagons in Strongly
Regular Graphs with Parameters lambda=1 and
mu=2"](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf),
*e-Journal of Analysis and Applied Mathematics* (2024), 1--14,
[DOI 10.62780/ejaam/2024-001](https://doi.org/10.62780/ejaam/2024-001);
also [arXiv:2409.10620](https://arxiv.org/abs/2409.10620). Full text
accessible; accessed 2026-07-23.

The paper defines `n_i` as the number of induced copies of the graph
numbered `i` in its Figure 3. On PDF pp. 10--12 it identifies `n12` as
the number of induced hexagons and derives

```text
n12 = (1/12) n k (k-2) (2k^2-21k+53) + n3.
```

Its Figure 3/type `N3` is the configuration described in the conclusion
as two triangles connected by two of the three possible matching edges.
For `(n,k)=(99,14)`,

```text
(1/12)(99)(14)(12)(2*14^2-21*14+53)
  = 99*14*151
  = 209286.
```

Thus the exact specialization is

```text
p6 = n12 = 209286 + n3.
```

The source then uses only the tautological `n3>=0` to prove Theorem 3.3.
It conjectures equality (`n3=0`) rather than proving it.

Consequently:

- the formula and the meaning of `n3`: **`CITED`**;
- the numerical specialization `209286+n3`: **`DERIVED`**;
- the implication `n3>=60 => p6>=209346`: **`DERIVED`**, conditional on
  an independently verified premise;
- a published unconditional `p6>=209346`: **`UNKNOWN`**.

### 3.2 November 2025 census keeps `n3` free

Reimbay Reimbayev, ["The Subgraphs of Order Six of the Family of
Strongly Regular Graphs with Parameters lambda=1 and
mu=2"](https://arxiv.org/abs/2508.03377), arXiv:2508.03377v2,
2025-11-03. Full text accessible; accessed 2026-07-23.

The introduction and PDF pp. 1--2 explicitly say that `n3` is retained
as a free variable. PDF p. 5 repeats

```text
n12 = (1/12) n k (k-2) (2k^2-21k+53) + n3,
```

and PDF p. 19 says the value of `n3` is not given; symmetry merely
suggests zero. This later, directly relevant census contains no lower
bound `n3>=60` and no exclusion of the integer 57.

There is a potentially misleading notation collision: the paper also
has a variable `n57`, but that means the count of its 57th enumerated
six-vertex graph `N57`. It is not the assertion `n3=57` and gives no
restriction on that value. This near-match fails applicability check 2.

## 4. Structural and spectral prior-art audit

### 4.1 Closest older triangle-graph treatment

Suzy Lou and Max Murin, ["On the Strongly Regular Graph of Parameters
(99,14,1,2)"](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf),
MIT PRIMES-USA manuscript (2014). Full text accessible; accessed
2026-07-23.

Section 5, PDF pp. 7--8, forms a graph `T` on the 231 triangles of a
putative Conway graph, adjacent when the triangles share a vertex. It
proves that `T` is 18-regular and studies three local counts
`alpha,beta,gamma`, obtaining

```text
alpha + beta = 180,
beta + 3 gamma = 36,
alpha - 3 gamma = 144,
```

with `0<=gamma<=12`, `gamma!=11`, and an obstruction if `gamma=12` at
every vertex. This is the closest located older source using the
triangle graph and local matching/cycle structure.

It does **not** define the Wave 18 variables `q(T)`, active labels,
active points `S_u`, or active set `X`; does not enumerate the nine
`r=14,...,19` profiles; and does not exclude `n3=57`. Its number 18 is
the valency of the whole triangle graph, not the Wave 18 profile
parameter `r`. It is therefore related background, not an exact match.

Petro--Phillips independently packages this triangle object as the
3-clique graph. Example 4 conditionally gives its spectrum for the
Conway parameters as

```text
18^1, 7^54, 0^44, (-3)^132.
```

That result also contains no exact Wave 18 active-set or crossing
argument.

### 4.2 The subset edge bound is a standard Rayleigh estimate

A putative `srg(99,14,1,2)` has adjacency eigenvalues
`14,3,-4`. For any vertex subset `X` of size `m`, decomposing its
indicator into the all-ones direction and its orthogonal complement and
using the second-largest eigenvalue `3` gives

```text
2e(G[X])
  <= 14 m^2/99 + 3(m-m^2/99)
   = 3m + m^2/9.
```

Thus the naked inequality appearing in Wave 18 is a standard spectral
subset-edge estimate and should not be presented as new. It is a
one-line **`DERIVED`** consequence of the known spectrum.

For broader induced-subgraph context, see Rhys J. Evans, ["Bounds for
regular induced subgraphs of strongly regular
graphs"](https://arxiv.org/abs/2202.03700), *Discrete Mathematics*
346(1) (2023), 113154,
[DOI 10.1016/j.disc.2022.113154](https://doi.org/10.1016/j.disc.2022.113154).
That paper surveys and strengthens eigenvalue/interlacing and block
intersection bounds for regular induced subgraphs. It was accessible via
arXiv on 2026-07-23. It does not contain the searched Conway-specific
active set or `r=18`/`r=19` application.

The literature question is therefore not whether the inequality is
known, but whether the following combination is prior art:

- building exactly this `X` from active point supports;
- proving the project-specific minimum-degree/crossing lower bounds;
- combining them with the spectral inequality at `m=27,28`; and
- eliminating the listed `r=18` and `r=19` endpoint profiles.

No exact source for that combination was found. Novelty remains
**`UNKNOWN`**.

### 4.3 Wilbrink, Makhnev, and access limits

- H. A. Wilbrink, ["On the (99,14,1,2) strongly regular
  graphs"](https://research.tue.nl/en/publications/on-the-991412-strongly-regular-graphs/),
  EUT Report 84-WSK-03 (1984), 342--355. The Eindhoven metadata page was
  accessible. A repository PDF is listed at
  `https://pure.tue.nl/ws/files/1856500/688724168091800.pdf`, but reliable
  text extraction was unavailable in this pass. Later sources cite its
  induced-subgraph counting work; no claim about the exact Wave 18
  statements is made here.

- A. A. Makhnev, ["Strongly regular graphs with lambda=1"],
  *Mathematical Notes* 44 (1988), 935--940,
  [DOI 10.1007/BF01158426](https://doi.org/10.1007/BF01158426);
  [Math-Net metadata](https://www.mathnet.ru/eng/mzm4220). Reliable full
  text was not available in this pass. Reimbayev's 2024 conclusion
  attributes to Makhnev a nonexistence result under the special
  `n3=0` condition. That is a restricted near-match, not `n3=57` or
  `n3>=60`; the original theorem was not re-audited here because of the
  access limitation.

## 5. Post-freeze comparison with the Wave 18 discovery report

The Wave 18 discovery report was first opened only after the plan above
was frozen and the source-first pass had located the maintained table,
recent open-status sources, the two Reimbayev papers, Lou--Murin, and the
2022 apparent-resolution paper. Its SHA-256 is recorded in the run
report. It is not cited as literature evidence.

| Exact proposed item inspected after the search | Closest located source | Literature outcome |
|---|---|---|
| `n3=57 => sum_T q(T)=38` and `q(T)=0` or `q(T)>=2` | Reimbayev defines the same `n3`; Lou--Murin has a different local `gamma` | No exact match; **`UNKNOWN`** |
| Nine profiles for `r=14,...,19`, including the two `r=18` profiles and `2^19` at `r=19` | Lou--Murin's triangle graph is 18-regular, but does not use this `r` or these profiles | Coincidental/related number only; **`UNKNOWN`** |
| Active point supports `S_u`, linearity, `sum |S_u|=3r`, active set `X` | General partial-quadrangle and induced-subgraph searches | No exact match; **`UNKNOWN`** |
| After shared-label deletion, crossing matrices have row/column degree 0 or 2; a size-2 point gives a disjoint `K_2,2` | No exact primary result located | **`UNKNOWN`** |
| Fixed-point identity `sum_{v~u} d_H(uv)=2 sum_{T in S_u} q(T)` | No exact-string or notation-equivalent result located | **`UNKNOWN`** |
| Every active label supplies two meeting neighbors and `delta(G[X])>=6` | No exact match | **`UNKNOWN`** |
| `2e(G[X])<=3|X|+|X|^2/9` | Standard Rayleigh/eigenvalue argument | Inequality **`DERIVED`** and standard; exact application **`UNKNOWN`** |
| `|X|>=27`, contradiction for `r<=17`, equality analysis at `r=18`, and `m=27,28` analysis at `r=19` | Baker's abstract is the closest recent induced-subgraph methodology, but supplies no theorem text | Exact prior art **`UNKNOWN`** |
| Combining a verified `n3=54` exclusion with a verified `n3=57` exclusion to get `n3>=60` | No source found making this combination | **`UNKNOWN`** pending both proof verification and prior-art resolution |
| `p6>=209346` from `n3>=60` | Reimbayev's exact identity | Conditional arithmetic **`DERIVED`**; exact published endpoint **`UNKNOWN`** |

This comparison says nothing about whether the discovery proof is
correct. It says only that no exact prior statement was located and that
the generic spectral ingredient is already standard.

## 6. Search log and alternate-notation audit

### 6.1 Executed status and numerical queries

All exact query families in the frozen plan were run, including ASCII
and Unicode inequality, subscript, spacing, comma, hyphen, and possessive
variants. The highest-value exact searches included:

```text
"srg(99,14,1,2)"
"SRG(99,14,1,2)" existence OR nonexistence
"Conway 99-graph" proof OR construction OR nonexistence
"Conway's 99-graph" 2026
"Conway-99" resolution
site:arxiv.org "Conway-99"
"Conway 99" proof nonexistence 2026 strongly regular graph
"srg(99,14,1,2)" 2026 proof OR construction OR counterexample
"99-graph" "Jul" 2026 Conway
site:arxiv.org Conway 99 graph 2026 strongly regular
"n3 >= 60" graph
"n_3 >= 60" graph
"n_3\geq 60" "strongly regular"
"n3 > 57" graph
"n_3 > 57" graph
"n3=57" Conway
"n_3=57" "99,14,1,2"
"exclude n3=57" graph
"209346" hexagons
"209,346" hexagons
"209346" "strongly regular"
"p6=209286+n3"
"209286+n3" graph
"lower bound" hexagons "99,14,1,2"
"six-vertex induced subgraphs" "99,14,1,2"
```

No primary exact hit for `n3>=60`, `n3=57` exclusion, or `209346` was
found. Searches that surfaced `n57` in Reimbayev 2025 were rejected after
the variable-identity check described above.

### 6.2 Executed structural queries

The frozen alternate-language searches were supplemented, after opening
the discovery report, by exact formula/profile searches:

```text
"r-1-3q" graph triangles
"3|X|+|X|^2/9" graph
"m^2/9" strongly regular subset edges
"sum q(T)" triangles graph
"row and column degree" "zero or two" graph
"fixed-point identity" strongly regular graph triangle
"active triangle" labels strongly regular
"triangle labels" "srg(99,14,1,2)"
"2^17 4" "r=18" graph
"2^16 3^2" "r=18" graph
"2^19" "r=19" Conway
"K2,2" crossing labels "strongly regular"
"active points" "Conway 99"
"active labels" "Conway 99"
"r=18" "Conway 99"
"r=19" "Conway 99"
"crossing bound" "strongly regular graph"
"partial quadrangle" "PQ(2,6,2)" active
"triangle graph" "99,14,1,2"
```

Citation-chain and author/title searches covered Wilbrink (1984),
Makhnev (1988), Lou--Murin (2014), Reimbayev (2024 and 2025),
Cesarz--Woldar (2025), Petro--Phillips (2025/2026), Evans (2022/2023),
Baker (2026), Phillips (2026), and Keramatipour (2026). Exact-title and
author searches for Baker found only the conference program.

No exact primary match to the active-point/crossing/profile mechanism
was found. Generic results about graph-drawing crossing numbers, other
partial quadrangles, generalized quadrangles, and
`srg(85,14,3,2)` were rejected as inapplicable. A search nonhit is not a
novelty certificate.

## 7. Source and access register

All entries were accessed 2026-07-23.

| Source | Exact use | Access result |
|---|---|---|
| [Brouwer SRG table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html) | Current `?` status and spectrum | Accessible |
| [Cesarz--Woldar 2025](https://doi.org/10.5802/alco.418) | Peer-reviewed open-status signal; automorphism restrictions | Journal page and PDF accessible |
| [Reimbayev 2024](https://doi.org/10.62780/ejaam/2024-001) | Definition of `n3`, exact induced-C6 identity, published lower bound | PDF accessible |
| [Reimbayev 2025](https://arxiv.org/abs/2508.03377) | Later six-vertex census; `n3` remains free; `n57` collision | v2 PDF accessible |
| [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf) | Triangle graph and nearest older local-count treatment | PDF accessible |
| [Petro--Phillips](https://doi.org/10.1016/j.disc.2025.114862) | 3-clique graph spectrum and 2026 publication-status signal | arXiv PDF accessible |
| [Phillips 2026](https://arxiv.org/abs/2605.22867) | Current clique-graph thesis and open-status wording | HTML accessible |
| [Keramatipour 2026](https://arxiv.org/abs/2604.23037) | Current SAT attempt without certificate/resolution | v2 accessible |
| [Baker conference abstract](https://www.auburn.edu/cosam/departments/math/cumberland-conference/34th_cumberland_program.pdf) | Closest current induced-subgraph methodological near-match | Abstract accessible; no paper/slides located |
| [Shpectorov lecture announcement](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html) | Later institutional status signal; reject different proved target | Accessible |
| [Evans 2023](https://doi.org/10.1016/j.disc.2022.113154) | General induced-subgraph spectral/interlacing context | arXiv accessible; publisher full text not needed |
| [Wilbrink 1984 metadata](https://research.tue.nl/en/publications/on-the-991412-strongly-regular-graphs/) | Foundational Conway-specific prior art | Metadata accessible; reliable PDF extraction unavailable |
| [Makhnev 1988 metadata](https://www.mathnet.ru/eng/mzm4220) | Restricted `n3=0` near-match as attributed by later source | Metadata/DOI found; reliable full text unavailable |
| [Ishihara 2022](https://doi.org/10.11517/jsaisigtwo.2022.AGI-021_01) | Apparent exact resolution; theorem directly audited | Official PDF accessible; decisive premise refuted |

Citation hygiene note: Reimbayev 2024 cites OEIS A248380 for Conway's
five problems, but [A248380](https://oeis.org/A248380) currently denotes
a Sylver Coinage sequence. It was not used as a Conway-status authority.

## 8. Final conservative labels

| Claim | Label | Reason |
|---|---|---|
| A Conway `srg(99,14,1,2)` exists | **`UNKNOWN`** | No authoritative construction/certificate found |
| No Conway `srg(99,14,1,2)` exists | **`UNKNOWN`** | No valid authoritative nonexistence proof found |
| Ishihara Theorem 28's displayed proof establishes nonexistence | **`REFUTED`** | Equation (88) rests on a false uniform residual-degree assertion |
| Reimbayev's `p6=209286+n3` specialization | **`CITED` / `DERIVED`** | General identity cited; parameter substitution checked |
| Published exact exclusion of `n3=57` | **`UNKNOWN`** | No exact source found; 2025 census leaves `n3` free |
| Published exact conditional `n3>=60` | **`UNKNOWN`** | No exact source found |
| Conditional `n3>=60 => p6>=209346` | **`DERIVED`** | Direct addition in the cited identity |
| Generic bound `2e(X)<=3|X|+|X|^2/9` | **`DERIVED`** | Standard Rayleigh estimate from eigenvalues `14,3,-4` |
| Exact prior r=18/r=19 active-point crossing/spectral elimination | **`UNKNOWN`** | No exact or equivalent theorem found |
| Novelty of the Wave 18 package | **`UNKNOWN`** | Nonhit plus inaccessible/abstract-only near-matches cannot certify novelty |

The literature lane therefore supplies no basis to promote the Wave 18
discovery to `VERIFIED`, and it supplies no prior-art basis to dismiss it.
The next gate is independent proof verification; only after that should
the project seek author contact or a broader expert novelty review,
especially concerning Baker's abstract-only 2026 work.
