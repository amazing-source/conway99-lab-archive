# Wave 19 source-search negative results and cautions

Search date: 2026-07-23 UTC

These are bibliographic negative results, not mathematical certificates. “No exact
hit” means that the recorded index-backed web queries and the inspected primary or
authoritative sources did not expose an exact occurrence. Different terminology,
unindexed material, talks, private circulation, or later work may exist.

The exact query strings and per-query outcomes are preserved in
[`query-log.json`](query-log.json). Exact source URLs, dates, and page/theorem
locations are preserved in [`source-matrix.json`](source-matrix.json).

## Exact-target search

| Target | Result | Important qualification |
|---|---|---|
| Accepted construction or nonexistence proof for `srg(99,14,1,2)` | No accepted proof or construction located. | The live Brouwer catalog still marks the parameters `?`; Cesarz–Woldar (published online 2025-04-24), Petro–Phillips (March 2026), and Keramatipour (April 2026) all continue to treat existence as unresolved. This triangulation is evidence of current community status, not a proof that no unnoticed source exists. |
| Conditional `n3 >= 63` | No exact statement located. | Reimbayev’s 2024 and 2025 preprints publish the affine induced-hexagon formula but retain `n3` as nonnegative/free or unknown. |
| Induced-C6 endpoint `209349` (or the strings `209349` / `209,349`) | No relevant academic hit located. | The already-published formula gives `n12 = 209286 + n3` after substituting `n=99,k=14`; therefore `n3 >= 63` would imply `n12 >= 209349`. The formula and baseline are prior art; only the strengthening was not found. |
| `r=20` all-size-two reduction | No exact indexed occurrence located. | Baker’s 2026 abstract is broad enough to create possible overlap but contains no `r=20` statement or theorem details. |
| `N A_R N^T = 2 A_L` | No exact indexed occurrence located under spaced and unspaced variants. | Incidence-matrix language is common; a notation mismatch could hide equivalent prior art. |
| `m=27` `K3,3`/triangular-prism obstruction | No exact use in the target problem located. | The classification of connected cubic graphs on six vertices as `K3,3` or the triangular prism is standard; novelty cannot attach to that bare fact. The exact reduction/obstruction combination was not found. |
| Cubic-order-20/Petersen residual | No exact target occurrence located. | Petersen occurrences found in nearby literature concern the missing Moore graph or a 10-vertex component in a different SRG problem. |
| Outside Gram decomposition | No exact target decomposition located. | Euclidean/Gram positive-semidefinite and rank arguments for SRGs are established methodology; Shpectorov–Zhao explicitly combine them with small-cubic enumeration for `srg(85,14,3,2)` and name Conway 99 as a possible future target. |

## Near hits that are not exact prior art

