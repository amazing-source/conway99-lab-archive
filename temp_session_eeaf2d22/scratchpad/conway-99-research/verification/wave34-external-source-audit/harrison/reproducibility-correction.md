# Harrison Lane E2 reproducibility correction

Date: 2026-07-24

The first verifier release serialized
`cnf_recipe_replay.elapsed_seconds` in `results.json`. An orchestrator rerun
therefore changed the result hash even though all 1,302 recipe hashes and
every mathematical verdict agreed.

The failed first-release result hash was:

```text
1366e8c5d7461d854966077f4d4bdee5a4a7ebd4c088730058af29fc8fd36d3c
```

The verifier was repaired by removing wall-clock time and normalizing local
temporary paths in the machine-readable result. No mathematical field, input,
recipe, certificate availability finding, or status was changed.

The orchestrator then ran the exact isolated-venv command twice. Both runs
returned:

```text
ok=true
recipe_replay=VERIFIED
k_ge_14=UNKNOWN
k13=UNKNOWN
r230_unsat=UNKNOWN
```

Both runs produced the same corrected `results.json` SHA-256:

```text
0d9ea150bb86e33c00f46e72620dec61e0a2b84c130597596299d80ab8e8baf2
```

This correction is reproducibility-only. It neither promotes any unavailable
proof body nor changes the scoped source-audit conclusions.
