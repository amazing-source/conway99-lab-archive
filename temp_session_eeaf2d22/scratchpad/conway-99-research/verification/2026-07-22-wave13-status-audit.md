# Wave 13 source/status audit

```yaml
role: verifier
date_utc: 2026-07-23T08:10:28Z
git_commit: c471801a7adf6852a208b5d5553bcc76a3372d6a
claim_label: VERIFIED
scope: bounded source-integrity and attribution audit of agents/2026-07-22-wave13-status-search.md; not a proof of novelty or of the global literature status
inputs:
  CONJECTURE.md: 7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58
  SOURCES.bib: 91feb4454a42782422512e669aaa60aa4c6615111a08f3d908e286397a717828
  agents/2026-07-22-wave13-status-search.md: 7e207efe73af88762495e08dc56dc8d06ca4d2643303d3f106eba062a8799dfe
  arxiv_source_2409.10620v1: 9e31eb63e878531124cb20df306698827b93057b4ef9feed207654aea8f31112
  arxiv_source_2409.15001v1: bfe308506459b5e78a2f1205275cd7cbf888b99e0460645adbd2e3e234af2c20
  arxiv_source_2502.17845v1: 70184d605bd3cb7732efae8311de44697ee55793be988bd8a880271da283e2c9
  arxiv_source_2508.03377v2: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
  arxiv_source_2511.06569v1: 5d1a5d22ad0bbde4fc4739fe4187faf13261255946cec57833aca2ccd6b53df3
  arxiv_source_2511.06572v1: 10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a
  arxiv_source_2604.23037v2: ddd6c002f142c9a3a0b648c28aa0e4d478f314b6af646b86810ec29129bf1caa
  arxiv_source_2605.22867v1: 5345e9c360caf0a501de83c8d4a4b552cb06034de3047a4c2e48874d33748b18
method: independent downloads from versioned official arXiv e-print URLs, SHA-256 replay, exact TeX inspection, a bounded current arXiv-targeted web search, and inspection of an official Math-Net citation trail
command: |
  Invoke-WebRequest -Uri "https://export.arxiv.org/e-print/<versioned-id>" -OutFile "<versioned-id>.src"
  Get-FileHash -Algorithm SHA256 <downloaded-source-archives>
  tar -xf <archive> -C <per-version-directory>
  rg -n -i -g '*.tex' '209334|209,334|fifteen active|15 active|active triangle|n_3\s*(\\neq|!=|>=|\\geq|>)\s*(45|48)|n3\s*(\\neq|!=|>=|\\geq|>)\s*(45|48)' <unpacked-source-root>
outputs:
  bounded_report_verdict: PASS
  exact_archive_hash_replay: PASS
  n45_n48_catalogue_index_warning: PASS
  global_search_exhaustiveness: UNKNOWN
  novelty: UNKNOWN
  srg_99_14_1_2: UNKNOWN
limitations: negative full-text and web searches are not exhaustive; several ancillary page-level attributions were not independently replayed before the bounded audit was closed
```

## Verdict

**PASS**, limited to the report's source-integrity, notation, and
publication-safe status boundaries.

The decisive warning is correct: Reimbayev v2's `n_{45}` and `n_{48}` are
counts of the 45th and 48th types in its enumerated six-vertex catalogue.
They are not statements that the project's separate count `n_3` equals 45 or
is at least 48.

No falsification of the report's conservative `NO_CHECKED_HIT` conclusion was
found. This is not an exhaustive literature result. In particular:

```text
novelty of the project n3 bounds: UNKNOWN
existence of srg(99,14,1,2):      UNKNOWN
```

## Exact source-boundary replay

On 2026-07-23 UTC, each of the eight versioned source archives was downloaded
independently from
`https://export.arxiv.org/e-print/<versioned-id>`. Every observed SHA-256
matched the hash declared in the discovery report:

| arXiv version | Observed SHA-256 | Result |
|---|---|---|
| `2409.10620v1` | `9e31eb63e878531124cb20df306698827b93057b4ef9feed207654aea8f31112` | PASS |
| `2409.15001v1` | `bfe308506459b5e78a2f1205275cd7cbf888b99e0460645adbd2e3e234af2c20` | PASS |
| `2502.17845v1` | `70184d605bd3cb7732efae8311de44697ee55793be988bd8a880271da283e2c9` | PASS |
| `2508.03377v2` | `f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834` | PASS |
| `2511.06569v1` | `5d1a5d22ad0bbde4fc4739fe4187faf13261255946cec57833aca2ccd6b53df3` | PASS |
| `2511.06572v1` | `10f8d9ea09dc72f4ca6bce4e9427ff1df32718d2978bb35a16db1af3c27cc39a` | PASS |
| `2604.23037v2` | `ddd6c002f142c9a3a0b648c28aa0e4d478f314b6af646b86810ec29129bf1caa` | PASS |
| `2605.22867v1` | `5345e9c360caf0a501de83c8d4a4b552cb06034de3047a4c2e48874d33748b18` | PASS |

The official version pages checked were:

- `https://arxiv.org/abs/2409.10620v1`
- `https://arxiv.org/abs/2409.15001v1`
- `https://arxiv.org/abs/2502.17845v1`
- `https://arxiv.org/abs/2508.03377v2`
- `https://arxiv.org/abs/2511.06569v1`
- `https://arxiv.org/abs/2511.06572v1`
- `https://arxiv.org/abs/2604.23037v2`
- `https://arxiv.org/abs/2605.22867v1`

Access date for all was 2026-07-23 UTC. This establishes that the report's
line-level source searches were bounded to the stated immutable versions,
rather than to mutable latest-version aliases.

