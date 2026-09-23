# Wave 60 failed routes and exact boundary

## The finite-field rank cut is redundant

Every incidence column has even intersection with each of the three fibres
and each of the three components.  The six indicator vectors span dimension
five, so over `F2` one has `rank(B)<=31`; because `BB^T` is alternating, its
rank must be even and at most 30.

The complete exact scan did not eliminate a component triple.  Across all
1,140 fibre-preserving type multisets the target ranks are only
`14,16,18,20,22,24`.  This is a checked failure of the proposed obstruction,
not evidence that an incidence design exists.

## Positive support is not the obstruction

Each component triple has between 15,936 and 27,200 distinct columns that
individually obey the fibre/component profiles and avoid zero Gram pairs.
There is no support-empty triple.  The aligned type-4 control has 20,928
candidates and all 21 formal component-pattern matrices occur.  Individual
abundance does not address simultaneous exact multiplicities.

## Bounded SAT remains unknown

For the aligned type triple `(4,4,4)`, the compressed CNF has:

- 20,928 candidate variables;
- 953,580 variables including sequential-counter auxiliaries;
- 1,971,780 clauses;
- 588 nontrivial exact off-diagonal Gram constraints.

Glucose 4.2 consumed 10,431 conflicts, 134,788 decisions, and 79,165,487
propagations in 25.29 solver seconds and returned `UNKNOWN`.  This run has no
proof and supplies no nonexistence evidence.

An earlier sequential-counter/CaDiCaL probe was stopped after it proved much
slower than the bounded Glucose telemetry; it emitted no result artifact.
MiniCard's native cardinality interface reached a Windows access violation
after larger conflict budgets.  Its 1,000-conflict smoke result was
`UNKNOWN`, but the unstable native route is not retained as evidence.

## Exact-marginal local search remains positive-error

The within-component Gram equations prescribe exactly sixty local pair
occurrences per component.  A memory-light search kept those marginals exact
and varied only their three-way coupling.  For aligned type `(4,4,4)`, the
best squared cross-Gram error was 88 for symmetric pattern ledgers with
`x_AAA=0` and `x_AAA=6`, and 104 for `x_AAA=12`.  For the smaller-candidate
type `(0,0,0)`, the best errors were 84, 88, and 82 respectively.  All best
states had no duplicate columns.

These searches use two-occurrence swaps in fixed aggregate pattern ledgers.
They are heuristic, do not cover asymmetric values of `x_AAA`, and cannot
certify infeasibility.

## Remaining exact wall

The safe simultaneous fibre relabelling reduces 1,140 component triples to
275 coordinate orbits.  A complete incidence result still requires either:

1. a directly checked 60-column matrix for one orbit representative; or
2. checkable UNSAT proofs, or an independently replayable exhaustive
   enumeration, for all 275 representatives.

No such candidate or complete exclusion is supplied here.  The conditional
`kappa=3` case and the Conway endpoint remain `UNKNOWN`.
