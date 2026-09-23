# Wave 30 novelty and status audit: frozen protocol

```yaml
role: literature
date_utc: 2026-07-24T04:49:58Z
git_commit: d6fb0ad0b249d089d2709c43f770ecb74ee2faee
claim_label: UNKNOWN
scope: >-
  Independent literature and current-status audit for two exact Wave 30
  signatures: a conditional classification of rootless integrally
  orthogonally decomposable h=729 endpoint S-forms, and an exact bare
  rank-20/rank-44 lattice construction. This role does not verify either
  mathematical result and does not claim novelty, n3=708, or a Conway-99
  resolution.
inputs:
  agents/2026-07-24-wave30-general-h729.md:
    sha256: 1bc63f569600bca88e12c977a0bd94ecdd03aa5f3fd8c4f203d4778fbec78efa
  attempts/wave30-general-h729/run-report.yaml:
    sha256: 77232c06827c4c62e7dc6f5380cc4ebe2a3c6d5496fe8c3592589986089e416f
  attempts/wave30-general-h729/exact-results.json:
    sha256: 93cc1633d0b25d5f3daecd4c49cbc3b2dc3f754576a3cd5c9364c729a79a7698
  verification/wave30-general-h729/audit.md:
    sha256: b1eb875095c7f7e81752b1c0dc5d28234f52be86b0913389eff446a3e9ae35ff
  verification/wave30-general-h729/run-report.yaml:
    sha256: a7a7394b2ad641632e5fde8ba9a8b440120ad7e39b30ac31fcfb535ede4505ca
  agents/2026-07-24-wave30-h729-construction.md:
    sha256: 479ed105825ea2b2a0802c34fcc332b8dc1420b27966bec41053702f3212451f
  attempts/wave30-h729-construction/run-report.yaml:
    sha256: bfe878cc209ec0699310bb81fd25f720babc73a9ccb326aa660c323629e53dcd
  attempts/wave30-h729-construction/exact-results.json:
    sha256: 0d3723ba4c185dc7865858d16bfc6ada99fd87b4e21da616ef1b1d1ad6b67e11
  verification/wave30-h729-construction/audit.md:
    sha256: b5511b585e8a3bb401f224e0e0a09f76378fdc9c21b929b428972d5e4f4d8b01
  verification/wave30-h729-construction/run-report.yaml:
    sha256: 31c676899531e21dfcf958ba84c8f90cd65fef446c916ee7344d03061bede359
limitations:
  - A finite search cannot prove novelty or certify global openness.
  - Index coverage, terminology, language, access, and posting delays may hide relevant work.
  - No downloaded paper, raw HTML, or raw API response will be retained.
```

## 1. Signature A frozen before searching

Assume the full frozen `n3=708` projector/Schur endpoint package and let
`S` be an even positive-definite integral rank-44 form with

```text
det(S)=729,
min(S)>=4,
S integrally orthogonally decomposable.
```

The exact conditional structural theorem to search is:

```text
S = A20 orthogonal_sum U24,
rank(A20)=20,       det(A20)=729,
rank(U24)=24,       det(U24)=1,
rows=(105,126),
tr(B_A),tr(B_U)=(36,24),
B_U=I24.
```

Here `A20` is merely a label for the determinant-729 rank-20 block, not the
ADE root lattice customarily denoted `A_20`; `U24` is rootless, even, and
unimodular. The identifying derivation signature is:

1. minimum-four direct-sum support forces block-supported integral frame rows;
2. every block rank is divisible by four and has `21*rank/4` rows;
3. `det(Q)=5`, so one block has determinant-five `Q` and the remaining
   `Q`-blocks are even unimodular;
4. rank/signature and odd-determinant congruences leave fifteen aggregate
   `(rank, v_3(det(S_block)))` types;
5. blockwise cubic row residues make the block traces positive multiples of
   six;
6. exact AM-GM, integral characteristic-pseudodeterminants, logarithmic
   determinant caps, and the equality/idempotent even-unimodular rank veto
   exclude fourteen types;
