# Wave 7 precise-status and novelty search

```yaml
role: literature
date_utc: 2026-07-23T00:53:29Z
git_commit: 0728b260e1282afdbaeaa9215659a4175cab25de
claim_label: UNKNOWN
scope: precise conditional bounds n3>=30 and induced_C6_count>=209316 for a putative srg(99,14,1,2)
inputs:
  agents/2026-07-22-wave7-triangle-side-incidence.md: 2225d7f26f8719d24bceca0c4ef6d8b829332a80793762769d282f176e75b651
  reimbayev_2024_pdf:
    url: https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf
    sha256: 484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521
  reimbayev_2025_v2_pdf:
    url: https://arxiv.org/pdf/2508.03377v2
    sha256: c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9
  cesarz_woldar_2025_pdf:
    url: https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf
    sha256: d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8
  lou_murin_2014_pdf:
    url: https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf
    sha256: 5df5b96709419c6168430c58601ee98ec26e6c08036034bd755247311c2fb211
method: targeted web and full-text search of primary sources under exact values, formulas, graph parameters, and alternate terminology
command: interactive web search and full-text PDF inspection using the exact queries recorded below
outputs:
  exact_bound_prior_art_hit: NONE_FOUND
  method_prior_art_overlap: LOU_MURIN_2014_FIXED_TRIANGLE_PROFILE_AND_Q_GAP
  novelty_established: false
search_date: 2026-07-22
correction_date_utc: 2026-07-23T01:42:30Z
verdict: NO_EXACT_BOUND_HIT_METHOD_OVERLAP_FOUND_NOVELTY_NOT_ESTABLISHED
limitations: absence from a targeted search is not proof of novelty or exhaustive bibliographic coverage
```

## Wave 8 prior-art correction

The initial Wave 7 search correctly found no checked source stating the exact
bound `n3>=30`, but its broader no-hit field was too strong. Lou and Murin's
2014 MIT PRIMES-USA report, Section 5, pages 7--8, already gives the equivalent
fixed-triangle partner equations

```text
alpha + beta = 180,
beta + 3 gamma = 36,
alpha - 3 gamma = 144,
distance-three count = 32-gamma,
gamma != 11.
```

The translation is `(alpha,beta,gamma)=(a1,a2,a3)` and `q=12-gamma`, so this
is exactly the Wave 7 partner profile and `q!=1` gap. Those ingredients are
prior art or independent rederivations, not novelty. No checked hit was found
for the Wave 7 global support exclusions of `n3=24,27` or the exact resulting
bound. The full correction and expanded search are recorded in
`agents/2026-07-22-wave8-status-search.md`.

## Queries

The independent status auditor searched variants including

```text
"n3 >= 30" "strongly regular"
"n_3 \ge 30" "strongly regular"
"209316" "srg(99"
"209,316" "srg(99"
"209,286" hexagons strongly regular
"srg(99,14,1,2)" hexagons
"Conway 99-graph" hexagons
"Conway 99" "N3" graph
site:arxiv.org "srg(99,14,1,2)" "n3"
"The Subgraphs of Order Six" Reimbayev
```

The full texts of both Reimbayev papers were also searched for `n3`, lower-
bound variants, the exact values `209316` and `209,316`, and the target
parameters.

## Primary-source findings

Reimbayev's 2024 paper,
[*The Lower Bound for Number of Hexagons in Strongly Regular Graphs with
Parameters lambda=1 and mu=2*](https://doi.org/10.62780/ejaam/2024-001),
derives

```text
p6 = (1/12) n k (k-2) (2k^2-21k+53) + n3.
```

For `(n,k)=(99,14)`, this is `p6=209,286+n3`. Its published lower bound uses
only `n3>=0`, and it does not state `n3>=30`.

The current 2025 order-six preprint,
[*The Subgraphs of Order Six of the Family of Strongly Regular Graphs with
Parameters lambda=1 and mu=2*](https://arxiv.org/abs/2508.03377v2), explicitly
treats `n3` as a free variable and expresses the other six-vertex counts in
terms of `n,k,n3`. Its conclusion does not determine `n3`; the exact Wave 7
bound and induced-cycle value do not appear.

Cesarz and Woldar's 2025 published paper,
[*On the automorphism group of a putative Conway 99-graph*](https://doi.org/10.5802/alco.418),
addresses automorphism restrictions rather than this induced-subgraph count.

## Conservative verdict

No checked primary source was found stating the conditional bound

```text
n3 >= 30
```

or its equivalent `p6>=209,316`. This targeted search does not establish
novelty, and the project makes no novelty claim. It also does not alter the
literature or project status of Conway-99 itself, which remains `UNKNOWN` here.
