# Wave 18 status and literature audit

```yaml
role: verifier
date_utc: 2026-07-23T13:04:40Z
git_commit: PENDING_ROOT_INTEGRATION
claim_label: VERIFIED
scope: >
  Verification of the source, status, and scope claims in
  agents/2026-07-23-wave18-status-search.md. VERIFIED applies only to
  that report as a conservative literature/status audit. It does not
  verify a Wave 18 proof, novelty, or either existence outcome for
  SRG(99,14,1,2), all of which remain UNKNOWN.
inputs:
  - path: AGENTS.md
    sha256: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  - path: CONJECTURE.md
    sha256: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  - path: STRUCTURE.md
    sha256: e8e478d641740936a6340978cb17784ac087d3a3056367758064006e66ff8547
  - path: agents/2026-07-23-wave18-n3-57-structural.md
    sha256: fa1dde1f96aaaf2c9a90c73308afbc967fab892fe79246bf7eafa2831fea38f6
  - path: agents/2026-07-23-wave18-status-search.md
    sha256: 9197c32813bf749b0dde1c7d64ed3294a56e9b4e6c3c92dd0d693ffe3e290ad3
method: >
  Froze the source/check matrix below before opening the submitted
  report; inspected maintained, journal, proceedings, institutional,
  arXiv, and author-hosted primary sources; executed exact and
  alternate-notation queries; then reconstructed Ishihara's local
  count from the frozen root labeling independently.
command: >
  Exact web queries and access results are recorded below. Local inputs
  were hashed with Get-FileHash -Algorithm SHA256. Remote resources
  were downloaded as response bytes in memory and hashed with
  System.Security.Cryptography.SHA256; no solver was used.
outputs:
  - verification/2026-07-23-wave18-status-audit.md
limitations: >
  A focused literature audit cannot establish novelty or exhaust all
  unpublished work. Conference abstracts are not proofs. A defect in a
  published proof is not a proof of existence or nonexistence of the
  target graph.
```

## Preinspection freeze

This matrix was written at 2026-07-23T12:54:00Z **before opening**
`agents/2026-07-23-wave18-status-search.md`.  The submitted status report
was excluded from the preceding workspace inventory.  The verifier will
not change the questions or acceptance rules after comparison; any added
lead will be marked postinspection.

| ID | Frozen source/query | Check | Acceptance rule |
|---|---|---|---|
| S1 | Andries Brouwer's current strongly regular graph table, row `(99,14,1,2)`, plus exact web queries `"99 14 1 2" strongly regular graph`, `"Conway's 99-graph"`, and `srg(99,14,1,2)` | Is the exact parameter set still displayed as unknown, and is there an authoritative later resolution? | Only an explicit construction with a checkable graph/certificate, or a proof of nonexistence in a primary source, resolves the target. A table mark and focused nonhits support only `UNKNOWN`. |
| S2 | Reimbayev primary paper located via exact queries `Reimbayev strongly regular six cycles 209286`, `"209286" graph`, and `Reimbayev p_6 n_3` | Verify the exact formula, notation, hypotheses, and whether `p6` counts induced/chordless 6-cycles. | Record the displayed equation/theorem and page. Do not invert the identity into an existence result. |
| S3 | Exact queries `"n_3=57" "99" graph`, `"n3=57" "strongly regular"`, `"n_3 >= 60" graph`, `"209346" graph`, and `"209346" "strongly regular"` | Search specifically for prior exclusion of the `n3=57` case, an `n3>=60` bound, or the corresponding `p6>=209346` bound. | Nonhits are evidence only of a focused unsuccessful search; novelty remains `UNKNOWN`. |
| S4 | Primary Ishihara 2022 source containing Theorem 28 and equation (88), located via exact queries `"Theorem 28" Ishihara partial quadrangle`, `Ishihara 2022 strongly regular 99 graph`, and `Ishihara "equation (88)"` | Read theorem hypotheses, frozen labels, equation (88), and adjacent prose. Reconstruct the asserted `H2`-to-`H1` neighbor count directly from the frozen root labeling in the repository. | The count must follow from definitions for every vertex in the named cell. A mismatch is a defect/gap in that proof step, not a target resolution. |
| S5 | Official May 2026 conference programme/abstract for Ben Baker, located via exact queries `"Ben Baker" "Conway's 99-graph"`, `"Ben Baker" 99 graph May 2026`, and `"Conway 99" conference 2026` | Quote/paraphrase only what the abstract actually claims; look separately for paper/slides. | An announcement or abstract without accessible proof/certificate cannot verify a resolution. Record unavailable materials and access dates. |
| S6 | Primary/standard sources for the Hoffman/Delsarte ratio (Rayleigh quotient) bound, plus exact queries `"Rayleigh quotient" strongly regular graph subset bound` and `"Hoffman bound" induced subgraph regular subset` | Decide whether the generic spectral/Rayleigh inequality used here is established prior art, independently of the new application. | Label the generic inequality `CITED` if sourced; do not infer that this exact Conway-99 application or numerical consequence was previously published. |
| L1 | `CONJECTURE.md`, `STRUCTURE.md`, `agents/2026-07-23-wave18-n3-57-structural.md`, and `verification/3-57-structural/preinspection-freeze.md` | Freeze the root-neighborhood labels and derive all possible neighbors of an `H2` vertex in `H1` without using the status report's derivation. | State the labeling explicitly and show the count algebraically/combinatorially. Any reliance on an unstated regularity or cell-equitability assumption is a failure. |
| C1 | Submitted `agents/2026-07-23-wave18-status-search.md`, opened only after this freeze | Compare every substantive source claim, URL, date, page, quote/paraphrase, and status label with S1--S6/L1. | Verifier may downgrade/veto but will not silently repair the submitted report. |

