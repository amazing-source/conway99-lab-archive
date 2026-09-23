# Wave 34 current-source discovery audit

Date: 2026-07-24

Frozen public base:
`0fa5b8161baf8b2a5404a67051b7d61cbc906da3`

Protocol SHA-256:
`60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4`

## Outcome

```text
Conway-99 existence/nonexistence:                       UNKNOWN
n3=708:                                                 UNKNOWN
exact prior Wave-33 six-block/rootless overlap found:   NO, in searched windows
new scoped Lean arithmetic formalization:               CANDIDATE, replay pending
new-to-ledger 2023 SAT framework:                       CITED
current k>=14 rooted-fiber claim:                       CANDIDATE, audit pending
complete 2-(15,3,2) catalogue located:                  NO
novelty or priority:                                    UNKNOWN
```

The strongest permitted sentence is:

> No exact prior result for the unrestricted Wave 34 six-block or rootless
> actual-incidence targets was found in the bounded sources searched on
> 2026-07-24.

That is a search report, not a novelty claim.

## Newly located formalization

Kuberwastaken's public Lean 4.27.0 project, pinned here at
`be7b0ae3394721a4c3a1375008a1dbfca44981fc`, formalizes the arithmetic and
matrix core of a fixed-point-free order-three automorphism restriction. Under
its named certificate inputs, the number of triangular vertex orbits is `6`
or `27`.

The repository is unusually clear about its wall: it does not yet construct
the quotient matrix from a `SimpleGraph (Fin 99)` and an automorphism.
Quotient regularity, orbit-type classification, the trace/multiplicity
formula, and the fixed-triangle congruence remain supplied certificate fields.
The work is therefore relevant scoped formal prior art, not a proof of a
graph theorem and not a resolution. Its public CI success is not this
repository's independent replay.

## Newly located older SAT report

Nathaniel Selub's seven-page 2023 University of Chicago REU report gives a
direct CNF framework with edge, triangle, and quadrilateral auxiliaries,
symmetry discussion, and a rooted-neighborhood reduction. Its final section
lists regularity constraints, improved at-most-one encodings, and additional
edge fixing as next steps. It reports no completed full-domain solve and no
SAT or UNSAT certificate.

The report was absent from the frozen bibliography and should be added after
an independent metadata/scope check. It is prior framework, not evidence that
the Wave 34 encoding is complete or tractable.

## Current rooted certificate claim needing audit

At commit `26b36c540611fa02c95a5a4bd78cd4a582257195`, Harrison Pedrero's
repository claims, conditional on an "honest rooted counting model," that no
vertex has at least 14 C4 fibers. It reports an SAT/LRAT ladder plus a mostly
overlapping exact rational Gram/Euclidean route. The same README says:

- the `k=13` rung has one residual whose proof is being re-verified;
- six `k=14` cores remain dependent on large SAT/LRAT artifacts;
- a third-party clean-machine replay has not occurred; and
- existence/nonexistence of the graph is not established.

The repository also preserves a correction trail after an earlier
unconditional overclaim relied on an unproved forced-edge table. This makes
the new scoped claim worth auditing, but it must remain `CANDIDATE` here until
the exact rooted-model bridge, certificate coverage, and independent
reproduction are checked at the pinned commit.

## Design-domain scale and a restricted corpus

Brendan McKay's combinatorial-generation slides estimate about
`1.5 x 10^21` nonisomorphic `2-(15,3,2)` designs. This is an approximate scale
statement, not an exact classification certificate, but it closes one bad
planning route: naive design-by-design enumeration cannot serve as a
credible unrestricted completeness argument.

The University of Rijeka data index does contain `2-(15,3,2)` incidence
matrices. Its own README says they are derived from `2-(71,15,3)` designs in
Folder 1, and Folder 1 is restricted to designs having an automorphism of
order six. Those files are useful hostile-test inputs only. They cannot be
described as the full design domain.

## Current-status boundary

Brouwer's maintained strongly regular graph table still marks
`(99,14,1,2)` with `?`. This agrees with current-source statements already in
the repository, but no finite status search proves that no unindexed result
exists.

## Required next checks

1. Independently build Kuber's pinned Lean project and inspect the printed
   axiom set and graph-to-certificate interface.
2. Audit Harrison's honest rooted base before touching downstream proof
   outputs; then replay the small exact-rational certificates and inventory
   every SAT/LRAT-only core and unavailable proof body.
3. Independently check Selub's bibliographic metadata and exact CNF semantics
   before adding it to `SOURCES.bib`.
4. Keep the unrestricted Wave 34 tracks free of every automorphism or selected
   design-corpus assumption.

## Limitations

- Ranked search windows and public GitHub search are incomplete.
- No absent hit establishes novelty, priority, openness, or nonexistence.
- No external repository was independently built in this discovery pass.
- No large Git LFS proof body was downloaded or checked.
- No complete design catalogue or complete graph domain was enumerated.
