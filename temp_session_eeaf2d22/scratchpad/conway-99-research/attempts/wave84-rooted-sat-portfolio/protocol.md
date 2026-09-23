# Wave 84 protocol

## Scope

Run a small solver portfolio on the exact complete-domain rooted CNF from
Wave 34.  The formula fixes only the already-forced signed Fano support and
uses no assumed automorphism of a target graph.

## Acceptance rules

- `SAT` requires a complete assignment, direct DIMACS evaluation, decoding,
  and the independent 99-vertex graph checker.
- `UNSAT` requires a complete proof against the exact frozen CNF and an
  independent proof checker.
- A timeout, signal, exit code, preprocessing reduction, or solver log is
  `UNKNOWN`.
- No solver may promote its own output.

## Frozen formula

```text
path: attempts/wave34-rooted-encoding/rooted-complete.cnf
sha256: 2362d15f3a20df0a0d7745eb619a94061cee9911c8dda36c191fb6d728c1c3d3
```

## Replay command templates

Run from the repository root inside WSL:

```text
cadical -t 900 -w result.sol attempts/wave34-rooted-encoding/rooted-complete.cnf
cadical --sat -t 900 -w result.sol attempts/wave34-rooted-encoding/rooted-complete.cnf
cadical --unsat -t 900 -w result.sol attempts/wave34-rooted-encoding/rooted-complete.cnf
build/third-party/kissat/build/kissat --time=900 attempts/wave34-rooted-encoding/rooted-complete.cnf
```

The first three local invocations used absolute equivalents of the displayed
formula and output paths.  Paths are semantically irrelevant to DIMACS
solving; the public commands avoid exposing host-specific directories.

## Provenance boundary

This is a retrospective null-run record, not a pre-frozen proof run.  If a
later solver reports UNSAT, solver, proof format, proof checker, hashes, and
commands must be frozen before the proof-producing rerun.

