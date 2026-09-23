# Wave 26 literature audit: failures and limitations

## Service and query limitations

- Crossref completed 23 of 28 frozen requests with HTTP 200. Q10, Q14, Q15,
  Q19, and Q24 were rate-limited with HTTP 429. The other databases and
  supplementary searches partly cover those strings, but this is not a full
  substitute.
- OpenAlex completed all 28 requests with HTTP 200. Eighteen queries returned
  zero records in its first-20 relevance interface.
- zbMATH returned HTTP 404 for all 28 requests, with a JSON internal status
  saying “successful access. No results found.” These are logged as explicit
  service-level zero results, not as mathematical evidence. The behavior may
  also reflect limitations of the public one-line endpoint.
- DuckDuckGo HTML returned HTTP 403 for all 28 automated first-page requests.
  They are failures, not zero-result searches. A separate available general
  web-search surface was used for the logged S01–S12 terminology-sharpening
  round, but its result-count/export interface was not exposed.
- arXiv returned HTTP 200 for all 28 requests, but its `all:` query parser
  broadened many quoted multi-token strings. Many first-20 records were
  obvious uses of “lattice” from lattice QCD or unrelated uses of `A2`,
  “Gram,” and “Schur.” Title inspection was therefore necessary.
- Crossref likewise broadened several quoted strings and produced lexical
  collisions. A returned count of 20 must not be read as 20 relevant papers.
- Each database search was capped at its first 20 relevance-ranked records.
  Ranking, indexing, and API contents can change after the audit date.
- MathSciNet was not available. zbMATH was the intended specialist
  bibliography, subject to the endpoint limitation above.
- The query set is English and notation driven. It does not exhaust
  non-English terminology, every decomposition notation, unpublished
  manuscripts, theses not indexed by the searched systems, or results whose
  title/abstract omits all frozen concepts.

## Scope limitations

- This is a literature/novelty audit only. It did not rerun or validate the
  Wave 26 frame, determinant, cubic-tensor, or lattice calculations.
- Post-freeze repository inspection was restricted to terminology. Statements
  about a 231-by-44 frame, row norm/alphabet, `W = M Hadamard-product M`, and
  an `A2` contradiction are treated as claims under audit, not established
  inputs.
- The phrase “Schur-origin” was ambiguous at freeze time. Q23–Q25 searched
  block-matrix Schur complements, whereas the repository usage is the
  entrywise Schur/Hadamard product. Both the mismatch and the corrective
  S01–S04 searches are recorded.
- The search cannot establish global novelty by failing to locate a match.
  The novelty label is therefore `UNKNOWN`.
- Generic compatibility of `A2` with tight-frame/strong-eutaxy and antipodal
  odd-moment identities does not refute a stronger obstruction using the
  additional discrete Wave 26 constraints.

## Execution and preservation notes

- `Get-Date -AsUTC` was unsupported in this Windows PowerShell environment;
  timestamps were obtained with `[DateTime]::UtcNow`.
- The first foreground collector invocation crossed the 10-second shell
  timeout, but the same process continued and completed. Completion was
  confirmed by its final ledger and the absence of a live collector process.
- A diagnostic PowerShell aggregation initially referenced a nonexistent
  `result_count` field; the correct field was `returned_results`. This did not
  modify captured search data.
- The collector transiently wrote 140 raw API/search response bodies and a
  larger parsed file. After deriving and validating `query-ledger.json`, those
  response bodies and the bulky parsed copy were deleted for publication
  hygiene. They are not publication evidence and were not otherwise retained.
  The retained collector can reproduce a fresh, time-dependent capture.
- No Git command was run. The full `git_commit` in `run-report.yaml` is copied
  from the inspected Wave 26 run reports and was not independently queried.
