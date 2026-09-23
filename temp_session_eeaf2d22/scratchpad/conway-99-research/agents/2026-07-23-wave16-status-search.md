# Wave 16 literature and status search: Conway's 99-graph

```yaml
role: literature
date_utc: 2026-07-23T11:34:57Z
git_commit: NOT_RECORDED_NO_GIT
claim_label: UNKNOWN
scope: >-
  Exact existence problem srg(99,14,1,2), with special attention to prior
  art for a conditional bound n3 >= 54 and the consequent induced-hexagon
  bound p6 >= 209340.
inputs:
  - Remote sources and search results listed below; accessed 2026-07-23 UTC.
  - No local source copies were created, so remote-content SHA-256 hashes are unavailable.
method: >-
  Exact-parameter, exact-number, terminology, author/title, citation, and
  current-status searches; inspection of source abstracts, theorem/formula
  pages, parameter-table legend and row, and available full texts.
command: N/A (web/source search; exact query families are recorded below)
outputs:
  - agents/2026-07-23-wave16-status-search.md
limitations: >-
  This was a broad but non-exhaustive public-web search, not a complete
  MathSciNet/ZbMATH citation review. Search non-discovery is not a novelty
  certificate. The Makhnev full text could not be independently extracted.
```

## Conservative conclusions

1. **Exact existence target — `UNKNOWN`.** Conway's problem is exactly the
   existence of an `srg(99,14,1,2)`. Recent sources searched continue to treat
   the target as unresolved: a peer-reviewed April 2025 paper calls existence
   an open problem; an arXiv work revised in April 2026 reports an unsuccessful
   SAT approach; and a June 2026 university lecture notice discusses only a
   *possible similar approach* to this graph after work on a different SRG. The
   lecture notice is neither a paper nor a resolution.

   **No resolution was found in the sources searched as of 2026-07-23.**

2. **Closest six-vertex/hexagon prior art — `CITED`.** Reimbayev (2024) proves,
   in the paper's notation for an `srg(n,k,1,2)`,

   \[
   p_6=\frac{1}{12}nk(k-2)(2k^2-21k+53)+n_3,
   \]

   where \(p_6=n_{12}\) counts induced \(C_6\)'s and \(n_3\) counts the
   paper's type-3 induced six-vertex configuration. Substitution of
   \((n,k)=(99,14)\) gives

   \[
   p_6=209286+n_3.
   \]

   Therefore a valid proof of \(n_3\ge 54\) would immediately give
   \(p_6\ge 209340\). The numerical substitution is `DERIVED`; it is not a
   separately stated theorem in the cited paper.

3. **Meaning of \(n_3\) — `DERIVED` from Reimbayev's figure/relations and
   \(\lambda=1\).** It is the number of induced configurations consisting of
   two vertex-disjoint triangles with exactly two cross-edges. The cross-edges
   must form a matching: two cross-edges sharing an endpoint would put a second
   triangle on an edge, contradicting \(\lambda=1\). Reimbayev characterizes
   \(n_3=0\) equivalently as the condition that two triangles joined by two
   cross-edges are also joined by the third matching edge.

4. **Previously visible lower information on \(n_3\).**

   - Reimbayev's published hexagon theorem uses only \(n_3\ge0\), yielding
     \(p_6\ge209286\).
   - Reimbayev reports that Makhnev's 1988 result rules out the target under
     the condition \(n_3=0\).
   - The relation
     \(3n_1+n_3=\tfrac14 nk(k-2)\) implies \(n_3\equiv0\pmod 3\) at
     \((99,14)\). Combining that integrality observation with the reported
     Makhnev exclusion gives the weak conditional consequence \(n_3\ge3\) for
     any putative target graph. This last consequence is `DERIVED`, not quoted
     as a published bound.

5. **Wave 16 bound-status / novelty — `UNKNOWN`.** No theorem, preprint, table,
   or exact-number hit asserting \(n_3\ge54\), \(p_6\ge209340\), or an
   equivalently strong bound was found. This is useful negative search
   evidence, but it is **not** a proof of novelty. Equivalent results could use
   different diagram numbering, count non-induced cycles, use partial
   quadrangle terminology, or be absent from indexed public sources.

