# Wave 24 source-first literature query plan

Frozen before inspecting any Wave 24 discovery report, checker, certificate, or
proof notes.

- Freeze time (UTC): 2026-07-23
- Search cutoff: sources and maintained status pages available through
  2026-07-23
- Target: existence of an `srg(99,14,1,2)` (Conway's 99-graph problem)
- New-result scope supplied to the literature agent: the `n3 = 708`
  index-boundary case, including a bound `det(B) <= 6561 = 3^8`, eight
  surviving index values, and a characteristic-pseudodeterminant/logarithmic
  inequality or an equivalent projector-lattice argument
- Separation rule: the discovery package remains unopened until this plan is
  written. Exact discovery notation may later be mapped onto these already
  frozen search families, but the families and reporting standard will not be
  changed in response to the proof.

## Frozen search families

Each query family will be attempted with ordinary punctuation, TeX-style
subscripts where useful, and at least one problem-identifying term. Generic
numeric searches without a Conway-99, strongly-regular-graph, lattice, or
spectral qualifier are excluded as too noisy.

### A. Current resolution status

1. `"srg(99,14,1,2)"`
2. `"SRG(99,14,1,2)"`
3. `"strongly regular graph" "99,14,1,2"`
4. `"Conway 99 graph problem"`
5. `"Conway's 99-graph problem"`
6. `"99-graph" Conway solved OR counterexample OR existence`
7. `site:arxiv.org "99,14,1,2"`
8. `site:mathscinet.ams.org "99,14,1,2"`
9. `site:zbmath.org "99,14,1,2"`

### B. Exact endpoint and equivalent subgraph count

1. `"n3=708" "99-graph"`
2. `"n_3 = 708" "strongly regular"`
3. `"n3" 708 Conway graph`
4. `"708" "srg(99,14,1,2)"`
5. `"209994" graph`
6. `"209,994" "6-cycles" graph`
7. `"induced 6-cycles" "99-graph"`
8. `"n3" "induced 6-cycles" Reimbayev`

### C. Exact determinant/index boundary

1. `"det(B)" 6561 graph`
2. `"det B" "3^8" lattice`
3. `"6561" "99-graph"`
4. `"6561" "srg(99,14,1,2)"`
5. `"3^8" "srg(99,14,1,2)"`
6. `"3^8" Conway graph lattice`
7. `"index" 6561 "strongly regular graph"`
8. `"index" "3^8" projector lattice graph`
9. `"determinant" 6561 spectral projector graph`

### D. Eight surviving index values

After the controlled proof reveal, transcribe the eight values exactly and
record that transcription in the ledger. For every value `h`, run the frozen
templates below; the substitution does not create a new search family.

1. `"<h>" "srg(99,14,1,2)"`
2. `"h=<h>" "99-graph"`
3. `"index <h>" Conway graph`
4. `"<h>" projector lattice "strongly regular graph"`
5. `"<h>" pseudodeterminant graph lattice`

Also search the entire ordered eight-value list as one quoted string in both
comma-separated and brace notation. A hit on a common integer alone is not
responsive evidence.

### E. Characteristic-pseudodeterminant/log method

1. `"characteristic pseudodeterminant" graph`
2. `"characteristic pseudo-determinant" graph`
3. `"pseudodeterminant" "strongly regular graph"`
4. `"pseudo-determinant" "spectral projector" graph`
5. `"characteristic polynomial" pseudodeterminant lattice graph`
6. `"log determinant inequality" spectral projector lattice`
7. `"logarithmic inequality" determinant "strongly regular graph"`
8. `"sum log" eigenvalues projector lattice determinant`
9. `"det(I+2C)" graph lattice`
10. `"I+2C" determinant "strongly regular"`
11. `"spectral projector" Gram lattice "strongly regular graph"`
12. `"projector lattice" Conway 99 graph`
13. `"integral lattice" spectral idempotent strongly regular graph`
14. `"Smith normal form" spectral projector strongly regular graph`
15. `"index obstruction" strongly regular graph lattice`

### F. Equivalent mathematical concepts

1. determinant bounds from a fixed trace and characteristic polynomial;
2. pseudo-determinants of compressions or restrictions to a codimension-one
   subspace;
3. integral/even lattices obtained from graph eigenspaces or primitive
   idempotents;
4. index divisibility and discriminant-form obstructions for strongly regular
   graphs;
5. logarithmic majorization, Jensen, AM-GM, or tangent-line bounds applied to
   positive eigenvalues of a graph-derived matrix;
6. endpoint equality or near-equality analyses with determinant bound `3^8`;
7. characteristic-polynomial derivative identities for principal
   restrictions/compressions.

Search each concept with at least one of `99-graph`, `srg(99,14,1,2)`,
`strongly regular graph`, or the names of the established Conway-99 sources.

### G. Source and citation traversal

Inspect current versions and bibliographies/citation trails, where accessible,
for:

1. the maintained Brouwer strongly regular graph table entry;
2. Reimbayev's Conway-99 subgraph-count result;
3. Makhnev's exclusion of the zero endpoint;
4. Cesarz and Woldar's current Conway-99 paper;
5. Keramatipour's current preprint/version;
6. Phillips's current thesis;
7. forward citations and later versions exposed by arXiv, DOI/Crossref,
   institutional repositories, Semantic Scholar/OpenAlex, or author pages.

For primary mathematical claims, prefer the paper/preprint/thesis itself.
Maintained tables may support only current status, and search-index snippets
may support only discovery of a source, never a theorem claim.

## Evidence and reporting rules

1. Record the literal query, search surface, retrieval time/date, responsive
   source URLs, and access failures.
2. Record stable provenance identifiers when available: DOI, arXiv identifier
   and version/date, repository handle, thesis record, or maintained-table URL.
   Record checksums only when source bytes are actually obtained. Do not imply
   a checksum for a search snippet or dynamically rendered page.
3. Do not vendor third-party papers, HTML caches, or search-result exports into
   the repository.
4. Separate an exact hit from a conceptual analogue. A concept match is not
   prior art for the Wave 24 result unless its hypotheses and conclusion cover
   the same endpoint and obstruction.
5. A search nonhit is `BOUNDED NON-DISCOVERY`, not proof of novelty.
6. Keep target existence `UNKNOWN` unless an authoritative source gives and
   substantiates a resolution. Keep Wave 24 novelty `UNKNOWN` absent an
   authoritative priority determination.
7. Any chronology claim is limited to the frozen cutoff and named search
   surfaces.