## 1. Verdict

The submitted report is **`VERIFIED` for its literature/status scope**.
Its main conclusions, source descriptions, applicability distinctions,
and conservative labels survived independent checking:

- no authoritative construction/certificate or valid nonexistence proof
  for `srg(99,14,1,2)` was located through 2026-07-23;
- Reimbayev's published result is the identity
  `p6=209286+n3` and the lower bound obtained only from `n3>=0`;
- no exact primary-source hit was found for exclusion of `n3=57`,
  `n3>=60`, or `p6>=209346`;
- Ishihara's Theorem 28 does make the claimed nonexistence assertion,
  but equation (88) rests on a false uniform-neighbor premise;
- Baker's May 2026 conference abstract is a real methodological
  near-match, but it is not a paper, proof, or resolution; and
- the generic subset-edge inequality is standard spectral prior art,
  while the exact Wave 18 active-set use is not thereby prior art.

Two annotations strengthen, rather than overturn, the submitted report:

1. Ishihara's failed count can be reconstructed exactly. The degrees
   from `H2` into `H1` are `1^20,2^51`, and the corrected double count is
   `10(10)+11(2)=122=2(71)-20`, not equation (88)'s `142`.
2. The report's claim that the generic Rayleigh inequality is standard
   is correct. Its citations should ideally include the Alon--Chung
   subset-edge lemma explicitly; Evans is useful context but is not the
   earliest generic source.

This verdict does **not** promote the prospective Wave 18 exclusion to
literature evidence or to a verified theorem. Target resolution and
novelty remain **`UNKNOWN`**.

## 2. Source integrity and access register

All remote resources below were accessed on 2026-07-23. SHA-256 values
are over the raw response bytes returned in this audit, not over
extracted text. Dynamic HTML hashes may change when a site changes its
markup.

