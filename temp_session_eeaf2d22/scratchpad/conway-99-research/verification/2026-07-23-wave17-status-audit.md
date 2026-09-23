# Wave 17 literature/status audit

## Preinspection source-and-check freeze

```yaml
role: literature
date_utc: 2026-07-23T12:28:16Z
git_commit: NO_GIT
claim_label: UNKNOWN
scope: independent current-status and prior-art audit for Conway-99 and the Wave 17 n3=54 residual, frozen before opening the submitted status report
inputs:
  submitted_report_to_inspect_later: agents/2026-07-23-wave17-status-search.md
method: primary/current-source verification, theorem-hypothesis matching, official-database provenance checks, and exact focused searches
command: web and official-database queries frozen below
outputs:
  verification/2026-07-23-wave17-status-audit.md: PREINSPECTION_PREFIX_THEN_APPENDED_AUDIT
limitations: no submitted report content had been inspected when this matrix was written; nonhits cannot establish novelty
```

This section was written before opening
`agents/2026-07-23-wave17-status-search.md`.  The assignment alone supplied
the topics to check.  The submitted report, its citations, wording, hashes,
and conclusions were not read.

### Frozen source matrix

| Claim family | Required independent evidence | Acceptance test |
|---|---|---|
| Current Conway-99 status through 2026-07-23 | Andries Brouwer's current strongly-regular-graph parameter table and any directly linked primary status note; primary papers for any claimed construction or nonexistence | The exact parameter set `(99,14,1,2)` must be located. “?” or equivalent is treated as open/unknown, not as proof. A secondary page alone is insufficient. |
| BDD intriguing-set definition and size formula | Original paper by the authors denoted BDD, preferably publisher/DOI or author manuscript | Record the exact ambient geometry, intriguing-set definition, eigenvalue/sign convention, cardinality formula, and every hypothesis. |
| Applicability to `PQ(2,6,2)` | Substitute the target partial-quadrangle parameters into the original theorem, not a paraphrase | Verify whether the target graph/geometry meets the theorem's hypotheses and integrality requirements. A parameter coincidence outside scope is non-evidence. |
| `(6,2)` near-match in `PQ(2,10,2)` | Same original theorem/source plus exact substitution | Distinguish a theorem-valid example in a different partial quadrangle from any result about Conway-99. |
| Munaro theorem | Munaro's original paper, DOI/publisher page or author preprint | Record theorem number, graph/geometric class, connectivity/regularity/eigenvalue assumptions, and exact conclusion. Do not extrapolate beyond its scope. |
| Reimbayev cycle identity | Reimbayev's original paper/preprint | Check notation for `p6` and `n3`, exact formula `p6=209286+n3`, graph hypotheses, and whether induced or non-induced six-cycles are counted. |
| House of Graphs counts `455+2` | Official House of Graphs pages/downloads/API or official generator provenance directly linked there | Reproduce what is being counted, connectedness, simplicity, cubicity, order, girth, isomorphism convention, and the split producing `455+2`. A search-result snippet is insufficient. |
| Prior `n3>=57` | Exact phrase/formula searches across web, scholarly indexes, arXiv, Crossref/publisher pages, and project-relevant terminology | A nonhit remains `NOVELTY_UNKNOWN`; inspect plausible hits before classification. |
| Prior exclusion of `n3=54` | Same, including variants `n_3=54`, “54 induced N3”, and Conway/SRG parameter terms | A census candidate or prospective proof is not accepted as an exclusion. |
| Prior `209343` six-cycle bound | Exact-number and formula searches with induced-six-cycle/SRG terminology | A nonhit remains `NOVELTY_UNKNOWN`; number-only incidental hits are rejected. |

### Frozen exact queries

The following searches will be run independently, with close variants only
to resolve terminology:

