# Wave 30 independent novelty and status literature audit

## Verdict

```text
exact prior result matching Signature A:  NOT FOUND IN SEARCHED SOURCES
exact prior result matching Signature B:  NOT FOUND IN SEARCHED SOURCES
novelty of either result:                  UNKNOWN
global Conway-99 status:                  UNKNOWN
literature claim label:                   UNKNOWN
```

The strongest justified negative statement is:

> No exact prior result was found in the sources searched as of 2026-07-24.

This is a bounded non-discovery, not a proof of novelty, priority, or global
openness. The two exact targets were frozen in `protocol-freeze.md` before
searching. In particular, `A20` in Signature A is a local label for a
rank-20 determinant-729 block, not the ADE root lattice `A_20`.

## 1. Exact signatures audited

Signature A is the conditional classification that every rootless, even,
positive-definite, integral, integrally orthogonally decomposable rank-44
determinant-729 endpoint form carrying the full frozen `n3=708`
projector/Schur package reduces to

```text
A20 orthogonal_sum U24,
determinants 729 and 1,
row split 105 and 126,
block traces 36 and 24,
B_U=I24,
```

with fourteen of fifteen aggregate rank/determinant types excluded and the
surviving rank-20 row-profile equations recorded in the protocol.

Signature B is the exact rank-20 rootless even lattice `T20` obtained by five
2-neighbors from `K12 orthogonal_sum E8`, with

```text
det(T20)=729,
min(T20)=4,
5076 norm-four vectors,
3*T20^(-1) and 21*T20^(-1) even integral,
root counts 240 -> 112 -> 48 -> 20 -> 6 -> 0,
Gram SHA-256
1890fe1973eed47850c307d0975ae393f2a8ab32a9d0b16b35ebcab7012445d6,
```

and its bare direct sum with the Leech lattice. Signature B expressly lacks
the determinant-five `Q`, compatible `B`, tight frames, `X`, `M`, `W`, Schur
identity, and graph realization needed for the endpoint problem.

## 2. Search coverage

The query ledger records 96 exact query strings in 24 batches:

| Service | Queries | Per-query limit or coverage |
|---|---:|---|
| Web search | 80 | Interactive ranked results; snippets used only for discovery |
| arXiv API | 8 | `max_results=5`; titles/abstract metadata inspected |
| OpenAlex API | 4 | `per-page=5`; metadata only |
| Crossref API | 4 | `rows=5`; metadata only; one query returned HTTP 429 |

The lanes covered exact numeric fingerprints, lattice and modular-lattice
terminology, theta series, 3-elementary and level-three terminology, Kneser
neighbors and the five-step root-count route, spherical designs, tight
frames, Euclidean graph representations, Schur/Hadamard squares, the exact
Gram hash, and current `srg(99,14,1,2)` records.

The arXiv queries for `5076` plus lattice, determinant 729 plus lattice, the
`K12`/`E8` neighbor combination, and rank-20 level-three lattices returned
zero indexed matches. OpenAlex returned zero for its four corresponding
metadata queries. Those index results are logged but are not evidence of
novelty. Three broad Crossref queries returned enormous generic result counts
whose leading records were irrelevant; the `K12 E8 neighbor lattice` query
was rate-limited and is recorded as an access failure, not a no-hit.

No raw PDF, raw HTML, XML feed, or API response is retained. The retained
objects are query strings, limits, source metadata, concise paraphrases,
access failures, and exact claim boundaries.

## 3. Signature B: strongest nearby lattice sources

### 3.1 Standard construction and classification context

Kneser's 1957 paper and Voight's modern survey supply the standard
neighbor-method context. Plesken and Pohst construct integral laminated
lattices with prescribed minimum, while Scharlau and Hemkemeier give broader
integral-lattice classification context. None of the inspected metadata,
abstracts, catalogue cross-references, or theorem-level descriptions states
the exact five-neighbor route, root sequence, final Gram, or shell count.

The Nebe-Sloane catalogue is broad and useful but explicitly warns that not
all entries have been checked. Its approximately 160,000 entries therefore
cannot certify novelty or completeness. No `5076` entry was found in its
searched index. Two standard rank-20 minimum-four near controls differ
decisively:

