# Wave 10 exact-claim and prior-art status audit

```yaml
role: literature
date_utc: 2026-07-23T03:23:41Z
git_commit: 6da2cb997ad091459b4d934675621671fe2ede42
claim_label: UNKNOWN
scope: exclusion n3=36; consequent bounds n3>=39 and induced_C6>=209325; active-q/common-point/point-clique/2K6/rook-saturation proof chain
inputs:
  agents/2026-07-22-wave9-status-search.md: add0d9d2afc335b7de9f9f6d5ffab72d66af97a568141cc8e885725984dc6b05
  agents/2026-07-22-wave8-status-search.md: 31511fd902d2887823174374c8a058c22452bb81950f49a25834e69efcc460ed
method: targeted primary-literature, arXiv, current-web, and public-code search through 2026-07-22 America/Los_Angeles
outputs:
  exact_wave10_result: NO_CHECKED_HIT
  novelty_status: UNKNOWN
  target_status: OPEN_IN_CHECKED_SOURCES
limitations: a negative search cannot establish novelty; indexing, terminology, unpublished work, and non-default-branch gaps remain
```

## Conservative conclusion

No checked paper or pre-existing public repository stated or proved
`n3!=36`, `n3>=39`, `induced_C6_count>=209325`, or the complete active-profile,
point-clique, forced-`2K6`, and rook-saturation argument. This is only
`NO_CHECKED_HIT`, not proof of novelty.

The safe description is:

> We obtain a conditional, internally verified exclusion of `n3=36`. No
> checked external source or pre-existing public repository was found
> containing this exclusion or the complete equality-case argument. External
> novelty remains unknown.

Several important ingredients are prior art and must not be advertised as new:
Lou--Murin's fixed-triangle profile and `q!=1` gap; Makhnev's condition used to
force `n3>0`; Reimbayev's congruence and hexagon formula; the general
common-point lemma for regular clique assemblies; and the identification of
`L(K3,3)` as the `srg(9,4,1,2)` rook graph.

## Attribution map

