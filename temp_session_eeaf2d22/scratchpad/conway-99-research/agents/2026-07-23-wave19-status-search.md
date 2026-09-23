# Wave 19 independent source-status search

```yaml
role: literature
date_utc: 2026-07-23
git_commit: NOT_RUN_NO_GIT
claim_label: UNKNOWN
scope: accepted status of srg(99,14,1,2); prior art for n3>=63 / induced-C6 endpoint 209349; exact Wave19 structural reductions; Baker 2026 and Fable/Jacobian source types
```

## Bottom line

As retrieved on 2026-07-23, no accepted construction or nonexistence proof for
`srg(99,14,1,2)` was located. The live Brouwer catalog still marks the
parameter set with `?`; the Cambridge parameter index defines that symbol as
“none is known.” A peer-reviewed 2025 paper calls existence an open problem,
and peer-reviewed/preprint work appearing in 2026 still treats it as an
existence problem rather than a solved case.

The affine induced-C6 formula is already in Reimbayev’s 2024 preprint and is
repeated in the expanded 2025 preprint:

`n12 = n*k*(k-2)*(2*k^2-21*k+53)/12 + n3`.

At `(n,k)=(99,14)`, this is `n12 = 209286 + n3`. I found no exact source for
`n3 >= 63` or the consequent endpoint `n12 >= 209349`. Thus the base formula
is prior art, while source novelty of the strengthening remains `UNKNOWN`.

No exact indexed occurrence was found for any of these bundled reductions:

- the `r=20` all-size-two reduction;
- `N A_R N^T = 2 A_L`;
- the `m=27` `K3,3`/triangular-prism obstruction;
- a cubic-order-20/Petersen residual;
- the named outside Gram decomposition.

There is meaningful nearby prior art for induced-subgraph equality bounds,
small-cubic enumeration, and Euclidean/Gram constraints. Negative searches
cannot certify novelty, so every exact-reduction novelty label remains
`UNKNOWN`.

No Wave 17 or Wave 18 artifact was read. The target labels above came from the
orchestrator’s assignment. No unverified alternate proof artifact was
inspected for correctness.

## Current existence status