## Exact problem and current-status evidence

### Official statement

- John H. Conway, *Five $1,000 Problems (Update 2017)*, Problem 2, “99-Graph.”
  The problem asks for a 99-vertex graph in which each edge lies in one
  triangle and each nonedge lies in one quadrilateral.
  - PDF: https://oeis.org/A248380/a248380.pdf
  - Relevant location: page 1, Problem 2.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` (official problem statement).

The two incidence conditions imply regularity and the SRG parameters
\((99,14,1,2)\); Reimbayev (2024), Propositions 2.1–2.2 and the surrounding
discussion, spell out this equivalence.

### Parameter tables

- Andries E. Brouwer and Hendrik Van Maldeghem, *Strongly Regular Graphs*,
  Cambridge University Press (2022).
  - Public manuscript: https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf
  - Book DOI: https://doi.org/10.1017/9781009057226
  - Chapter 12 legend, printed page 371: `?` is the existence-column marker
    used when neither an example nor a nonexistence result is recorded.
  - Printed page 374, parameter row: `? 99 14 1 2`, with restricted
    eigenvalues \(3^{54}\) and \((-4)^{44}\).
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` (curated monograph table; not by itself a live 2026 status
    certificate).

- Brouwer's online SRG parameter table:
  - Legend/index: https://aeb.win.tue.nl/graphs/srg/srgtab.html
  - 51–100 row table:
    https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html
  - Row on access: `? 99 14 1 2 3^54 -4^44`; the next row is its complement
    \((99,84,71,72)\).
  - HTTP metadata observed during the search reported `Last-Modified:
    2025-01-27`, so this table alone was not treated as current to July 2026.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED`.

### Recent research/status sources

- Patrick G. Cesarz and Andrew J. Woldar, “On the automorphism group of a
  putative Conway 99-graph,” *Algebraic Combinatorics* 8(2) (2025), 379–398.
  - Article: https://alco.centre-mersenne.org/articles/10.5802/alco.418/
  - DOI: https://doi.org/10.5802/alco.418
  - Published online: 2025-04-24.
  - Exact relevance: the abstract explicitly treats existence as an unresolved
    open problem. Its proved results concern automorphisms: if the automorphism
    group order is even, it divides 6; if divisible by 7, the group is cyclic
    of order 7.
  - It does not give a hexagon or \(n_3\) lower bound.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` (peer-reviewed primary research).

- Ali Keramatipour, “Approaching the Conway-99 problem using SAT solvers,”
  arXiv:2604.23037v2.
  - Abstract/history: https://arxiv.org/abs/2604.23037
  - PDF: https://arxiv.org/pdf/2604.23037
  - Submitted 2026-04-24; revised 2026-04-28.
  - Exact relevance: the work encodes the target as SAT but reports that the
    attempted solver strategy does not handle the search in reasonable time;
    it does not supply a construction or nonexistence certificate.
  - Caveat: the PDF identifies the underlying work as a June 2023 thesis.
    The 2026 date is the arXiv upload/revision date, not the date of the
    experiments.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` (preprint; negative computational outcome, not a proof).

- Hebei Normal University notice for Sergey Shpectorov's lecture,
  “Non-existence of the strongly regular graph srg(85,14,3,2),” posted
  2026-06-24.
  - Notice:
    https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html
  - Exact relevance: after describing an enumeration/elimination method for
    `srg(85,14,3,2)`, the notice says the lecture will discuss a *possible
    similar approach* for `srg(99,14,1,2)`.
  - This wording is evidence of an active direction, not evidence of a solved
    target. The page is an institutional event notice, not a peer-reviewed
    result or computational certificate.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` only for what the notice announces.

- Rayan Ibrahim, Hudson LaFayette, and Kevin McCall, “Minimum 2-percolating
  sets in 2-connected, diameter 2 graphs,” *Australasian Journal of
  Combinatorics* 93(1) (2025), 60–89.
  - PDF: https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf
  - Relevant location: Section 4 / Theorem 4.19.
  - Exact relevance: the authors still formulate the 99-graph condition
    hypothetically and derive bootstrap-percolation consequences for any such
    graph. They do not settle existence or state the Wave 16 bound.
  - Accessed: 2026-07-23 UTC.
  - Label: `CITED` (peer-reviewed but peripheral to \(n_3\)).

