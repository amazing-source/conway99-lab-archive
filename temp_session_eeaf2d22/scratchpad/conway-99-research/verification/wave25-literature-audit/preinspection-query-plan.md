# Wave 25 source-first literature and novelty audit: frozen query plan

Frozen at: 2026-07-23T21:49:09Z

## Separation and scope

This plan was written before opening any Wave 25 discovery, proof, certificate,
test, or verifier artifact.  The auditor has only the independently supplied
claim synopsis below.  Search results will not be used to validate the proof;
they address only target status, chronology, attribution, and novelty.

Exact target context:

- the existence problem for `srg(99,14,1,2)`, also called the Conway 99-graph
  problem;
- the boundary case `n3 = 708`;
- an equality-case argument involving an integral self-adjoint idempotent and
  an integral orthogonal splitting;
- an even-unimodular positive-definite rank-36 obstruction;
- the claimed sharpened determinant ceiling `det(B) <= 6525`; and
- the same eight surviving index values
  `{9,21,49,81,189,441,729,1029}`.

The target existence status and the novelty of the exact refinement both start
as `UNKNOWN`.  Failure to find a match in the frozen searches below will be
reported only as bounded non-discovery.

## Source hierarchy

1. Primary mathematical papers and author-hosted manuscripts.
2. Current authoritative problem/status databases and authors' research pages.
3. Publisher and bibliographic records used only to locate primary texts.
4. Secondary expositions used only for terminology or citation discovery.

Search snippets, model-generated summaries, social posts, and solver exit codes
are never evidence for a theorem or for novelty.  A source counts as an exact
match only if its full text or authoritative record explicitly connects the
claimed method or numerical result to `srg(99,14,1,2)`.

## Frozen query families

The following 30 queries are fixed before inspection.  Harmless syntax changes
forced by a search engine will be logged, not silently substituted.

### A. Exact target and numerical fingerprints

1. `"srg(99,14,1,2)" "n3" 708`
2. `"strongly regular graph" "99,14,1,2" 708`
3. `"Conway 99 graph" 708 determinant`
4. `"Conway 99-graph" "det(B)"`
5. `"srg(99,14,1,2)" "6525"`
6. `"Conway 99 graph" "6525"`
7. `"det(B) <= 6525" graph`
8. `"det B" 6525 lattice graph`
9. `"9,21,49,81,189,441,729,1029"`
10. `"1029" "729" "441" "strongly regular"`

### B. Exact equality-case mechanism in target context

11. `"srg(99,14,1,2)" "even unimodular"`
12. `"Conway 99 graph" "even unimodular"`
13. `"99,14,1,2" "rank 36" lattice`
14. `"99,14,1,2" "integral idempotent"`
15. `"Conway 99 graph" "integral idempotent"`
16. `"Conway 99 graph" "orthogonal split" lattice`
17. `"n3=708" "even unimodular"`
18. `"n_3=708" strongly regular`
19. `"rank 36" "det(B)" idempotent`
20. `"rank 36" "self-adjoint idempotent" lattice`

### C. Current status and chronology

21. `"strongly regular graph (99,14,1,2)" existence`
22. `"Conway's 99-graph problem" open`
23. `"99-graph problem" Conway strongly regular latest`
24. `site:win.tue.nl strongly regular 99 14 1 2`
25. `site:arxiv.org "99,14,1,2" strongly regular`

### D. Conceptual prior art, searched independently

26. `"integral idempotent" orthogonal decomposition lattice`
27. `"integral self-adjoint idempotent" lattice`
28. `positive definite even unimodular lattice rank divisible by 8`
29. `"rational idempotent" lattice projector Gram matrix`
30. `Bacher Venkov rational idempotent lattices`

## Inclusion, exclusion, and adjudication

- Record every frozen query, engine, UTC time, result count when exposed, and
  the URLs actually inspected.
- Preserve null results and access failures.
- Record a distinct ledger entry when following a citation from a result.
- For exact-match adjudication, require all of: target context, the specific
  boundary or determinant conclusion, and a materially matching mechanism.
- A source giving only the divisibility-of-rank theorem for even unimodular
  lattices is conceptual prior art, not an exact target match.
- A source discussing rational projector/idempotent lattices without the
  Conway-99 boundary calculation is conceptual prior art.
- A database saying the graph is unknown establishes only that database's
  recorded status and date; it does not prove nonexistence of later work.
- A purported resolution is not accepted from an abstract or snippet alone.
  The proof-bearing primary text and its exact statement must be inspected.
- No conclusion about the mathematical correctness of Wave 25 will be drawn
  from this audit.

## Planned outputs

- `source-query-ledger.json`: machine-readable query and inspection record.
- `2026-07-23-wave25-literature-audit.md`: source-first findings and limits.
- `run-report.yaml`: protocol-compliant run summary.
- `publication-hashes.sha256`: hashes of publishable audit artifacts.