| Source | Exact location and date | What it establishes |
|---|---|---|
| [Brouwer live SRG table](https://aeb.win.tue.nl/graphs/srg/srgtab51-100.html) | row `99 14 1 2`, accessed 2026-07-23 | The target remains marked `?`; no construction or nonexistence citation is attached. |
| [Brouwer–Van Maldeghem parameter index](https://assets.cambridge.org/97813165/12036/index/9781316512036_index.pdf) | printed p.451, 2022 | Defines `?` as “none is known” and lists `(99,14,1,2)?`. |
| [Brouwer–Van Maldeghem monograph PDF](https://homepages.cwi.nl/~aeb/math/srg/rk3/srgw.pdf) | printed pp.16–17, Table 1.2 and “Money,” 2022 | The target is not in the nonexistence table. The text records Conway’s reward for a construction or nonexistence proof and then only automorphism restrictions. |
| [Cesarz–Woldar](https://alco.centre-mersenne.org/articles/10.5802/alco.418/) | *Algebraic Combinatorics* 8(2), 379–398; published online 2025-04-24; abstract | Calls existence an elusive open problem. DOI `10.5802/alco.418`. |
| [Petro–Phillips](https://www.sciencedirect.com/science/article/pii/S0012365X25004704?dgcid=rss_sd_all) | *Discrete Mathematics* 349(3), March 2026, 114862; [preprint](https://arxiv.org/pdf/2502.17845), Example 4, pp.27–28 | Treats the parameters as a long-standing existence question and derives the hypothetical triangle-clique spectrum. It does not settle existence. |
| [Keramatipour](https://arxiv.org/abs/2604.23037) | arXiv v2, 2026-04-28; abstract | Reports that the tested SAT approach is not capable of handling the search in reasonable time; it is not a construction or nonexistence certificate. |

This triangulation supports the `CITED` statement that the accepted public
status remained open at the retrieval date. It is not an exhaustive proof that
no unindexed or newly circulated claim exists.

An online proceedings/research-group PDF surfaced in searching as making an
alternate nonexistence claim. Per instructions, I recorded its URL in the
evidence bundle but did not inspect or judge it. It does not override the live
catalog or current peer-reviewed status in this report.

## Induced-C6 and `n3`

Reimbayev’s
[*The Lower Bound for Number of Hexagons ...*](https://arxiv.org/pdf/2409.10620)
(arXiv v1, 2024-09-16) derives `n12 = F(n,k)+n3` on printed p.10 and gives the
closed formula on printed p.11, Theorem 2. The theorem uses only `n3 >= 0`.
The conclusion presents `n3=0` as conjectural and explains that this would
trigger an earlier conditional nonexistence result.

The expanded
[*Subgraphs of Order Six ...*](https://arxiv.org/pdf/2508.03377)
(arXiv v2, 2025-11-03) is even clearer:

- printed p.2 declares `n3` a free/unknown parameter;
- printed p.5 rederives the same `n12` formula;
- printed pp.16–19 list every order-six count in terms of `n,k,n3`;
- printed pp.23–24 say one additional parameter is still required and draw no
  conclusion resolving it.

Substitution is exact:

`2*14^2 - 21*14 + 53 = 151`,

so the parameter-only term is

`99*14*12*151/12 = 209286`.

Therefore:

`n12 = 209286 + n3`,

and the proposed conditional strengthening `n3 >= 63` is equivalent to
`n12 >= 209349`. Exact-string and structural queries found no source stating
the strengthening or endpoint. Claim classification:

- affine formula and `209286` baseline: `CITED`;
- `n3 >= 63` and `209349` endpoint as prior-art/novelty questions: `UNKNOWN`.

## Exact structural reductions

### `r=20` all-size-two reduction and matrix identity

Exact searches for “all-size-two,” “size-two points,” the spaced and unspaced
matrix identity, and combinations with Conway 99 produced no exact academic
hit. Incidence-matrix techniques are standard, so terminology mismatch is a
material limitation. Baker’s abstract creates additional overlap uncertainty,
discussed below. Status: `UNKNOWN`.

### `m=27` `K3,3`/triangular-prism obstruction

The bare fact that the connected cubic graphs on six vertices are `K3,3` and
the triangular prism is standard and cannot itself support a novelty claim.
What was searched was the exact use of that dichotomy as the stated Conway-99
obstruction. No such use was located.

Two near hits are not exact:

- Lou–Murin’s [manuscript](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf),
  Theorem 2.1 on PDF pp.2–4, uses a different configuration it calls a prism.
- Ibrahim–LaFayette–McCall,
  [Theorem 4.19 on journal p.84](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf),
  bounds induced copies of `K3 square K3`, the line graph of `K3,3`, in a
  hypothetical Conway graph. It is a percolation result, not the named
  `m=27` cubic obstruction.

Exact-combination status: `UNKNOWN`.

### Cubic-order-20/Petersen residual

No exact occurrence was located. Petersen hits in the inspected literature
refer to the missing Moore graph or, in a different SRG problem, a 10-vertex
component. They do not instantiate an order-20 Conway residual. Status:
`UNKNOWN`.

### Outside Gram decomposition

Shpectorov–Zhao’s
[*srg(85,14,3,2) do not exist*](https://arxiv.org/pdf/2504.02449)
is important broad prior art. Its abstract and Introduction pp.1–3 combine
classification of small cubic graphs, exhaustive neighborhood enumeration,
and Euclidean Gram positive-semidefinite/rank tests. The conclusion around
printed p.22 names Conway 99 as a possible candidate for extending the method.

Thus a generic claim of novelty for “cubic enumeration plus Gram constraints”
would be unsupported. The exact outside decomposition, dimensions, identity,
and residual structure named in the assignment were not found. Exact-form
status: `UNKNOWN`.

## Baker 2026 source status

The official
[34th Cumberland Conference program](https://www.auburn.edu/cosam/departments/math/cumberland-conference/34th_cumberland_program.pdf)
contains Ben Baker’s “An Induced Subgraph Paradigm for Strongly Regular Graph
Constructions” on PDF page 5 (printed program p.4). The official
[conference page](https://www.auburn.edu/cosam/departments/math/cumberland-conference/home.htm)
dates the meeting to 2026-05-16 and 2026-05-17.

The abstract publicly discloses:

- upper and lower bounds for disjoint copies of an induced subgraph `H`,
  depending on neighborhood size;
- even edge distribution in equality cases;
- a generalization of Lou–Murin’s independence bound;
- an application to Conway’s 99-graph problem.

It does not disclose a formal theorem statement, complete hypotheses,
formulas, proof, certificate, or any of the exact named reductions. Exact-title,
author/title, arXiv-site, and repository searches found the program plus a
[2024 Auburn seminar listing](https://auburn.edu/cosam/events/2024/03/dms_combinatorics_seminar2.htm),
but no paper.

Source classification: `CITED` conference abstract/public disclosure. Proof
classification: none available from the located source. Exact-overlap and
novelty classification: `UNKNOWN`.

## Fable/Jacobian recheck

This recheck was confined to source type and is unrelated to Conway 99.

The original source is an
[X announcement by Levent Alpöge](https://x.com/__alpoge__/status/2079028340955197566),
reported as 2026-07-20 by
[MathWorld](https://mathworld.wolfram.com/JacobianConjecture.html) and as
2026-07-19 by an
[independent explainer](https://jacobianfun.org/jacobian-explained).
MathWorld, updated 2026-07-22, explicitly says “announced” and reproduces the
map, determinant, and colliding points. The explainer also deliberately uses
“announced” because the record is new, while supplying exact symbolic checks.
A [Zihan Zhang follow-on note](https://zzhang-iu.github.io/papers/direct-consequences-jacobian/)
is an author-hosted web note, not a peer-reviewed publication.

This distinction matters:

- Baker: conference abstract with broad claims but no inspectable proof or
  certificate in the located source.
- Fable/Jacobian: social-media announcement, not a journal proof, but it
  publishes a short finite object whose decisive identities can be checked
  independently.

No query connected Fable or the Jacobian announcement to Conway 99. It has no
bearing on the graph’s status.

## Limitations and publication guidance

- Search coverage included the live SRG catalog, a current monograph,
  peer-reviewed/current papers, arXiv, the official Baker program, and targeted
  exact/structural web queries. It did not exhaust MathSciNet, zbMATH, all
  theses, all recordings, private manuscripts, or correspondence.
- Different notation can conceal equivalent matrix or residual statements.
- No Baker manuscript or talk recording was found and no author was contacted.
- Search absence is not a novelty certificate.
- Quarantined alternate proof claims were not assessed.

The safe public wording is:

> Current authoritative sources still list `srg(99,14,1,2)` as unresolved.
> The induced-C6 affine formula is known. We did not locate the proposed
> `n3 >= 63` strengthening or exact structural reductions in indexed sources,
> but their novelty remains unknown pending a fuller literature/author check.

## Evidence files

- [`attempts/wave19-status-search/query-log.json`](../attempts/wave19-status-search/query-log.json)
- [`attempts/wave19-status-search/source-matrix.json`](../attempts/wave19-status-search/source-matrix.json)
- [`attempts/wave19-status-search/negative-results.md`](../attempts/wave19-status-search/negative-results.md)
- [`attempts/wave19-status-search/run-report.yaml`](../attempts/wave19-status-search/run-report.yaml)