## Closest prior art for \(n_3\) and induced \(C_6\)'s

### Reimbayev 2024: exact hexagon identity

Reimbay Reimbayev, “The lower bound for number of hexagons in strongly regular
graphs with parameters \(\lambda=1\) and \(\mu=2\),” *e-Journal of Analysis and
Applied Mathematics* (2024), 1–14.

- Journal PDF:
  https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf
- DOI: https://doi.org/10.62780/ejaam/2024-001
- arXiv version: https://arxiv.org/abs/2409.10620
- Relevant locations:
  - Proposition 3.2, equations (5) and (6): \(n_4=2n_3\).
  - Page 12 / immediately before Theorem 3.3:
    \(n_{12}=F(n,k)+n_3\), followed by the closed formula
    \[
    n_{12}=\frac1{12}nk(k-2)(2k^2-21k+53)+n_3.
    \]
  - Theorem 3.3 drops \(n_3\) using only nonnegativity.
  - Conclusion: equality is the \(n_3=0\) case, and the paper connects that
    condition to Makhnev's restricted nonexistence theorem.
- Accessed: 2026-07-23 UTC.
- Label: `CITED`.

Arithmetic audit for the target parameters:

\[
2(14)^2-21(14)+53=151,
\]
\[
\frac1{12}(99)(14)(12)(151)=99\cdot14\cdot151=209286.
\]

Hence

\[
p_6=n_{12}=209286+n_3.
\]

This paper is the most direct located prior art for the proposed
\(209340=209286+54\) threshold.

### Reimbayev 2025: all six-vertex counts still depend on \(n_3\)

Reimbay Reimbayev, “The Subgraphs of Order Six of the Family of Strongly
Regular Graphs with Parameters \(\lambda=1\) and \(\mu=2\),”
arXiv:2508.03377v2.

- Abstract/history: https://arxiv.org/abs/2508.03377
- PDF: https://arxiv.org/pdf/2508.03377
- Submitted 2025-08-05; revised 2025-11-03.
- Relevant locations:
  - Introduction: the paper explicitly selects \(n_3\) as a free variable.
  - Pages 2–6: \(n_1=\tfrac1{12}nk(k-2)-\tfrac13n_3\),
    \(n_4=2n_3\), and
    \(n_{12}=\tfrac1{12}nk(k-2)(2k^2-21k+53)+n_3\).
  - Page 19: the paper says the value of \(n_3\) is not supplied and all other
    six-vertex counts are expressed using it.
  - Conclusion: one extra parameter remains necessary in the author's
    analysis; no positive lower bound for it is concluded.
- It contains no located statement \(n_3\ge54\) or
  \(n_{12}\ge209340\).
- Accessed: 2026-07-23 UTC.
- Label: `CITED` (preprint; formulas were inspected, not independently
  re-proved in this literature run).

### Makhnev 1988: the \(n_3=0\) restricted case

A. A. Makhnev, “Strongly regular graphs with \(\lambda=1\),”
*Mathematical Notes of the Academy of Sciences of the USSR* 44 (1988),
847–850; translated from *Matematicheskie Zametki* 44(5), 667–672.

- DOI/metadata page:
  https://link.springer.com/article/10.1007/BF01158426
- MathNet record:
  https://www.mathnet.ru/eng/mzm4220
- DOI: https://doi.org/10.1007/BF01158426
- Bibliographic identifiers exposed by MathNet: MR 980587; Zbl 0737.05078.
- Exact relevance as reported by Reimbayev (2024, conclusion): Makhnev proves
  nonexistence of `srg(99,14,1,2)` under the condition that two triangles
  connected by two cross-edges must also have the third matching cross-edge,
  i.e. the \(n_3=0\) condition in Reimbayev's numbering.
