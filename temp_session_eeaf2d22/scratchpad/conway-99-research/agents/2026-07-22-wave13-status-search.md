# Wave 13 exact-claim and prior-art status audit

```yaml
role: literature
date_utc: 2026-07-23T07:30:24Z
git_commit: c471801a7adf6852a208b5d5553bcc76a3372d6a
claim_label: UNKNOWN
scope: external status of n3!=45, n3>=48, induced_C6_count>=209334, and the fifteen-active-triangle equality framework for srg(99,14,1,2)
inputs:
  SOURCES.bib: 91feb4454a42782422512e669aaa60aa4c6615111a08f3d908e286397a717828
  agents/2026-07-22-wave12-status-search.md: b3118d19d2c5b74af6cb8a48667f1b674e6a1b3df12a1a94ca46f64e1fcef7e6
  arxiv_source_2409.10620v1: 9e31eb63e878531124cb20df306698827b93057b4ef9feed207654aea8f31112
  arxiv_source_2409.15001v1: bfe308506459b5e78a2f1205275cd7cbf888b99e0460645adbd2e3e234af2c20
  arxiv_source_2502.17845v1: 70184d605bd3cb7732efae8311de44697ee55793be988bd8a880271da283e2c9
  arxiv_source_2508.03377v2: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
  arxiv_source_2511.06569v1: 5d1a5d22ad0bbde4fc4739fe4187faf13261255946cec57833aca2ccd6b53df3
  arxiv_source_2511.06572v1: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
  arxiv_source_2604.23037v2: ddd6c002f142c9a3a0b648c28aa0e4d478f314b6af646b86810ec29129bf1caa
  arxiv_source_2605.22867v1: 5345e9c360caf0a501de83c8d4a4b552cb06034de3047a4c2e48874d33748b18
method: targeted current web search, direct arXiv metadata queries, primary-source citation-trail inspection, and exact full-text search of version-pinned TeX sources through 2026-07-22 America/Los_Angeles
command: interactive exact-phrase searches plus rg -n -i over the unpacked, hash-pinned arXiv source archives
outputs:
  exact_n3_ne_45: NO_CHECKED_HIT
  exact_n3_ge_48: NO_CHECKED_HIT
  exact_induced_C6_ge_209334: NO_CHECKED_HIT
  fifteen_active_triangle_framework: NO_CHECKED_HIT
  novelty_status: UNKNOWN
  target_status: UNKNOWN
limitations: targeted negative search cannot establish novelty, exhaust non-indexed or unpublished material, or certify the mathematical status of the Conway-99 problem
```

## Conservative conclusion

No checked primary source states or proves any of

```text
n3 != 45,
n3 >= 48,
induced_C6_count >= 209334,
```

or the fifteen-active-triangle equality reduction used by the project. Every
one of these literature-search outcomes is `NO_CHECKED_HIT`, not evidence of
novelty.

The arithmetic implication should be kept separate from the missing equality
exclusion. Reimbayev's prior-art identities give

```text
3 | n3,
induced_C6_count = 209286 + n3.
```

Thus, conditional on an independently verified project result `n3>=45`,
excluding `n3=45` would force the next permitted value `n3>=48`, and then
`induced_C6_count>=209334`. The search found no external source for that new
exclusion. External novelty and the existence or nonexistence of the target
both remain `UNKNOWN`.

## Frozen vocabulary and alternate notation

Here `n3` means Reimbayev's count of induced six-vertex subgraphs of type
`N_3`: two vertex-disjoint triangles joined by exactly two independent
cross-edges. Searches also used `n_3`, `N3`, `N_3`, “graph 3,” “two disjoint
triangles connected/joined by two edges,” and the equivalent Makhnev-style
condition concerning two triangles with at least two joining edges.

The terms “active triangle,” `q(T)`, “point set,” and “point clique” appear to
be project vocabulary. To avoid missing equivalent prior art, the search also
used:

