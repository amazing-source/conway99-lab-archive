# Wave 53 proof-A: exact endpoint proof cover

```yaml
role: proof_a
date_utc: 2026-07-27T19:44:37Z
git_commit: a4a61658356253fb95cf68252c972a4f79df38fe
claim_label: DERIVED
scope: exact normalized 33-case cover conditional on n3=4158, with a bounded proof-producing branch-15 remainder run
inputs:
  attempts/wave53-proof-cover/input-freeze.sha256: upstream hashes frozen
method: exact orbit reconstruction, explicit unit/case certificate, three-second Exact run, raw and kernel proof replay
command: see attempts/wave53-proof-cover/run-report.yaml
outputs:
  attempts/wave53-proof-cover/coverage-certificate.json: exhaustive conditional branch map
  attempts/wave53-proof-cover/bounded-run.json: checked NO CONCLUSION run record
limitations: no complete case UNSAT, no endpoint exclusion, no upper-bound improvement, no graph, and no novelty claim
```

## Verdict

The 33-case split is not the missing theorem. It is an exact, exhaustive
conditional cover of the normalized `n3=4158` endpoint:

```text
all normalized states:                 10,395
all refined stabilizer orbits:             78
endpoint-incompatible orbits / weight: 45 / 3,751
endpoint-compatible cases / weight:    33 / 6,644
completed-graph automorphism assumed:  no
```

The machine-readable certificate freezes every endpoint nonedge unit, all
twelve parent branch definitions, every surviving matching representative,
every refinement literal, and every orbit weight. Its exact filter reproduces
parents `4,5,8,10,12` and refined cases:

```text
15--18, 19--22, 36--41, 50--57, 68--78.
```

This establishes branch coverage under the frozen endpoint assumptions, not
branch UNSAT. No complete case has a checked contradiction:

```text
conditional case coverage:            33/33
checked complete-case proof coverage:  0/33
```

## Smallest missing ingredient

The prior Wave 39 proof closes only `branch15 AND x187=1`. The complementary
`branch15 AND x187=0` shard is the exact remainder of the only endpoint case
whose formula is already exported. A checked terminal contradiction for that
remainder would close branch 15 and raise complete-case coverage to `1/33`.
The other 32 complete cases would still need checked proofs.

Thus the smallest ready proof-producing target is not a new symmetry split.
It is a terminal certificate for `branch15 AND x187=0`. At the global level,
the missing ingredient is a repeatable case-owned pipeline producing 33
independently replayed terminal certificates.

## Bounded experiment

I exported the exact remainder by appending only:

```text
+1 ~x187 >= 1 ;
```

to the frozen branch-15 OPB and incrementing its declared constraint count.
Pinned Exact was run with a three-second bound and retained a 72,584-byte raw
proof. It returned:

```text
result:                    UNKNOWN
CPU / parse / solve:       3.448 / 3.345 / 0.103 seconds
propagations / decisions:  912 / 21
conflicts / solutions:     0 / 0
```

Strict raw VeriPB replay, elaboration, strict kernel replay, and CakePB all
returned `VERIFIED NO CONCLUSION`. The proof is retained, but it proves only
that the bounded run made no claim. It contributes zero case coverage.

The practical engineering lesson is narrow: the `--timeout=3` run was almost
entirely parser/presolve time for this 29.8 MB formula; the flag was not a
strict process wall. A future run needs a materially longer post-parse search
window or a safe persisted parse, not status inflation from another
parsing-dominated timeout.

Discovery reported free memory above 56%, beyond its 20% reserve, but retained
no raw monitor transcript. The percentages are self-reported, not
independently replayable, and have no mathematical role.

## Mathematical boundary

For an UNSAT route, the current branch formulas are sufficient despite their
partial fixed-triangle prism catalogs: they encode necessary endpoint
conditions, so a checked contradiction excludes the case. For a SAT route,
the converse fails; a decoded assignment must pass the complete SRG checker
and exhaustive global prism oracle.

No complete case, `n3=4158`, strict upper bound below 4158, graph, Conway-99
resolution, or novelty claim follows. All remain `UNKNOWN`.