- Access limitation: Springer exposed metadata only. MathNet advertised a
  full-text PDF, but its HTML failed in the browser decoder and the PDF endpoint
  returned access/safety errors during this run. Consequently the theorem text
  was **not independently extracted**; the condition-to-result mapping above
  is a transparent secondary reading from Reimbayev's primary paper, not an
  independent verification of Makhnev's proof.
- Accessed: 2026-07-23 UTC.
- Label: `CITED_WITH_ACCESS_LIMITATION`.

## Other structural prior art found

These sources constrain putative graphs but did not contain the proposed
\(n_3\) or induced-\(C_6\) bound.

- H. A. Wilbrink, “On the (99,14,1,2) strongly regular graphs,” in *Papers
  dedicated to J. J. Seidel*, EUT Report 84-WSK-03 (1984), 342–355.
  - Record:
    https://research.tue.nl/en/publications/on-the-991412-strongly-regular-graphs/
  - PDF:
    https://pure.tue.nl/ws/files/1856500/688724168091800.pdf
  - The paper proves that a putative graph has no automorphism of order 11,
    hence is not vertex-transitive.
  - It also places the graph in partial-quadrangle/semipartial-geometry
    language.
  - Label: `CITED`.

- Dean Crnković and Marija Maksimović, “Construction of strongly regular
  graphs having an automorphism group of composite order,” *Contributions to
  Discrete Mathematics* 15(1) (2020), 22–41.
  - Article: https://cdm.ucalgary.ca/article/view/62323
  - PDF: https://cdm.ucalgary.ca/article/download/62323/54015/204856
  - It excludes putative 99-graphs whose full automorphism group is
    \(\mathbb Z_6\), \(S_3\), \(\mathbb Z_9\), or \(E_9\).
  - Label: `CITED`.

- A. Mohammadian and B. Tayfeh-Rezaie, “On a family of diamond-free strongly
  regular graphs,” arXiv:1303.0473.
  - Abstract: https://arxiv.org/abs/1303.0473
  - It states the equivalence between a partial quadrangle
    \(\mathrm{PQ}(s,t,\mu)\) and a diamond-free SRG with parameters
    \[
    \left(1+s(t+1)+\frac{s^2t(t+1)}{\mu},\,s(t+1),\,s-1,\,\mu\right).
    \]
    Substituting \((s,t,\mu)=(2,6,2)\) yields
    \((99,14,1,2)\).
  - Label: `CITED` for the equivalence and `DERIVED` for the substitution.

- H. Petro and C. Phillips, “On Clique Graphs and Clique Regular Graphs,”
  arXiv:2502.17845.
  - Abstract: https://arxiv.org/abs/2502.17845
  - It studies clique graphs of locally linear SRGs and lists
    \((99,14,1,2)\) among longstanding existence questions. No \(n_3\) bound
    was located.
  - Label: `CITED` (peripheral).

## Alternate terminology and indexing hazards

Searches should include all of the following:

- `srg(99,14,1,2)`, `SRG(99,14,1,2)`, and
  “strongly regular graph with parameters (99,14,1,2)”;
- “Conway 99-graph,” “Conway's 99-vertex graph,” “Conway-99 problem,”
  “99-graph problem”;
- “locally linear strongly regular graph” and “locally matched strongly
  regular graph”;
- “diamond-free strongly regular graph”;
- partial quadrangle \(\mathrm{PQ}(2,6,2)\);
- a semipartial geometry with 3 points per line, 7 lines through each point,
  and two common neighbours for noncollinear points;
- the triangle system as a 7-regular linear 3-uniform hypergraph / partial
  Steiner triple system;
- “two disjoint triangles with two joining edges,” “two triangles connected
  by exactly two edges,” type-\(N_3\), and \(n_3\);
- “induced hexagon,” “induced \(C_6\),” \(p_6\), \(n_{12}\), and “six-vertex
  induced subgraph.”

Two notable hazards:

1. Reimbayev's \(n_3\) and \(n_{12}\) are figure-specific labels, so searches
   on those symbols alone have weak recall.
