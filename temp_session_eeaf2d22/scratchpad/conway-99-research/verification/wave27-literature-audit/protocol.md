# Wave 27 statement and literature audit: frozen protocol

Frozen at: 2026-07-24T00:23:20Z  
Repository commit observed before the search: `2ac11809fafee7ab752965ae49a96e922859b5ee`

This protocol was written before opening any Wave 27 discovery, proof,
construction, verification, or overlap-analysis prose or code.

## Questions frozen for audit

- **A. Conway-99:** current status of a strongly regular graph with parameters
  `srg(99,14,1,2)`, including an exact construction, an impossibility proof, or
  an authoritative statement that the problem remains open.
- **B. E6 integral optimization:** even positive-definite integral Gram matrices
  related to the `E6` root lattice and its scaled dual; in particular, direct
  precedent for minimizing `tr(E6 Q)` subject to `Q` even integral positive
  definite and `E6 Q ≡ I (mod 2)`.
- **C. E6 frames/tensors:** integer or rational tight frames on `E6`, third
  moments or symmetric cubic tensors, tensor parity cosets, and obstructions to
  orthogonal `E6` summands.
- **D. A6 analogue:** the corresponding tight-frame, cubic-tensor, parity, or
  orthogonal-summand obstruction for `A6`.
- **E. lattice-complement comparison:** precedent comparing
  `E8^4 ⊥ E6^2` with `E8^5 ⊥ A2^2`, especially by discriminant forms and root
  systems.

The string `21E6^{-1}` in the assignment is treated conservatively: searches
include literal/typographic variants of a factor-2 scaled inverse/dual, without
silently fixing an intended notation.

## Classification vocabulary

- **EXACT:** the source states or proves the same mathematical assertion.
- **NEAR-DIRECT:** the source studies the same object and invariant with only a
  small, explicit mismatch.
- **CONCEPTUAL:** the source supplies a method or general theorem but does not
  state the target assertion.
- **BOUNDED NON-DISCOVERY:** no qualifying hit appeared within this protocol;
  this is not evidence of nonexistence or novelty.

Claims about novelty, priority, or first discovery remain **UNKNOWN** unless a
direct, authoritative source establishes them. Search-engine snippets, model
judgment, and absence from the bounded result set cannot establish priority.

## Source policy

Technical claims will be supported only by primary or authoritative sources:
original papers/preprints, authors' manuscripts, official problem statements,
standard reference tables maintained by subject experts, or publisher/DOI
records used only for bibliographic facts. Secondary pages may be recorded as
leads but not used as technical evidence. Candidate sources are checked by
title/abstract/full text when accessible. Chronology uses the earliest
verifiable public version and records later publication separately.

## Frozen discovery queries

For Crossref, OpenAlex, and zbMATH, inspect at most the first 10 records returned
per query in the service's default relevance order. For arXiv, inspect at most
the first 10 records in relevance order. For general web search, inspect only
the first returned results page exposed by the search tool, with no more than
10 results reviewed per query. Duplicate records count once as sources but each
executed query remains in the ledger.

### Crossref (C01-C10)

1. `C01` — `"strongly regular graph" 99 14 1 2 Conway`
2. `C02` — `"Conway's 99-graph problem"`
3. `C03` — `"E6 lattice" even dual`
4. `C04` — `"E6" trace integral quadratic form congruence`
5. `C05` — `"tight frame" E6 lattice rational`
6. `C06` — `"third moment" E6 lattice tensor`
7. `C07` — `"tight frame" A6 lattice`
8. `C08` — `"cubic tensor" A6 lattice`
9. `C09` — `"E8" "E6" discriminant form orthogonal complement`
10. `C10` — `"E8" "A2" discriminant form root lattice`

### OpenAlex (O01-O10)

1. `O01` — `"strongly regular graph" 99 14 1 2 Conway`
2. `O02` — `"Conway 99-graph"`
3. `O03` — `"E6 lattice" "scaled dual"`
4. `O04` — `"E6 lattice" trace even integral`
5. `O05` — `"tight frames" E6 lattice`
6. `O06` — `"third moments" E6 lattice tensor`
7. `O07` — `"tight frames" A6 lattice`
8. `O08` — `"symmetric cubic tensor" A6 lattice`
9. `O09` — `"E8" "E6" discriminant forms`
10. `O10` — `"E8" "A2" root lattice orthogonal complement`

### zbMATH Open (Z01-Z10)

1. `Z01` — `srg(99,14,1,2)`
2. `Z02` — `"99-graph" Conway`
3. `Z03` — `E6 lattice scaled dual`
4. `Z04` — `E6 trace even integral quadratic form`
5. `Z05` — `tight frame E6 lattice`
6. `Z06` — `third moment E6 tensor`
7. `Z07` — `tight frame A6 lattice`
8. `Z08` — `cubic tensor A6 lattice`
9. `Z09` — `E8 E6 discriminant form`
10. `Z10` — `E8 A2 discriminant form`

### arXiv (X01-X05)

1. `X01` — `all:"strongly regular graph" AND all:"99" AND all:"14"`
2. `X02` — `all:"E6 lattice" AND (all:"scaled dual" OR all:"trace")`
3. `X03` — `all:"E6 lattice" AND (all:"tight frame" OR all:"third moment" OR all:"cubic tensor")`
4. `X04` — `all:"A6 lattice" AND (all:"tight frame" OR all:"cubic tensor")`
5. `X05` — `(all:"E8" AND all:"E6" AND all:"discriminant form") OR (all:"E8" AND all:"A2" AND all:"orthogonal complement")`

### General web (G01-G10)

1. `G01` — `"srg(99,14,1,2)"`
2. `G02` — `"Conway 99-graph" OR "Conway's 99-graph"`
3. `G03` — `"E6 lattice" ("scaled dual" OR "2E6 inverse" OR "2 E6^-1")`
4. `G04` — `"tr(E6 Q)" OR ("E6 Q" "mod 2" "even integral")`
5. `G05` — `"E6 lattice" ("tight frame" OR "rational frame")`
6. `G06` — `"E6" ("third moment" OR "symmetric cubic tensor" OR "tensor parity coset")`
7. `G07` — `"A6 lattice" ("tight frame" OR "rational frame")`
8. `G08` — `"A6" ("third moment" OR "symmetric cubic tensor" OR "tensor parity coset")`
9. `G09` — `"E8^4" "E6^2" lattice`
10. `G10` — `"E8^5" "A2^2" lattice`

## Follow-up and stopping rules

Exact-title, DOI, author-site, journal, and cited-reference retrieval is allowed
only to authenticate or read a candidate already exposed by the frozen queries
or an authoritative source's bibliography. Such retrievals are logged with
`R` identifiers and are not new discovery queries. No synonym expansion or
additional discovery query will be introduced after the freeze. Each theme is
reported even if it yields no relevant record. A failed endpoint, inaccessible
full text, ambiguous notation, or incomplete index coverage is retained in
`failures.md`.

Only after the search ledger and source classification are substantially
complete may Wave 27 artifacts be opened, and then solely to classify overlap
against this independently assembled literature map.