| Lattice | Rank | Determinant | Minimum | Kissing number | Match? |
|---|---:|---:|---:|---:|---|
| `KAPPA20` | 20 | 81 | 4 | 15390 | No |
| `LAMBDA20` | 20 | 64 | 4 | 17400 | No |
| frozen `T20` | 20 | 729 | 4 | 5076 | Target |

The catalogue's `K12`, `E8`, and Leech records corroborate the standard
ingredient invariants only. They do not identify the neighbor route or `T20`.

### 3.2 The 3-elementary near hit

Boecherer and Nebe, *On theta series attached to maximal lattices and their
adjoints* (arXiv:0909.1184; JRMS 25 (2010), 265-284), is the strongest
conceptual near hit. Its abstract fixes maximal even lattices of exact level
`N` and determinant `N^2`. At `N=3`, that is determinant 9, not determinant
729. Its rank-20 dual-extremal 3-elementary uniqueness statement is in a
different genus, and the displayed full-genus class-number field is not a
completed classification count. It neither gives the `5076` shell nor the
five-neighbor genealogy.

The distinction between terminology is material. A genuinely 3-modular
rank-20 lattice has determinant `3^10`; the frozen `T20` has determinant
`3^6`. The verified scaled-dual integrality conditions do not by themselves
supply a similarity with the dual. The audit therefore did not inflate
`T20` into a 3-modular classification claim.

### 3.3 Construction conclusion

No inspected source matched all or a substantial identifying combination of:

```text
rank 20 + determinant 729 + minimum 4 + kissing number 5076,
five 2-neighbors from K12 orthogonal_sum E8,
240 -> 112 -> 48 -> 20 -> 6 -> 0,
the exact Gram hash,
the two scaled-dual integrality conditions.
```

That non-discovery is bounded by the coverage limitations in Section 7.

## 4. Signature A: frame, design, and graph near hits

Delsarte-Goethals-Seidel and Benedetto-Fickus provide foundational spherical
design and finite normalized tight-frame theory. They do not contain the
rank-44 determinant-729 decomposition, 105/126 rows, 36/24 traces,
determinant-five allocation, `B_U=I24`, or fourteen-type exclusion.

The strongest Conway/frame near hit is Greaves, Iverson, Jasper, and Mixon,
*Frames over finite fields: Equiangular lines in orthogonal geometry*
(arXiv:2012.13642; LAA 639 (2022), 50-80; DOI
`10.1016/j.laa.2021.11.024`). Its Example 5.5 associates a hypothetical
Conway graph with a `(2,1,4)` equiangular tight frame of 100 vectors over
`F_5^45`. That is finite-field, 100-by-45 data, not the real/integral
231-row rank-44 projector and lattice package in Signature A.

Exact searches for `M^2=21M`, `231 44 105 126`, `B_U=I`, `det(Q)=5`, the
rank split, trace pair, and fourteen-of-fifteen exclusion found no exact
result. No inspected paper, catalogue record, or current preprint stated the
conditional classification.

## 5. Current Conway-99 records

Several current primary sources still discuss existence as unresolved:

- Cesarz and Woldar, *Algebraic Combinatorics* 8(2) (2025), DOI
  `10.5802/alco.418`, explicitly describe existence as an elusive open
  problem while deriving conditional automorphism restrictions.
- Keramatipour, arXiv:2604.23037v2 (April 2026), reports SAT approaches that
  do not resolve the finite search.
- Ibrahim, LaFayette, and McCall, *Australasian Journal of Combinatorics*
  93(1) (2025), treat the putative graph conditionally.
- Reimbayev, arXiv:2409.10620 / DOI `10.62780/ejaam/2024-001`, derives
  structural bounds for the parameter family without construction or
  nonexistence.

A June 2026 Hebei Normal University seminar notice concerns nonexistence of
`srg(85,14,3,2)` and mentions only a possible similar approach to
`srg(99,14,1,2)`. It is corroborating institutional context, not literature
evidence for a Conway-99 theorem.

Together these sources support the narrower report:

```text
no current Conway-99 resolution was found in this search.
```

They do not make a finite literature search globally complete. The global
status field therefore remains `UNKNOWN`, rather than being promoted by
absence of a found resolution.

