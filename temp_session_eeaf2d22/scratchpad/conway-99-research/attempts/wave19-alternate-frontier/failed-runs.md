# Wave 19 alternate-frontier retained failures

These runs are retained to prevent accidental reuse.  None is evidence for
existence or nonexistence.

## 1. Naive exact-cover DFS timed out

A hand-written depth-first search imposed point degree two and rectangle
coverage zero-or-two directly on the exceptional connected point graphs.  The
first high-nullity case did not finish in ten minutes.  The exact process
started by this lane was identified by creation time and full command line and
stopped.  No output or mathematical conclusion was used.

This failure motivated the local-C6 / symmetric-neighborhood reduction in the
final checker.

## 2. Raw SAT and oversized pseudo-Boolean scouts

`python-sat`/CaDiCaL scouts returned raw `UNSAT` on eleven exceptional
girth-five cases.  A separate exploratory binary-Gram CNF for one
two-Petersen model used 754,849 variables and 1,513,138 clauses and returned
raw `UNSAT` after about 462 seconds.  Neither run emitted a checked proof, so
both are `UNSAT_UNVERIFIED` and absent from the final evidence.

The final package replaces them with standard-library exhaustive catalogs,
exact rational linear algebra, and a small integer Farkas certificate.

## 3. Invalid least-eigenvalue `-3` route

An exploratory message proposed checking `A_X+3I` as positive semidefinite.
That premise is false: the target spectrum is `14,3,-4`, so principal
interlacing only gives `A_X+4I` positive semidefinite.  Every conclusion from
the `A_X+3I` kernel scout was discarded.  The corrected nonempty-`Z` path uses
the full exact matrix

```text
B = 12I - A_X - A_X^2 + 2J = C C^T,
```

entrywise nonnegativity, exact positive semidefiniteness, complete binary
column enumeration, exact Gram systems, and the final Farkas inequality.

## 4. Root display/model-extraction scouts

Two non-evidentiary root-side diagnostics were disclosed to this lane and are
recorded for transparency:

1. a display-only `TypeError` attempted to hash an unhashable set after the
   useful local-C6 counts had printed; and
2. an initial SAT-model display assumed primary variable identifiers were at
   most 225 even though an encoder had allocated auxiliary variables.  It
   printed truncated eight-edge rows and was discarded.  A later scout
   preallocated identifiers and asserted 30 selected edges.

The final checker imports neither diagnostic nor any SAT model.

## 5. Background launch quoting failure

The first background launch passed the absolute script path through
`Start-Process` without quoting the workspace space.  Python tried to execute
`<workspace>\[truncated-at-first-space]` and stopped immediately with a
`SyntaxError`.  The path-normalized stderr is retained in `run.stderr.log`.

## 6. Mistyped order-12 pin

The next deterministic run completed the expensive connected order-20 scan
but stopped before writing artifacts because the order-12 SHA-256 constant
omitted the substring `b2`.  A direct refetch confirmed stable upstream bytes:

```text
bytes   1105
sha256  21bab16fbf7db826928315b9ca1d64684c0b1f7014b02fab0c6f2fb2f247104b
records 85
```

The metadata transcription was repaired; no mathematical code changed.  The
exact traceback is retained in `run2.stderr.log`.

## 7. Scout/checker coordinate mismatch

The third deterministic run completed the connected and disconnected
catalog censuses and the exhaustive 120-model two-Petersen orbit check, then
stopped at the assertion identifying the sole non-inconsistent nonempty-`Z`
orbit with a scout witness.  The exact traceback is retained in
`run3.stderr.log`.

This was not treated as a mathematical failure or silently bypassed.  Direct
diagnostics established that the scout coordinate set
`{(0,20),(1,22),(2,23)}` is not even an eligible `Z`-set for the checker's
chosen labeled model: its matrix has a negative entry and rank 29.  Holding
those three coordinates fixed while testing all 120 labeled two-Petersen
models found zero eligible cases.  Thus the copied scout coordinates and
Farkas weights use a different point labeling, rather than identifying the
exact census's residual representative in the current checker coordinates.
The repair must exhibit and check the point relabeling or regenerate an exact
certificate in the current coordinates; removing or weakening the orbit
assertion is not permitted.

An attempted diagnostic relaunch repeated the absolute-path quoting failure
from item 5 and stopped before executing the checker.  Its stderr is retained
separately in `run4.stderr.log`.

The next correctly launched replay retained the hard assertion and printed
both canonical representatives:

```text
withdrawn scout canonical: ((0,15),(3,23),(4,28))
exact residual canonical:  ((0,23),(1,22),(2,17))
```

Its traceback is retained in `run5.stderr.log`.  The old scout-coordinate
witness and its weights are withdrawn, not relabeled by assumption.  A fresh
exact separator was subsequently derived for the exact residual in the
checker's own coordinates and is checked against every candidate binary
support by the final package.