```text
"srg(99,14,1,2)"
"strongly regular graph" "99,14,1,2"
site:win.tue.nl/~aeb "99 14 1 2"

"intriguing set" "PQ(2,6,2)"
"intriguing set" "PQ(2,10,2)"
"partial quadrangle" "intriguing set" BDD
"partial quadrangle" "(6,2)" "(10,2)"

Munaro "intriguing set" strongly regular graph
Munaro partial quadrangle theorem

Reimbayev 209286
Reimbayev p6 n3 strongly regular graph
"209286+n3"

site:houseofgraphs.org cubic girth 5 18
site:houseofgraphs.org cubic girth 5 12
"455" "cubic graphs" "girth" 18

"n3 >= 57" Conway graph
"n_3 >= 57" "99,14,1,2"
"n3=54" Conway graph
"n_3=54" strongly regular
"54" "induced N3" strongly regular
"209343" "induced 6-cycles"
"209343" "strongly regular graph"
```

### Frozen decision rules

1. Primary papers and official databases outrank secondary summaries.
2. Every theorem must be matched hypothesis by hypothesis before use.
3. An inaccessible primary source is recorded as inaccessible; a secondary
   description cannot silently replace it.
4. House of Graphs search counts must be bound to exact query parameters and
   provenance, not inferred from filenames or snippets.
5. Solver `UNSAT`, timeouts, census nonhits, and the prospective Wave 17
   structural/algebraic program are not literature evidence for excluding
   `n3=54`.
6. Exact-search nonhits support only `NOVELTY_UNKNOWN`.
7. Conway-99 status is reported conservatively as `UNKNOWN` unless a current,
   primary-backed construction or nonexistence proof is found.

---

<!-- The independent postinspection audit is appended below this line. -->

## Independent postinspection audit

```yaml
role: verifier
date_utc: 2026-07-23T12:34:54Z
git_commit: NO_GIT
claim_label: VERIFIED
scope: >
  Independent verification of the in-scope status and literature claims in
  agents/2026-07-23-wave17-status-search.md, without treating the Conway-99
  conjecture itself, novelty, or a prospective census exclusion as verified.
inputs:
  - path: agents/2026-07-23-wave17-status-search.md
    sha256: dfac5da305b2c11298eb768e27c8a2a32bc275942478683670af127d97c28698
  - path: AGENTS.md
    sha256: 4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3
  - path: agents/2026-07-23-wave17-n3-54-structural.md
    sha256: ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18
  - path: agents/2026-07-23-wave17-n3-54-algebra.md
    sha256: 4c46c718e05a5816d48b9529602fad94a1765fb8c6390166fc916b7e1bcf87b1
  - path: verification/2026-07-23-wave17-status-audit.md
    scope: preinspection prefix only, before this appended audit
    bytes: 5376
    sha256: c0cf06e8a1194199d736733bc09faee505f773aa0271afa85cd779059f4b7dc6
method: >
  Freeze the source/check matrix; authenticate and inspect the submitted
  report; independently open primary/current sources; match theorem
  hypotheses; recompute parameter substitutions; rerun exact prior-art
  searches; distinguish official citations from independently reproduced
  computations.
command: >
  Web queries listed below; source bytes were fetched in memory and hashed
  with SHA-256. No catalog was downloaded, regenerated, or searched locally.
outputs:
  - path: verification/2026-07-23-wave17-status-audit.md
    sha256: SELF_HASH_REPORTED_OUTSIDE_THIS_SELF_REFERENTIAL_FILE
limitations: >
  The live House of Graphs /Cubic route exposed only a JavaScript shell to
  the direct text fetcher; exact counts and provenance were available through
  the search index for that official URL. The Munaro repository injects
  changing download metadata, so repeated byte hashes differ. Search nonhits
  do not establish novelty.
```

### Verdict

**PASS WITH ACCESS QUALIFICATIONS.** The submitted report is conservative
and materially correct on every claim assigned to this lane:

1. The existence of `srg(99,14,1,2)` remains **`UNKNOWN`** in the current
   sources checked through 2026-07-23.
2. The Bamberg--De Clerck--Durante definition, size formula, target
   translation, non-applicability, and `(6,2)` near-match are correct.
3. Munaro's Theorem 7 covers exactly a 4-regular line-graph layer; it does
   not cover the 6-regular union in the Wave residual.
