# Wave 9 exact-claim and prior-art status audit

```yaml
role: literature
date_utc: 2026-07-23T02:25:06Z
git_commit: 3d47bb260a71c5c2606347d8bb53e3ad766236e8
claim_label: UNKNOWN
scope: exact exclusion n3=33, bound n3>=36, and the labeled crossing-graph/point-clique/K5 argument for srg(99,14,1,2)
method: targeted primary-literature, arXiv, web, and public-code search through 2026-07-22 local time; downloaded papers were searched in normalized full text
outputs:
  exact_wave9_result: NO_CHECKED_HIT
  novelty_status: UNKNOWN
limitations: a negative search cannot establish novelty; indexing gaps, unpublished work, and terminology differences remain possible
```

## Conservative conclusion

No checked primary source contained the exclusion `n3=33`, the bound
`n3>=36`, the induced-six-cycle value `209322`, or the complete labeled
crossing-graph, point-clique, forced-`K5`, and residual-matching argument.
This is only `NO_CHECKED_HIT`, not proof of novelty.

The safe description is:

> a conditional project derivation, independently verified internally and
> pending external review.

Substantial upstream ingredients are prior art: Lou--Murin's fixed-triangle
profile and `q!=1` gap, Makhnev's extra-condition nonexistence theorem used by
contrapositive to force `n3>0`, and Reimbayev's `n3` congruence and hexagon
formula. The project must not describe those ingredients as new.

## Attribution map

| Ingredient | Primary source and location | Conservative status |
|---|---|---|
| Triangle graph on 231 triangles, 18-regular, with local perfect matchings | [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf), Section 5, PDF pages 7--8 | `CITED` |
| `alpha+beta=180`, `beta+3gamma=36`, `alpha-3gamma=144`, and `gamma!=11` | Same source, PDF page 8 | `CITED`; under `(a1,a2,a3)=(alpha,beta,gamma)` and `q=12-gamma`, this is the fixed profile and `q!=1` |
| `n3>0` for a putative Conway graph | [Makhnev 1988](https://www.mathnet.ru/eng/mzm4220), PDF page 2 and proof on pages 5--6 | `CITED` as a contrapositive; it gives no quantitative bound near 36 |
| `3n1+n3=(1/4)nk(k-2)` | [Reimbayev 2024](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf), Proposition 3.2, PDF page 9 | `CITED`; for the target it gives `n3=0 (mod 3)` |
| `induced_C6_count=209286+n3` | Same source, Section 3, PDF pages 11--12 | `CITED` |
| Published lower bound using only `n3>=0` | Same source, Theorem 3.3, PDF page 12 | Does not imply `209322` |
| Exclusion `n3=33`, hence `n3>=36` | No checked hit | `DERIVED` in this project; external novelty `UNKNOWN` |
| Labeled crossing-graph singleton lemma | No checked hit | Project lemma; no novelty assertion |
| Point-clique budget, forced `K5`, and residual `K6` minus matching contradiction | No checked exact-target hit | Project derivation; no novelty assertion |

## Current-status evidence

The checked current sources continue to describe existence of
`srg(99,14,1,2)` as unresolved:

- [Cesarz--Woldar 2025](https://alco.centre-mersenne.org/item/10.5802/alco.418.pdf),
  PDF page 2 / printed page 379;
- [Petro--Phillips, arXiv v1](https://arxiv.org/pdf/2502.17845v1), PDF
  page 28; the paper later appeared in *Discrete Mathematics* 349(3), 114862;
- [Keramatipour, arXiv v2](https://arxiv.org/pdf/2604.23037v2), PDF pages
  3, 7, 39, and 49--50;
- [DeLeo 2025](https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p048.pdf),
  Section 4, printed pages 57--59;
- [Reimbayev's six-vertex manuscript](https://arxiv.org/pdf/2508.03377v2),
  PDF pages 1--2 and 24; and
- [Reimbayev's Hamiltonian-cycle manuscript](https://arxiv.org/pdf/2511.06572v1),
  PDF pages 2--7.

The two later Reimbayev manuscripts retain `n3` as a free parameter and do
not contain the Wave 9 bound.

## Search coverage

Queries included:

- “Conway 99 graph,” “Conway's 99-graph,” and `srg(99,14,1,2)`;
- `n3`, induced `N3`, two triangles joined by two edges, and triangle-pair
  crossing matchings;
- induced `C6`, hexagons, `p6`, `n12`, `209322`, and `209,322`;
- active triangles, triangle partners, crossing/support graph, point clique,
  `K5` component, and fixed-original-point; and
- the exact Lou--Murin equations and public-code variants.

No exact hit appeared in the checked web, arXiv, primary-PDF, or public-code
searches. That supports only `NO_CHECKED_HIT`.

## Download ledger

The PDFs were downloaded to an untracked temporary audit directory and hashed
with SHA-256:

| File | SHA-256 |
|---|---|
| Lou--Murin 2014 | `5df5b96709419c6168430c58601ee98ec26e6c08036034bd755247311c2fb211` |
| Makhnev 1988 | `ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431` |
| Reimbayev 2024 | `484ff4bbcf13ea26d478baa4c24b97f6996ac3fc35ef8459c15fb61b61b98521` |
| Reimbayev six-vertex manuscript v2 | `c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9` |
| Reimbayev Hamiltonian-cycle manuscript v1 | `d98d474ef277b6a32fc4125690c75d3808450225b0657dbd46290673b7a014f7` |
| Cesarz--Woldar 2025 | `d88f3832337b949edbd21cadf0836bd0df77bf84bf5c225a1b834d9883ca65a8` |
| Petro--Phillips arXiv v1 | `9adb7132b4a40ce87d77b2326fc6ddf1370aa12665f86617aa285b9e824797be` |
| Keramatipour arXiv v2 | `8fadd666b4b8eaa538874b209c3b4f113704bfdc9d567efdb66e6c8296fe0cc8` |
| DeLeo 2025 | `4a635eca12254c11c141f22bfc3fe58e6c6b437829ea7a61172bf807c28485ff` |

Downloaded sources are linked rather than vendored. Their original licenses
and copyrights remain with their authors and publishers.
