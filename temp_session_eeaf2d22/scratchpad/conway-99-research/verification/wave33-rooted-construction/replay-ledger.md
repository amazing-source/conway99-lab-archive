# Wave 33 rooted construction: replay ledger

All replays occurred after the clean-room precomparison bytes were frozen and
after static candidate inspection. No replay result is used as proof of
nonexistence.

## Independent hostile-search reproduction

The verifier reimplemented the fixed-design construction, parallel-class and
resolution enumeration, seeded packet initialization, and annealing updates
using only the Python standard library. It did not import or execute
`search_partial_design.py`.

```text
parallel classes per STS: 56
resolutions per STS:      240
restarts completed:       9
steps per restart:        200000
best restart/step:        8 / 166762
best squared defect:      10
certificate SHA-256:      340e5df716ad63bceba25c745ab04c22ea1a3dca01e939072f09775a5fc5f634
byte-identical:           yes
```

## Exact-checker invocation correction

The orchestrator's initial replay omitted the partial-certificate flag:

```text
python -B attempts/wave33-rooted-construction/exact_check.py --output TEMP
exit:    0
SHA-256: 97f30719cc41bb48c3b562faf5bc7037112cd8cf35c737b3717614217a9c1ea1
```

That hash is the frozen `base-results.json`. The command was valid but asked
for base results only. It is an orchestrator replay mistake, not a candidate
defect.

The correct frozen command was then replayed:

```text
python -B attempts/wave33-rooted-construction/exact_check.py --partial-certificate attempts/wave33-rooted-construction/partial-design-certificate.json --output TEMP
exit:    0
SHA-256: ba6640eacd041bc8349024a1d3f13e3d74bd67cdad64d2d78c9a94927319c496
byte-identical to exact-results.json: yes
```

## SciPy/HiGHS metadata replay

The exact frozen restricted-search command was replayed with its output
redirected to a temporary path. The local solver-source and binary hashes
matched `solver-inspection.md`.

```text
exit:                    1
output created:          no
assignment primal:       none
active O-O phase:        not entered
message:                 Time limit reached. (HiGHS Status 13:
                         model_status is Time limit reached;
                         primal_status is None)
```

This confirms the recorded local status metadata only. It is not a solver
certificate and carries no negative mathematical status.