## Decisive `n_{45}` / `n_{48}` audit

The exact `2508.03377v2` TeX says:

- line 85: the author sets `n_3` as a free variable;
- lines 118--123: `n_3` is again explicitly called a free/unknown parameter;
- line 224: the author notes that the subgraphs have been numbered;
- lines 228--229: “For `n_{45}`” is followed by a construction and a formula
  `n_{45}=<parameter polynomial>+n_3`;
- lines 243--254: “For `n_{48}`” is followed by a construction of subgraphs
  `N_{48}` and a formula `n_{48}=<parameter polynomial>+14n_3`;
- lines 390 and 393 repeat those two catalogue formulas in the summary;
- lines 411 and 528--530 continue to leave `n_3` undetermined.

Thus the notation itself separates three different counts:

```text
n_3    = count of catalogue type N_3, retained as the free parameter
n_{45} = count of catalogue type N_45
n_{48} = count of catalogue type N_48
```

Indeed, the displayed formulas express `n_{45}` and `n_{48}` *in terms of*
`n_3`. Reading their subscripts as numerical bounds on `n_3` is
grammatically and mathematically incompatible with the paper. The discovery
report correctly rejected these two string hits as false positives.

## Reimbayev identity and arithmetic boundary

The exact `2409.10620v1` TeX supports the report's cited arithmetic:

- line 125 defines `p_6` as the number of induced subgraphs isomorphic to
  `C_6`;
- lines 335--367 identify catalogue count `n_{12}` with the hexagon count and
  derive `n_{12}=F(n,k)+n_3`;
- lines 396--402 give

  ```text
  n_{12} = (1/12)n k(k-2)(2k^2-21k+53) + n_3.
  ```

For `(n,k)=(99,14)`, the parameter term evaluates exactly to

```text
(1/12)(99)(14)(12)(2*14^2-21*14+53) = 209286.
```

The same source gives

```text
3n_1+n_3 = (1/4)n k(k-2)
```

at lines 308 and 323. For the target, the right side is `4158`, divisible by
3, so `3 | n_3`. Therefore the discovery report correctly separates:

1. the cited identities `3 | n_3` and
   `induced_C6_count=209286+n_3`; from
2. the project-dependent implication that, if `n_3=45` is excluded after a
   verified `n_3>=45`, then divisibility forces `n_3>=48` and hence
   `induced_C6_count>=209334`.

The checked source supplies item 1. It does not supply the Wave 13 equality
exclusion in item 2.

## Exact-claim replay over the pinned TeX corpus

The command recorded in the run header returned no match in the unpacked TeX
for:

```text
209334
209,334
fifteen active
15 active
active triangle
n_3 or n3 compared by !=, \neq, >, >=, or \geq to 45 or 48
```

This supports, but cannot make exhaustive, the report's
`NO_CHECKED_HIT` result for the exact Wave 13 claims.

The bounded current web searches actually rerun on 2026-07-23 were:

```text
site:arxiv.org "Conway-99"
site:arxiv.org "srg(99,14,1,2)"
site:arxiv.org "n_3" "99,14,1,2"
site:arxiv.org "209334" strongly regular graph
```

They produced no checked source contradicting the report. Search-engine
coverage, indexing latency, synonym choice, unpublished work, and sources
outside arXiv remain unresolved.

## Older theorem and page-attribution checks

The official Math-Net English text of Makhnev--Paduchikh (1997),
`https://www.mathnet.ru/php/getFT.phtml?jrnid=im&paperid=136&what=fullteng`,
states on printed page 745 that Makhnev's cited 1988 work studied strongly
regular graphs with `lambda=1` that **do not have two disjoint triangles
joined by exactly two edges**. This independently confirms the alternate
description of the hypothesis used to identify catalogue type `N_3`.

The official Makhnev 1988 PDF was also retrieved from
`https://www.mathnet.ru/php/getFT.phtml?jrnid=mzm&paperid=4220&what=fullt&option_lang=eng`
with SHA-256
`ca870226aae6a00af8b878d68bc64ca42c987dff40c4df39caefdab186e20431`.
However, the local `pdftotext` command was unavailable before this bounded
audit was closed. Consequently, this audit marks the *direct replay of the
full 1988 theorem's exact conclusion* `UNKNOWN`; it verifies the hypothesis
wording through the later same-author primary source and finds no
contradiction.

The following ancillary citation details from the discovery report were not
independently replayed to theorem/page precision in this bounded pass and
therefore remain `UNKNOWN` here, without being rejected:

- Lou--Murin (2014), Section 5, pp. 7--8 and the project correspondence to
  `q=1`;
- the exact line-level common-point statement in `2409.15001v1`;
- Guest--Hammer--Johnson--Roblee (2017), Lemma 1;
- the absence of an `n_3` bound throughout Petro--Phillips beyond the exact
  regex replay above.

These unresolved citation-detail checks do not alter the publication-safe
conclusion because the discovery report attributes them only as prior general
framework and does not use them to claim external verification of
`n_3 != 45`.

## Final publication boundary

The independently supported status is:

```text
source archives are the declared versions:                 PASS
Reimbayev n_{45}/n_{48} warning:                            PASS
Reimbayev base hexagon identity and target arithmetic:      PASS
exact Wave 13 strings absent from the pinned TeX corpus:     PASS (bounded)
all semantically equivalent published formulations absent:  UNKNOWN
novelty of n3 != 45 / n3 >= 48 / C6 >= 209334:              UNKNOWN
existence or nonexistence of srg(99,14,1,2):                 UNKNOWN
```

No external source was found that may be promoted to a proof or
counterexample certificate.