## 6. Verifier provenance wall

The local verifier record is provenance, not literature evidence.

At the pre-search freeze, the structural audit bytes had SHA-256
`b1eb875095c7f7e81752b1c0dc5d28234f52be86b0913389eff446a3e9ae35ff`.
During this audit, the independent verifier package was concurrently
completed. At the report-time snapshot, HEAD was
`5a5eebfc888d7e3f278390a165de66b0c07235b4`, and the relevant verifier
records were:

```text
ffe5b103d60a9a4d26fc00c7012113adf7e4c0db4e0dea6551bf8a7dc0c95178
  verification/wave30-general-h729/audit.md
3a4097668c9f2ebaa13c5dc088215f418969395e042353aad1256d10e8ad4c21
  verification/wave30-general-h729/run-report.yaml
abba8583533a3ccafe774d7a5b5760a0f76eb23c6427642476a3496c1662fb5c
  verification/wave30-h729-construction/audit.md
e9acd34f333a2a26467f27ca3e360604f722a2c1ae7fc0edb2988ad6304d2c7f
  verification/wave30-h729-construction/run-report.yaml
```

The structural verifier's semantic wall at that snapshot is:

```text
scoped conditional mathematical classification:  VERIFIED
submitted discovery replay:                        FAIL
publication of submitted package as-is:            VETOED
required repair and independent reverification:    OUTSTANDING
```

The construction verifier's narrow wall is:

```text
exact bare T20 construction:       VERIFIED
exact bare rank-44 S/G package:    VERIFIED
five-neighbor route classification: NOT CLAIMED
Q, B, frame, X, M, W, graph:        NOT CONSTRUCTED
Conway-99 and novelty:               UNKNOWN
```

No literature result can repair a replay failure, and no literature no-hit
can promote a mathematical claim. This audit did not modify either verifier
package and preserves the publication veto.

## 7. Coverage limits and failure discipline

This audit did not comprehensively cover Google Scholar, MathSciNet, zbMATH,
all citation networks, non-English work, books without indexed metadata,
unpublished manuscripts, newly posted material, or every theorem inside every
paper. Search-engine ranking and index terminology can suppress relevant
work. One Crossref query was rate-limited, several DOI or publisher opens
failed, and the ScienceDirect page for the finite-field-frame paper returned
an access error; alternate authoritative metadata was used where available.

The following were deliberately excluded as evidence:

- a self-published Preprints.org item with internally inconsistent
  even-unimodular rank claims;
- a self-published numerology page reached through numeric fingerprints; and
- generic numeric search hits and snippets.

Absence from an index, catalogue, or returned result window is not evidence
of nonexistence. No complete lattice-genus enumeration or complete
bibliographic universe was audited.

## 8. `SOURCES.bib` mapping

Existing repository keys cover:

```text
Voight2024Kneser
NebeSloaneK12
NebeSloaneE8
NebeSloaneModularLattices
ConwaySloane1983CoxeterTodd
DelsarteGoethalsSeidel1977
BenedettoFickus2003
CesarzWoldar2025
Keramatipour2026
IbrahimLaFayetteMcCall2025
Reimbayev2024
HebeiShpectorov2026
```

Metadata inspected in this audit but absent from `SOURCES.bib` at report time
includes Kneser 1957, Plesken-Pohst II, Scharlau-Hemkemeier, the catalogue
index and its KAPPA20/LAMBDA20/Leech pages, Boecherer-Nebe,
and Greaves-Iverson-Jasper-Mixon. The exact mapping for all 21 records is in
`source-metadata.json`. This read-only audit makes no central bibliography
edit.

## 9. Final bounded conclusion

Neither frozen signature was located under the searched lattice, modular,
theta-series, neighbor, frame, design, projector, and Conway-99 terminology.
The current literature records inspected also supplied no Conway-99
construction or nonexistence theorem.

The audit therefore records:

```text
NO_EXACT_PRIOR_RESULT_FOUND_IN_SEARCHED_SOURCES
```

and nothing stronger. Novelty, priority, the global status of Conway-99, the
remaining decomposition type, the full endpoint, and `n3=708` remain
`UNKNOWN`. The structural discovery package remains under the verifier's
recorded publication veto until repair and independent reverification.
