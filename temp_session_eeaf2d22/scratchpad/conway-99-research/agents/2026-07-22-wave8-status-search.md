# Wave 8 status, provenance, and prior-art audit

```yaml
role: literature
date_utc: 2026-07-23T01:42:30Z
git_commit: b2a31846d243a76b9e516f85304e21137e3fe874
claim_label: UNKNOWN
scope: conditional bounds n3>=33 and induced_C6_count>=209319, including provenance of the fixed-triangle and fixed-original-point arguments
inputs:
  wave8_draft:
    path: agents/2026-07-22-wave8-n3-equality.md
    sha256_at_audit: b612eb0a47514b20c11539cd5cc54cecaa2a5489e1eb47bd0be79db308e8ca70
    note: the final report adds this audit's attribution correction without changing the mathematical proof
  agents/2026-07-22-wave7-triangle-side-incidence.md: 2225d7f26f8719d24bceca0c4ef6d8b829332a80793762769d282f176e75b651
  lou_murin_2014_pdf:
    url: https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf
    sha256: 5df5b96709419c6168430c58601ee98ec26e6c08036034bd755247311c2fb211
  reimbayev_2024_pdf:
    url: https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf
    sha256: 484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521
  reimbayev_2025_six_vertex_v2_pdf:
    url: https://arxiv.org/pdf/2508.03377v2
    sha256: c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9
  reimbayev_2025_hamiltonian_v1_pdf:
    url: https://arxiv.org/pdf/2511.06572v1
    sha256: d98d474ef277b6a32fc4125690c75d3808450225b0657dbd46290673b7a014f7
  cesarz_woldar_2025_pdf:
    url: https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf
    sha256: d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8
  petro_phillips_v1_pdf:
    url: https://arxiv.org/pdf/2502.17845v1
    sha256: 9adb7132b4a40ce87d77b2326fc6ddf1370aa12665f86617aa285b9e824797be
  keramatipour_v2_pdf:
    url: https://arxiv.org/pdf/2604.23037v2
    sha256: 8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8
method: targeted current web and citation-trail search, full-text extraction of version-pinned primary PDFs, visual inspection of relevant pages and figures, and exact alternate-notation comparison
command: interactive web search plus version-pinned PDF download, SHA-256 hashing, and page-by-page text inspection
outputs:
  exact_n3_ge_33_hit_in_checked_primary_sources: NONE_FOUND
  exact_209319_hit_in_checked_primary_sources: NONE_FOUND
  fixed_triangle_profile_prior_art: FOUND_LOU_MURIN_2014
  q_equals_1_exclusion_prior_art: FOUND_LOU_MURIN_2014
  fixed_original_point_identity_prior_art: NONE_FOUND
  point_clique_cubic_complement_prior_art: NONE_FOUND
  target_status_in_checked_current_primary_sources: OPEN
  novelty_established: false
verdict: NO_CHECKED_HIT_FOR_EXACT_BOUND_METHOD_PRIOR_ART_OVERLAP_FOUND_NOVELTY_NOT_ESTABLISHED
limitations: a targeted search cannot establish novelty or exhaust all publications, theses, repositories, or non-indexed sources
```

## Prior-art correction: Lou--Murin 2014

Lou and Murin's MIT PRIMES-USA report,
[*On the Strongly Regular Graph of Parameters (99, 14, 1, 2)*](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf),
Section 5, pages 7--8, constructs the 231-vertex graph of graph-triangles and
studies the partners of a fixed triangle. In their notation,

```text
alpha + beta = 180,
beta + 3 gamma = 36,
alpha - 3 gamma = 144,
distance-three count = 32 - gamma = 20 + beta/3,
gamma != 11.
```

Under the Wave 7 notation for disjoint partners having `r` cross-edges,

```text
a1 = alpha,
a2 = beta,
a3 = gamma,
a0 = 32-gamma.
```

Putting `q=12-gamma` yields exactly

```text
(a0,a1,a2,a3) = (20+q,180-3q,3q,12-q),
```

and `gamma!=11` is precisely `q!=1`. The fixed-triangle partner profile and
the `q`-gap must therefore be attributed to Lou--Murin or described as an
independent rederivation. They are not project novelty.

The report does not contain the Wave 6/7 global `N3` support graph, the fixed-
original-point identity

```text
sum_{v: uv in E(G)} d_H(uv) = 4 |S_u|,
```

the point-clique cubic-complement contradiction, or the exact bounds `n3>=33`
and `p6>=209319`.

## Other primary-source findings

Reimbayev's 2024 paper derives

```text
p6 = (1/12) n k (k-2) (2k^2-21k+53) + n3.
```

For `(n,k)=(99,14)` this is `p6=209286+n3`; its published lower bound uses
only `n3>=0`. The 2025 six-vertex v2 paper continues to treat `n3` as a free
parameter. The November 2025 Hamiltonian-subgraph paper also retains `n3` as
free, states the original lower bound for `p6`, and conjectures that lower
bound is exact. None contains the exact Wave 8 values, active triangles,
point cliques, a support graph, Mantel's theorem, or a cubic-complement
argument.

Cesarz--Woldar explicitly state that Conway-99 existence remains open.
Petro--Phillips, published in March 2026, call the parameter set an unknown
existence problem. Keramatipour v2 records unsuccessful SAT experiments and
future work, not a construction or nonexistence proof. The target therefore
remains open in the checked current primary literature.

## Exact query families

The audit used exact values, alternate notation, method phrases, and citation
trails, including:

```text
"n3 >= 33" "strongly regular"
"n_3" "33" "strongly regular" hexagon
"209319" graph hexagons
"209,319" "Conway" graph
"Conway 99" "active triangles"
"srg(99,14,1,2)" "fixed point" triangle
"Conway 99-graph" triangles hexagons
"N3" "The Subgraphs of Order Six" strongly regular
"two disjoint triangles" "srg(99,14,1,2)"
"triangle partners" "Conway 99"
"triangular prism" "srg(99, 14, 1, 2)"
"N_3" "srg(n,k,1,2)"
"n_3" "srg(99,14,1,2)"
"209286" "n3" graph
"two triangles" "two edges" "srg(99,14,1,2)"
"gamma cannot be 11" "99, 14, 1, 2"
"alpha + beta = 180" graph triangle
"beta + 3 gamma = 36" graph
"32 - gamma" "srg(99"
"On the strongly regular graph of parameters (99, 14, 1, 2)" Lou Murin pdf
site:math.mit.edu "S. Lou" "M. Murin" 99 graph
site:arxiv.org "srg(99,14,1,2)" 2026
site:arxiv.org "Conway 99-graph" 2026
"Conway 99" "remains open" 2026
"On Clique Graphs and Clique Regular Graphs" Conway-99 open
site:arxiv.org/abs/2604.23037 Conway 99 SAT status
site:arxiv.org/abs/2508.03377 "Subgraphs of Order Six"
site:arxiv.org "Hamiltonian Subgraphs of Order Seven" srg
"10.62780/ejaam/2024-001"
"Reimbayev" "n3" strongly regular graph
```

## Conservative verdict

No checked external primary source states `n3>=33`, `p6>=209319`, the fixed-
original-point identity, or the final point-clique contradiction. That is not
a novelty finding. The substantial Lou--Murin overlap corrects the project's
earlier source boundary, and all public summaries now credit it. The exact
Wave 8 bound remains a conditional project derivation pending external review;
Conway-99 itself remains `UNKNOWN`.
