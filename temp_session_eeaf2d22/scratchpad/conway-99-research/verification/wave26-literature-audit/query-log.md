# Wave 26 literature audit: query log

## Gate chronology

- `2026-07-23T22:50:16.910Z`: preinspection search protocol frozen in
  `protocol-freeze.md`.
- `2026-07-23T22:51:25.863Z`: repository-context inspection authorized to
  begin. No repository or Wave 26 proof artifact had been inspected before
  this timestamp.
- Inspection purpose is restricted to terminology and public-context
  sharpening. Proof validity remains outside this audit.

## Execution log

### Post-freeze terminology inspection

The following files were inspected only after the gate timestamp. Their role
was to recover the discovery-side vocabulary, not to assess proof validity.

| Path | SHA-256 |
|---|---|
| `agents/2026-07-23-wave26-a2-frame-obstruction.md` | `2870c4b9195d5569655fded93a7d1b3d4131663e3ef37ce2ef346c03cf8f2925` |
| `agents/2026-07-23-wave26-a2-cubic-obstruction.md` | `da701181c9d591498cf112ab8b0342d09d3ada4094396cebebe3e0dd81c44d1a` |
| `verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md` | `5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3` |
| `attempts/wave26-a2-frame-obstruction/run-report.yaml` | `7cd99c1a5a3443bc85a0f372f29685217a4e315d44c9124cd3b003f352317f3e` |
| `attempts/wave26-a2-cubic-obstruction/run-report.yaml` | `008a154f928d64c5c3fbc672ce0aabc1115a84984e9d6d231757016bdb2b2003` |
| `verification/global-schur/2026-07-23T170612Z-status-literature-audit.md` | `b3a7b0a882e7f822ae6e2ed08df4314357d5d554903f788305979e03b08fc651` |
| `verification/global-schur/2026-07-23T170612Z-status-source-query-ledger.json` | `127b5d99e5145291bcb3b307ebcd3047b5b3c891fccfd02fad25af0e5b422dd9` |

Terminology recovered: the frame lane uses a claimed integral
`231 x 44` tight frame with restricted row data. The cubic lane uses an
entrywise Schur/Hadamard square `W = M Hadamard-product M`. This is not a
block-matrix Schur complement.

### Frozen database capture

- Start: `2026-07-23T22:57:15.436Z`
- Finish: `2026-07-23T22:59:00.170Z`
- Command:
  `python verification/wave26-literature-audit/collect-search-results.py`
- Requests attempted: 140 = 28 exact frozen queries times 5 services.
- Compact metadata ledger derived:
  `query-ledger.json` (exact query, encoded endpoint, UTC interval, HTTP
  status, total/returned count when supplied, and error state for every
  request).

| ID | Crossref | OpenAlex | zbMATH | arXiv | DDG |
|---|---:|---:|---:|---:|---:|
| Q01 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q02 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q03 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q04 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q05 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q06 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q07 | 20 | 20 | 0* | 8 | HTTP 403 |
| Q08 | 0 | 0 | 0* | 20 | HTTP 403 |
| Q09 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q10 | HTTP 429 | 0 | 0* | 20 | HTTP 403 |
| Q11 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q12 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q13 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q14 | HTTP 429 | 1 | 0* | 20 | HTTP 403 |
| Q15 | HTTP 429 | 0 | 0* | 20 | HTTP 403 |
| Q16 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q17 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q18 | 20 | 8 | 0* | 20 | HTTP 403 |
| Q19 | HTTP 429 | 1 | 0* | 20 | HTTP 403 |
| Q20 | 20 | 6 | 0* | 20 | HTTP 403 |
| Q21 | 20 | 1 | 0* | 20 | HTTP 403 |
| Q22 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q23 | 20 | 20 | 0* | 20 | HTTP 403 |
| Q24 | HTTP 429 | 20 | 0* | 20 | HTTP 403 |
| Q25 | 20 | 20 | 0* | 20 | HTTP 403 |
| Q26 | 20 | 7 | 0* | 20 | HTTP 403 |
| Q27 | 20 | 0 | 0* | 20 | HTTP 403 |
| Q28 | 20 | 0 | 0* | 20 | HTTP 403 |

Counts are records returned, not relevant matches. `0*` means zbMATH
responded HTTP 404 with the internal status “successful access. No results
found.” Crossref’s HTTP 429 requests were Q10, Q14, Q15, Q19, and Q24.
DuckDuckGo’s HTTP 403 requests are failures, not zero-result searches.

Title-level review found no direct or near-direct target source among the
returned first-20 sets. The broad arXiv and Crossref results contained many
keyword collisions (especially lattice QCD, generic Gram matrices, and
block-matrix Schur complements). Relevant machinery was routed to
`sources.md`; unselected response bodies/titles were not retained as
publication artifacts.

### Logged terminology-sharpening queries

The following exact queries were run on the available general web-search
surface after the repository vocabulary was known:

| ID | Exact query | Inspected-page result |
|---|---|---|
| S01 | `"Schur square" Gram matrix tight frame` | No target-specific match; generic Schur/Hadamard material |
| S02 | `"Hadamard square" Gram matrix spherical design` | No target-specific match; nearby Gram/design machinery |
| S03 | `"Schur product" projection matrix tight frame` | No target-specific match; generic Schur/frame material |
| S04 | `"Hadamard products of Gram matrices" frame` | Peng–Waldron, DOI `10.1016/S0024-3795(01)00551-1`; general machinery only |
| S05 | `"A2 root system" "tight frame"` | No target-specific match; broader Sunada root-system/frame source |
| S06 | `"A_2 root system" "spherical 5-design"` | No target-specific match |
| S07 | `"orthogonal A2 summand" "tight frame"` | No relevant inspected-page result |
| S08 | `"E8^5" "A2^2" projector` | No relevant inspected-page result |
| S09 | `"231" "A2" "tight frame"` | No target-specific match |
| S10 | `"norm-four" tight frame lattice A2` | No target-specific match |
| S11 | `"crystallographic tight frame" root system A2` | Sunada, DOI `10.1017/9781316576571.018`; general machinery only |
| S12 | `"integer frame" "A2"` | Casazza et al., arXiv `1307.4328`; generic integer-frame literature only |

The web-search surface did not expose a stable total-result count or raw export.
The table therefore records the exact query and the result actually used in
the audit, not an assertion that no uninspected result exists.

### Citation/reference chase

One outward chase round was made from the included projector/frame,
lattice/eutaxy, SRG/two-distance, and Hadamard-Gram sources. It routed the
foundational or adjacent sources listed as S02, S08, S10, S12, and S14 in
`sources.md`. No class D or N item emerged; the next items were machinery,
background, or keyword collisions, so the frozen stopping rule was met.

### Preservation event

- `2026-07-23T23:04:00.921Z`: compact 140-record request ledger generated.
- By `2026-07-23T23:11:04.602Z`: 140 transient raw response files
  (1,693,392 bytes) and the 471,104-byte bulky parsed copy were deleted after
  the compact ledger was checked.
- Reason: publication hygiene and third-party-content minimization.
- Consequence: transient bodies are not publication evidence. Fresh,
  time-dependent responses can be regenerated with the retained collector.

### Search disposition

- Direct prior-art match (class D): **none found in scoped search**.
- Near-direct theorem visibly covering the target (class N): **none found in
  scoped search**.
- General machinery (class M): **found and cited**.
- Claim validity: **not assessed; `UNKNOWN`**.
- Global novelty: **`UNKNOWN`**.
