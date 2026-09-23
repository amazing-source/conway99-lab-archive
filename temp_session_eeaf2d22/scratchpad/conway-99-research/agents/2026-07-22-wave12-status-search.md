# Wave 12 exact-claim and prior-art status audit

```yaml
role: literature
date_utc: 2026-07-23T06:08:46Z
git_commit: 4d561fb8b5e0b335d430c2ac93962cbf0ae40184
claim_label: UNKNOWN
scope: exclusion n3=42; consequent bounds n3>=45 and induced_C6_count>=209331; fourteen-active-triangle equality framework
inputs:
  SOURCES.bib: 91feb4454a42782422512e669aaa60aa4c6615111a08f3d908e286397a717828
  agents/2026-07-22-wave11-status-search.md: ce6ffaa2e95fec787f7404876244da50ab7d92054f8c6ff0debf7ea17c9c41c1
  arxiv_source_2508.03377v2: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
  arxiv_source_2511.06572v1: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
  arxiv_source_2604.23037v2: ddd6c002f142c9a3a0b648c28aa0e4d478f314b6af646b86810ec29129bf1caa
method: targeted current web search, primary-source citation-trail search, and full-text inspection of version-pinned arXiv TeX sources through 2026-07-22 America/Los_Angeles
command: interactive web search plus exact full-text search of downloaded arXiv source archives
outputs:
  exact_n3_42_exclusion: NO_CHECKED_HIT
  exact_n3_ge_45_bound: NO_CHECKED_HIT
  exact_induced_C6_ge_209331_bound: NO_CHECKED_HIT
  novelty_status: UNKNOWN
  target_status: OPEN_IN_CHECKED_PRIMARY_SOURCES
limitations: a targeted negative search cannot establish novelty, exhaust non-indexed material, or prove current mathematical status
```

## Conservative conclusion

No checked primary source states or proves

```text
n3 != 42,
n3 >= 45,
induced_C6_count >= 209331,
```

or the fourteen-active-triangle equality reduction. This is
`NO_CHECKED_HIT`, not evidence of novelty.

The safe description is:

> The `n3=42` frontier is a conditional project derivation under internal
> study. External novelty is unknown, and Conway-99 remains unresolved in
> the checked primary sources.

## Exact attribution boundary

The following upstream ingredients remain prior art:

| Ingredient | Checked primary source | Status |
|---|---|---|
| Fixed-triangle partner equations and exclusion of `q=1` | [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf), Section 5, pages 7--8 | `CITED` |
| Target-specific implication `n3>0` | [Makhnev 1988](https://www.mathnet.ru/eng/mzm4220), used by contrapositive | `CITED` |
| `3 | n3` and `induced_C6_count=209286+n3` | [Reimbayev 2024](https://doi.org/10.62780/ejaam/2024-001) | `CITED` |
| General common-point obstruction for regular clique assemblies | [Guest--Hammer--Johnson--Roblee 2017](https://doi.org/10.5556/j.tkjm.48.2017.2237), Lemma 1 | `CITED` |
| Clique-graph framework and Conway-99 application context | [Petro--Phillips 2025/2026](https://arxiv.org/abs/2502.17845) | `CITED` framework |
| Exact `n3=42` active profiles and equality reduction | No checked hit | project `DERIVED`; novelty `UNKNOWN` |
| Exclusion `n3=42` or bound `n3>=45` | No checked hit and not established in this project | `UNKNOWN` |

## Full-text primary-source findings

Reimbayev's published 2024 paper derives

```text
induced_C6_count = 209286+n3
```

for the target and obtains its published lower bound only from `n3>=0`.

The version-pinned source of
[*The Subgraphs of Order Six of the Family of Strongly Regular Graphs with
Parameters lambda=1 and mu=2*](https://arxiv.org/abs/2508.03377v2) was
searched in full. It explicitly declares `n3` a free variable, expresses the
other six-vertex induced-subgraph counts in terms of it, and concludes without
determining it. It contains neither 42 as a lower bound for this variable nor
an equality exclusion at 42.

The version-pinned source of
[*Hamiltonian Subgraphs of Order Seven in srg(n,k,1,2)*](https://arxiv.org/abs/2511.06572v1)
was also searched in full. It retains `n3` and a second count `h11` as free
variables, including only the displayed relation

```text
2 n3 <= h11 <= 4 n3.
```

It does not give an `n3=42` exclusion or the project active-triangle
framework.

[Cesarz--Woldar 2025](https://doi.org/10.5802/alco.418) explicitly calls
existence of the target an elusive open problem and studies its possible
automorphism group. The full source of
[Keramatipour v2](https://arxiv.org/html/2604.23037v2) reports unsuccessful
direct SAT experiments, describes the target as open, and lists future work;
it contains no `n3` equality argument. The later clique-graph paper and thesis
checked in the Wave 10--11 audits likewise do not resolve the target.

## Query coverage

Exact-number and alternate-terminology searches included:

```text
"n3=42" "strongly regular"
"n_3=42" "strongly regular"
"n3 >= 45" "Conway"
"n_3 ge 45" "srg(99,14,1,2)"
"209328" hexagons strongly regular
"209,328" Conway graph
"209331" strongly regular graph
"209,331" hexagons graph
"Conway 99" fourteen active triangles
"Conway 99" point hypergraph
"Conway 99" triangle partners
"two disjoint triangles" "99,14,1,2"
"N_3" "srg(n,k,1,2)"
"gamma" triangle partners "99,14,1,2"
site:arxiv.org/abs "Conway 99-graph"
site:arxiv.org/abs "srg(99,14,1,2)"
```

The exact values were also searched directly in the full TeX sources of the
2025 six-vertex paper, the 2025 seven-vertex paper, and Keramatipour v2.
Search-engine false positives for `42`, `n3`, and the six-digit cycle counts
were discarded unless they referred to the exact graph-theoretic quantity.

## Status boundary

The checked primary sources support only their dated statements that the
target is open. The targeted search found no later checked resolution through
2026-07-22, but literature search cannot prove absence. No novelty claim is
made for the Wave 11 bound, the Wave 12 profile work, or any future equality
exclusion.

The project status must remain:

```text
n3=42 exclusion:            UNKNOWN
conditional n3 lower bound: 42
srg(99,14,1,2):             UNKNOWN
```
