# Wave 17 literature/status audit: `n3=54` equality boundary

## Preinspection search-plan freeze

```yaml
role: literature
date_utc_plan_frozen: 2026-07-23T12:11:18Z
claim_label: UNKNOWN
scope: >
  Current target status and prior art for n3>=57 / exclusion of n3=54,
  the exact n3=54 equality residual, positive intriguing/equitable 27-sets,
  active cubic/2-factor matrix identities, related surface terminology,
  and exact cubic-catalog coverage.
inspection_boundary: >
  This plan was recorded before either frozen Wave 17 proof report was
  opened. Earlier Wave 15/16 reports and the assigned task text supplied
  the terminology listed here.
```

The source search will proceed in this order:

1. Audit Bamberg--De Clerck--Durante, *Intriguing sets of partial
   quadrangles*, arXiv:0812.2871 and DOI `10.1002/jcd.20269`, from the
   manuscript/publisher text.  Record the exact definition of positive and
   negative intriguing sets, theorem hypotheses, classified partial
   quadrangles, and whether `PQ(2,6,2)` or a hypothetical
   `srg(99,14,1,2)` lies in scope.
2. Check current primary Conway-99 sources and maintained registries for a
   construction, nonexistence proof, or status change through 2026-07-23.
3. Search exact and alternate terminology for prior `n3>=57`, exclusion of
   `n3=54`, the `27+72` equitable partition with quotient
   `[[6,8],[3,11]]`, and positive intriguing sets with
   `(h1,h2)=(6,3)`.
4. Search the exact active residual under partial-quadrangle, regular-set,
   intriguing-set, tactical-configuration, twofold-cover, cubic
   triangle-free, line-graph, 2-factor, and matrix-factorization
   terminology.
5. Audit official House of Graphs pages for the cubic girth-at-least-five
   catalog: generator/provenance, order coverage, connectedness, canonical
   format, and whether absence from the catalog can say anything about the
   active residual.
6. Search the proposed topological formulation under quadrangulation,
   hexangulation, nonorientable genus/crosscap, Euler characteristic
   `-9`, and regular maps/hypermaps.
7. Only after this freeze, open the two frozen Wave 17 proof reports and
   compare their exact claims and notation with the source findings.

Exact planned query families:

```text
"srg(99,14,1,2)"
"Conway 99-graph" existence OR nonexistence
"Conway's 99-graph" 2026
"n_3 >= 57" graph
"n3 >= 57" "Conway"
"n_3=54" "99,14,1,2"
"n3=54" "Conway 99"
"209343" hexagons graph
"intriguing sets of partial quadrangles"
"PQ(2,6,2)" intriguing
"partial quadrangle" "(2,6,2)"
"srg(99,14,1,2)" intriguing set
"positive intriguing set" 27
"intriguing set" "h1" "h2" partial quadrangle
"regular set" "99,14,1,2"
"equitable partition" "99,14,1,2"
"equitable partition" "[[6,8],[3,11]]"
"intriguing set" "(6,3)"
"27-set" "partial quadrangle"
"18 lines" "two-fold cover" points
"18-line" "2-fold" point cover
"2-regular 3-uniform hypergraph" 18 27
"cubic triangle-free graph" 18 "2-factor" line graph
"2-factor" "line graph" "cubic" 18
"N A_R N^T" "2 A_L"
"H R H^T" "2L" graph
"twofold rectangle cover" graph
"nonorientable surface" "Euler characteristic -9"
"nonorientable genus 11" hexangulation
"hexagonal" map "chi=-9"
"cubic graphs" girth 5 order 18 catalog
site:houseofgraphs.org cubic girth 5 18
site:houseofgraphs.org "cubic" "girth at least 5"
```

Planned status discipline:

- Direct source statements are `CITED`.
- Transparent arithmetic or applicability deductions are `DERIVED`.
- Search nonhits, catalog absence, and inaccessible pages remain `UNKNOWN`.
- No source will be treated as classifying `PQ(2,6,2)` unless every stated
  hypothesis and parameter translation is checked.
- The target and novelty remain `UNKNOWN` unless a complete authoritative
  resolution or precise prior statement is located.

## Run report

