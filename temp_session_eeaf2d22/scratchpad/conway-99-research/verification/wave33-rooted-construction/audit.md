# Independent audit: Wave 33 rooted construction/search package

## Verdict

`VERIFIED` only for the frozen, scoped candidate facts:

- the public Wave 32 support reconstructs the fixed `14 x 70` incidence
  matrix `B`;
- the frozen O-Q certificate is a simple `2-(15,3,2)` design;
- it has row degrees `3^70`, column degrees `14^15`, and all 105 Q-pair
  intersections equal to two;
- it fails exactly ten of the 210 equations `BF=2J`, with five defects `-1`,
  five defects `+1`, and squared defect 10;
- it supplies no O-O adjacency layer;
- the frozen MILP source encodes 4,900 binary assignment variables and
  `70+70+210=350` equalities, covering all `70!` block-to-O bijections of
  one fixed simple design only; and
- the 25-second status-1 timeout returned no primal or output and never
  entered the O-O phase.

This is no construction and no exclusion. The complete graph extension,
rooted endpoint, `n3=708`, Conway-99, and novelty remain `UNKNOWN`.

## Clean-room separation

The checker, 27 hostile precomparison tests, fixture, derivation, and first
results were written from public Wave 32 inputs and hash-frozen before
candidate release. The precomparison manifest has SHA-256
`4ccbbad9c01eab764d9aa6fb207114e43f8c5a36bec3ec5bf0d161708ce0360d`
and still verifies byte-for-byte.

After release, all 17 candidate-freeze entries, all 16 nested artifact
entries, seven initial inputs, and the continuation-protocol addendum
verified before static inspection. No discovery module was imported.
`search_partial_design.py` was never executed. A separate standard-library
reimplementation reproduced its 56 parallel classes and 240 resolutions per
STS, all nine 200,000-step restarts, the best state at restart 8 / step
166762, and the certificate byte-for-byte.

Only after static comparison, the frozen exact checker and MILP command were
invoked as replays. Their outputs are status metadata, not proof evidence.

## Obligation table

| Obligation | Result |
|---|---|
| Precomparison bytes unchanged | `PASS` |
| Candidate freeze, nested artifact manifest, and input freezes | `PASS` |
| Exact public support/O label domain; no outside automorphism | `PASS` |
| Fixed design: 70 distinct triples, point degree 14, pair count 2 | `PASS` |
| Assignment encoding: 4,900 binaries, 350 equalities | `PASS` |
| Encoding scope: all `70!` bijections of one fixed design only | `PASS` |
| Timeout metadata: status 1, no primal/objective/node/gap | `PASS` |
| No bounded output and no active O-O phase | `PASS` |
| Certificate row/column/Q-pair counts | `PASS` |
| `BF=2J` recomputation | `FAIL` at exactly 10 entries; expected hostile result |
| Squared `BF` defect | `10` |
| O-O layer | `UNSUPPLIED` |
| Empty-D hostile control | degree `5^70,14^29`; matrix identity `FAIL` |
| Candidate and report status walls | `PASS` |
| Deterministic hostile-search reimplementation | `PASS`, byte-identical |
| Correct exact-checker replay | `PASS`, byte-identical |
| Complete graph / rooted endpoint / Conway-99 | `UNKNOWN` |

## Independent encoding reconstruction

The first 70 binary equalities choose one block for each fixed O label. The
next 70 use every one of the 70 distinct blocks exactly once. These two sets
are precisely the permutation matrices, hence `70!` assignments before
balance filtering. For each of 14 support groups and 15 Q points, the final
210 rows sum the relevant assignment variables to two. The independently
rebuilt system has:

```text
4,900 binary variables
140 rows of width 70
210 rows of width 140
39,200 nonzero unit coefficients
row-system SHA-256 1a654646baa1a64e0ca460ef1fb8504ae05d20654a77e2366198ee36bedd0264
```

Static inspection of `search_relaxation.py` lines 24-68 and 92-139 matches
this system. Simplicity and the choice of this particular design are explicit
restrictions, not without-loss-of-generality reductions. Other nonisomorphic
simple `2-(15,3,2)` designs are not covered.

## Exact hostile O-Q object

Independent reconstruction gives the support-point count histogram

```text
1^5, 2^200, 3^5.
```

The ten nonzero defects occur in five R-side support groups; all seven P
groups and two R groups are exact. Their machine-readable list has SHA-256
`26fbfd01ba81b743fd77a800f57fb56e4325d2cf0776a977d950945149a007ed`.
The design equations on Q are exact, but `BF=2J` already fails.

The certificate contains only O-Q triples. It does not set the O-O layer to
zero. The verifier separately tests the empty-D completion as a hostile
control; that control leaves every O vertex at degree five and is not a
search restriction or an argument against some other O-O completion.

## Replays and chronology

The orchestrator initially replayed `exact_check.py` without
`--partial-certificate`. That valid but wrong invocation emitted the
base-only result with SHA-256
`97f30719cc41bb48c3b562faf5bc7037112cd8cf35c737b3717614217a9c1ea1`.
This was an orchestrator replay mistake, not a candidate defect. The frozen
run-report command includes the required flag and regenerates
`exact-results.json` byte-identically at
`ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496`.

The 25-second SciPy/HiGHS replay again exited 1 with no output and the exact
recorded status-1/no-primal message. It remains no mathematical evidence.
The source accepts a seed argument but does not pass it to `scipy.optimize.milp`;
this has no bearing on the honest timeout boundary.

## Nonblocking checker coverage gaps

The discovery checker exactly validates the label/triple arithmetic and
rejects a top-level promotion from `CANDIDATE`. It does not bind the
certificate's `scope`, `evidence_kind`, `restrictions`, `limitations`, or
discovery-status metadata, and ordinary `json.loads` does not reject
duplicate keys. These are real hostile-checker coverage gaps in the frozen
discovery bytes.

They are nonblocking for the scoped candidate facts because the frozen
certificate is honestly worded and the pre-frozen clean-room verifier uses a
strict duplicate-key loader and exact scope/status gates. The gaps are
recorded here rather than silently treated as discovery-checker coverage.

## Correction-ledger scope

The correction ledger is accurate: the three block equations are complete
for the labeled `srg(99,14,1,2)` graph-extension domain, but that domain is
only a finite relaxation of the full rooted `n3=708` endpoint package with
its projector, lattice, tensor, and Schur conditions. A proper relaxation,
timeout, heuristic nonhit, or partial object decides neither domain.

## Replay

From this directory:

```text
python -B -m unittest -v test_independent_check.py test_candidate_comparison.py
python -B candidate_comparison.py --reproduce-search
```

The combined suite passes 37 tests. The second command independently
reproduces the hostile-search certificate in about 17 seconds on the audited
machine without importing or executing discovery code.