4. Reimbayev's identity specializes to `p6=209286+n3`, with the notation
   caveat stated below.
5. The official House of Graphs indexed page states the counts `455` and
   `2` and the three-generator provenance. This is **`CITED` with an access
   caveat**, not an independently regenerated or checksum-validated census.
6. No prior source was found for `n3>=57`, exclusion of `n3=54`, or the
   exact number `209343`; all three novelty questions remain **`UNKNOWN`**.

There is no substantive disagreement. The two qualifications are evidentiary:
the House of Graphs live route could not be rendered by the direct fetcher,
and the Munaro repository PDF has unstable request-time metadata.

## 1. Current Conway-99 status

The exact statement in Conway's original problem asks for a 99-vertex graph
in which every edge lies in a unique triangle and every non-edge is a
diagonal of a unique quadrilateral. The standard parameter translation is
`srg(99,14,1,2)`.

Independent current checks:

| Source | Exact evidence and status | URL / DOI | SHA-256 of bytes fetched 2026-07-23 |
|---|---|---|---|
| Conway, “Five $1,000 Problems,” Problem 2 | Primary problem statement; poses existence, not a resolution | [OEIS-hosted PDF](https://oeis.org/A248380/a248380.pdf) | `88db8359f230a1eaa01ce3d94f82b8e058278729edf1b71a02564288c56a28ea` |
| Cesarz--Woldar, *Algebraic Combinatorics* 8 (2025), 379--398 | Refereed abstract says existence “remains an elusive open problem”; published online 2025-04-24 | [journal page](https://alco.centre-mersenne.org/articles/10.5802/alco.418/), DOI [`10.5802/alco.418`](https://doi.org/10.5802/alco.418) | journal PDF: `d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8` |
| Brouwer maintained SRG table | Exact row `99 14 1 2` is marked `?`; this is a maintained status indicator, not a proof of openness | [orders 51--100](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html), [legend](https://aeb.win.tue.nl/graphs/srg/srgtab.html) | dynamic HTML; no stable content hash asserted |
| Petro--Phillips, *Discrete Mathematics* 349(3) (2026), 114862 | Treats the Conway case as an existence problem and derives conditional clique-graph information; no construction or nonexistence proof | [arXiv manuscript](https://arxiv.org/abs/2502.17845), DOI [`10.1016/j.disc.2025.114862`](https://doi.org/10.1016/j.disc.2025.114862) | arXiv PDF: `9adb7132b4a40ce87d77b2326fc6ddf1370aa12665f86617aa285b9e824797be` |
| Keramatipour, arXiv:2604.23037v2, 2026-04-28 | Frames the instance as unresolved and reports that the tested SAT approach is not capable of handling it in reasonable time | [arXiv](https://arxiv.org/abs/2604.23037), DOI [`10.48550/arXiv.2604.23037`](https://doi.org/10.48550/arXiv.2604.23037) | `8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8` |
| Brouwer--Van Maldeghem current online monograph copy | Records Conway's prize and only conditional automorphism restrictions; no resolution is recorded | [author-hosted PDF](https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf) | `fa73d72e86bbd8dc3fbfcbca45679cb8f2671d777e91c009eeff0a563fd9289d` |

The June 2026 Hebei Normal University
[lecture notice](https://www.hebtu.edu.cn/a/2026/06/24/AD3624B468444197AA2464C61CBDEE63.html)
describes a prospective attempt to apply a similar method to Conway-99 after
a different nonexistence result. It is not a construction, proof, preprint,
or status change.

**Audit label:** the proposition “Conway-99 has been resolved” is
**`UNKNOWN`**, and the submitted report correctly does not inflate the
available status evidence into a theorem that the problem is open.

## 2. Bamberg--De Clerck--Durante

Primary source: J. Bamberg, F. De Clerck, and N. Durante, “Intriguing sets of
partial quadrangles,” *Journal of Combinatorial Designs* 19(3) (2011),
217--245, DOI
[`10.1002/jcd.20269`](https://doi.org/10.1002/jcd.20269);
[author manuscript](https://cage.ugent.be/geometry/Files/287/IntriguingSetsofPQfinal.pdf).
The fetched manuscript has SHA-256
`511b2ed60e47950cf20163aba06dd1154f973f47a099b593bc0f12ec7862e22f`.

### Definition and size formula

For a proper vertex subset `I` of a strongly regular point graph, the paper
defines intersection numbers `(h1,h2)` by:

- every vertex in `I` has `h1` neighbors in `I`;
- every vertex outside `I` has `h2` neighbors in `I`.

It calls `I` positive or negative according as `h1-h2` is the positive or
negative restricted eigenvalue. Lemma 2.1(ii) states

\[
|I|=\frac{h_2v}{k-h_1+h_2}.
\]

For a partial quadrangle `PQ(s,t,mu)`, the source gives valency
`s(t+1)`, positive restricted eigenvalue

\[
e^+=\frac{-\mu-1+s+\sqrt{(\mu-1-s)^2+4st}}2,
\]

and point count

\[
1+\frac{s(t+1)(\mu+st)}{\mu}.
\]

Substituting `(s,t,mu)=(2,6,2)` gives point-graph parameters
`(v,k,lambda,mu)=(99,14,1,2)` and `e+=3`. For `(h1,h2)=(6,3)`,

\[
|I|=\frac{3\cdot99}{14-6+3}=27,\qquad h_1-h_2=3.
\]

Thus the Wave set is exactly a positive intriguing 27-set if the frozen
quotient data hold. This is a transparent **`DERIVED`** translation, not an
existence claim.

### Hypothesis and family audit

The paper does not classify intriguing sets in every partial quadrangle.
Its relevant constructions have hypotheses that miss the target:

- Section 5 starts with a generalized quadrangle of order `(s,s^2)` and
  removes a point-perp, producing `PQ(s-1,s^2,s(s-1))`. Setting the first
  parameter to `2` forces `s=3`, hence `PQ(2,9,6)`.
- Theorem 5.2 retains that generalized-quadrangle-minus-perp hypothesis.
  Nothing in it transfers to an arbitrary hypothetical `PQ(2,6,2)`.
- Section 6 starts from a hemisystem in a generalized quadrangle of order
  `(s,s^2)`, with `s` odd, and produces
  `PQ((s-1)/2,s^2,(s-1)^2/2)`. First parameter `2` forces `s=5`, hence
  `PQ(2,25,8)`.
- Section 7 lists the three known exceptional linear-representation cases
  as `PQ(2,10,2)`, `PQ(2,55,20)`, and `PQ(3,77,14)`.
- The thin-partial-quadrangle section concerns triangle-free point graphs,
  whereas the target has `lambda=1`.

Accordingly, the claim that this paper classifies or excludes the target
`(6,3)` set is **`REFUTED`**. The submitted non-applicability conclusion is
**`VERIFIED`**.

### Exact near-match

For the Coxeter-cap `PQ(2,10,2)`, Table 8 gives positive eigenvalue `4` and
positive-set size `(27/2)h2`; Section 7.1 explicitly reports positive sets
of size `27`. Therefore `h2=2` and `h1-h2=4`, so `(h1,h2)=(6,2)`.

This verifies the submitted near-match. It is not an exact match: its
ambient partial quadrangle, positive eigenvalue, outside intersection
number, and quotient matrix differ from those of `PQ(2,6,2)`.

## 3. Munaro theorem scope

Primary source: Andrea Munaro, “On Line Graphs of Subcubic Triangle-Free
Graphs,” *Discrete Mathematics* 340(6) (2017), 1210--1226, DOI
[`10.1016/j.disc.2017.01.006`](https://doi.org/10.1016/j.disc.2017.01.006);
[author manuscript](https://pureadmin.qub.ac.uk/ws/portalfiles/portal/186487120/dmline.pdf).

Theorem 7 says that, **for any 4-regular graph `G`**, the following are
equivalent:

1. `G` is `(K4, claw, diamond)`-free;
2. `G` is the line graph of a cubic triangle-free graph;
3. `G` is locally linear;
4. every edge of `G` lies in exactly one triangle.

No connectivity assumption is stated in Theorem 7. Its controlling
hypothesis is 4-regularity. Consequently it applies to the reported
4-regular `L(F)` layer, not to the 6-regular
`G[X]=L(F) union R` or to the compatibility matrix equation. The submitted
scope restriction is **`VERIFIED`**.

The institutional repository makes the primary manuscript accessible, but
it injects changing request-time metadata. Three consecutive 935,647-byte
fetches produced distinct SHA-256 values:

```text
bb7fd12674e713a00ed59316e220d958e8b0435429cc0efbfea4dd2c591f5cc8
65a9fc68ec4f7a365c5128648f99cc486001c63d960081c7938112d87664b7ed
7e29843cfc00e6bffc997b1635ddac0c6b2ee28dc9023567c46d46af32cb7ed8
```

The theorem text and DOI were stable; no single stable repository-byte hash
is asserted.

## 4. Reimbayev identity

Primary source: Reimbay Reimbayev, “The lower bound for number of hexagons
in strongly regular graphs with parameters `lambda=1` and `mu=2`,”
*e-Journal of Analysis and Applied Mathematics* 2024 (2024), 1--14, DOI
[`10.62780/ejaam/2024-001`](https://doi.org/10.62780/ejaam/2024-001);
[journal PDF](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf).
The fetched PDF has SHA-256
`484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521`.

The paper's hypotheses are a simple regular graph satisfying:

- every edge lies in a unique triangle, hence `lambda=1`;
- every non-edge lies in a unique quadrilateral, hence `mu=2`.

It defines `p6` as the number of **induced** subgraphs isomorphic to `C6`.
Later it numbers the surviving six-vertex induced types and defines `n_i`
as the number of induced copies of type `i`. Type 12 is the hexagon, so
`n12=p6`. The source derives

\[
n_{12}=\frac1{12}nk(k-2)(2k^2-21k+53)+n_3.
\]

Here `n3` is the count of the paper's induced six-vertex **type 3**. It is
not the earlier symbol `p3` for the number of triangles. With
`(n,k)=(99,14)`,

\[
\frac1{12}(99)(14)(12)(2\cdot14^2-21\cdot14+53)
=99\cdot14\cdot151
=209286,
\]

so

\[
p_6=n_{12}=209286+n_3.
\]

The identity and specialization are **`VERIFIED`**. The paper's later
suggestion that the lower-bound case `n3=0` should be the true value is
explicitly conjectural and supplies no proof of `n3>=57`, `n3>54`, or an
exclusion at `n3=54`.

## 5. Official House of Graphs counts and provenance

The relevant official route is
[House of Graphs: Connected cubic graphs](https://houseofgraphs.org/Cubic),
accessed 2026-07-23. Its indexed official-page text has the heading
“Connected cubic graphs,” describes downloadable `graph6` lists, and gives:

| vertices | connected cubic graphs of girth at least 5 |
|---:|---:|
| 12 | 2 |
| 18 | 455 |

The same official indexed text states:

> All numbers for minimum girths 3, 4 and 5 were independently confirmed
> by genreg, minibaum and snarkhunter up to 30 vertices.

The parent [meta-directory](https://houseofgraphs.org/meta-directory) says
its complete lists contain all pairwise non-isomorphic graphs within the
specified graph class up to the stated order. Thus `455` and `2` refer to
isomorphism classes of connected simple cubic graphs at the displayed order
and girth threshold.

Access qualification: opening `/Cubic` directly returned only “You need to
enable JavaScript to run this app.” The 2,476-byte application shell fetched
in this environment had SHA-256
`3368d9b9bd2de73a37b5eabf0da9749ed99358034a7fc36b3606b954d257ebf7`;
that hash does **not** authenticate the indexed table data. The exact table
and provenance were obtained from the search index for the official URL,
not from a secondary page. Under the frozen rule that an indexed snippet
alone is insufficient for full independent verification, these counts are
accepted as **`CITED` with an official-access caveat**, not promoted to
**`VERIFIED`** by this lane.

No `graph6` file was downloaded, hashed, regenerated, or compared. No
compatible 2-factor `R` was enumerated. Therefore:

- the official page supports the finite universe of possible `F`;
- it does not verify any local catalog artifact;
- it does not enumerate the pairs `(F,R)`;
- and it cannot exclude `n3=54` or Conway-99.

Any future exclusion based on this census must supply the exact downloaded
inputs and hashes, every restriction, a complete candidate/certificate
format, and an independent verifier run. A prospective or conditional
search is not accepted as an exclusion here.

## 6. Exact prior-art reruns

The following exact or punctuation-normalized searches were rerun on
2026-07-23:

```text
"n3 >= 57" strongly regular graph
"n_3 \ge 57" strongly regular graph 99 14 1 2
"n3≥57" graph hexagons
"n_3>=57" srg(99,14,1,2)

"n3 = 54" "strongly regular" graph
"n_3=54" srg 99 14 1 2
"n3=54" hexagons graph
"exclude" "n3" "54" "srg(99,14,1,2)"

"209343" strongly regular graph
"209,343" hexagons graph
"p6 = 209343" graph
"p_6" "209343" srg

site:arxiv.org "209343" graph
site:doi.org "209343" "strongly regular"
site:arxiv.org "n3" "srg(99,14,1,2)"
site:arxiv.org "n_3" "99,14,1,2"
```

No relevant primary hit was found for:

- a theorem `n3>=57`;
- exclusion of `n3=54`;
- or the derived threshold `p6>=209343`.

Hits in unrelated numerical contexts were rejected. Broader current-status
searches for `"srg(99,14,1,2)"`, `"Conway's 99-graph"`, construction, proof,
and nonexistence found the unresolved/current sources recorded in Section 1,
not a resolution.

These results are **search nonhits only**. They do not cover unindexed
literature, alternate notation, non-English sources, or equivalent
formulations. The novelty of all three statements remains **`UNKNOWN`**.

## 7. Final claim matrix

| Proposition | Audit label | Result |
|---|---|---|
| Conway-99 is currently resolved | **`UNKNOWN`** | Current primary/maintained sources still treat it as open; no resolution located |
| BDD definition and size formula were quoted correctly | **`VERIFIED`** | Definition, sign convention, and Lemma 2.1(ii) checked in the manuscript |
| `PQ(2,6,2)` and `(6,3)` imply a positive intriguing 27-set | **`VERIFIED`** as a derivation | Exact parameter and arithmetic substitution checked; existence is not asserted |
| BDD classify or exclude that target set | **`REFUTED`** | Every audited family/theorem has different parameters or hypotheses |
| BDD contain a size-27 `(6,2)` near-match in `PQ(2,10,2)` | **`VERIFIED`** | Table 8 and Section 7.1 checked |
| Munaro Theorem 7 covers `L(F)` | **`VERIFIED`** | The theorem is exactly for 4-regular graphs |
| Munaro Theorem 7 covers the full 6-regular `G[X]` | **`REFUTED`** | 4-regularity fails; the extra 2-factor and compatibility equation are outside scope |
| Reimbayev proves `p6=209286+n3` for the target parameters | **`VERIFIED`** | `p6=n12`; `n3` is the induced six-vertex type-3 count |
| House of Graphs states counts `455+2` and three-generator confirmation | **`CITED`** | Exact official indexed text found; live page was JS-only |
| This lane independently validates the catalog files or searches all `(F,R)` | **`REFUTED`** | No catalog download, hash, regeneration, or compatibility search occurred |
| Prior literature proves `n3>=57` | **`UNKNOWN`** | Focused searches nonhit |
| Prior literature excludes `n3=54` | **`UNKNOWN`** | Focused searches nonhit |
| `209343` is a previously published exact threshold | **`UNKNOWN`** | Focused searches nonhit |
| Novelty of the Wave 17 residual | **`UNKNOWN`** | Nonhits are not a novelty certificate |

The submitted report may be used as a conservative literature/status report
with the House of Graphs and Munaro hash qualifications above. It must not
be cited as verification of a construction, nonexistence proof, complete
census, or novelty claim.
