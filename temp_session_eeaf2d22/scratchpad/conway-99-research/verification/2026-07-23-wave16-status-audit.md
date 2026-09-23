# Wave 16 independent literature/status audit

## Outcome

As of **2026-07-23**, this audit found no authoritative source that resolves the
existence of a strongly regular graph with parameters
\(\operatorname{srg}(99,14,1,2)\). The strongest current sources found still
treat Conway's 99-graph as open. The target therefore remains **`UNKNOWN`**.

This audit also found no source stating either of the precise Wave 16 necessary
bounds

\[
n_3\geq 54
\qquad\text{or}\qquad
p_6\geq 209340,
\]

under the definitions used below. Their literature novelty therefore remains
**`UNKNOWN`**, not `VERIFIED`. A search nonhit is not a novelty certificate.

The value \(209340\) is, however, a transparent arithmetic consequence of a
published exact identity and the separately claimed Wave 16 inequality:

\[
p_6=209286+n_3,\qquad n_3\geq54
\quad\Longrightarrow\quad
p_6\geq209340.
\]

Here \(p_6\) counts **induced** copies of \(C_6\), and \(n_3\) is the count of
the six-vertex catalog configuration \(N_3\); it is not “catalog number 54.”
This report audits sources and scope only. It does not independently verify the
Wave 16 proof of \(n_3\geq54\).

## Run record

```yaml
role: literature
date_utc: 2026-07-23T11:36:17Z
git_commit: b218f3a21f1d23b60e7ad1ece8884c9e7a3697d9
claim_label: UNKNOWN
scope: >-
  Current existence status of srg(99,14,1,2), and prior art for the exact
  necessary bounds n3 >= 54 and induced_C6 >= 209340.
inputs:
  - temporary_name: cesarz-woldar.pdf
    source: https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf
    sha256: d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8
  - temporary_name: reimbayev-hexagons.pdf
    source: https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf
    sha256: 484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521
  - temporary_name: reimbayev-six-v2.pdf
    source: https://arxiv.org/pdf/2508.03377v2
    sha256: c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9
  - temporary_name: reimbayev-seven-v1.pdf
    source: https://arxiv.org/pdf/2511.06572v1
    sha256: d98d474ef277b6a32fc4125690c75d3808450225b0657dbd46290673b7a014f7
  - temporary_name: reimbayev-srg19-v1.pdf
    source: https://arxiv.org/pdf/2511.06569v1
    sha256: a3a2a799e91120a7b6ccb0ed5a2e9feba8c14612bf7033d9476433b392fad26d
  - temporary_name: keramatipour-v2.pdf
    source: https://arxiv.org/pdf/2604.23037v2
    sha256: 8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8
method: >-
  Checked maintained SRG tables, publisher and DOI records, current arXiv
  versions, exact relevant PDF pages, later citations, correction/erratum
  searches, general graph databases, and alternate terminology. Kept cited
  facts, search nonhits, and mathematical inference separate.
command: >-
  $base = [int64](99*14*12*(2*14*14-21*14+53)/12);
  $rhs = [int64](99*14);
  [pscustomobject]@{base_hexagons=$base; with_n3_54=($base+54);
  nk=$rhs; three_n1_plus_n3=($rhs*3)}
outputs:
  - path: verification/2026-07-23-wave16-status-audit.md
    sha256: supplied at handoff because a file cannot contain its own stable hash
limitations: >-
  Public-web and citation-index searching is nonexhaustive; some publisher
  pages blocked automated access; MathSciNet and zbMATH full records were not
  available through this environment; private manuscripts and unindexed work
  may exist. Downloaded source copies were ephemeral and are not committed;
  their public URLs and observed hashes are retained above. No search nonhit
  is treated as proof of novelty or nonexistence.
```

All URLs in this report were accessed on **2026-07-23**.

## 1. Known-source facts: exact target status

### 1.1 Maintained strongly regular graph table

Andries Brouwer's maintained strongly regular graph table says that its first
column records “existence”:

- table guide: <https://aeb.win.tue.nl/graphs/srg/srgtab.html>
- orders 51–100: <https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html>

The order-99 row currently reads

```text
? 99 14 1 2 3^54 -4^44
```

