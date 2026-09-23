# Wave 36 rooted-branch failed routes and engineering boundary

All statuses in this note are discovery-only. None changes the mathematical
status of `n3=4158` or Conway-99.

## Full reverse wedge implications

The compact rooted encoding globally forces every named wedge variable to be
the conjunction it represents. Adding both reverse implications for all
285,852 wedge variables is therefore equivalence-preserving, but the resulting
direct native-cardinality formula was much slower on a branch-4 calibration:

```text
variant:              direct
ordinary clauses:     857,706 after endpoint and branch units
AtMost constraints:   9,324
conflict budget:      100,000
status:               BUDGET_UNKNOWN
solver seconds:       83.0625
decisions:            426,161
propagations:         797,696,737
```

This route improved propagation per decision but increased total propagation
cost too much to justify a five-branch sweep.

## Initial phase calibration

Explicitly assigning the negative initial phase to every variable reproduced
MiniCard's default branch-4 trajectory exactly at 100,000 conflicts. Phase
selection supplied no improvement.

## Fixed-triangle direct clauses

For each of the six branch-fixed triangles through coordinate 2, forbidding a
second perfectly matched triangle gives an exact `P=0` clause family. On every
parent branch this yields 282,774 active clauses after fixed-unit filtering:

```text
length 3:     606
length 5: 282,168
```

The completed branch-4 MiniCard scout still stopped at 100,000 conflicts with
`BUDGET_UNKNOWN`. It is retained in `branch-04-prism-100k.json`. This timeout
has no mathematical evidentiary value.

## Refined fresh-solver sweep

The verified oriented-common-neighbor cover splits the five parents into 33
cases:

```text
parent 4:   4 cases
parent 5:   4 cases
parent 8:   6 cases
parent 10:  8 cases
parent 12: 11 cases
```

The first implementation creates a fresh solver for every case and buffers
all records until terminal completion. This is safe against learned-state
contamination, but repeated parsing of roughly 568,000 clauses dominates
runtime and the terminal-only buffer prevents honest case-level progress
reporting. A nonterminal run was deliberately excluded from the publication
package. No status may be inferred from its elapsed time.

Any continuation should:

1. append and flush one atomic JSONL record after each completed case;
2. support exact-key resume;
3. reuse a single base solver per parent for discovery under assumptions;
4. use fresh proof-producing instances only for apparent `UNSAT`; and
5. independently test the proposed wedge-compressed ternary representation
   before using it.

The wedge-compressed idea replaces the two required edge pairs in a
five-literal prism clause by the existing exact wedge variables. It appears to
turn the 282,168 five-literal clauses into ternary clauses without changing
the satisfying graphs, but it is only a continuation proposal until separately
implemented and checked.
