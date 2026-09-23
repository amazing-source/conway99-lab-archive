# Wave 26 literature audit: preinspection protocol freeze

## Freeze metadata

- Freeze written: `2026-07-23T22:50:16.910Z`
- Search cutoff: material discoverable on or before `2026-07-23`
- Role: statement/literature agent
- Proof status authority: none
- Artifact-inspection state at freeze: **no Wave 26 proof artifact, report, script, output, or central ledger inspected**
- Inputs available at freeze: the task instructions and the claim synopsis reproduced below, and nothing from Wave 26 discovery internals

This file freezes the search before repository or Wave 26 proof-artifact inspection. Later terminology expansion is permitted only when it is recorded with its source and timestamp in `query-log.md`; it may not silently replace or narrow the frozen queries.

## Frozen claim synopsis

The endpoint under discussion is hypothetical and has `n3 = 708` in the
`srg(99,14,1,2)` project. A previously enumerated abstract even-lattice survivor
is said to have scaled-dual form

`E8^5 orthogonal-sum A2^2`.

The discovery-side claim is that the additional required structure of a
231-row projector/Schur-origin representation rules out any orthogonal `A2`
summand.

This audit asks only whether published or publicly indexed prior art directly
states that conclusion, or supplies recognizably close general machinery. It
does **not** determine whether the discovery-side argument is correct.

## Frozen questions

1. Is there a directly matching theorem about a projector/Gram/Schur-origin
   lattice construction excluding an orthogonal `A2` summand?
2. Is there a directly matching theorem for the parameter-specific
   `srg(99,14,1,2)`, `n3 = 708`, or 231-row setting?
3. What prior art exists on integral or rational tight frames and projector
   Gram matrices that could subsume such an obstruction?
4. What prior art connects even lattices, orthogonal root-lattice summands
   (especially `A2`), eutaxy, and spherical 2- or 3-design moments?
5. What prior art gives Schur-complement or block-projector moment identities
   that might be relevant?
6. If no direct match is found in the scoped search, what is the strongest
   supportable literature-status statement?

## Frozen exact query strings

The following strings are case-insensitive except where a search service
implements phrase quoting. Hyphen/underscore variants may be run only as
logged supplementary queries.

| ID | Exact query string |
|---|---|
| Q01 | `"srg(99,14,1,2)" lattice` |
| Q02 | `"srg(99,14,1,2)" projector` |
| Q03 | `"strongly regular graph" "99,14,1,2" lattice` |
| Q04 | `"n3 = 708" lattice` |
| Q05 | `"231-row" projector lattice` |
| Q06 | `"231 rows" projector Gram lattice` |
| Q07 | `"E8^5" "A2^2"` |
| Q08 | `"E_8^5" "A_2^2"` |
| Q09 | `"orthogonal A2 summand" lattice` |
| Q10 | `"A2 summand" projector lattice` |
| Q11 | `"A_2" "orthogonal summand" even lattice` |
| Q12 | `"integral tight frame" lattice projector` |
| Q13 | `"integer tight frame" Gram projector` |
| Q14 | `"finite unit norm tight frame" integral Gram matrix` |
| Q15 | `"rational tight frame" lattice Gram matrix` |
| Q16 | `"projector Gram matrix" lattice` |
| Q17 | `"idempotent Gram matrix" tight frame lattice` |
| Q18 | `eutaxy lattice spherical 2-design Gram matrix` |
| Q19 | `"strongly eutactic" lattice root system A2` |
| Q20 | `"spherical 2-design" lattice projector` |
| Q21 | `"spherical 3-design" lattice moment obstruction` |
| Q22 | `"spherical design" "A2" lattice eutaxy` |
| Q23 | `"Schur complement" Gram matrix moment identity` |
| Q24 | `"Schur complement" tight frame projector` |
| Q25 | `"Schur complement" lattice projector` |
| Q26 | `"moment identity" projector Gram matrix` |
| Q27 | `"root lattice A2" tight frame` |
| Q28 | `"orthogonal direct summand" A2 lattice design` |

## Search systems and frozen coverage

The search will use:

1. Crossref Works API (bibliographic database), first 20 records by relevance
   for every Q01--Q28.
2. OpenAlex Works API (bibliographic database), first 20 records by relevance
   for every Q01--Q28.
3. zbMATH Open, where its public API/search interface is reachable, first 20
   records for every Q01--Q28.
4. arXiv API, first 20 records by relevance for Q01--Q28, to catch preprints.
5. General web search for Q01--Q28, examining at least the first results page
   returned by the available engine.
6. Citation and reference chasing from included sources until one full round
   produces no new source in a higher relevance class. Every chased item is to
   be logged.

Service failures, access limits, result-count ambiguity, and truncation will be
recorded rather than silently treated as zero results.

## Frozen inclusion, relevance, and source-quality rules

### Source quality

Priority order:

1. Original peer-reviewed paper, monograph, thesis, or author-hosted/preprint
   version with stable bibliographic metadata.
2. Publisher page, DOI registration, arXiv record, institutional repository,
   or established mathematical bibliography (zbMATH/MathSciNet metadata).
3. Reliable bibliographic databases (Crossref, OpenAlex) for discovery and
   metadata corroboration.
4. Secondary surveys only when they accurately route to primary sources or
   synthesize terminology.

Blogs, generated summaries, forum posts, snippets without an inspectable
source, and model prose cannot support `CITED`. They may only provide a search
lead.

### Relevance classes

- **D (direct):** the same parameter-specific setting, or a theorem explicitly
  excluding an orthogonal `A2` summand under the stated projector/Schur-origin
  structure.
- **N (near-direct):** a general theorem whose stated hypotheses visibly cover
  integral/rational projector Gram matrices and orthogonal `A2` summands,
  without supplying a parameter-specific application.
- **M (machinery):** established results about tight frames/projectors,
  eutaxy/spherical designs, root-lattice summands, or Schur/block identities
  that are plausibly relevant but do not state the target obstruction.
- **B (background):** terminology or broad context only.
- **X (excluded):** keyword collision or no meaningful relation.

### Inclusion

An item is included in the bibliography if it is D, N, or M and an
inspectable primary source or authoritative bibliographic record is available.
Background sources may be included sparingly when needed to define standard
terminology. The report will identify whether full text or only metadata was
inspected.

## Frozen status rules

- `CITED` is reserved for a proposition accurately attributed to a source that
  was actually inspected.
- `UNKNOWN` is the default status for both (a) whether the target argument is
  valid and (b) whether the claim is globally novel.
- “No matching source found in this scoped search” is permitted when supported
  by the query log.
- “Novel,” “first,” “new theorem,” or equivalent language is forbidden unless
  independently established by evidence beyond absence of search hits.
- A solver/search exit code, database zero count, or snippet is not a
  literature certificate.
- This literature agent will not inspect or adjudicate proof validity and will
  not promote any discovery claim to `VERIFIED`.

## Frozen stopping and reporting rules

The search stops after all frozen queries have been attempted in the specified
systems, included sources have undergone one complete citation/reference-chase
round, and one terminology-sharpening round (if repository context justifies
it) has been logged. Exact search responses will be retained where licensing
and the interface permit; otherwise the returned result titles/URLs and the
limitation will be transcribed.

The final report will distinguish:

1. directly matching prior art;
2. near-direct general theorems;
3. relevant machinery only;
4. scoped-search negative results;
5. global novelty, which remains `UNKNOWN` absent affirmative evidence.