| Ingredient | Primary source and location | Conservative status |
|---|---|---|
| Fixed-triangle profile and `q!=1` | [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf), Section 5, PDF page 8: `alpha+beta=180`, `beta+3gamma=36`, `alpha-3gamma=144`, and `gamma!=11`; project notation is `q=12-gamma` | `CITED`; not new |
| `n3>0` | [Makhnev 1988](https://www.mathnet.ru/eng/mzm4220), theorem statement on PDF page 2 and proof on pages 5--6, used by contrapositive | `CITED`; no quantitative bound near 36 |
| `n3=0 (mod 3)` | [Reimbayev 2024](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf), Proposition 3.2, PDF page 9: `3n1+n3=(1/4)nk(k-2)` | `CITED` |
| `induced_C6_count=209286+n3` | Same source, PDF pages 11--12; Theorem 3.3 uses only `n3>=0` | `CITED`; it does not imply 209325 |
| Common-point rule | [Guest--Hammer--Johnson--Roblee 2017](https://doi.org/10.5556/j.tkjm.48.2017.2237), Lemma 1 and printed pages 303--304; [Petro--Phillips](https://arxiv.org/pdf/2502.17845v1), proof of Theorem 3.18, PDF page 19 | General lemma is `CITED`; the Wave 10 equality-case use is project-specific |
| Triangle/clique graph and point cliques | [Petro--Phillips](https://arxiv.org/pdf/2502.17845v1), definition on PDF page 3 and locally-linear specialization on pages 24--27; Lou--Murin Section 5 | General framework is prior art; no checked source used the exact active complement `K` reduction |
| `L(K3,3)` is the `3`-by-`3` rook graph `srg(9,4,1,2)` | Petro--Phillips, Theorem 4.3, PDF pages 21--22, specialized to `n=3` | `CITED` and elementary |
| `n3=36` active profiles | No checked exact hit | Project derivation; novelty `UNKNOWN` |
| Forced `K=2K6` equality domain | No checked target-specific hit | Project application downstream of cited general ingredients |
| Rook saturation contradiction | No checked source contained the support mapping or extra-common-neighbor contradiction | Project application; novelty `UNKNOWN` |
| `n3!=36`, hence `n3>=39` | No checked hit | Conditional project result; novelty `UNKNOWN` |
| `induced_C6_count>=209325` | No checked hit | Conditional corollary of the project bound and Reimbayev's formula |

Reimbayev's later six-vertex manuscript explicitly retains `n3` as a free
variable and records `p6=209286+n3` for the target
([arXiv:2508.03377v2](https://arxiv.org/pdf/2508.03377v2), PDF pages 3, 6,
and 20). The seven-vertex manuscript does likewise
([arXiv:2511.06572v1](https://arxiv.org/pdf/2511.06572v1), PDF pages 2--7).
Neither contains the equality exclusion.

## Current-status evidence

The checked current sources still treat existence of `srg(99,14,1,2)` as
unresolved:

- [Cesarz--Woldar 2025](https://alco.centre-mersenne.org/articles/10.5802/alco.418/)
  says existence remains an elusive open problem;
- [Petro--Phillips](https://arxiv.org/pdf/2502.17845v1), PDF page 27, lists the
  target among the unresolved `lambda=1,mu=2` parameter sets;
- [Phillips's May 2026 thesis](https://arxiv.org/pdf/2605.22867), PDF pages 5
  and 29, says Conway's bounty remains unclaimed and does not resolve
  existence;
- [Keramatipour v2](https://arxiv.org/abs/2604.23037v2), April 28, 2026,
  reports that direct SAT encodings remain infeasible in reasonable time;
- [Harrison Pedrero's July 2026 repository](https://github.com/harrisonpedrero/conway-99-graph)
  expressly retracts an earlier overclaim and says that nothing there closes
  the problem; and
- the [July 2026 closed-`A9` package](https://github.com/klabianco/closed-a9-conway99)
  labels its result as a narrow quotient subcase that does not settle the
  unrestricted target.

A 2022 JSAI SIG proceedings item, Ishihara's *Theory of the pain of humans
etc.*, states a nonexistence ``Theorem 28`` on PDF pages 16--17
([PDF](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_pdf/-char/en)).
Its argument passes through unproved component-uniformity and counting claims
before equations (88)--(90). Later specialist and peer-reviewed sources
continue to call the problem open. It therefore cannot be treated as an
accepted resolution and does not verify the Wave 10 claim.

## Search coverage

Exact web, arXiv, and public-code variants included:

- `"n3=36" "strongly regular"`, `"n_3=36"`, and `"n3 36 Conway 99"`;
- `"n3 >= 39"`, `"n_3 ge 39"`, `209325`, `209,325`, and `209_325`;
- `209286+n3` and spacing variants;
- active triangle `q`, triangle partners, common point, and Berge triangle;
- point-clique complement `K`, forced `2K6`, `L(K3,3)`, and rook saturation;
  and
- the principal visible Conway-99 repositories, including
  [GrayTaylor/conway99](https://github.com/GrayTaylor/conway99),
  [caitlin-hutnyk/conway-99](https://github.com/caitlin-hutnyk/conway-99),
  [lucas-zach35/Conway99SAT](https://github.com/lucas-zach35/Conway99SAT),
  [Noufeine/conway_99_graph](https://github.com/Noufeine/conway_99_graph),
  [mzurel/99Graph](https://github.com/mzurel/99Graph), and
  [ColourfulPizza/Thesis](https://github.com/ColourfulPizza/Thesis).

Searches for `209325`, `n3=36`, `2K6`, and `L(K3,3)` returned no relevant
public-code result. GitHub indexing can omit notebooks, binaries, PDFs,
non-default branches, or newly pushed material. That limitation, together with
terminology and publication-indexing gaps, is why external novelty remains
`UNKNOWN`.
