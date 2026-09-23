# Wave 125: extended motif-SAT scout

Status: `UNKNOWN_TIMEOUT`.

This run gave the verified Wave110 row-lex motif encoding a 900-second
MiniCard search window on branch `eX0=0`.  It preserved the required 15%
host-memory reserve, but returned no model and no proof.

The result is deliberately non-promotional:

- a timeout is not evidence that a graph exists;
- a timeout is not evidence that no graph exists;
- the run emitted no candidate certificate; and
- the solver process ended normally after the requested wall-clock limit.

An initial Windows path-quoting failure was corrected before the substantive
run.  Only `branch0-900s-launch2.*` and `branch0-900s.json` belong to the
public package.
