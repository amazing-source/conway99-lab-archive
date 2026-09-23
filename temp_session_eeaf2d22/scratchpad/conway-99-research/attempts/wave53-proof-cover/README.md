# Wave 53 endpoint proof cover

Status: `DERIVED/CANDIDATE`. The exact branch cover is exhaustive under the
frozen `n3=4158` endpoint assumptions, but no complete branch is closed.

## What the 33 cases do prove

The normalized endpoint state space contains 10,395 labelled
matching/common-neighbor states and has 78 exact stabilizer orbits. The 84
endpoint nonedge units immediately conflict with seven of the twelve parent
matching orbits. The five surviving parents contain exactly:

| parent | cases | refined branches | state-orbit weight |
|---:|---:|:---|---:|
| 4 | 4 | 15--18 | 132 |
| 5 | 4 | 19--22 | 528 |
| 8 | 6 | 36--41 | 704 |
| 10 | 8 | 50--57 | 1,056 |
| 12 | 11 | 68--78 | 4,224 |
| total | 33 | | 6,644 |

`coverage-certificate.json` freezes every endpoint unit, all 66 parent units
for each parent, every matching representative, every refinement edge and
literal, and every orbit weight. The deterministic checker reconstructs the
certificate from the pinned prior independent orbit implementation.

Therefore the 33 cases are an exhaustive conditional branch cover. This is
not an UNSAT result. A branch cover says every endpoint graph must lie in at
least one listed case; branch UNSAT coverage asks how many complete listed
cases have checked contradiction proofs. The answers are:

```text
conditional branch coverage:       33/33
checked complete-case UNSAT proofs:  0/33
endpoint status:                    UNKNOWN
```

## Smallest missing ingredient

The only exported complete case is refined branch 15. A prior independently
checked proof excludes its `x187=1` polarity, so the exact remainder is
`branch15 AND x187=0`. Closing that remainder would close the first complete
case. Repeating a proof-producing solve for every other case would still be
required to exclude the endpoint.

This makes the missing ingredient precise: it is not another case split. It
is a checked terminal certificate for the branch-15 remainder, followed by
32 more complete-case certificates. For UNSAT, the existing formulas contain
only necessary endpoint constraints, so a checked contradiction is sound
even though their static prism clauses are incomplete. For SAT, a candidate
must instead pass complete graph decoding and an exhaustive global prism
oracle.

## Bounded proof-producing experiment

`branch-15-x187-zero.opb.gz` is the frozen source formula with the single
explicit unit `+1 ~x187 >= 1 ;` appended. Pinned Exact was run with
`--timeout=3` and retained `branch-15-x187-zero.raw.pbp`. The result was:

```text
Exact:                       UNKNOWN
CPU / parse / solve seconds: 3.448 / 3.345 / 0.103
decisions / conflicts:       21 / 0
raw proof bytes:             72,584
```

Strict raw VeriPB replay, VeriPB elaboration, strict kernel replay, and CakePB
all returned `VERIFIED NO CONCLUSION`. That is useful pipeline evidence but
zero mathematical evidence. The run spent almost its whole budget parsing,
so a future bounded experiment needs a materially larger post-parse solving
window or a persisted parsed representation.

Discovery reported free physical memory between 56.25% and 57.46%, above its
20% guard, but retained no raw monitor transcript. Those historical numbers
are self-reported rather than independently replayable and are not
mathematical evidence.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -B attempts\wave53-proof-cover\build_coverage.py
.\.venv\Scripts\python.exe -B attempts\wave53-proof-cover\check_coverage.py
.\.venv\Scripts\python.exe -B attempts\wave53-proof-cover\export_remainder.py `
  --raw attempts\wave53-proof-cover\branch-15-x187-zero.opb `
  --gzip attempts\wave53-proof-cover\branch-15-x187-zero.opb.gz `
  --metadata attempts\wave53-proof-cover\branch-15-x187-zero-formula.json
.\.venv\Scripts\python.exe -B attempts\wave53-proof-cover\record_bounded_run.py
.\.venv\Scripts\python.exe -B -m unittest discover `
  -s attempts\wave53-proof-cover -p "test_*.py" -v
```

The Exact/VeriPB/CakePB commands, binary hashes, proof hashes, and checker
transcripts are recorded in `bounded-run.json`. Regenerate the ignored raw OPB
from the published deterministic gzip before replaying the retained proofs.

## Status boundary

- Exact cover of endpoint-compatible normalized states: `DERIVED`.
- Complete endpoint cases with checked UNSAT proofs: `0/33`.
- Bounded branch-15 remainder run: `VERIFIED NO CONCLUSION` by the tools.
- Branch 15, `n3=4158`, a strict general upper bound, Conway-99, and novelty:
  `UNKNOWN`.