7. only `(rank,v_3(det))=(20,6)` survives, and equality forces `B_U=I24`.

The additional surviving-block row fingerprint is:

```text
c_i in {9,10,11},
n9=n11+4,
n10=122-2*n11,
0<=n11<=61.
```

This is a conditional classification, not a construction or exclusion of the
last type, rooted or indecomposable forms, `n3=708`, or Conway-99.

## 2. Signature B frozen before searching

The exact construction target is a rank-20 rootless even lattice `T20`
obtained from

```text
K12 orthogonal_sum E8
```

by five explicit 2-neighbor steps, with:

```text
rank(T20)=20,
det(T20)=729,
min(T20)=4,
number of norm-four vectors=5076,
3*T20^(-1) even integral,
21*T20^(-1) even integral,
canonical Gram SHA-256=
  1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6.
```

The root-count fingerprint along the neighbor route is:

```text
240 -> 112 -> 48 -> 20 -> 6 -> 0.
```

Its bare rank-44 extension is:

```text
S44 = T20 orthogonal_sum Leech,
G44 = 21*S44^(-1),
rank(S44)=44,
det(S44)=729,
min(S44)=4,
S44*G44=21*I44,
S44 and G44 even integral positive definite.
```

This supplies no determinant-five `Q`, compatible `B`, 105/126 tight frames,
`X`, `M`, `W`, Schur identity, graph, or endpoint realization.

## 3. Verifier provenance wall

The local verifier record is context, not literature evidence:

- the structural implication in Signature A was independently reconstructed
  and labelled `VERIFIED`;
- publication of its submitted discovery package was nevertheless `VETOED`
  because the submitted replay freezes a stale Wave-29 audit hash and runs
  zero tests before failing;
- Signature B's exact bare construction and rank-44 `S/G` package were
  independently labelled `VERIFIED` with narrow scope.

This literature role neither repairs the veto nor promotes either theorem.
The veto must remain visible even if no prior-art match is found.

## 4. Pre-registered search lanes

1. **Exact structural signature:** rootless decomposable rank-44 determinant
   729 lattices, rank `20+24`, determinant `729*1`, shell rows `105+126`,
   traces `36/24`, and fourteen-of-fifteen type exclusions.
2. **Endpoint/frame language:** Conway-99, `srg(99,14,1,2)`, Euclidean
   representations, integral tight frames, projectors, Schur/Hadamard
   squares, cubic moments, and `h=729`.
3. **Construction identity:** rank-20 determinant-729 rootless or
   3-modular lattices, minimum four, kissing number 5076, and the exact Gram
   hash.
4. **Neighbor route:** Kneser 2-neighbors of `K12 orthogonal_sum E8`, the
   five-step root-count sequence, genus/spinor-genus/classification tables,
   and theta series.
5. **Alternate modular/design terminology:** strongly modular, level three,
   dual-integral, theta series, spherical designs, harmonic theta series,
   shells, eutaxy, frames, and even-unimodular rank-24 complements.
6. **Standard ingredients:** primary or authoritative sources for Kneser
   neighbors, `K12`, the Leech lattice, even/strongly modular lattice
   classifications, tight frames, and lattice designs.
7. **Current target status:** recent primary articles, preprints, corrections,
   and institutional records concerning existence of
   `srg(99,14,1,2)`.

## 5. Evidence and retention policy

- Prefer original papers, journal/publisher or DOI records, arXiv records,
  institutional repositories, and author-maintained mathematical catalogues.
- Search snippets are discovery aids only.
- Inspect actual abstracts, theorem statements, tables, or catalogue metadata
  where access permits.
- Record every query string, service, batch, disposition, access failure,
  source title, authors, stable URL/DOI, and the exact claim supported.
- Retain metadata and concise paraphrases only; save no PDF, raw HTML, XML
  feed, or raw API response.
- An index zero or no-hit query is not evidence of nonexistence or novelty.
- The strongest permissible negative conclusion is:

  > No exact prior result was found in the sources searched as of 2026-07-24.

Novelty, the global Conway-99 status, and both broader mathematical outcomes
remain `UNKNOWN`.