```yaml
role: literature
date_utc: 2026-07-23T12:11:18Z
git_commit: 45c7a9af8cb79ff3ce01085f1e70e54561054796
claim_label: UNKNOWN
scope: >
  Literature, terminology, status, and finite-catalog audit for the
  Conway srg(99,14,1,2) target and the frozen Wave 17 n3=54 equality
  residual.  No construction or nonexistence claim is made.
inputs:
  - path: AGENTS.md
    sha256: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  - path: agents/2026-07-23-wave17-n3-54-structural.md
    sha256: ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18
  - path: agents/2026-07-23-wave17-n3-54-algebra.md
    sha256: 4c46c718e05a5816d48b9529602fad94a1765fb8c6390166fc916b7e1bcf87b1
method: >
  Source-first web search of exact phrases and terminology variants;
  inspection of primary manuscripts, journal pages, arXiv records,
  maintained tables, and the official House of Graphs catalog page;
  parameter and theorem-hypothesis audit; then comparison with the two
  frozen Wave 17 reports after the search plan above had been recorded.
command: >
  Not computational.  Exact search strings are recorded in the frozen
  plan and execution log below.
outputs:
  - path: agents/2026-07-23-wave17-status-search.md
    sha256: >
      Self-hash necessarily recorded in the orchestrator handoff after
      final freeze, rather than recursively embedded in this file.
limitations: >
  Search nonhits are not novelty evidence.  This was not a systematic
  review of every paywalled database, citation graph, thesis repository,
  or non-English source.  No complete enumeration of the 2-factor R,
  incidence placements, or matrix compatibility constraint was run.
  The official House of Graphs page was directly client-rendered and
  returned only a JavaScript requirement to the text fetcher; its
  indexed official-page text supplied the catalog statements and counts.
```

All URLs below were accessed on **2026-07-23** unless a more specific
date is stated.

## Executive finding

- **`UNKNOWN` — target resolution.** No authoritative construction or
  nonexistence proof for `srg(99,14,1,2)` was found.  A 2025 refereed
  paper, a maintained strongly regular graph table, a March 2026
  journal article, and an April 2026 SAT preprint all continue to treat
  existence as open.
- **`UNKNOWN` — novelty of the Wave 17 residual.** No source found states
  `n3>=57`, excludes `n3=54`, or gives the complete equality residual
  frozen below.  These are exact-search nonhits, not a novelty claim.
- **`CITED`/`DERIVED` — known terminology, not a classification.** A
  27-set with quotient `[[6,8],[3,11]]` in the target point graph is
  precisely a positive intriguing set with `(h1,h2)=(6,3)`, equivalently
  a regular set/equitable two-partition.  Bamberg--De Clerck--Durante do
  not classify or exclude this parameter case.
- **`CITED` — finite cubic universe.** The official House of Graphs
  connected-cubic catalog gives exactly **455** connected cubic graphs
  on 18 vertices of girth at least 5 and exactly **2** on 12 vertices.
  Its page says the girth-3, girth-4, and girth-5 counts through order 30
  were independently confirmed by `genreg`, `minibaum`, and
  `snarkhunter`.  This is external support for the finite `F` universe,
  not a verification of any downloaded file and not an enumeration of
  compatible `R`.

## 1. Target-status audit

### Current primary and maintained sources