with `?` in that existence column. The site does not provide a nearby textual
legend defining every status symbol, so this row is used as registry evidence
and not as the sole basis for interpreting the problem as open.

### 1.2 Peer-reviewed 2025 status statement

Patrick G. Cesarz and Andrew J. Woldar, “On the automorphism group of a
putative Conway 99-graph,” *Algebraic Combinatorics* 8(2) (2025), 379–398,
DOI [10.5802/alco.418](https://doi.org/10.5802/alco.418):

- publisher record:
  <https://alco.centre-mersenne.org/articles/10.5802/alco.418/>
- publisher PDF:
  <https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf>

The abstract on the publisher page and printed page 379 state explicitly that
existence “remains an elusive open problem.” The paper studies restrictions on
the automorphism group of a **putative** graph; it does not construct or exclude
the graph.

This is the clearest peer-reviewed, target-specific status statement located.

### 1.3 2026 work remains exploratory

Robert R. Petro and Connor M. Phillips, “On Clique Graphs and Clique Regular
Graphs,” *Discrete Mathematics* 349(3) (March 2026), article 114862, DOI
[10.1016/j.disc.2025.114862](https://doi.org/10.1016/j.disc.2025.114862):

- publisher record:
  <https://www.sciencedirect.com/science/article/pii/S0012365X25004704>
- arXiv record: <https://arxiv.org/abs/2502.17845>

The abstract applies clique-graph results to Conway's 99-graph problem and
other SRG existence problems. No statement resolving the target, and no bound
\(n_3\geq54\), was found.

Ali Keramatipour, “Approaching the Conway-99 problem using SAT solvers,”
arXiv:2604.23037v2 (2026), DOI
[10.48550/arXiv.2604.23037](https://doi.org/10.48550/arXiv.2604.23037):

- record: <https://arxiv.org/abs/2604.23037>
- current PDF: <https://arxiv.org/pdf/2604.23037v2>

The abstract says the experiments demonstrate the inability of the tested SAT
approach to handle the problem in reasonable time. Printed page 42 records
12-hour test limits, page 47 discusses only what the failed search may suggest
about automorphisms, and page 49 reports solver failure and future work. A
timeout or solver failure is not a nonexistence certificate.

Reimbay Reimbayev, “Nonexistence of \(\operatorname{srg}(19,6,1,2)\):
Combinatorial Proof,” arXiv:2511.06569v1 (2025), DOI
[10.48550/arXiv.2511.06569](https://doi.org/10.48550/arXiv.2511.06569):

- record: <https://arxiv.org/abs/2511.06569>
- PDF: <https://arxiv.org/pdf/2511.06569v1>

Printed pages 1 and 4 distinguish the proved nonexistence of the order-19 graph
from the still ongoing order-99 search. This is corroborating preprint evidence,
not a stronger status authority than the peer-reviewed 2025 paper.

### 1.4 June 2026 Shpectorov lecture: scope boundary

Hebei Normal University's official announcement for Sergey Shpectorov's
2026-06-25 lecture, “Non-existence of the strongly regular graph
\(\operatorname{srg}(85,14,3,2)\),” is:

<https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html>

The announcement says complete enumeration and elimination concerns
\(\operatorname{srg}(85,14,3,2)\). For
\(\operatorname{srg}(99,14,1,2)\), it says only that the speakers will discuss
“a possible similar approach.” Thus the event notice is evidence of an ongoing
methodological direction, not a Conway-99 proof, counterexample, complete
search, or prior statement of either Wave 16 bound.

## 2. Exact page audit of the induced-hexagon identity

Reimbay Reimbayev, “The lower bound for number of hexagons in strongly regular
graphs with parameters \(\lambda=1\) and \(\mu=2\),” *e-Journal of Analysis
and Applied Mathematics* (2024), 1–14, DOI
[10.62780/ejaam/2024-001](https://doi.org/10.62780/ejaam/2024-001):

- exact PDF:
  <https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf>

The relevant hypotheses and definitions were checked directly:

- Printed page 3 defines \(p_i\), for \(i=3,4,5,6\), as the number of
  **induced** subgraphs isomorphic to \(C_i\). Therefore its \(p_6\) is an
  induced-\(C_6\) count, not the count of all six-cycles possibly carrying
  chords.
- Printed page 10 identifies \(n_{12}\) with the relevant type of hexagon.
- Printed page 11 obtains \(n_{12}=F(n,k)+n_3\).
- Printed page 12 gives the exact identity

  \[
  p_6=n_{12}
  =\frac1{12}nk(k-2)(2k^2-21k+53)+n_3.
  \]

- Theorem 3.3 on printed page 12 uses only \(n_3\geq0\), giving the published
  general lower bound.
- Printed page 13 discusses equality \(n_3=0\) as conjectural context. It does
  not prove \(n_3=0\).

For \(n=99\) and \(k=14\),

\[
\begin{aligned}
\frac1{12}(99)(14)(12)
  \left(2\cdot14^2-21\cdot14+53\right)
&=(99)(14)(151)\\
&=209286.
\end{aligned}
\]

Hence the cited identity specializes to

\[
p_6=209286+n_3.
\]

The published lower bound alone is \(p_6\geq209286\). The strengthened value
\(209340\) is not the theorem stated in this paper; it follows only after an
additional, independently justified \(n_3\geq54\).

## 3. What the existing six- and seven-vertex work says about \(n_3\)

### 3.1 Six-vertex catalog

Reimbay Reimbayev, “The Subgraphs of Order Six of the Family of Strongly
Regular Graphs with Parameters \(\lambda=1\) and \(\mu=2\),”
arXiv:2508.03377v2 (2025), DOI
[10.48550/arXiv.2508.03377](https://doi.org/10.48550/arXiv.2508.03377):

- record: <https://arxiv.org/abs/2508.03377>
- v2 PDF: <https://arxiv.org/pdf/2508.03377v2>

Printed pages 2–3 define 62 induced six-vertex types \(N_i\), with counts
\(n_i\), and select \(n_3\) as a free parameter. Figure 1 on printed page 4
depicts \(N_3\): two vertex-disjoint triangles joined by exactly two independent
cross-edges. Printed page 3 gives

\[
2p_4=3n_1+n_3.
\]

For the Conway parameters,

\[
p_4=\frac{nk(k-2)}8=2079,
\qquad
3n_1+n_3=4158,
\]

so \(3\mid n_3\). This is an elementary consequence of the displayed relation.
It does not imply \(n_3\geq54\).

Printed pages 17–20 consolidate the 62 affine formulas in \(n_3\). Printed page
20 explicitly leaves \(n_3\) free and suggests zero only through informal
symmetry motivation; the conclusion on printed page 24 does not turn that
suggestion into a theorem. No statement \(n_3\geq54\) was found in v2.

### 3.2 Makhnev's conditional result

A. A. Makhnev, “Strongly regular graphs with \(\lambda=1\),” *Mathematical
Notes* 44 (1988), 847–850 (Russian original *Mat. Zametki* 44(5), 667–672),
DOI [10.1007/BF01158426](https://doi.org/10.1007/BF01158426):

- MathNet record: <https://www.mathnet.ru/eng/mzm/v44/i5/p667>

The indexed abstract says that Makhnev studies the case with no two triangles
joined by exactly two edges and, under that condition, excludes the parameter
set \((99,14,1,2)\). In a graph with \(\lambda=1\), cross-edges between two
disjoint triangles form a matching, so this is the \(n_3=0\) case represented
by \(N_3\).

Accordingly, the conditional theorem implies that any existing Conway graph
must have \(n_3>0\). Combined with \(3\mid n_3\), it gives only
\(n_3\geq3\). It does not supply \(n_3\geq54\).

The MathNet page could not be decoded directly in this environment; the title,
bibliography, and abstract scope were checked through its authoritative indexed
record and DOI metadata. This access limitation is material and is not hidden.

### 3.3 Seven-vertex continuation

Reimbay Reimbayev, “Hamiltonian Subgraphs of Order Seven in
\(\operatorname{srg}(n,k,1,2)\),” arXiv:2511.06572v1 (2025), DOI
[10.48550/arXiv.2511.06572](https://doi.org/10.48550/arXiv.2511.06572):

- record: <https://arxiv.org/abs/2511.06572>
- PDF: <https://arxiv.org/pdf/2511.06572v1>

Printed pages 2 and 4–7 retain \(n_3\) as a free parameter and introduce a
seven-vertex parameter \(h_{11}\), including

\[
2n_3\leq h_{11}\leq4n_3.
\]

This does not force a positive lower bound for \(n_3\), does not resolve the
target, and does not state either Wave 16 number.

## 4. Later citations, corrections, and database coverage

### 4.1 Citation-index check for the 2024 hexagon paper

The following exact Semantic Scholar API query was used:

<https://api.semanticscholar.org/graph/v1/paper/DOI:10.62780/ejaam/2024-001?fields=title,year,citationCount,citations.title,citations.year,citations.externalIds>

It returned three citing works:

1. arXiv:2508.03377, the six-vertex catalog audited above;
2. arXiv:2511.06569, the order-19 nonexistence preprint;
3. arXiv:2511.06572, the seven-vertex continuation audited above.

None states \(n_3\geq54\), \(p_6\geq209340\), or a correction to the exact
hexagon identity.

Crossref was queried at
<https://api.crossref.org/works/10.62780%2Fejaam%2F2024-001>; it records the
journal article and `is-referenced-by-count: 0`. OpenAlex was queried at
<https://api.openalex.org/works/https://doi.org/10.62780/ejaam/2024-001>; it
also returned a zero citation count at access time. These conflicting counts
show why citation indexes are discovery aids, not exhaustive certificates.

No publisher correction, erratum, revised journal version, or arXiv correction
that changes the identity or provides the two Wave 16 bounds was located.

### 4.2 Strongly regular graph and general graph databases

- Brouwer's maintained SRG table is the relevant order-99 status registry and
  is discussed in Section 1.1.
- Ted Spence's SRG collection,
  <https://www.maths.gla.ac.uk/~es/srgraphs.php>, states that its collection
  covers strongly regular graphs on at most 64 vertices. It therefore cannot
  settle whether an order-99 graph is present.
- Searches of House of Graphs,
  <https://houseofgraphs.org/>, did not locate an exact Conway-99 object. House
  of Graphs is a general submitted-graph database; absence from it is not
  evidence of nonexistence.

## 5. Search nonhits

The following exact search strings produced no indexed source stating the Wave
16 bounds or resolving the exact target. The strings are preserved to prevent
silent inflation of search coverage.

### Exact target and current status

```text
"srg(99,14,1,2)"
"strongly regular graph" "99, 14, 1, 2"
"Conway 99-graph" OR "Conway's 99-graph" OR "Conway-99"
"99-graph" Conway strongly regular
"99 14 1 2" strongly regular database
"(99,14,1,2)" "open problem" 2026
"(99,14,1,2)" "unknown" 2025 2026 graph
"Conway 99" "2026" graph
```

### Exact Wave 16 numbers

```text
"209340" graph hexagons
"209,340" graph hexagons
"n_3" "99,14,1,2"
"n3" "Conway 99" graph
"n_3 >= 54" graph
"n_3 ≥ 54" graph
"n3 >= 54" "strongly regular"
"209286" "n_3"
"p_6" "209340" graph
"p6" "209340" graph
"209,340" "C_6" graph
"209340" "strongly regular graph"
```

The exact `209340` hits returned only unrelated product numbers or identifiers.

### Alternate structural terminology

```text
"n3=51" "Conway" graph
"n_3=51" "Conway" graph
"active triangle" "Conway 99"
"point hypergraph" "Conway 99"
"sum_T q(T)" "Conway" graph
"two disjoint triangles" "n_3" strongly regular
"two disjoint triangles" "99,14,1,2"
"induced C6" "99,14,1,2"
```

No indexed source was found for the exact \(n_3=51\) exclusion, the “active
triangle” or “point hypergraph” formulation, or the displayed local-support
expression.

### Citations and corrections

```text
"10.62780/ejaam/2024-001" citations
"The lower bound for number of hexagons" Reimbayev cited
"The Subgraphs of Order Six" Reimbayev
"2508.03377" citations OR correction OR erratum
site:arxiv.org Reimbay Reimbayev "srg(99,14,1,2)"
site:arxiv.org Reimbayev "n_3" "srg(n,k,1,2)"
site:arxiv.org "Conway-99" "n_3"
site:arxiv.org "Conway 99" "hexagons"
```

### Database and collection aliases

```text
site:houseofgraphs.org "99" "14" strongly regular
House of Graphs Conway 99 graph
site:maths.gla.ac.uk/~es/srgraphs "99" strongly regular
Ted Spence strongly regular graphs database order 99
```

### Grey-literature checks

```text
Guseinov Conway 99 graph "two triangles"
Guseinov Conway 99 graph hexagon
"Five new results of Conway's 99-graph problem"
"On Conway's 99-graph: Parts 1-20"
```

Grey literature and public code concerning Conway-99 exist, but no indexed
item located under these queries stated the exact Wave 16 bounds. Unrefereed
claims would in any case require an independent proof audit before status
promotion.

### June 2026 Shpectorov check

```text
Shpectorov June 2026 lecture srg(99,14,1,2)
Shpectorov 2026 Conway 99 strongly regular lecture
"srg(99, 14, 1, 2)" Shpectorov
"SRG(99,14,1,2)" Shpectorov
"99,14,1,2" "Shpectorov"
"possible similar approach" strongly regular 99 Shpectorov
```

These queries found the official lecture announcement audited in Section 1.4.
The wording does not claim a result for order 99.

## 6. Search and access failures retained

1. PowerShell in this environment does not support `Get-Date -AsUTC`; the UTC
   timestamp was instead obtained with
   `[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')`.
2. Initial `pypdf` extraction failed under the default Windows code page on a
   Unicode minus sign. Re-running with `PYTHONIOENCODING=utf-8` succeeded.
3. An initial unversioned Keramatipour PDF fetch produced arXiv v1
   (SHA-256
   `fe3ab8141805dcbac77690f7d20ddc397749cf0ab928dee4ebeb4837d7d13e34`).
   Inspection of the official arXiv record showed that v2 is current, so all
   conclusions above use v2 (SHA-256
   `8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8`).
4. A Semantic Scholar lookup by `ARXIV:2508.03377` returned an empty response;
   the DOI-based request listed in Section 4.1 succeeded.
5. A later Crossref repetition returned HTTP 429 after an earlier successful
   response. The successful metadata response is what is reported.
6. The MathNet HTML record produced a Unicode decoding error in automated
   opening; its indexed authoritative record and DOI metadata were used, and
   no stronger page-level claim is attributed to it.
7. The Elsevier landing page returned HTTP 403 during an automated re-check.
   The DOI metadata and arXiv manuscript were available. The Petro–Phillips
   paper is not used as the decisive open-status source.
8. Search engines returned noisy false positives, including unrelated uses of
   “SRG” and raw number `209340`. These were not treated as mathematical
   sources.

## 7. Inference audit and final labels

The following deductions are arithmetic or logical inferences from cited
relations; they are not quotations from the literature:

1. From Reimbayev's exact identity at \(n=99,k=14\),
   \(p_6=209286+n_3\).
2. From \(2p_4=3n_1+n_3\) and \(p_4=2079\),
   \(3n_1+n_3=4158\), hence \(3\mid n_3\).
3. Makhnev's conditional exclusion of \(n_3=0\), combined with divisibility,
   gives only \(n_3\geq3\).
4. If the separately audited Wave 16 proof establishes \(n_3\geq54\), then
   \(p_6\geq209286+54=209340\).

| Claim | Label in this audit | Reason |
|---|---|---|
| An \(\operatorname{srg}(99,14,1,2)\) exists | `UNKNOWN` | No construction/certificate found; current sources call existence open. |
| No \(\operatorname{srg}(99,14,1,2)\) exists | `UNKNOWN` | No proof/complete-search certificate found. |
| \(p_6=209286+n_3\) for the exact cited definitions | `CITED` | Published 2024 identity; hypotheses and pages checked. |
| \(n_3\geq54\) for every putative Conway graph | `UNKNOWN` | No prior source found; Wave 16 proof not reverified by this status audit. |
| \(p_6\geq209340\), conditional on verified \(n_3\geq54\) | `DERIVED` | Direct substitution in the cited identity. |
| Literature novelty of either exact Wave 16 bound | `UNKNOWN` | Broad nonhit search is not an exhaustive novelty certificate. |

No item in this report promotes the target or either Wave 16 inequality to
`VERIFIED`.
