# Wave23 literature-audit preinspection query plan

```yaml
role: literature
frozen_utc: 2026-07-23T19:39:08Z
target: existence of a strongly regular graph with parameters (99,14,1,2)
proof_material_inspected_before_freeze: false
scope:
  - current status of the exact existence problem
  - chronology and strength of prior lower bounds involving Reimbayev's n_3
  - the exact relation between n_3 and the number of induced 6-cycles
  - prior appearance of n_3 >= 708 or induced_C6 >= 209994
  - prior appearance of an endpoint argument using determinant/index constraints,
    a product-of-eigenvalues bound (including Maclaurin/KKT language), and an
    even-unimodular lattice obstruction
non_goals:
  - proving or verifying the Wave23 mathematics
  - claiming exhaustive novelty
  - promoting the target existence status
```

## Source hierarchy

1. Primary papers and their versioned source files: arXiv abstracts, PDFs, and
   TeX source packages for arXiv:2409.10620, arXiv:2308.02978, and
   arXiv:2604.23037.
2. Authoritative parameter tables maintained by A. E. Brouwer, including the
   specific `(99,14,1,2)` entry and linked references.
3. Primary papers/preprints reached from the above sources' reference lists,
   "cited by" trails, or exact-title/author searches.
4. Search-engine result metadata only as a discovery aid. Search snippets are
   not treated as evidence; a claim is counted only when its underlying primary
   or authoritative source is inspected.

## Frozen exact web/search queries

Each query is to be run verbatim where the search interface permits it. Domain
restricted variants may add `site:arxiv.org`, `site:doi.org`, or the Brouwer
table host without changing the quoted terms.

1. `"srg(99,14,1,2)"`
2. `"SRG(99,14,1,2)"`
3. `"strongly regular graph" "99,14,1,2"`
4. `"Conway's 99-graph problem"`
5. `"Conway 99-graph problem" open`
6. `"n_3" "Conway" "99"`
7. `"n3" "Conway" "99-graph"`
8. `"n_3" 705 "strongly regular"`
9. `"n_3" 708 "strongly regular"`
10. `"n3>=708" graph`
11. `"n_3 \\geq 708" graph`
12. `"209991" graph`
13. `"209994" graph`
14. `"209,994" "6-cycles"`
15. `"induced 6-cycles" "99" "strongly regular"`
16. `"determinant" "index" "srg(99,14,1,2)"`
17. `"determinant" "Conway's 99-graph"`
18. `"even unimodular" "Conway 99"`
19. `"Maclaurin" "Conway 99"`
20. `"KKT" "Conway 99"`
21. `"projector lattice" "strongly regular graph" "99"`
22. `"product of eigenvalues" "99-graph"`
23. `"lattice" "srg(99,14,1,2)"`
24. `"Hamiltonian 7-cycles" "Conway 99"`

## Frozen in-document terms

Search all downloaded text/source for:

`99,14,1,2`, `99-graph`, `Conway`, `n_3`, `n3`, `705`, `708`,
`209991`, `209994`, `six-cycle`, `6-cycle`, `induced`, `determinant`,
`index`, `lattice`, `unimodular`, `Maclaurin`, `KKT`, `projector`,
`eigenvalue`, and `Hamiltonian`.

## Claims and verdict categories

The audit will test:

- **S1:** The exact target is the existence of `srg(99,14,1,2)`.
- **S2:** Authoritative current sources still list its existence as open as of
  2026-07-23.
- **S3:** The strongest located prior published/preprint lower bound for
  Reimbayev's `n_3`, with its precise hypotheses and version, is correctly
  identified.
- **S4:** The exact identity converting `n_3` to the induced 6-cycle count is
  correctly quoted or derived from a cited primary source.
- **S5:** Whether any inspected source contains `n_3 >= 708` or
  `induced_C6 >= 209994`.
- **S6:** Whether any inspected source contains the same structural endpoint
  argument as Wave23: determinant/index reduction, exact eigenvalue-product
  bound, and even-unimodular rank/signature obstruction.

Each conclusion must be labeled one of:

- **CONFIRMED:** directly supported by an inspected primary/authoritative
  source.
- **BOUNDED NON-DISCOVERY:** not found in the enumerated queries and inspected
  sources; this is not evidence of global absence.
- **UNKNOWN:** not established by the audit, including all global novelty
  claims.

## Evidence protocol and limitations fixed in advance

- Save versioned source artifacts when the host permits, compute SHA-256, and
  record retrieval UTC, URL, version/date, and local path.
- Record exact queries actually executed and the resulting primary sources
  inspected.
- Inspect source/TeX as well as PDF text when practical, because equations and
  symbols are poorly indexed.
- After this file is written, its SHA-256 is the preinspection freeze. Only
  then may the Wave23 report be opened to compare the exact claim.
- Citation-search coverage, web indexing, and arXiv search are incomplete.
  Therefore a failure to locate the Wave23 numerical bound or argument can
  support only **BOUNDED NON-DISCOVERY**; novelty remains **UNKNOWN**.
