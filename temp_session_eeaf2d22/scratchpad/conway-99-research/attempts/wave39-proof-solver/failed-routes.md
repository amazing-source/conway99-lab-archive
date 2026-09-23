# Wave 39 proof-solver failed and deferred routes

## Full proof-producing OPB solve

Initially deferred for resource safety. The host reported approximately
2.5 MiB of free physical memory and WSL failed to start with `HCS/0x800705aa`
(insufficient system resources). After memory recovered, the propagation-local
shard was run through pinned Exact and VeriPB. Exact emitted an UNSAT proof;
raw replay, elaboration, and strict kernel replay all passed.

CakePB was started, but the enclosing task was interrupted before the checker
emitted any result. The lane-owned checker process was terminated and its
empty transcript removed. CakePB status is therefore `NO_CONCLUSION`, not a
failure or success.

## Existing embedded scouts

The Gluecard4 all-33 scout and MiniCard parent-4 scout were observed alive and
CPU-active. Neither output file existed. Their scripts write only after the
entire selected queue finishes, so no completed prefix can be harvested.
They were not signaled, attached to, stopped, or modified.

## PySAT proof logging

The installed PySAT bindings expose DRUP logging for several CNF solvers, but
the endpoint OPB contains 5,838 native cardinality constraints. Translating
those constraints to sequential-counter CNF would materially increase memory
use, and no independent DRAT/LRAT checker is on the Windows `PATH`. A solver
return or unchecked DRUP body would not be a certificate, so this route was
not launched at target scale.

## Static all-prism OPB

Rejected as impractical. The complete static schema contains at least
24,388,892,640 residual-only prism clauses before branch simplification.
Wave 38's exact lazy oracle remains the appropriate global-prism route.

## What was completed instead

A four-constraint generalized-unit certificate closes the exact positive
`x187` polarity shard inside refined branch 15. This is a real logical
reduction, but it closes no complete endpoint case. Complete proof coverage
therefore remains `0/33`.