| Resource | Bytes | SHA-256 | Exact use |
|---|---:|---|---|
| [Brouwer SRG table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html) | 24,003 | `db88468cc47bb5aa9108d488596557de3a68ec80dcf5f7ffea9f2e16d3f60f89` | Current row for `(99,14,1,2)` |
| [Cesarz--Woldar article page](https://alco.centre-mersenne.org/articles/10.5802/alco.418/) | 46,202 | `2a4c80ca0e181217b7ca5272c3a50c0eff868ac655c618859195ca093282fd08` | Publication metadata and abstract |
| [Cesarz--Woldar PDF](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf) | 964,747 | `d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8` | Open-status wording and root labeling |
| [Ishihara article page](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_article/-char/en) | 63,026 | `638f37bbd9dd794b53f41d94c67313dfa50d76d4629e264f4d4ed3405c376f7e` | Official metadata |
| [Ishihara PDF](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_pdf/-char/en) | 291,964 | `274818e17f4ae2df8cb74d157e2025d18d8b8ca3a6c910586187a1165f143c3b` | Theorem 28, (88)--(90), pp. 15--16 |
| [Reimbayev 2024 PDF](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf) | 372,641 | `484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521` | `n3`, `n12`, and Theorem 3.3 |
| [Reimbayev 2025 arXiv v2 PDF](https://arxiv.org/pdf/2508.03377) | 873,456 | `c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9` | Later census retaining `n3` as free |
| [Petro--Phillips PDF](https://arxiv.org/pdf/2502.17845) | 3,107,011 | `9adb7132b4a40ce87d77b2326fc6ddf1370aa12665f86617aa285b9e824797be` | Recent conditional clique-graph context |
| [Keramatipour PDF](https://arxiv.org/pdf/2604.23037) | 2,763,608 | `8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8` | April 2026 SAT attempt without certificate |
| [Phillips thesis PDF](https://arxiv.org/pdf/2605.22867) | 1,059,251 | `12247e688b93fae41726ce7e5175d6c496a38b7537f2f5ce0f87f094031f86e9` | May 2026 open-status signal |
| [Baker/Cumberland program PDF](https://www.auburn.edu/cosam/departments/math/cumberland-conference/34th_cumberland_program.pdf) | 411,540 | `ccaeef479f24c2a8e7994ba11220b6846ba7fddb541079c9954152bb6906090d` | Official abstract, PDF p. 4 |
| [Cumberland conference home](https://www.auburn.edu/cosam/departments/math/cumberland-conference/home.htm) | 31,459 | `30731815470ae8509fa22b9e78bb1d68a8ef82470950bb3994dcd4428e78440f` | Official May 16--17, 2026 dates |
| [Hebei Normal announcement](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html) | 24,491 | `9de956e78febf23483b337a7c1d851363720c55158d1a4164f3249dcb673a57e` | June 2026 different-target status signal |
| [Alon--Chung author-hosted reprint](https://web.math.princeton.edu/~nalon/PDFS/Publications/Explicit%20construction%20of%20linear%20sized%20tolerant%20networks.pdf) | 161,581 | `713d14971516e2a78bd619d04867d2da210c6990027161a0e45d2d2736f775f7` | Generic induced-subset spectral estimate |
| [Brouwer--Van Maldeghem corrected preprint](https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf) | 2,902,008 | `fa73d72e86bbd8dc3fbfcbca45679cb8f2671d777e91c009eeff0a563fd9289d` | Standard interlacing/Rayleigh context |
| [Evans arXiv PDF](https://arxiv.org/pdf/2202.03700) | 561,185 | `59e5766303d5d5fd033d51f4463de5d6a51a992cd9d28fe09c32c9eaac6a543e` | Regular induced-subgraph context |

Access limits:

- [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf)
  was readable through browser PDF extraction (12 pages), but the
  independent raw-byte request returned HTTP 403, so no verifier-side
  response hash is asserted.
- The old TU/e direct PDF URL for Wilbrink returned 404 to the raw-byte
  client; search-index text and the [metadata
  page](https://research.tue.nl/en/publications/on-the-991412-strongly-regular-graphs/)
  were available, but a stable full-text hash was not obtained.
- The Math-Net metadata for Makhnev was discoverable, but reliable
  original-text extraction failed in this lane. The audit therefore
  relies only on Reimbayev's explicit description of the restricted
  `n3=0` consequence and makes no stronger claim about Makhnev.
- No Baker manuscript or slide deck was located. Consequently there is
  nothing beyond the conference abstract to hash or theorem-check.
- The frozen L1 row accidentally omitted the leading `n` from the
  actual path
  `verification/n3-57-structural/preinspection-freeze.md`. The
  correctly named file existed at completion (SHA-256
  `2127ca8b3468cfe04d649180f37cc3f4a2a5b283b4988d309ccd3ccc798bf001`)
  and was not used in this literature derivation. The root labeling was
  reconstructed from `CONJECTURE.md`, `STRUCTURE.md`, and the hashed
  structural report.

## 3. Current Conway-99 status through 2026-07-23

The maintained Brouwer table displays

```text
? 99 14 1 2 3^54 -4^44
```

at row 96. This is a current status signal, not a proof that no very
recent result exists.

The strongest recent primary signals found are mutually consistent:

- Patrick G. Cesarz and Andrew J. Woldar, *On the automorphism group of
  a putative Conway 99-graph*, *Algebraic Combinatorics* 8(2) (2025),
  379--398, [DOI 10.5802/alco.418](https://doi.org/10.5802/alco.418),
  published online 2025-04-24. The abstract and introduction, PDF
  pp. 2--3 (journal pp. 379--380), call existence an elusive,
  longstanding open problem and prove only automorphism restrictions.
- Ali Keramatipour,
  [arXiv:2604.23037v2](https://arxiv.org/abs/2604.23037), revised
  2026-04-28, reports that the tested SAT encoding cannot handle the
  instance in reasonable time and says better strategies are needed.
  It supplies neither a satisfying assignment nor an UNSAT certificate.
- Connor M. Phillips,
  [arXiv:2605.22867](https://arxiv.org/abs/2605.22867), May 2026,
  treats the Conway prize as unclaimed and studies possible
  clique-graph methods; it gives no resolution.
- The 2026-06-24 Hebei Normal University announcement is titled
  *Non-existence of the strongly regular graph srg(85,14,3,2)*. It says
  only that a “possible similar approach” to `(99,14,1,2)` will be
  discussed. The proved/computational target is different.
- Baker's May 2026 abstract considers an application of a general
  induced-subgraph paradigm to Conway-99, but states no construction or
  nonexistence theorem.

The exact searches

```text
"srg(99,14,1,2)" 2026 proof construction nonexistence
"Conway 99-graph" 2026 resolution
site:arxiv.org "Conway-99" OR "Conway 99" 2026 strongly regular
"99,14,1,2" July 2026 strongly regular
```

found the sources above and restricted/older work, but no authoritative
resolution. Search nonhits cannot establish that a problem is open.
Accordingly both “a target graph exists” and “no target graph exists”
remain **`UNKNOWN`**.

## 4. Reimbayev's exact scope

Reimbay Reimbayev, *The Lower Bound for Number of Hexagons in Strongly
Regular Graphs with Parameters lambda=1 and mu=2*, *e-Journal of
Analysis and Applied Mathematics* (2024), 1--14,
[DOI 10.62780/ejaam/2024-001](https://doi.org/10.62780/ejaam/2024-001),
is the primary source.

The notation and pages check as follows:

- printed p. 8 (PDF index 7), Figure 3 and the adjacent prose, defines
  `ni` to count induced copies of graph type `i`;
- printed p. 11 (PDF index 10), after equations (5) and (6), derives
  `n4=2n3` and `n12=F(n,k)+n3`;
- printed p. 12 (PDF index 11) gives

  ```text
  n12 = (1/12) n k (k-2) (2k^2-21k+53) + n3
  ```

  and Theorem 3.3 uses only `n3>=0`; and
- printed p. 13 describes the type-3 obstruction as two disjoint
  triangles connected through two edges. In the Figure 3 convention,
  these are two of the three possible independent cross edges.

Thus `n12` is the number of induced/chordless 6-cycles, and project
notation may set `p6=n12`. For `(n,k)=(99,14)`,

```text
2(14)^2 - 21(14) + 53 = 151
(1/12)(99)(14)(12)(151) = 99*14*151 = 209286.
```

Therefore

```text
p6 = 209286 + n3.
```

The published lower bound is only `p6>=209286`. The statement

```text
n3>=60  ==>  p6>=209346
```

is correct conditional arithmetic, but `n3>=60` is not supplied by that
paper. Reimbayev's later
[arXiv:2508.03377v2](https://arxiv.org/abs/2508.03377), pp. 1--2 and
printed p. 6, again retains this same `n3` as a free variable and repeats
the identity. Its symbol `n57` elsewhere is a count of enumerated graph
type `N57`, not the value assertion `n3=57`.

Labels:

- general identity: **`CITED`**;
- specialization `209286+n3`: **`DERIVED`**;
- implication from a separately verified `n3>=60`: **`DERIVED`**;
- unconditional published `p6>=209346`: **`UNKNOWN`**.

## 5. Focused numerical prior-art searches

The following frozen families and punctuation/TeX variants were
executed:

```text
"n_3=57" "99" graph
"n3=57" "strongly regular"
"n3=57" Conway
"n_3=57" "99,14,1,2"
"exclude n3=57" graph
"n3 >= 60" Conway graph
"n_3 >= 60" "strongly regular"
"n_3\geq 60" "strongly regular"
"n3 > 57" graph
"209346" "strongly regular"
"209346" Conway "99" graph
"209,346" hexagons
"p6=209286+n3"
"209286+n3" graph
```

The relevant hits led back to Reimbayev's 2024 identity and 2025 census.
The other `209346` hits were unrelated numeric noise. No primary exact
hit was found for:

- exclusion of `n3=57`;
- a conditional or unconditional `n3>=60`; or
- an induced-hexagon endpoint `209346`.

This is a focused nonhit only. It does not certify novelty. All three
prior-art questions remain **`UNKNOWN`**.

## 6. Generic Rayleigh-bound prior art

Let `A` be the adjacency matrix of a `d`-regular graph on `n` vertices,
let `X` have size `m`, and let `r` be the second-largest adjacency
eigenvalue. Write

```text
1_X = (m/n) 1 + y,    y perpendicular to 1,
||y||^2 = m - m^2/n.
```

Rayleigh's inequality on `1^\perp` gives

```text
2e(X) = 1_X^T A 1_X
      <= d m^2/n + r(m-m^2/n).
```

For the target spectrum `14,3,-4`,

```text
2e(X) <= 14m^2/99 + 3(m-m^2/99)
       = 3m + m^2/9.
```

The calculation is exact and uses the one-sided second-largest
eigenvalue `3`, not the absolute nonprincipal maximum `4`.

The generic method is established prior art. N. Alon and F. R. K.
Chung, *Explicit construction of linear sized tolerant networks*,
*Discrete Mathematics* 72 (1988), 15--19,
[DOI 10.1016/0012-365X(88)90189-6](https://doi.org/10.1016/0012-365X(88)90189-6),
was reprinted in *Discrete Mathematics* 306 (2006), 1068--1071,
[DOI 10.1016/j.disc.2006.03.025](https://doi.org/10.1016/j.disc.2006.03.025).
Lemma 2.3 on reprint p. 1069 gives the classic induced-subset density
estimate using a bound on absolute nonprincipal eigenvalues. The
one-sided second-eigenvalue upper form above is the immediate Rayleigh
variant commonly called the Alon--Chung lemma. Brouwer and Van
Maldeghem, *Strongly Regular Graphs*, corrected preprint, Section
1.1.14, printed pp. 25--26, supplies standard interlacing and equality
context.

Hence:

- generic Rayleigh/Alon--Chung subset-edge method:
  **`CITED` / `DERIVED`**, standard;
- substitution of the target spectrum: **`DERIVED`**;
- the exact active-set definition, lower crossing count, and endpoint
  use in Wave 18: novelty **`UNKNOWN`**.

The submitted report is mathematically right on this point. Adding the
Alon--Chung citation would improve attribution but is not a correctness
repair.

## 7. Ishihara Theorem 28 and equation (88)

### 7.1 What the primary source asserts

Hideto Ishihara, *Theory of the pain of humans etc.*, JSAI Technical
Report, 2022 AGI-021 article 01, released 2022-07-14,
[DOI 10.11517/jsaisigtwo.2022.AGI-021_01](https://doi.org/10.11517/jsaisigtwo.2022.AGI-021_01).

On PDF p. 15, Theorem 28 asserts that no
`srg(99,14,1,2)` exists. The proof fixes `w0`, calls its neighborhood
`L1^0`, and calls the 84-vertex residual graph `L2^0`. In each residual
component `Hk`, it fixes `wk`, defines `H1^k` as the residual neighbors
of `wk`, and defines `H2^k` as the remaining component vertices. It
then states that every vertex of `H2^k` has exactly two neighbors in
`H1^k`.

With `sk` and `tk` counting vertices of `H1^k` having respectively 10
and 11 neighbors in `H2^k`, and `bk=|H2^k|`, PDF pp. 15--16 display

```text
10 sk + 11 tk = 2 bk              (88)
sk + tk = 12                      (89)
sum_k bk = 84 - 13K               (90)
```

The note immediately below (90) explicitly says (88) comes from the
asserted uniform degree two from `H2^k` into `H1^k`.

### 7.2 Independent exact reconstruction

Assume a target graph `G` only for the purpose of checking the claimed
necessary count. Fix `x=w0`.

1. Since `lambda=1`, `G[N(x)]` is a perfect matching on 14 vertices.
   Every residual vertex has exactly two neighbors in `N(x)` by
   `mu=2`; call this unordered pair its root label.
2. A root label cannot be a matched pair, because its endpoints already
   have `x` as their unique common neighbor. Conversely, every
   nonmatched pair in `N(x)` has, besides `x`, a unique residual common
   neighbor. Thus the 84 residual vertices are in bijection with the
   `C(14,2)-7=84` nonmatched pairs.
3. The residual graph is connected. If residual vertices in different
   components were chosen, they would have no residual common neighbor.
   Their two common neighbors would both lie in `N(x)`, so their root
   labels would be identical, contradicting the bijection. Therefore
   Ishihara's `K=1`.
4. Fix `w` with label `P={a,b}`. Among other valid labels, 11 contain
   `a` and 11 contain `b`, so exactly 22 meet `P`.
5. Exactly one residual neighbor of `w` has a label containing `a`:
   it is the unique residual common neighbor of the adjacent pair
   `(w,a)`. Similarly exactly one contains `b`. Hence `H1=N_R(w)` has
   two intersecting-label vertices and ten disjoint-label vertices.
6. Consequently `H2=R\({w} union H1)` has 71 vertices: 20 labels meet
   `P`, and 51 are disjoint from `P`.
7. If `z` in `H2` has a label meeting `P`, then `z` and `w` already
   share one common neighbor in `N(x)`. Because they are nonadjacent and
   `mu=2`, they have exactly one residual common neighbor. Thus `z` has
   exactly one neighbor in `H1`.
8. If the labels of `z` and `w` are disjoint, none of their common
   neighbors lies in `N(x)`. Both `mu=2` common neighbors are residual,
   so `z` has exactly two neighbors in `H1`.

The exact `H2`-to-`H1` degree multiset is therefore

```text
1^20, 2^51,
```

not uniform degree two.

The other side of the double count is equally explicit. A vertex of
`H1` whose label meets `P` has no neighbor inside `H1`: its one common
neighbor with the adjacent vertex `w` is already the shared root
neighbor. A disjoint-label vertex of `H1` has exactly one neighbor
inside `H1`, the unique residual common neighbor with `w`. After
subtracting its two root neighbors and `w`, its `H2` degree is therefore
11 in the first case and 10 in the second. Thus

```text
s=10, t=2, b=71,
10s+11t = 100+22 = 122,
sum_{z in H2} deg_H1(z) = 20+2(51) = 122 = 2b-20.
```

Equation (88) instead sets the last quantity to `2b=142`. The corrected
count is consistent and produces no contradiction.

The submitted report's weaker “at least ten” argument is already
sufficient to falsify the premise; the exact reconstruction above
strengthens it.

The logically distinct labels are:

- Ishihara's uniform `H2`-to-`H1` premise: **`REFUTED`**;
- the displayed proof establishes Theorem 28: **`REFUTED`**;
- a target graph exists: **`UNKNOWN`**;
- no target graph exists: **`UNKNOWN`**.

This is a defect in a purported proof, not a construction and not a
resolution in either direction.

## 8. Ben Baker's May 2026 abstract

The official 34th Cumberland Conference site gives the dates
2026-05-16--17 at Auburn University. The official program's PDF p. 4
contains:

```text
An Induced Subgraph Paradigm for Strongly Regular Graph Constructions
Ben Baker
Auburn University
```

The abstract says that it gives upper and lower bounds on disjoint
copies of an induced subgraph `H` depending on the size of their
neighborhood; equality forces outgoing edges to be evenly distributed;
this generalizes a Lou--Murin independence bound; and the approach is
considered for Conway's 99-graph problem.

It does **not** state:

- existence or nonexistence of a Conway graph;
- a value or inequality for `n3`;
- exclusion of `57`, a lower bound `60`, or the number `209346`;
- the Wave 18 `r=18` or `r=19` endpoint statements; or
- a complete theorem formula, proof, graph, or certificate.

The exact searches

```text
"An Induced Subgraph Paradigm for Strongly Regular Graph Constructions"
"Ben Baker" "Induced Subgraph Paradigm"
site:arxiv.org "Ben Baker" strongly regular graph Conway
site:auburn.edu "Ben Baker" Conway "99-graph"
```

located the conference program and an older Auburn seminar announcement,
but no manuscript or slides. Exact overlap with Wave 18 is therefore
**`UNKNOWN`**. The abstract is a near-match deserving author follow-up,
not a resolution or a novelty certificate.

## 9. Comparison with the submitted status report

| Submitted substantive claim | Independent result | Audit |
|---|---|---|
| Current Conway-99 outcome remains `UNKNOWN` | Maintained table and 2025--2026 primary signals agree; no certificate/proof found | **Verified**, with the same nonhit caveat |
| Ishihara Theorem 28 is an apparent exact resolution whose equation (88) premise fails | Primary pp. 15--16 checked; exact correction is `1^20,2^51` and `122=2b-20` | **Verified and strengthened** |
| Reimbayev gives `p6=209286+n3`, with only `n3>=0` published | Primary printed pp. 8, 11--13 checked and arithmetic reproduced | **Verified** |
| Reimbayev 2025 retains `n3` as a free variable | arXiv v2 pp. 1--2 and formula section checked | **Verified** |
| Focused searches found no exact `n3=57`, `n3>=60`, or `209346` result | Independent exact and alternate-notation searches gave no primary match | **Verified as a search result**, novelty still `UNKNOWN` |
| Generic `2e(X)<=3m+m^2/9` is standard | Direct Rayleigh derivation reproduced; Alon--Chung prior art identified | **Verified**, citation strengthening suggested |
| Baker is abstract-only and exact overlap is unknown | Official program p. 4 checked; no paper/slides found | **Verified** |
| Prospective Wave 18 work is not literature evidence | It was used only after the matrix/source-first phase for comparison | **Verified** |

No substantive source claim in the submitted report requires a
correction. The Ishihara exact-count refinement and Alon--Chung citation
are transparent annotations, not silent repairs.

## 10. Final conservative labels

| Claim | Label | Reason |
|---|---|---|
| Submitted report is accurate for its stated literature/status scope | **`VERIFIED`** | Primary-source and query audit above |
| A Conway `srg(99,14,1,2)` exists | **`UNKNOWN`** | No construction/certificate located |
| No Conway `srg(99,14,1,2)` exists | **`UNKNOWN`** | No valid nonexistence proof located |
| Ishihara equation (88)'s uniform-degree premise | **`REFUTED`** | Exact degrees are `1^20,2^51` |
| Ishihara's displayed proof resolves Conway-99 | **`REFUTED`** | Correct count is consistent, not contradictory |
| Reimbayev general hexagon identity | **`CITED`** | Primary printed p. 12 |
| `p6=209286+n3` specialization | **`DERIVED`** | Exact parameter substitution |
| Published exclusion of `n3=57` | **`UNKNOWN`** | Focused nonhit is not a novelty certificate |
| Published `n3>=60` | **`UNKNOWN`** | No exact primary match found |
| `n3>=60 => p6>=209346` | **`DERIVED`** | Conditional arithmetic only |
| Generic subset-edge Rayleigh bound | **`CITED` / `DERIVED`** | Standard Alon--Chung/Rayleigh method |
| Exact Wave 18 active-set/crossing application is prior art | **`UNKNOWN`** | No exact source; Baker has abstract only |
| Novelty of the Wave 18 package | **`UNKNOWN`** | Search nonhits and inaccessible materials cannot certify novelty |

The submitted report may be integrated as a verified literature/status
gate. This status lane alone does not verify the structural proof;
independent proof verification is a separate project gate.