2. “Conway graph” is ambiguous. Brouwer–Van Maldeghem's monograph also uses
   that name for rank-3 graphs on 1408 and 2300 vertices. Searches should
   retain `99`, `99-graph`, or the full SRG parameter tuple.

## Query log

Representative exact/general queries run on 2026-07-23 UTC:

### Exact target and status

- `"srg(99,14,1,2)"`
- `"SRG(99, 14, 1, 2)" existence`
- `"99,14,1,2" strongly regular graph`
- `"Conway 99 graph" problem strongly regular`
- `"Conway-99" 2026 graph`
- `"Conway 99 graph" 2026 solution nonexistence existence`
- `"99-graph" Conway graph problem`
- `site:arxiv.org "99,14,1,2"`
- `site:doi.org "Conway 99-graph"`

### Exact proposed numbers and notation

- `"209340" graph hexagons strongly regular`
- `"209337" graph hexagons strongly regular`
- `"209286" hexagons`
- `"n3" "209286"`
- `"n_3" "209286"`
- `"n3" "54" "strongly regular" hexagons`
- `"n3 ≥ 54" graph`
- `"n3>=54" graph`
- `"n3" "srg(99, 14, 1, 2)"`
- `"n_3" "srg(99, 14, 1, 2)"`
- `srg 99 14 1 2 hexagons n_3`
- `"number of hexagons" "99,14,1,2"`

### Structural synonyms

- `"two triangles connected by exactly two edges" strongly regular`
- `"no two triangles" "(99, 14, 1, 2)" Makhnev`
- `"partial quadrangle" "99" "14" "1" "2"`
- `"PQ(2,6,2)" strongly regular graph`
- `"diamond-free strongly regular" "99"`
- `"locally linear strongly regular graph" "99"`
- `"semipartial geometry" "99" "14" "1" "2"`

### Author/title/citation chaining

- Exact-title searches for both Reimbayev papers.
- Exact-title and DOI searches for Makhnev (1988).
- Citation-neighbour searches through the Reimbayev, Cesarz–Woldar,
  Wilbrink, Crnković–Maksimović, and Brouwer–Van Maldeghem references.
- Current-source searches around Shpectorov–Zhao and the 2026 SAT upload.

## Negative-search results and failures

- Exact searches for `209340`, `n3>=54`, and close variants returned no
  relevant mathematical source beyond pages related to the already known
  hexagon formula. This is **not** a complete-search certificate.
- Searches for exact `PQ(2,6,2)` had poor precision/recall. The equivalence was
  recovered through the general partial-quadrangle parameter formula instead.
- General web search inconsistently surfaced arXiv:2508.03377; exact title and
  arXiv searches were required.
- OpenAlex exact-title/parameter attempts returned no useful matching record.
- Semantic Scholar API access returned HTTP 429 during part of the search.
- Crossref searches on numeric/formula fragments were mostly noisy and did not
  locate a bound.
- MathNet's `mzm4220` page declared Windows-1251 and failed the web decoder.
  Its advertised full-text endpoint was not successfully retrieved, while the
  Springer page was subscription-limited.
- No authenticated MathSciNet or full ZbMATH review search was available.
- The Brouwer online table's observed last-modified date predates this search,
  and the monograph is from 2022; they were corroborating sources, not sole
  evidence of July 2026 status.
- The June 2026 lecture notice is institutional publicity and announces a
  possible method, not a paper or proof.
- arXiv submissions and web pages may be revised after the cutoff.

## Publication-status recommendation

- Exact existence/nonexistence of `srg(99,14,1,2)`: `UNKNOWN`.
- Reimbayev identity \(p_6=209286+n_3\): `CITED`, pending any project-level
  independent mathematical verification policy.
- Makhnev exclusion of \(n_3=0\): `CITED_WITH_ACCESS_LIMITATION`.
- Wave 16 implication
  \(n_3\ge54\Longrightarrow p_6\ge209340\): `DERIVED` once its premise is
  independently verified.
- Wave 16 premise \(n_3\ge54\): do not promote based on this literature run;
  it requires the project verifier.
- Novelty of \(n_3\ge54\) or the \(209340\) obstruction: `UNKNOWN`.
