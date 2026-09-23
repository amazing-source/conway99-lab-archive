---
role: literature
date_utc: 2026-07-23T18:28:43Z
git_commit: c8ea3d731722c07a99f4a875ca4e59cc9d8aa4a5
claim_label: UNKNOWN
scope: "Current public-source status of the apparent omission of +n23 from the printed m7(n-5) equation in arXiv:2508.03377v2; later-version, correction, journal/author-copy, and exact-prior-equation checks through the stated cutoff."
inputs:
  - path: verification/wave21-six-vertex-lp/2026-07-23T174137Z-audit.md
    sha256: 954978d992cb6896336ef457a1f2e1397422d90b9d2227317afac1506f9050cc
  - path: verification/wave21-six-vertex-lp/source-manifest.json
    sha256: ac44ce9120fdad127177bed6925517dfd59529d836d4ea06c3693441441d6465
  - url: https://export.arxiv.org/e-print/2508.03377v1
    sha256: db11b5dee4805dd8b946eb7612d402ddf4278345e327f77fd921f41028f18bae
  - url: https://export.arxiv.org/e-print/2508.03377v2
    sha256: f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834
method: "Freeze the scoped claim; inspect the official arXiv record, v1/v2 source archives, versioned and current PDFs, the official author feed, and the two later author arXiv sources; run bounded exact-title, identifier, equation, correction, institutional, and journal-domain searches; retain failures and avoid inferring novelty from non-discovery."
command: "curl.exe -fsSL <pinned-url> -o <temporary-file>; tar -tf <source-archive>; tar -xf <source-archive> -C <temporary-directory>; Get-FileHash -Algorithm SHA256 <download>; Select-String -Pattern '2508\\.03377|Subgraphs of Order Six|m_?\\{?7\\}?\\s*\\(n-5\\)|n_?\\{?23\\}?|errat|correct' <extracted-tex>"
outputs:
  - path: verification/wave21-six-vertex-lp/status/source-manifest.json
    sha256: a6b0a44f85481a4e9c36998a4558c9a62633f0e9907c910528abfcfab212da54
  - path: verification/wave21-six-vertex-lp/status/2026-07-23T182843Z-source-status-audit.md
    sha256: "computed after report freeze"
limitations: "This bounded public-source audit cannot prove that no correction or prior statement exists. Search indexing may lag; private correspondence, talks, inaccessible manuscripts, and unindexed copies were outside scope. PDF bytes were pinned, but equation-level inspection used official TeX because local PDF extraction dependencies were unavailable. This report does not re-prove the separate residual or unique-repair computation."
---

# Wave 21 source-status audit

## Verdict

As of `2026-07-23T18:28:43Z`, the official arXiv record for
[2508.03377](https://arxiv.org/abs/2508.03377) is still **v2**, last revised
`2025-11-03T21:34:38Z`. No v3 or later version is listed.

The official v1 and v2 TeX sources both print the `m7(n-5)` deletion-deck
equation without `+n23`. The v2 revision changes other four-to-five equations
and a bibliography entry, but leaves this `m7` equation unchanged. The
unversioned current PDF is byte-identical to the v2 PDF.

This audit located:

- no later arXiv version;
- no formal erratum or correction notice;
- no journal-hosted or author-hosted corrected version;
- no exact primary source that already states the `+n23` correction.

Those are bounded non-discovery results, not novelty evidence. The exact
correction's novelty remains **UNKNOWN**, and Conway's
`srg(99,14,1,2)` existence status remains **UNKNOWN**.

## Exact source observations

The official arXiv Atom record reports:

```text
current id:    arXiv:2508.03377v2
submitted:     2025-08-05T12:27:36Z
last updated:  2025-11-03T21:34:38Z
journal_ref:   absent
journal DOI:   absent
```

The source archives were path-safety checked before extraction. In both
versions, `The_Subgraphs_of_Order_Six.tex` line 501 begins the same printed
`m_7(n-5)` equation, and `n_{23}` is absent from that equation:

| Source | Archive SHA-256 | TeX SHA-256 | Observation |
|---|---|---|---|
| v1 | `db11b5dee4805dd8b946eb7612d402ddf4278345e327f77fd921f41028f18bae` | `bd963e2deb0c2d27cbbd76f21dd69cceccf29c8ea32df11bb2931125a2c56ade` | `+n23` absent |
| v2 | `f8429d2f839267e2aaf98b04451cb2f0252c0353f75bee6ec6e6947eab0d5834` | `823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f` | `+n23` absent |

The current PDF and explicitly versioned v2 PDF were each 873,456 bytes and
had SHA-256
`c25d3c989343a7af843ddfaa07187558ecc115c19b100f96d599b296ef203fe9`.
That proves the unversioned PDF endpoint served v2 bytes at the cutoff. It
does not substitute for equation extraction; the equation-level finding above
comes from the official TeX.

## Later primary sources by the author

The official arXiv author feed returned five works. The only two entries later
than the six-vertex v2 update were inspected from their source archives:

1. [Hamiltonian Subgraphs of Order Seven in
   `srg(n,k,1,2)`](https://arxiv.org/abs/2511.06572v1) cites the six-vertex
   paper as prior work. Its TeX contains no occurrence of `m7(n-5)`, `n23`,
   `erratum`, or `correction`.
2. [Nonexistence of `srg(19,6,1,2)`: Combinatorial
   Proof](https://arxiv.org/abs/2511.06569v1) contains no occurrence of the
   six-vertex title or identifier, the equation terms, `erratum`, or
   `correction`.

These checks show only that these two later author sources do not announce or
state the correction. They do not establish that no other communication
exists.

## Bounded correction and publication search

Exact-title, arXiv-identifier, equation-fragment, `erratum`, and `correction`
searches were run, including targeted `arxiv.org`, `auburn.edu`, and
`ejaam.org` queries. No official correction, journal version, institutional
author copy, or primary citing paper with the corrected equation was located.

A ResearchGate preprint listing surfaced during discovery, but it was not
treated as an official correction record and its bytes were not retrieved.
The arXiv Atom record itself has neither a journal reference nor a journal DOI.

Accordingly, the defensible status is:

| Item | Status |
|---|---|
| Current arXiv version | `v2` |
| Omission present in official v1 source | `YES` |
| Omission present in official v2 source | `YES` |
| Later arXiv repair found | `NO` |
| Formal erratum/correction found | `NO` |
| Corrected journal/author version found | `NO` |
| Exact prior primary source stating `+n23` found | `NO` |
| Novelty of the correction | `UNKNOWN` |
| Target resolution | `UNKNOWN` |

Here, every `NO` means "not located within this bounded audit," never a claim
of nonexistence.

## Separation from mathematical verification

The independent Wave 21 verifier reports that the raw equation has residual
exactly `n23` and that adding one deletion card to row `M7` is the unique
one-card repair. This literature agent did not rerun or promote that
mathematical verification. Its narrower contribution is to establish that the
current official source still prints the omission and that no public official
correction was found by the cutoff.

## Retained failures

The companion manifest records all material access and harness failures:

- the web tool rejected an arXiv Atom URL and an ar5iv redirect under its safe
  URL policy; direct official HTTPS retrieval succeeded for the Atom record;
- the first author-feed query used the wrong author syntax and returned zero
  entries; the corrected official query returned five;
- local `pdftotext` and `pypdf` were unavailable, and bundled dependency
  discovery was interrupted;
- the first Atom parser omitted the arXiv namespace; the corrected parse
  confirmed the absent journal reference and DOI.

None of these failures changes the current-version finding. They limit the PDF
content and search-completeness claims exactly as stated above.
