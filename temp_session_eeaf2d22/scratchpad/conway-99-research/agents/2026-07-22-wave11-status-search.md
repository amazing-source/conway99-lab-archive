# Wave 11 exact-claim and prior-art status audit

```yaml
role: literature
date_utc: 2026-07-23T05:32:00Z
git_commit: 867d875
claim_label: UNKNOWN
scope: exclusion n3=39; consequent bounds n3>=42 and induced_C6>=209328; thirteen-active-triangle point-hypergraph proof
method: targeted primary-literature, arXiv, current-web, and public-code search through 2026-07-22 America/Los_Angeles
outputs:
  exact_wave11_result: NO_CHECKED_HIT
  novelty_status: UNKNOWN
  target_status: OPEN_IN_CHECKED_SOURCES
limitations: a negative search cannot establish novelty; indexing, terminology, unpublished work, and non-default-branch gaps remain
```

## Conservative conclusion

No checked source stated or proved `n3!=39`, `n3>=42`,
`induced_C6_count>=209328`, or the complete thirteen-active-triangle
point-hypergraph argument used in Wave 11. This is `NO_CHECKED_HIT`, not proof
of novelty.

The safe description is:

> We obtain a conditional, internally verified exclusion of `n3=39`. No
> checked external source or pre-existing public repository was found
> containing this exclusion or the complete equality-case argument. External
> novelty remains unknown.

Important upstream ingredients remain prior art: Lou--Murin's fixed-triangle
partner equations and `q!=1` gap; Makhnev's condition forcing `n3>0` by
contrapositive; Reimbayev's congruence and induced-six-cycle formula; and the
general common-point obstruction for regular clique assemblies. No novelty is
claimed for those ingredients.

## Exact attribution map

| Ingredient | Checked source | Conservative status |
|---|---|---|
| Fixed-triangle profile and `q!=1` | [Lou--Murin 2014](https://math.mit.edu/research/highschool/primes/materials/2014/Lou-Murin.pdf), Section 5, PDF page 8 | `CITED`; not new |
| `n3>0` | [Makhnev 1988](https://www.mathnet.ru/eng/mzm4220), theorem statement and proof | `CITED`; no bound near 39 |
| `n3=0 (mod 3)` and `induced_C6_count=209286+n3` | [Reimbayev 2024](https://ejaam.org/articles/2024/10.62780-ejaam-2024-001.pdf), Proposition 3.2 and Theorem 3.3 discussion | `CITED`; it does not imply 209328 without the project bound |
| Common-point rule | [Guest--Hammer--Johnson--Roblee 2017](https://doi.org/10.5556/j.tkjm.48.2017.2237), Lemma 1; [Petro--Phillips](https://arxiv.org/abs/2502.17845), proof of Theorem 3.18 | General result is `CITED`; Wave 11 application is project-specific |
| Active point-clique framework | [Petro--Phillips](https://arxiv.org/abs/2502.17845) and Lou--Murin Section 5 | General framework is prior art; no exact Wave 11 reduction was found |
| `n3=39` active profiles | No checked exact hit | Project derivation; novelty `UNKNOWN` |
| Expansion `s<=4` and rooted flower contradictions | No checked target-specific hit | Project application; novelty `UNKNOWN` |
| `n3!=39`, hence `n3>=42` | No checked hit | Conditional project result; novelty `UNKNOWN` |
| `induced_C6_count>=209328` | No checked hit | Conditional corollary of the project bound and Reimbayev's formula |

## Current-status evidence

The checked current sources still treat existence of `srg(99,14,1,2)` as
unresolved:

- [Cesarz--Woldar 2025](https://alco.centre-mersenne.org/articles/10.5802/alco.418/)
  calls existence an elusive open problem;
- [Petro--Phillips](https://arxiv.org/abs/2502.17845) lists the target among
  unresolved `lambda=1,mu=2` parameter sets;
- [Phillips's 2026 thesis](https://arxiv.org/abs/2605.22867) does not resolve
  existence; and
- [Keramatipour 2026](https://arxiv.org/abs/2604.23037) reports that direct
  SAT encodings remain infeasible in reasonable time rather than producing a
  construction or proof.

These sources establish only what they say at their publication dates. The
project's targeted search found no later checked resolution through the audit
date; a literature search cannot prove that none exists.

## Search coverage

Exact web, scholarly-index, and public-code variants included:

- `"n3=39" "strongly regular"`, `"n_3=39"`, and `"n3 39 Conway 99"`;
- `"n3 >= 42"`, `"n_3 ge 42"`, `209328`, `209,328`, and `209_328`;
- `209286+n3` and spacing variants;
- active triangle `q`, thirteen active triangles, point hypergraph, linear
  spaces, Berge triangles, singleton-side crossings, rooted flowers, and
  `F/U` degree accounting; and
- the visible Conway-99 repositories already enumerated in the Wave 8--10
  status reports.

The exact-number searches returned no relevant mathematical hit. Public-code
indexing can omit notebooks, PDFs, binaries, newly pushed work, and
non-default branches. Terminology may also differ. Those limitations are why
external novelty remains `UNKNOWN`.
