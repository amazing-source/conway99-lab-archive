# Wave 29 novelty/status audit: frozen protocol

```yaml
role: literature
date_utc: 2026-07-24T03:43:22Z
git_commit: 74b6f3adcee19ca2b0480258bb7bf51198bd085a
claim_label: UNKNOWN
scope: >-
  Literature and status audit for one exact result: exclusion of
  S0=K12 orthogonal_sum LAMBDA(F) as the S-form of the frozen full
  n3=708 projector/Schur endpoint package.
inputs:
  agents/2026-07-24-wave29-s0-frame-exclusion.md: e6ae61331a54d53f2a98712296ebac855f45b46de32ff2ec4d85018f2d8a5045
  attempts/wave29-s0-frame-exclusion/run-report.yaml: 91fba9dad3bb9d906eb69c06ca97be82ff804296dcb010be3f6749e67beba286
  attempts/wave29-s0-frame-exclusion/exact-results.json: 7a85c5321b5e91365c246dff7bae9264cc82494da5c866b1b351511099f6638c
  verification/wave29-s0-frame-exclusion/protocol-freeze.md: 8ab139038fa6792cd9abad0030a0ee17f8cb5cd6eee749a312e2d13a0abd5e30
  verification/wave29-s0-frame-exclusion/audit.md: 4101a394252807fb9de8c39fb32b780bc88410d99e47dfe698da251b49f3e061
limitations:
  - The search cannot prove novelty or openness.
  - Bibliographic discovery depends on indexing, terminology, and source access.
  - No downloaded paper, raw HTML, or raw API response will be retained.
```

## 1. Exact formulation frozen before searching

The literature target is the following single-lattice non-realizability
statement.

Let

```text
S0 = K12 orthogonal_sum LAMBDA(F),
```

where `K12` is the rank-12 Coxeter-Todd lattice and `LAMBDA(F)` is the
rank-32 extremal even unimodular lattice represented by the frozen Wave 28
Gram matrix. There is no full `n3=708` endpoint package with this exact
`S`-form:

```text
X in Z^(231 x 44), full column rank
G = X^T X
S = 21 G^(-1) = S0
M = X S X^T
W = M hadamard_product M
Q = X^T W X
B = S Q = I + 2 C
```

subject to the frozen endpoint conditions, including

```text
M 1 = 0
diag(M) = 4
offdiag(M) in {0,1,-1,-2}
S and Q even positive-definite integral
B integral and positive for the G-inner product
tr(B) = 60
det(B) <= 6525
det(Q) >= 5 and det(Q) = 1 mod 4.
```

The identifying proof signature is:

1. minimum-four orthogonal support splits the 231 rows as `63+168`;
2. `M,W,Q,B` inherit the two blocks;
3. determinant arithmetic and the impossibility of an even positive-definite
   unimodular rank-12 lattice force
   `det(Q_K),det(Q_L)=(5,1)` and `det(B_K),det(B_L)=(3645,1)`;
4. the row alphabet and `M^2=21M` make both block traces positive multiples
   of six, while AM-GM forces `tr(B_K),tr(B_L)=(24,36)`;
5. for the integral, self-adjoint
   `C_K=(B_K-I_12)/2`, characteristic-pseudodeterminant integrality and
   the pointwise inequality

   ```text
   log(1+2x)
     <= x log(3) - (log(3)-2/3) log|x|,
   x > -1/2, x != 0,
   ```

   give `det(B_K)<=3^6=729`, contradicting `det(B_K)=3645`.

This exact combination, not any ingredient in isolation, is the novelty
question.

## 2. Claims explicitly outside the audit target

The candidate does **not** claim:

- exclusion of any other determinant-729 rank-44 lattice;
- exclusion of every `h=729` endpoint form;
- `n3>=709`;
- construction or nonexistence of `srg(99,14,1,2)`;
- a resolution of the Conway 99-graph problem;
- a classification of Coxeter-Todd or rank-32 unimodular lattices;
- novelty, publication, or external peer review.

The global target and every broader endpoint class remain `UNKNOWN`.

## 3. Pre-registered search lanes

Searches will be logged before their results are interpreted.

1. **Exact object pair:** `K12`, `Coxeter-Todd`, `Lambda(F)`,
   `Koch-Venkov`, orthogonal/direct sums, rank 44, determinant 729.
2. **Numerical fingerprints:** `231`, `44`, `63`, `168`, `3645`, `729`,
   trace `24/36`, and rank-12/rank-32 block decompositions.
3. **Endpoint language:** Conway 99, `srg(99,14,1,2)`, Euclidean
   representations, integral tight frames, projectors, Hadamard/Schur
   squares, and cubic moments.
4. **Final obstruction:** characteristic pseudodeterminants, integral
   matrix spectra, determinant-vs-trace inequalities, and the displayed
   logarithmic inequality under alternate notation.
5. **Standard ingredients:** primary or authoritative sources for the two
   lattices, the even-unimodular signature restriction, tight frames,
   strongly regular graph eigenspace representations, and lattice shells.
6. **Current target status:** recent primary articles/preprints that state
   whether the exact Conway 99-graph existence problem is open or resolved.

## 4. Evidence and retention policy

- Prefer journal/publisher pages, DOI records, arXiv records, institutional
  archives, author-maintained mathematical catalogues, and original papers.
- Search snippets are discovery aids, not theorem evidence.
- A source supports only claims visible in its inspected metadata, abstract,
  or theorem statement.
- Record query text, date, service, result disposition, source title,
  authors, stable URL/DOI, and access limitation.
- Retain metadata and concise paraphrases only. Do not save raw HTML, API
  responses, PDFs, or copyrighted paper text.
- A no-hit query is not evidence of nonexistence or novelty.
- The strongest permissible negative conclusion is:
  “No exact prior result was found in the sources searched as of
  2026-07-24.”
