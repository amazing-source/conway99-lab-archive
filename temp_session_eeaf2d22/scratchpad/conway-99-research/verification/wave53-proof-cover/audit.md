# Independent audit of Wave 53 endpoint proof cover

Final verifier status: `VERIFIED` for the exact scoped conditional cover and
for the proof tools' `NO CONCLUSION` status. The mathematical target remains
`UNKNOWN`. All verifier-requested discovery corrections are resolved.

## Verdict

The discovery package correctly separates a branch cover from an UNSAT cover.
Independent reconstruction obtained:

```text
labelled matching/candidate states:        10,395
exact oriented-stabilizer orbits:              78
endpoint-compatible cases / weight:      33 / 6,644
endpoint-incompatible orbits / weight:   45 / 3,751
conditional case coverage:                    33/33
complete-case checked UNSAT coverage:           0/33
```

All 84 endpoint units, all 66 units for each of twelve parents (792 total),
all 33 recorded refinement literals, every recorded representative,
stabilizer size, case identifier, and orbit weight agree with the independent
finite reconstruction. The compatible parent branches are exactly
`4,5,8,10,12`; the incompatible parents are exactly `1,2,3,6,7,9,11`.

This verifies exhaustiveness only under the frozen normalized `n3=4158`,
zero-prism endpoint assumptions. It does not prove any complete case
unsatisfiable.

## Symmetry attack

The checker exhaustively filtered all 645,120 elements of the automorphism
group `C2 wreath S7` of the seven-pair local scaffold. The exact stabilizer of
the frozen N3 unit has order 768, and its oriented subgroup has order 384.
Those exhaustive filters equal the independently generated groups.

The orbit reduction therefore uses canonical relabelling of the local
scaffold. It does not assume that a completed graph has a nontrivial
automorphism. Orbit-stabilizer and Burnside checks independently give 12
parent orbits and 78 refined orbits.

## Branch-15 remainder

The pinned Wave 37 source gzip decompresses to SHA-256
`4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5`
with 574,615 constraint lines. The Wave 53 shard is exactly:

1. the source header with the declared constraint count changed from 574,615
   to 574,616;
2. the source body unchanged byte-for-byte; and
3. the appended constraint `+1 ~x187 >= 1 ;`.

In OPB literal semantics, `~x187` is true exactly when `x187=0`. The raw shard
has SHA-256
`b1681416ee2860c4b40ce854fb533062af8e1c7a9dc0c423ba0c5f0545677d08`;
the gzip has SHA-256
`5d026ebdd3f4e05c46a494ba357fbcaa7e994f7c518a89b8c7f5dc956ac8ee9c`;
and decompressing that gzip reproduces the raw bytes exactly.

Combined with the previously independent Wave 39 result for
`branch15 AND x187=1`, this identifies `branch15 AND x187=0` as the exact open
polarity remainder. It does not close branch 15.

## Proof replay and resource guard

The retained Exact transcript is `UNKNOWN`. Fresh pinned-tool runs returned:

```text
Exact:                    UNKNOWN
VeriPB raw:               VERIFIED NO CONCLUSION
VeriPB fresh elaboration: VERIFIED NO CONCLUSION
VeriPB kernel:            VERIFIED NO CONCLUSION
CakePB kernel:            VERIFIED NO CONCLUSION
```

The fresh Exact proof reproduced raw-proof SHA-256
`ca94b003b5506bbf7164223db415f5df677381a0a1ec99ccc816508b81d36861`.
Fresh VeriPB elaboration reproduced kernel-proof SHA-256
`251cc6158e9afba4db8e49eb0dcf02ec564bcfaf03de16151b1bbab0c0d968b9`.
All tool hashes match the discovery lock.

The final fresh runs observed at least 45.61% free physical memory, above the frozen
15% reserve. The historical discovery values 56.25--57.46% are recorded in
the discovery JSON but have no separate raw monitor artifact; they are not
independently replayable. Also, Exact's `--timeout=3` is not a strict
three-second whole-process wall: the final fresh run reported 3.666 seconds
CPU, 3.589 seconds parse, and 0.077 seconds solve. This affects resource
wording, not proof status.

A valid `VERIFIED NO CONCLUSION` proof shows that the proof transcript made no
invalid inference before stopping; it proves neither SAT nor UNSAT. Its UNSAT
case-coverage contribution is exactly zero.

## Discovery-package correction resolution

All nine frozen input hashes and all 25 entries listed in the final discovery
package manifest match current bytes. The four-item correction ledger is
complete:

1. `W53-PC-C001`: a package-local ignore rule now excludes exactly the
   regenerable `branch-15-x187-zero.opb`; it is correctly absent from the
   publication manifest.
2. `W53-PC-C002`: `run-report.yaml` now lists the consumed
   `attempts/wave37-proof-producing-endpoint/branch-15-formula.json` input and
   its correct hash.
3. `W53-PC-C003`: historical RAM readings are labeled self-reported and
   non-replayable, and `--timeout=3` is no longer described as a strict
   whole-process wall.
4. `W53-PC-C004`: the run report now records the corrected
   `bounded-run.json` hash
   `39a49bc0dc363d014b64d89541bab76a739988c06ffb75c09c3641abc90e492c`.

The final discovery manifest SHA-256 is
`b6b5c0de2290e1ed68c42f0ca63328025c456655ebe6328896a97100d08a0c38`.
No discovery correction remains open. None changes the verified cover counts
or mathematical status.

## Final evidence boundary

```text
complete endpoint cases checked UNSAT: 0/33
branch 15:                            UNKNOWN
n3=4158 endpoint:                    UNKNOWN
strict general upper bound <4158:    not proved here
Conway-99:                            UNKNOWN
graph or novelty claim:              none
```