```text
triangle partner, gamma vertex, triangle decomposition, triangle graph,
clique graph, locally linear graph, regular clique assembly,
linear point hypergraph, common-point obstruction, Berge triangle,
fifteen triangles, 15 triangles, equality case
```

No checked source matched the exact fifteen-active-triangle framework after
inspection of the surrounding theorem or definition.

## Exact attribution boundary

| Ingredient | Checked primary source and date | Attribution |
|---|---|---|
| The target cannot satisfy the condition that two triangles joined by at least two edges are always joined by three | [Makhnev 1988](https://doi.org/10.1007/BF01158426), *Strongly Regular Graphs with lambda=1* | `CITED`; with `lambda=1`, the contrapositive supplies at least one induced `N_3`, not a quantitative bound |
| Fixed-triangle partner equations and exclusion of the case corresponding to project `q=1` | [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf), Section 5, especially pp. 7--8 | `CITED`; their notation is `alpha,beta,gamma`, not global `n3` |
| `3 | n3` and `induced_C6_count=209286+n3` for the target | [Reimbayev, submitted 2024-09-16](https://arxiv.org/abs/2409.10620), published as [DOI 10.62780/ejaam/2024-001](https://doi.org/10.62780/ejaam/2024-001) | `CITED`; the paper uses only `n3>=0` for its published lower bound |
| General fact that three mutually adjacent triangle-vertices in the clique graph share one original vertex | [Reimbayev, submitted 2024-09-23](https://arxiv.org/abs/2409.15001), source line 95 | `CITED` general framework |
| General common-point obstruction for regular clique assemblies | [Guest--Hammer--Johnson--Roblee 2017](https://doi.org/10.5556/j.tkjm.48.2017.2237), Lemma 1 | `CITED` general framework |
| Clique-graph treatment with Conway-99 as an application | [Petro--Phillips, submitted 2025-02-25](https://arxiv.org/abs/2502.17845), journal [DOI 10.1016/j.disc.2025.114862](https://doi.org/10.1016/j.disc.2025.114862) | `CITED` general framework; no checked `n3` bound |
| Fifteen active triangles, their equality profiles, and exclusion of `n3=45` | No checked primary-source hit | project-specific work under study; novelty `UNKNOWN` |
| Consequent `n3>=48` and `induced_C6_count>=209334` | No checked primary-source hit | `UNKNOWN` until the equality exclusion is independently verified |

The 1997 Makhnev--Paduchikh paper
[*On 2-locally Seidel graphs*](https://www.mathnet.ru/php/getFT.phtml?jrnid=im&paperid=136&what=fullteng)
was also followed as a citation trail. It describes Makhnev's 1988 hypothesis
as excluding two disjoint triangles joined by exactly two edges. This confirms
the alternate description of `N_3`; it does not add a lower bound on `n3`.

## Full-text checks closest to the exact claims

### Reimbayev's six- and seven-vertex work

The complete TeX of
[*The Subgraphs of Order Six ...* v2](https://arxiv.org/abs/2508.03377v2)
(submitted 2025-08-05, revised 2025-11-03) explicitly calls `n3` a free
variable at source lines 85 and 118--123 and again leaves it undetermined in
the conclusion. It reproduces

```text
n12 = (1/12)n k(k-2)(2k^2-21k+53) + n3,
```

but supplies no `n3!=45`, `n3>=48`, or active-triangle argument.

Two potentially misleading string hits were checked rather than counted as
evidence: the paper has symbols `n_{45}` and `n_{48}` at source lines
228--229 and 243--254. They count the 45th and 48th graph types in the paper's
six-vertex catalogue. They are not the assertions `n_3=45` or `n_3>=48`.

The complete TeX of
[*Hamiltonian Subgraphs of Order Seven ...* v1](https://arxiv.org/abs/2511.06572v1)
(submitted 2025-11-09) retains both `n3` and `h11` as free parameters. Its
relevant inequality is only

```text
2 n3 <= h11 <= 4 n3.
```

It contains none of the Wave 13 exact claims or equality framework.

### Other current target-specific sources

- [Reimbayev's `srg(19,6,1,2)` paper](https://arxiv.org/abs/2511.06569v1),
  submitted 2025-11-09, says in its conclusion that existence of
  `srg(99,14,1,2)` is still undefined and the search is ongoing. It does not
  give a target `n3` bound.

- [Cesarz--Woldar](https://doi.org/10.5802/alco.418), published online
  2025-04-24, calls target existence an elusive open problem and restricts
  possible automorphisms. It does not use this equality framework.

- [Keramatipour v2](https://arxiv.org/abs/2604.23037v2), submitted
  2026-04-24 and revised 2026-04-28, reports that dedicated direct SAT
  processes could not run long enough, then lists future work. Full source
  search found no `n3`, `209334`, or fifteen-active-triangle argument.

- [Phillips's thesis v1](https://arxiv.org/abs/2605.22867v1), submitted
  2026-05-19, says the Conway bounty had yet to be claimed. Its full
  clique-graph treatment contains no checked occurrence of the exact claims.

These are dated status statements, not proof that no resolution appeared
elsewhere after their publication.

## Index, query, and citation-trail coverage

The direct arXiv API query

```text
https://export.arxiv.org/api/query?search_query=all:%22Conway-99%22&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending
```

returned five records through the cutoff, with Keramatipour v2 the newest.
Exact-parameter queries for `srg(99,14,1,2)` and `99,14,1,2` were also run.
An author query for `au:"Reimbay_Reimbayev"` returned five records, newest
`2511.06572`, `2511.06569`, and `2508.03377`. Metadata-query counts are only
coverage notes; they are not nonexistence certificates.

Exact-number searches included:

```text
"n3=45" "strongly regular"
"n_3=45" "strongly regular"
"n3!=45" graph
"n3≠45" graph
"n3 > 45" "Conway 99"
"n3 >= 48" "Conway" graph
"n_3 >= 48" "srg(99,14,1,2)"
"n_3" "\geq 48" "strongly regular"
"n3" "at least 48" "Conway" graph
"209286+n3" graph
"209286 + 48" graph hexagons
"209334" "strongly regular"
"209,334" "strongly regular"
"209334" hexagons graph
"209334" "Conway 99-graph"
```

Framework and alternate-description searches included:

```text
"fifteen active triangles" graph
"15 active triangles" "strongly regular"
"active triangle" "Conway 99"
"triangle partners" "Conway" "99" graph
"point clique" "Conway 99"
"point hypergraph" "srg(99,14,1,2)"
"common point" triangles "Conway 99"
"Berge triangle" "Conway 99"
"two disjoint triangles" "99,14,1,2"
"two disjoint triangles" "lambda=1" "mu=2"
"N_3" "srg(n,k,1,2)"
site:arxiv.org/abs "Conway 99-graph"
site:github.com "Conway 99" "n3"
```

The exact values and terminology were then searched in the hash-pinned TeX
sources listed in the run header. Search-engine hits were discarded unless
their surrounding text concerned the exact subgraph count. In particular,
ordinary occurrences of 45 or 48, graph-catalogue indices `n_{45}` and
`n_{48}`, and unrelated uses of `n3` were not treated as claim matches.

## Status boundary

The checked primary sources consistently describe the target as unresolved at
their respective dates, and the targeted search found no later checked
resolution through 2026-07-22 America/Los_Angeles. That does not certify an
exhaustive global status result. The publication-safe status is therefore:

```text
external hit for n3!=45:                 NO_CHECKED_HIT
external hit for n3>=48:                 NO_CHECKED_HIT
external hit for induced C6 >= 209334:   NO_CHECKED_HIT
external hit for fifteen-active framework: NO_CHECKED_HIT
novelty:                                 UNKNOWN
srg(99,14,1,2):                          UNKNOWN
```

No novelty claim is made for the Wave 13 equality work or for any bound that
would depend on it.
