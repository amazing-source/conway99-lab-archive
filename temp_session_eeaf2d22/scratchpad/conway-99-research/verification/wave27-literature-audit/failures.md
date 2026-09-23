# Failures and limitations

1. **Frozen interpretation defect.** `protocol.md` treated `21E6^{-1}` as
   possibly factor two. The file remains byte-for-byte unchanged at
   `f52683741f227d8e9c4f80b5474e73744a235b5e4383a2996a1439ed4b84742f`.
   `protocol-correction.md` changes the operational meaning to twenty-one
   times the inverse and adds R00. The original G03 was still executed.

2. **zbMATH partial service failure.** The documented live route
   `/v1/document/_search` returned HTTP 200 for Z01--Z02, but HTTP 404 with
   payload status `Entry not found!...` for Z03--Z10, R00, and the late
   A20-Z01 query. These are endpoint failures, not zero-result evidence.

3. **General-web attribution replay.** The first three multi-query tool calls
   merged snippets without dependable query attribution. All eleven exact
   queries were replayed individually. Both attempts are retained through
   `attempt_count: 2` in `query-log.jsonl`; only the individual replay was
   coded.

4. **General-web result-cap behavior.** The wrapper sometimes displayed more
   than ten snippets even though the protocol cap was ten. Only the first ten
   were coded. One post-cap E6 discriminant slide was inadvertently opened
   during authentication; it is not cited or used as evidence.

5. **Crossref precision.** Crossref's general `query` endpoint reports very
   large corpus totals and does not enforce exact phrase semantics. Every
   top-ten record was still inspected, but totals must not be read as counts
   of mathematical matches. Crossref R00's ten records were lexical false
   positives.

6. **Service syntax differs.** The exact frozen text was translated only as
   required by each API: arXiv field prefixes, URL encoding, and zbMATH's
   documented `|` operator for R00. No discovery synonym was added.

7. **Candidate mismatch.** E6 can denote a Lie group, Lie algebra, root
   system, lattice, equation label, experimental group, or medical protein.
   Likewise `A6` and "frame" have many unrelated uses. A source was not
   classified as overlap unless its title/abstract/full text reached the
   rank-six lattice target.

8. **Current-status limit.** A bounded index audit cannot prove that a
   problem is open or that no later/unindexed manuscript exists. The audit
   reports what qualifying sources state through the cutoff.

9. **No raw corpus.** No result-page corpus, PDF corpus, abstract dump, or
   full-text cache is stored. The ledger keeps query metadata and the source
   file keeps only evidence-bearing citations.

10. **No novelty inference.** Zero results, false positives, endpoint
    failures, and absence within the cap are all non-certificates. Novelty
    remains `UNKNOWN`.

11. **Late A20 scope.** The A20 trace/summand target was supplied after the
    original protocol and correction had been executed. It was searched only
    under the separately timestamped six-query `protocol-a20-addendum.md`.
    This does not rewrite or expand the original freeze. The exact trace
    identity and orthogonal-summand use were not found; the standard `A_n`
    Cartan matrix is only conceptual overlap.
