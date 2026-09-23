# Native-cardinality discovery backend

> **Record type:** synthesis note, not a run manifest. Reproducible commands,
> source commits, and artifact hashes are recorded in the linked Wave 2 and
> Wave 3 verifier reports; this note makes no independent verification claim.

Status: `VERIFIED_ENCODING`; target result: `UNKNOWN`

Scope: exact representation of the rooted residual equations

Automorphism assumption: none

## Representation

The compact encoding's ordinary wedge clauses are retained:

```text
(x[p,r] and x[q,r]) -> y[p,q;r].
```

Every equality `sum(L)=k` is represented as the two native constraints

```text
AtMost(L,k)
AtMost(not L, |L|-k),
```

and each pair capacity remains the native constraint

```text
sum_r y[p,q;r] + x[p,q] <= 2 - |label(p) intersection label(q)|.
```

This is a change of representation only. The existing global-saturation proof
still applies: the profile equations force 504 residual edges and therefore
5,544 actual wedges, while the sum of all pair capacities after accounting for
the 924 intersecting label pairs and 504 edges is also 5,544. Every actual
wedge forces its named `y` variable, so equality of the global sums makes every
local upper bound exact.

For `pair_count=7`, the deterministic counts are:

| item | count |
|---|---:|
| residual edge variables | 3,486 |
| named wedge variables | 285,852 |
| all variables | 289,338 |
| ordinary clauses | 285,852 |
| native `AtMost` constraints | 5,838 |

The `AtMost` count is

```text
2 * (14 * 84) + binom(84,2) = 5,838.
```

## Independent review and controls

An adversarial verifier regenerated the constraints without the discovery
script, exhaustively compared all 64 primary assignments for `pair_count=2`,
and found exact agreement among the rooted semantics, sequential-counter CNF,
and native formulation. The sole satisfying assignment decodes to the
`srg(9,4,1,2)` calibration graph and passes both independent certificate
validators.

Both complete `pair_count=3` branches return `UNSAT`, but MiniCard's result is
not itself evidence. The same branch-unit CNFs were separately solved by
CaDiCaL 3.0.1, converted from DRAT to LRAT by `drat-trim`, and accepted by the
independent `lrat-check` calibration path.

At conflict limits of 10,000 and 100,000, all 11 complete target branches
returned `UNKNOWN`. Those bounded runs are explicitly `NON_EVIDENTIARY`.
Recorded wall times compare implementations, not mathematical progress, and
conflict counts from different solvers are not directly comparable.

The public committed-code reproduction at 10,000 conflicts is
`logs/2026-07-22-native-10000.json`; its source and output hashes are recorded
in `logs/2026-07-22-wave2.json`.

## Certificate boundary

Embedded MiniCard is used only to find candidate models or rank branches. A
SAT model must decode to a complete graph and pass independent validators. An
apparent UNSAT result must be regenerated either as ordinary DIMACS or as the
exact native-cardinality OPB export, solved by a pinned proof-producing solver,
and replayed with independent proof checkers. A nonexistence claim must cover
an explicitly proved complete search split; the legacy split has 11 branches,
while a theorem-forced `N3` normalization uses a different stabilizer and must
not be naively intersected with those representatives.
