# Wave 53 proof-cover correction ledger

These corrections were requested by the independent Wave 53 verifier before
publication. They do not change the conditional branch cover, formula bytes,
proof bytes, or `NO CONCLUSION` mathematical status.

## W53-PC-C001: raw OPB ignore rule

The README said that the 29.8 MB raw OPB was ignored and regenerated from the
published deterministic gzip. It was absent from the package manifest, but no
matching Git ignore rule existed. A package-local `.gitignore` now excludes
exactly `branch-15-x187-zero.opb`.

## W53-PC-C002: complete run-report input list

`input-freeze.sha256` and the coverage certificate correctly pinned
`attempts/wave37-proof-producing-endpoint/branch-15-formula.json`, but the
human run report omitted it from its input list. The run report now records
that already-consumed source metadata and hash.

## W53-PC-C003: resource telemetry boundary

The discovery recorder embedded two interactively observed free-memory
percentages without retaining a raw monitor transcript. Those historical
values are now explicitly labeled self-reported and not independently
replayable; they are not used as mathematical evidence. The independent
verifier records its own fresh resource observation separately.

The Exact `--timeout=3` flag is also described as a solver timeout setting,
not a strict three-second process wall: parsing and presolve can run outside
the effective search interval.

## W53-PC-C004: corrected bounded-run output hash

After W53-PC-C003 regenerated `bounded-run.json`, the run report temporarily
retained the pre-correction output hash. The independent verifier caught the
stale reference during focused reseal review. The run report now records the
corrected artifact hash
`39a49bc0dc363d014b64d89541bab76a739988c06ffb75c09c3641abc90e492c`.