1. Reimbay Reimbayev, *The Lower Bound for Number of Hexagons in Strongly
   Regular Graphs with Parameters lambda=1 and mu=2*,
   [arXiv:2409.10620](https://arxiv.org/pdf/2409.10620), printed pp.10–11,
   proves

   `n12 = n*k*(k-2)*(2*k^2-21*k+53)/12 + n3`

   and obtains its theorem using only `n3 >= 0`. At `(n,k)=(99,14)` this is
   `n12 = 209286 + n3`. The paper does not state `n3 >= 63`.

2. Reimbayev, *The Subgraphs of Order Six ...*,
   [arXiv:2508.03377v2](https://arxiv.org/pdf/2508.03377), printed p.2, p.5,
   pp.16–19, and Conclusion pp.23–24, again treats `n3` as a free/unknown
   additional parameter and gives all order-six counts in terms of it. It does
   not resolve the proposed strengthening.

3. Ibrahim–LaFayette–McCall, *Minimum 2-percolating sets in 2-connected,
   diameter 2 graphs*,
   [Australasian Journal of Combinatorics 93(1) (2025), 60–89](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p060.pdf),
   journal p.84, Theorem 4.19, bounds induced copies of `K3 square K3` in a
   hypothetical Conway graph. Since `K3 square K3` is the line graph of
   `K3,3`, this is a genuine nearby hit, but it is not the named
   `m=27` cubic `K3,3`/prism obstruction.

4. Lou–Murin,
   [*On the Strongly Regular Graph of Parameters (99,14,1,2)*](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf),
   Theorem 2.1 and Theorem 4.3, use a different configuration called a
   “prism” and prove the independence-number/equal-outside-degree result that
   Baker says he generalizes. Neither is the exact Wave 19 target.

5. Shpectorov–Zhao,
   [*Strongly regular graphs with parameters (85,14,3,2) do not exist*](https://arxiv.org/pdf/2504.02449),
   Introduction pp.1–3 and conclusion around printed p.22, establish broad
   methodological prior art for small-cubic classification, exhaustive local
   enumeration, and Euclidean/Gram tests. Their graph, local order, parameters,
   and decomposition differ; they present Conway 99 only as a possible future
   candidate.

6. Petro–Phillips,
   [*On clique graphs and clique regular graphs*](https://arxiv.org/pdf/2502.17845),
   Example 4 on pp.27–28, derives the spectrum of the triangle-clique graph of
   a hypothetical Conway graph. Searches within the full preprint did not find
   Petersen, `K3,3`, triangular prism, or the named matrix identity.

## Baker 2026: abstract, not proof source

The official [34th Cumberland Conference program](https://www.auburn.edu/cosam/departments/math/cumberland-conference/34th_cumberland_program.pdf)
contains Ben Baker’s abstract on PDF page 5 (printed program p.4). The
[conference page](https://www.auburn.edu/cosam/departments/math/cumberland-conference/home.htm)
dates the meeting to 2026-05-16 through 2026-05-17.

The abstract says there are neighborhood-size upper/lower bounds for disjoint
induced copies of a graph `H`, equality forces even edge distribution, the
result generalizes Lou–Murin, and an application to Conway 99 is considered.
It does not include a formal theorem statement, definitions sufficient to
identify the equality cases, formulas, a proof, or a certificate. Exact-title,
author/title, author/topic, arXiv-site, and ResearchGate-site searches found
only the program and an older Auburn seminar listing, not a paper.

Consequently, the abstract establishes a public disclosure and a material
overlap risk. It does not establish that any exact Wave 19 reduction was
previously proved.

## Fable/Jacobian announcement: source-type control only

The original URL is Levent Alpöge’s
[X post](https://x.com/__alpoge__/status/2079028340955197566); direct text
extraction returned no content. [MathWorld](https://mathworld.wolfram.com/JacobianConjecture.html),
updated 2026-07-22, calls it a July 2026 announcement credited to Fable and
reproduces an explicit polynomial, a constant Jacobian determinant, and
colliding points. The independent
[Jacobian explainer](https://jacobianfun.org/jacobian-explained) explicitly
uses “announced” because the public record is new, while providing exact
rational-arithmetic checks. Zihan Zhang’s
[follow-on web note](https://zzhang-iu.github.io/papers/direct-consequences-jacobian/)
is likewise author-hosted rather than a peer-reviewed paper.

This is not analogous to a theorem-free conference abstract: the public
announcement carries a short finite certificate that third parties can check.
It is nevertheless an announcement, not a journal publication. No searched
source connected Fable or the Jacobian announcement to Conway 99, so it has no
bearing on the target’s source status.

## Quarantined claims and false positives

- A [J-STAGE research-group/proceedings PDF](https://www.jstage.jst.go.jp/article/jsaisigtwo/2022/AGI-021/2022_01/_pdf/-char/en)
  surfaced as making an online nonexistence claim. Per the task restriction, it
  was not inspected or evaluated for correctness and is not used to alter
  status. Current authoritative and peer-reviewed sources continue to mark the
  target unknown/open.

- A self-archived
  [Figshare preprint](https://figshare.com/articles/preprint/Five_New_Results_on_Conway_s_99-Graph_Problem/23732622/2?file=41679612)
  is cited by Ibrahim et al. It was recorded but not opened for proof
  assessment.

- A search snippet for a
  [critical-group paper](https://www.sciencedirect.com/science/article/pii/S0097316521000236)
  can misleadingly place a nonexistence phrase near Conway material. The
  nonexistence statement is about a different parameter set; it is not evidence
  about `(99,14,1,2)`.

## Limitations

- The search covered the live Brouwer catalog, the 2022 monograph/index,
  current journal and arXiv records found by exact and structural terminology,
  the 2026 Baker conference material, and targeted web queries. It was not an
  exhaustive search of MathSciNet, zbMATH, every thesis, every conference
  recording, private correspondence, or non-indexed repositories.
- Exact strings are fragile. Equivalent statements may use different
  notation, transpose conventions, graph names, or parameter labels.
- No author was contacted, and no talk recording or Baker manuscript was
  located.
- No negative bibliographic result here is a novelty certificate.
- No correctness judgment was made about quarantined alternate proof claims.
- Therefore the exact-reduction novelty label must remain `UNKNOWN`.
