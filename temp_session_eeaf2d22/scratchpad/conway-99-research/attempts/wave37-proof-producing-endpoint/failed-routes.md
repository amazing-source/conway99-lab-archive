# Wave 37 proof-producing formula corrections and boundaries

## Metadata path correction

The first successful export wrote a Windows-backslash path to its JSON
metadata. The exporter was changed to use a repository-relative POSIX path
and the formula and metadata were regenerated. The OPB bytes did not change:

```text
SHA-256 4c1607f4aef7e20569592ccb4ac20dfe30c1e1d220a8fbc0a202554bed6d84e5
```

## Interpreter mismatch

The first root-level unit-test command used the Windows Store Python rather
than the repository virtual environment and failed during import:

```text
ModuleNotFoundError: No module named 'pysat'
```

The exact same suite passed under `.\.venv\Scripts\python.exe`. The failed
run is an environment error and supplies no evidence about the formula.

## Initial WSL quoting error

An initial `--onlyparse` invocation split the formula path at its spaces and
produced a false parser diagnostic about the first line. The command was
corrected by quoting the full WSL path inside the Bash command. The pinned
Exact binary then accepted the formula with exit code zero. The failed shell
invocation is not a formula failure.

## Deliberately omitted bounded solve

No short Exact solving run was published. Earlier calibrated target-scale
timeouts generated proofs larger than 100 MB whose checked conclusion was
only `NO CONCLUSION`. Such a run has zero mathematical evidentiary value and
would compete with two healthy discovery processes already in progress.

The next valuable computational event is either:

1. a candidate assignment, followed by independent full-graph validation; or
2. a terminal `UNSAT` result with a retained proof accepted by independent
   VeriPB and CakePB replay.

Until then, branch 15, the whole `n3=4158` endpoint, and Conway-99 are
`UNKNOWN`.