1. **`CITED` — Cesarz and Woldar (2025).** Patrick Cesarz and Andrew
   Woldar, “On automorphism group of putative Conway 99-graph,”
   *Algebraic Combinatorics* 8(2) (2025), 379--398,
   DOI [`10.5802/alco.418`](https://doi.org/10.5802/alco.418);
   [journal landing page](https://alco.centre-mersenne.org/articles/10.5802/alco.418/);
   [journal PDF](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf).
   The landing-page abstract says that existence remains an elusive open
   problem.  The same page records online publication on 2025-04-24.

2. **`CITED` — Brouwer maintained SRG table.** Andries Brouwer,
   [“Strongly regular graphs on at most 100 vertices”](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html),
   row `99 14 1 2`, marks the case with `?` and gives spectrum
   `14^1 3^54 (-4)^44`; see also the
   [table entry point and legend](https://aeb.win.tue.nl/graphs/srg/srgtab.html).
   A maintained table is a status indicator, not a proof of openness.

3. **`CITED` — Petro and Phillips (2026).** N. Petro and B. Phillips,
   “On Clique Graphs and Clique Regular Graphs,” *Discrete Mathematics*
   349(3) (March 2026), article 114862,
   DOI [`10.1016/j.disc.2025.114862`](https://doi.org/10.1016/j.disc.2025.114862);
   [publisher page](https://www.sciencedirect.com/science/article/pii/S0012365X25004704);
   [arXiv manuscript](https://arxiv.org/abs/2502.17845).
   Example 4 (manuscript pp. 26--27) lists the 99-vertex case among the
   longstanding unknown cases and derives information about its
   3-clique graph; it does not resolve existence.

4. **`CITED` — Keramatipour (2026).** Ali Keramatipour,
   [“Approaching the Conway-99 problem using SAT solvers”](https://arxiv.org/abs/2604.23037),
   arXiv:2604.23037v2, submitted 2026-04-24 and revised 2026-04-28.
   The abstract says the tested SAT approach cannot handle the instance
   in reasonable time; it reports neither a model nor an unsatisfiability
   certificate.

5. **`CITED` — original problem statement.** John Conway’s problem
   statement is preserved in the
   [original problem PDF](https://oeis.org/A195264/a195264_4.pdf),
   p. 1: construct a graph on 99 vertices in which adjacent pairs have
   one common neighbor and nonadjacent pairs have two.  Some later
   references point to OEIS A248380, but that sequence is about Sylver
   Coinage and is not a reliable identifier for this graph problem.

6. **`CITED` — later 2026 institutional status signal.** The
   [Hebei Normal University lecture announcement of 2026-06-25](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html)
   reports a complete enumeration/nonexistence result for
   `srg(85,14,3,2)` and presents a similar approach to the Conway
   problem as prospective work.  It does not claim resolution of the
   99-vertex case.

These independent current signals support the conservative status
**`UNKNOWN`**.  They do not prove that no resolution exists elsewhere.

## 2. `n3`, hexagon count, and the equality boundary

1. **`CITED` — Reimbayev (2024).** R. Reimbayev, “Lower bound for number
   of hexagons in strongly regular graphs,” *Eurasian Journal of Applied
   Mathematics* (2024),
   DOI [`10.62780/ejaam/2024-001`](https://doi.org/10.62780/ejaam/2024-001);
   [article PDF](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf).
   Equations in the six-vertex count on PDF pp. 10--11 give
   \[
   n_{12}=\frac1{12}n k(k-2)(2k^2-21k+53)+n_3,
   \]
   using only `n3>=0` for the lower bound.

2. **`DERIVED`.** Substitution of `(n,k)=(99,14)` gives
   `p6=209286+n3`.  The paper’s later suggestion `n3=0` is presented as
   a conjectural equality case, not as a proof of any lower bound such
   as `n3>=57`.

3. **`CITED` — Reimbayev et al. (2025).**
   [“The number of six-vertex induced subgraphs of strongly regular graphs”](https://arxiv.org/abs/2508.03377),
   arXiv:2508.03377v2 (2025).  The introduction and summary (manuscript
   pp. 1--2 and 16--18) retain `n3` as a free variable; the discussion
   near p. 23 says the authors were unable to eliminate it.  The
   symmetry intuition there is not a proof that `n3=0`.

4. **`UNKNOWN` — prior bound/exclusion.** The exact and variant searches
   below found no primary source for `n3>=57`, `n3>54`, or exclusion of
   `n3=54`.  This nonhit cannot establish novelty.

## 3. Intriguing sets and partial quadrangles

### Definitions and exact parameter translation

**`CITED`.** J. Bamberg, F. De Clerck, and N. Durante,
“Intriguing sets of partial quadrangles,”
[arXiv:0812.2871](https://arxiv.org/abs/0812.2871),
DOI [`10.1002/jcd.20269`](https://doi.org/10.1002/jcd.20269);
[author manuscript PDF](https://cage.ugent.be/geometry/Files/287/IntriguingSetsofPQfinal.pdf).
The definition on manuscript p. 2 says an intriguing set has constants
`h1,h2` such that a point inside the set has `h1` neighbors in it and a
point outside has `h2`; it is positive when `h1-h2` is the positive
restricted eigenvalue.  Lemma 2.1(ii), manuscript p. 2, gives
\[
 |I|=\frac{h_2v}{k-h_1+h_2}.
\]

**`DERIVED`.** For the point graph `srg(99,14,1,2)`, the proposed set
with `(h1,h2)=(6,3)` has:

- quotient matrix `[[6,8],[3,11]]`;
- size `3*99/(14-6+3)=27`;
- `h1-h2=3`, the positive restricted eigenvalue.

Thus “positive intriguing 27-set,” “`(6,3)`-regular set,” and “equitable
two-partition with quotient `[[6,8],[3,11]]`” are equivalent descriptions
here.

**`CITED`.** B. De Bruyn and H. Suzuki, “Intriguing sets of vertices of
regular graphs,” *Graphs and Combinatorics* 26(5) (2010), 629--646,
DOI [`10.1007/s00373-010-0924-y`](https://doi.org/10.1007/s00373-010-0924-y);
[repository metadata](https://biblio.ugent.be/publication/1105494);
[manuscript PDF](https://backoffice.biblio.ugent.be/download/1105494/1105506).
The first manuscript page identifies a nontrivial intriguing set exactly
with a regular/equitable two-partition and notes “regular set” as
alternate terminology.

### Applicability audit

**`DERIVED` — no classification of the target.** The Bamberg--De
Clerck--Durante paper develops results for named constructions and
families, not a classification of all positive intriguing sets in every
partial quadrangle.

- Its generalized-quadrangle-minus-perp family has parameters
  `PQ(s-1,s^2,s(s-1))`; setting the first parameter to 2 gives
  `PQ(2,9,6)`, not `PQ(2,6,2)`.
- Its hemisystem family has parameters
  `PQ((s-1)/2,s^2,(s-1)^2/2)`; setting the first parameter to 2 gives
  `PQ(2,25,8)`, not the target.
- The exceptional linear-representation cases listed on manuscript
  p. 18 are `PQ(2,10,2)`, `PQ(2,55,20)`, and `PQ(3,77,14)`.
- Theorem 5.2 is conditional on the generalized-quadrangle-minus-perp
  construction.  It cannot be transferred to a hypothetical
  `PQ(2,6,2)`.
- The thin partial-quadrangle section has different hypotheses.

Consequently this source neither constructs nor excludes the target
`(6,3)` set and cannot be cited as a classification.

### Near-match audit

**`CITED`/`DERIVED`.** The paper does contain a positive intriguing set
of size 27 in its Coxeter-cap `PQ(2,10,2)` example (manuscript p. 19 and
the associated table).  Combining the stated size/eigenvalue data with
Lemma 2.1 yields `(h1,h2)=(6,2)`, not `(6,3)`.  It is a useful numerical
near-match, but the ambient point graph, outside intersection number,
and quotient matrix differ.  It is not prior art for the exact Wave 17
residual.

## 4. Frozen Wave 17 residual and prior-art comparison

The two Wave 17 proof reports were opened only after the preinspection
plan above was frozen.  Their common equality-boundary content is:

```text
n3=54, r=18, q=2^18, |X|=27
X is 6-regular
X/Y quotient = [[6,8],[3,11]]
F is a simple cubic triangle-free graph on 18 active labels
R is a simple 2-factor on E(F)
N A_R N^T = 2 A_L
G[X] = L(F) union R
no nonadjacent pair of F has exactly two common neighbors
F is connected of girth >=5, or K3,3 plus a connected
  cubic graph of order 12 and girth >=5
```

Here `N` is the vertex-edge incidence matrix of `F`, `A_R` is the
adjacency matrix of the 2-factor on `E(F)`, and `A_L` is the adjacency
matrix of the associated label graph from the frozen reports.

### What is known terminology

1. **`CITED` — only the line-graph part.** Andrea Munaro,
   “On Line Graphs of Subcubic Triangle-Free Graphs,”
   *Discrete Mathematics* 340(6) (2017), 1210--1226,
   DOI [`10.1016/j.disc.2017.01.006`](https://doi.org/10.1016/j.disc.2017.01.006);
   [author manuscript](https://pureadmin.qub.ac.uk/ws/portalfiles/portal/186487120/dmline.pdf).
   Theorem 7 (manuscript p. 6) characterizes a 4-regular graph as the
   line graph of a cubic triangle-free graph, equivalently as locally
   linear/every edge lying in exactly one triangle (with equivalent
   forbidden-induced-subgraph conditions).

   This applies to the 4-regular structural layer `L(F)` only.  The full
   induced graph in the Wave residual is the 6-regular graph
   `G[X]=L(F) union R`; neither that union nor the compatibility equation
   is covered by Munaro’s theorem.

2. **`CITED`/`DERIVED` — incidence duality.** G. Erskine and J. Tuite,
   “Small Graphs and Hypergraphs of Given Degree and Girth,”
   *Electronic Journal of Combinatorics* 30(1) (2023), P1.57,
   DOI [`10.37236/11765`](https://doi.org/10.37236/11765);
   [journal page](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v30i1p57);
   [journal PDF](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v30i1p57/pdf/).
   The paper uses the standard duality between 2-regular 3-uniform
   hypergraphs and cubic graphs.  The Wave incidence object can therefore
   be described as a simple linear 2-regular 3-uniform hypergraph with
   27 points and 18 triples, or an incidence configuration of type
   `(27_2,18_3)`, dual to `F`.

### What was not located

**`UNKNOWN`.** No searched source contains the exact combination:

- an 18-line, twofold point cover with this target ambient geometry;
- a cubic triangle-free `F` on 18 vertices together with a 2-factor
  `R` on the 27 vertices `E(F)`;
- the matrix identity `N A_R N^T=2A_L`;
- or the full decomposition `G[X]=L(F) union R` under the Conway
  parameters.

The absence of a hit is not evidence that these formulations are new.

## 5. Official House of Graphs finite-universe audit

Source: the official
[House of Graphs “Connected cubic graphs” page](https://houseofgraphs.org/Cubic)
and its [meta-directory](https://houseofgraphs.org/meta-directory),
accessed 2026-07-23.

**`CITED`.**

- The page’s scope is **connected cubic graphs**.
- The downloadable lists are stated to be in `graph6` format, with
  larger files gzip-compressed.
- Its table gives the following exact cumulative girth counts:

| vertices | girth at least 3 | girth at least 4 | girth at least 5 | girth at least 6 |
|---:|---:|---:|---:|---:|
| 12 | 85 | 22 | **2** | 0 |
| 18 | 41301 | 7805 | **455** | 5 |

- Immediately above the table, the page says that every minimum-girth
  3, 4, and 5 count through 30 vertices was independently confirmed by
  the three generators `genreg`, `minibaum`, and `snarkhunter`.

**`DERIVED` — coverage of the frozen `F` cases.**

- The connected 18-vertex branch is covered by a finite universe of 455
  pairwise nonisomorphic connected cubic girth-at-least-5 graphs.
- The disconnected branch specified by the frozen proof is
  `K3,3` disjoint union one of the 2 connected 12-vertex cubic
  girth-at-least-5 graphs.  `K3,3` itself has girth 4, so the disconnected
  graph is not an entry in the connected girth-at-least-5 list; the
  two-component decomposition must be assembled separately.

**Important provenance distinction.** The quoted three-generator
statement is independent-enumeration support for the **counts**.  This
lane did not download the `graph6` files, compute checksums, or
independently regenerate their isomorphism classes.  Catalog checksum
validation and independent enumeration are different claims.  The
official counts establish a credible finite search universe, but they do
not certify:

- that a particular local download is intact;
- that every 2-factor `R` on `E(F)` has been searched;
- that `N A_R N^T=2A_L` has been tested;
- or that no compatible Wave residual exists.

Direct non-browser text access to both official URLs returned only “You
need to enable JavaScript to run this app.”  The counts, format statement,
and generator-confirmation sentence above were recoverable from the
search engine’s indexed text of that same official page.  This access
failure is why no file links or checksums are asserted here.

## 6. Surface terminology audit

**`DERIVED`.** The frozen structural report constructs a possibly
disconnected cellulation with
`V=27`, `E=54`, `F=18`, every face of length 6, and every vertex of
valence 4.  Hence total Euler characteristic is
`27-54+18=-9`.  In map terminology this is a hexagonal cellulation, or
an equivelar map of type `{6,4}` if “map” is used under the relevant
cell-embedding hypotheses.

Because a disconnected surface can have total Euler characteristic
`-9`, the precise conclusion is only that at least one component is
nonorientable.  If connected, it is the nonorientable surface of genus
(crosscap number) `2-(-9)=11`.  The literature search did not justify
connectedness and did not locate an exact type-`{6,4}` object with these
counts.

The term “hexangulation” is convention-dependent: some graph-embedding
papers additionally impose cubicity of the embedded graph, which the
4-valent Wave cellulation does not satisfy.  “Hexagonal cellulation of
type `{6,4}`” is the safer phrase.

Searches for regular maps with negative Euler characteristic produced
classification papers whose hypotheses require regularity and/or prime
Euler characteristic.  Neither is available here (`-9` is composite),
so those results were rejected as inapplicable.

## 7. Executed query log and nonhits

In addition to the exact planned strings above, these strings were
executed verbatim or with only search-engine punctuation normalization:

```text
"n3" "57" "srg(99,14,1,2)"
"n_3" "57" "Conway 99"
"n3 ≥ 57" "strongly regular"
"n_3=54" graph "99"
"parameters (6, 3)" "intriguing"
"(h1,h2)=(6,3)" graph
"positive intriguing set" "(6,3)"
"quotient matrix" "6 8" "3 11" graph
"27_2" "18_3" configuration
"18 lines" "2-regular" "3-uniform"
"18-line twofold point cover"
"N A_R N^T" graph
"N A_R N^{T}" graph
"H R H^T" "2L" graph
"cubic triangle-free" "2-factor" "edge set"
"line graph" cubic triangle-free "2-factor"
"hexagonal" map "Euler characteristic -9"
"hexangulation" "Euler characteristic" "-9"
"nonorientable genus 11" hexangulation
"type {6,4}" "genus 11" map
"hexangulation" "27 vertices" "18 faces"
site:houseofgraphs.org/Cubic "455" "independently confirmed"
site:houseofgraphs.org/Cubic "2" "girth at least 5" "12"
site:arxiv.org "Conway-99" 2026
site:doi.org "99,14,1,2"
```

The following exact targets were **not found**:

- a published `n3>=57` theorem or an `n3=54` exclusion;
- the exact `(6,3)` positive intriguing 27-set in `PQ(2,6,2)`;
- a classification theorem applicable to all such sets;
- the exact 18-line/twofold-cover formulation;
- the exact pair `(F,R)` and matrix identity;
- or the exact Euler-characteristic `-9`, type-`{6,4}` cellulation.

Each item remains **`UNKNOWN`** as a novelty question.  Synonym drift,
unindexed sources, and equivalent formulations make exact-query nonhits
especially weak evidence.

## 8. Final labels

| proposition | label | basis |
|---|---|---|
| The Conway `srg(99,14,1,2)` is resolved | **UNKNOWN** | Current sources still call it open; no resolution found |
| A prior source proves `n3>=57` | **UNKNOWN** | Exact/variant searches nonhit |
| A prior source excludes `n3=54` | **UNKNOWN** | Exact/variant searches nonhit |
| The equality set is a positive intriguing `(6,3)` 27-set | **DERIVED** | BDD definition and size lemma plus frozen quotient |
| BDD classify/exclude the target set | **REFUTED** | Audited family parameters/hypotheses do not include `PQ(2,6,2)` |
| BDD contain an exact target match | **REFUTED** | Their size-27 near-match is `(6,2)` in `PQ(2,10,2)` |
| `L(F)` has standard line-graph prior art | **CITED** | Munaro Theorem 7 |
| The full `G[X]=L(F) union R` is covered by that theorem | **REFUTED** | The theorem covers only the 4-regular `L(F)` layer |
| House of Graphs gives 455 connected order-18 cases and 2 connected order-12 cases | **CITED** | Official cubic table |
| Those counts were independently confirmed by three generators | **CITED** | Explicit official-page provenance statement |
| This lane independently regenerated or checksum-validated the catalogs | **REFUTED** | Neither action was performed |
| The Wave surface is connected nonorientable genus 11 | **UNKNOWN** | True only under the unproved connectedness condition |
| Novelty of the complete Wave 17 equality residual | **UNKNOWN** | No exact prior hit; no novelty proof |
